---
title: "Making SQL Keyword Suggestions Work"
summary: "Implementing levenshtein distance naïvely (and very slow) in Rust"
date: 2024-11-23
math: true
tags:
  - rust
  - sqleibniz
  - sql
---

_Taken from [Why I love Rust for tokenising and parsing](/posts/2024/rust-pldev/)_:

> I am currently writing a analysis tool for Sql:
> [`sqleibniz`](https://github.com/xnacly/sqleibniz), specifically for the
> sqlite dialect.
>
> The goal is to perform static analysis for sql input, including: syntax
> checks, checks if tables, columns and functions exist. Combining this with an
> embedded sqlite runtime and the ability to assert conditions in this runtime,
> creates a really great dev experience for sql.
>
> Furthermore, I want to be able to show the user high quality error messages
> with context, explainations and the ability to mute certain diagnostics.
>
> This analysis includes the stages of lexical analysis/tokenisation, the
> parsing of SQL according to the sqlite documentation[^sqlite-sql-docs] and
> the analysis of the resulting constructs.
>
> After completing the static analysis part of the project, I plan on writing a
> lsp server for sql, so stay tuned for that.

[^sqlite-sql-docs]: https://www.sqlite.org/lang.html

## The Problem: Inaccurate and Incomplete diagnostics

This post is about the SQL keyword suggestions implementation: If the input
contains an identifier at a point at which a SQL keyword was expected, the
sqleibniz parser should generate a diagnostic containing a suggestions for a
keyword the identifier could be.

For example, misspelling the `SELECT` keyword:

```sql
SELET INDEX username;
```

Invoking sqleibniz with these statements results in the following diagnostic:

```text
error[Unimplemented]: Unknown Token
 -> /home/teo/programming/sqleibniz/example/stmt.sql:1:1
 01 | SELET INDEX username;
    | ^^^^^ error occurs here.
    |
    ~ note: sqleibniz does not understand the token Ident("SELET"), skipping ahead to next statement
  * Unimplemented: Source file contains constructs sqleibniz does not yet understand
=============================== Summary ================================
[-] example/stmt.sql:
    1 Error(s) detected
    0 Error(s) ignored

=> 0/1 Files verified successfully, 1 verification failed.
```

However, this diagnostic is really not that useful. The parser knows it expects
a keyword and a keyword can only be one of the list of known keywords. The
parser thus should propagate this knowledge to the user. Sqleibniz now does
exactly this.

## The Solution: A new Diagnostic

```text
error[UnknownKeyword]: Unknown Keyword
 -> /home/teo/programming/sqleibniz/example/stmt.sql:1:1
 01 | SELET INDEX username;
    | ^^^^^ error occurs here.
    |
    ~ note: 'SELET' is not a know keyword, did you mean:
        - SELECT
        - SET
        - LEFT
  * UnknownKeyword: Source file contains an unknown keyword
=============================== Summary ================================
[-] example/stmt.sql:
    1 Error(s) detected
    0 Error(s) ignored

=> 0/1 Files verified successfully, 1 verification failed
```

This reworked diagnostic includes a specific new rule: `Rule::UnknownKeyword`,
this rule is used for all identifiers found at a point where a keyword should
have occured. Furthermore the `note` of the diagnostic includes a list of, at
most three, known keywords similar to the found identifier.

## Computing similarity of two words

> There is a list of algorithms to choose from when attempting to classify the
> similarity of two strings, for instance:
>
> - [Hamming Distance](https://en.wikipedia.org/wiki/Hamming_distance)
> - [Simple matching coefficient](https://en.wikipedia.org/wiki/Simple_matching_coefficient)
> - [Jaro–Winkler distance](https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance)
> - [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)

I choose the last item of that list: the _levenshtein_ distance.

### The Idea

The idea of the levenshtein distance is to compute the minimum number of
insertions, deletions and substitutions of characters to change a word `a` to a
word `b`. The naïve and slow implementation is fairly easy to code up, the
wikipedia article linked above already includes a nice mathematical definition of:

$$
\textrm{lev}(a,b)
\begin{cases}
    |a| & |b| = 0 \\
    |b| & |a| = 0 \\
    \textrm{lev}(\textrm{tail}(a), \textrm{tail}(b)) & \textrm{head}(a) = \textrm{head}(b) \\
    1 + \textrm{min}
    \begin{cases}
        \textrm{lev}(\textrm{tail}(a), b) \\
        \textrm{lev}(a, \textrm{tail}(b)) \\
        \textrm{lev}(\textrm{tail}(a), \textrm{tail}(b)) \\
    \end{cases} & \textrm{otherwise}
\end{cases}
$$

> If you do now know this notation, the left part of the definition is the
> operation to execute, the right side is the condition for this to happen, for
> instance `|a| |b| = 0` resolves to returning the length of `a` if the
> length of `b` is equal to 0. Other useful bits to know regarding this notation:
>
> - `|x|`: length of `x`
> - `head(x)`: first character of `x`
> - `tail(x)`: all characters except the first of `x`

Levenshtein works like this: If either of `a` or `x` is equal to `0`, return
the other. If the first characters are equal, return the distance of both the
tails. Otherwise, the distance is equal to one plus the lowest value of either
the insertion (line 1), deletion (line 2) or the substitution (line 3):

$$
1 + \textrm{min}
\begin{cases}
    \textrm{lev}(\textrm{tail}(a), b) \\
    \textrm{lev}(a, \textrm{tail}(b)) \\
    \textrm{lev}(\textrm{tail}(a), \textrm{tail}(b)) \\
\end{cases}
$$

### The Implementation

Implementing this is a one to one match to the above definitions:

```rust
pub fn distance(a: &[u8], b: &[u8]) -> usize {
    if b.len() == 0 {
        a.len()
    } else if a.len() == 0 {
        b.len()
    } else if a[0] == b[0] {
        return distance(
            a.get(1..).unwrap_or_default(),
            b.get(1..).unwrap_or_default(),
        );
    } else {
        let first = distance(a.get(1..).unwrap_or_default(), b);
        let second = distance(a, b.get(1..).unwrap_or_default());
        let third = distance(
            a.get(1..).unwrap_or_default(),
            b.get(1..).unwrap_or_default(),
        );
        let mut min = first;
        if min > second {
            min = second
        }
        if min > third {
            min = third
        }
        1 + min
    }
}
```

I took a test from the wikipedia article:

```rust
#[cfg(test)]
mod lev {
    use super::distance;

    #[test]
    fn kitten_sitting() {
        // https://en.wikipedia.org/wiki/Levenshtein_distance#Example
        assert_eq!(distance("kitten".as_bytes(), "sitting".as_bytes()), 3);
    }
}
```

## Hooking it up to the diagnostic creation in the parser

I then created a list of the already known keywords, mapped it to a tuple of
their `distance` value with the identifier found and the keyword itself.
Collecting these tuples into a binary tree map (`BTreeMap`) and extracting the
values in this map sorts these keywords according to their distance to the
identifier, I only want the top three, so I take these:

```rust
impl Keyword {
    /// suggestions returns three suggestions based on their smallest Levenshtein_distance computed via lev::distance
    pub fn suggestions(s: &str) -> Vec<&str> {
        let input = s.to_uppercase();
        let bytes = input.as_bytes();
        vec![
            "ABORT",
            // .....
            "WITHOUT",
        ]
        .into_iter()
        .map(|keyword| (lev::distance(bytes, keyword.as_bytes()), keyword))
        .collect::<BTreeMap<usize, &str>>()
        .into_values()
        .take(3)
        .collect()
    }
}
```

> `Keyword` is the value enclosed in `Type::Keyword` and holds all possible SQL keywords.

If a top level token with the `Type::Ident` is found, the diagnostic is
generated:

```rust
/// Function naming directly corresponds to the sqlite3 documentation of sql syntax.
///
/// ## See:
///
/// - https://www.sqlite.org/lang.html
/// - https://www.sqlite.org/lang_expr.html
impl<'a> Parser<'a> {
    /// see: https://www.sqlite.org/syntax/sql-stmt.html
    fn sql_stmt(&mut self) -> Option<Box<dyn nodes::Node>> {
        let r = match self.cur()?.ttype {
            // ....
            Type::Ident(_) => {
                if let Type::Ident(name) = &self.cur()?.ttype {
                    self.errors.push(self.err(
                        "Unknown Keyword",
                        &format!(
                            "'{}' is not a know keyword, did you mean: \n\t- {}",
                            name,
                            Keyword::suggestions(name).join("\n\t- ").as_str()
                        ),
                        self.cur()?,
                        Rule::UnknownKeyword,
                    ));
                }
                self.skip_until_semicolon_or_eof();
                None
            }

        };
        // ...
    }
}
```

Generating a diagnostic with my architecture works by pushing diagnostics into
the array in the `Parser.errors` field - an error is created via `Parser.err`,
this method fills the values of the `error::Error` structure with a title, the
position in the source code and a note. These errors are then passed to a
formatter in the `error` module. This module is responsible for implementing
the pretty printing of the diagnostic locations and the color highlighting.

The whole implementation is probably not the fastest or even remotely efficient
way of doing it, I will switch to a matrix approach, as described in
[Wagner–Fischer
algorithm](https://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm).
Once I've done so, I will also use the `lev::distance` function to suggest
column names and table names.
