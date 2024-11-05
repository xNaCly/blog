---
title: "Why I love Rust for tokenising and parsing"
summary: "Macros, iterators, patterns, error handling and match make Rust almost perfect"
date: 2024-11-04
draft: true
tags:
- rust
- sql
---

> I am currently writing a analysis tool for Sql: [`sqleibniz`](github.com/xnacly/sqleibniz), specifically for the sqlite
> dialect. 
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
>
> After completing the static analysis part of the project, I plan on writing a
> lsp server for sql, so stay tuned for that.

[^sqlite-sql-docs]: https://www.sqlite.org/lang.html

In the process of the above, I need to write a tokenizer and a parser - both
for SQL. While I am nowhere near completion of sqleibniz, I still made some
discoveries around rust and the handy features the language provides for
developing said software.

## Macros

Macros work different in most languages. However they are used for mostly the
same reasons: code deduplication and less repetition.

### AST Macros

A node for a statement in `sqleibniz` implementation is defined as follows:

{{<callout type="Tip">}}
The example shows the `Literal`-node. `Token` is defined in
[src/types/mod.rs](https://github.com/xNaCly/sqleibniz/blob/master/src/types/mod.rs#L97-L102).
{{</callout>}}


```rust

#[derive(Debug)]
/// holds all literal types, such as strings, numbers, etc.
pub struct Literal {
    pub t: Token,
}
```

Furthermore all nodes are required to implement the `Node`-trait, this trait
is returned by all parser functions and is later used to analyse the contents
of a statement:

```rust
pub trait Node: std::fmt::Debug {
    fn token(&self) -> &Token;
}
```

{{<callout type="Tip">}} `std::fmt::Debug` is used as a super trait for the
`Node`-trait here, see [Using Supertraits to Require One Trait’s Functionality
Within Another
Trait](https://doc.rust-lang.org/book/ch19-03-advanced-traits.html#using-supertraits-to-require-one-traits-functionality-within-another-trait)

**TLDR**:
_using a super trait enables us to only allow implementations of the `Node`
trait if the type already satisfies the `std::fmt::Debug` trait._
{{</callout>}}


#### Code duplication

Thus every node not only has to be defined, but an implementation for the
`Node`-trait has to be written. This requires a lot of code duplication and
rust has a solution for that. 

I want a macro that is able to:

- define a structure with a given identifier and a doc comment
- add arbitrary fields to the structure
- satisfying the `Node` trait by implementing `fn token(&self) ->&Token`

Lets take a look at the full code I need the macro to produce for the
`Literal` and the `Explain` nodes. While the first one has no further fields
except the `Token` field `t`, the second node requires a child field with a
type.

```rust
#[derive(Debug)]
/// holds all literal types, such as strings, numbers, etc.
pub struct Literal {
    /// predefined for all structures defined with the node! macro
    pub t: Token,
}
impl Node for Literal {
    fn token(&self) -> &Token {
        &self.t
    }
}


#[derive(Debug)]
/// Explain stmt, see: https://www.sqlite.org/lang_explain.html
pub struct Explain {
    /// predefined for all structures defined with the node! macro
    pub t: Token,
    pub child: Option<Box<dyn Node>>,
}
impl Node for Explain {
    fn token(&self) -> &Token {
        &self.t
    }
}
```

I want the above to be generated from the following two calls:

```rust
node!(
    Literal,
    "holds all literal types, such as strings, numbers, etc.",
);
node!(
    Explain,
    "Explain stmt, see: https://www.sqlite.org/lang_explain.html",
    child: Option<Box<dyn Node>>,
);
```

#### Code deduplication with macros

The macro for that is fairly easy, even if the rust macro docs arent that good:

```rust
macro_rules! node {
    ($node_name:ident,$documentation:literal,$($field_name:ident:$field_type:ty),*) => {
        #[derive(Debug)]
        #[doc = $documentation]
        pub struct $node_name {
            /// predefined for all structures defined with the node! macro, holds the token of the ast node
            pub t: Token,
            $(
                pub $field_name: $field_type,
            )*
        }
        impl Node for $node_name {
            fn token(&self) -> &Token {
                &self.t
            }
        }
    };
}
```

Lets disect this macro. The Macro argument/metavariable definition starts with
`$node_name:ident,$documentation:literal`:

```text
$node_name : ident , $documentation : literal
^^^^^^^^^^ ^ ^^^^^ ^
|          | |     |
|          | |     metavariable delimiter
|          | |
|          | metavariable type
|          |
|          metavariable type delimiter
|
metavariable name
```

Meaning, we define the first metavariable of the macro to be a valid
identifier rust accepts and the second argument to be a literal. A literal
refers to a literal expression, such as chars, strings or raw strings.

{{<callout type="Tip">}}
For the `literal` and the `ident` meta variable types, see [Literal
expressions](https://doc.rust-lang.org/reference/expressions/literal-expr.html)
and [Identifiers](https://doc.rust-lang.org/reference/identifiers.html). For
the whole metavariable type reference, see
[Metavariables](https://doc.rust-lang.org/reference/macros-by-example.html#metavariables).
{{</callout>}}

The tricky part that took me some time to grasp is the way of defining
repetition of metavariables in macros, specifically `$($field_name:ident:$field_type:ty),*`.

```text
$($field_name:ident:$field_type:ty),*
^^                 ^              ^ ^
|                  |              | | 
|                  metavariable   | repetition  
|                  delimiter      | (any) 
|                                 | 
     sub group of metavariables
```

As I understand, we define a subgroup in our metavarible definition and
postfix it with its repetition. We use `:` to delimit inside the metavariable
sub-group, this enables us to write the macro in a convienient `field_name:
type` way:

```rust
node!(
    Example,
    "Example docs", 

    // sub group start
    field_name: &'static str,
    field_name1: String
    // sub group end
);
```

We can use the `$(...)*` syntax to "loop over" our sub grouped metavariables,
and thus create all fields with their respective names and types:

```rust
pub struct $node_name {
    pub t: Token,
    $(
        pub $field_name: $field_type,
    )*
}
```

{{<callout type="Tip">}}
See
[Repetitions](https://doc.rust-lang.org/reference/macros-by-example.html#repetitions)
for the metavariable repetition documentation.
{{</callout>}}

Remember: the `$documentation` metavariable holds a literal containing our doc
string we want to generate for our node - we now use the `#[doc = ...]`
annotation instead of the commonly known `/// ...` syntax to pass our macro
metavariable to the compiler:

```rust
#[doc = $documentation]
pub struct $node_name {
    // ...
}
```

I'd say the trait implementation for each node is pretty self explanatory.

### Test Macros

Lets start off with me saying: I love table driven tests and the way Go allows
to write them:

```go
func TestLexerWhitespace(t *testing.T) {
    cases := []string{"","\t", "\r\n", " "}
    for _, c := range cases {
        t.Run(c, func (t *testing.T) {
            l := Lexer{}
            l.init(c)
            l.run()
        })
    }
}
```

In Go, I define an array of cases and just execute a test function for each
case `c`. As far as I know, Rust does not offer a similar test method - so
made one 😼. 

#### Lexer / Tokenizer Tests

```rust
#[cfg(test)]
mod should_pass {
    test_group_pass_assert! {
        string,
        string: "'text'"=vec![Type::String(String::from("text"))],
        empty_string: "''"=vec![Type::String(String::from(""))],
        string_with_ending: "'str';"=vec![Type::String(String::from("str")), Type::Semicolon]
    }

    // ...
}

#[cfg(test)]
mod should_fail {
    test_group_fail! {
        empty_input,
        empty: "",
        empty_with_escaped: "\\",
        empty_with_space: " \t\n\r"
    }

    // ...
}
```

Executing these via `cargo test`, results in the same output I love from table
driven tests in Go, each function having its own log and feedback
(`ok`/`fail`):

```text
running 68 tests
test lexer::tests::should_pass::string::empty_string ... ok
test lexer::tests::should_pass::string::string ... ok
test lexer::tests::should_pass::string::string_with_ending ... ok
test lexer::tests::should_fail::empty_input::empty ... ok
test lexer::tests::should_fail::empty_input::empty_with_escaped ... ok
test lexer::tests::should_fail::empty_input::empty_with_space ... ok

test result: ok. 68 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; 
finished in 0.00s
```

The macro accepts the name of the test group, for example: `booleans` and
`string` and a list of input and expected output pairs. The input is passed to
the `Lexer` initialisation and the output of the `Lexer.run()` is compared
against the expected output. Inlining the `test_group_pass_assert!` call for
`string` results in the code below. Before asserting the equality of the
resulting token types and the expected token types, a transformation is
necessary, I map over the token vector and only return their types.

```rust
mod string {
    use crate::{lexer, types::Type};

    #[test]
    fn string() {
        let input = "'text'".as_bytes().to_vec();
        let mut l = lexer::Lexer::new(&input, "lexer_tests_pass");
        let toks = l.run();
        assert_eq!(l.errors.len(), 0);
        assert_eq!(
            toks.into_iter().map(|tok| tok.ttype).collect::<Vec<Type>>(),
            (vec![Type::String(String::from("text"))])
        );
    }

    #[test]
    fn empty_string() {
        let input = "''".as_bytes().to_vec();
        let mut l = lexer::Lexer::new(&input, "lexer_tests_pass");
        let toks = l.run();
        assert_eq!(l.errors.len(), 0);
        assert_eq!(
            toks.into_iter().map(|tok| tok.ttype).collect::<Vec<Type>>(),
            (vec![Type::String(String::from(""))])
        );
    }

    #[test]
    fn string_with_ending() {
        let input = "'str';".as_bytes().to_vec();
        let mut l = lexer::Lexer::new(&input, "lexer_tests_pass");
        let toks = l.run();
        assert_eq!(l.errors.len(), 0);
        assert_eq!(
            toks.into_iter().map(|tok| tok.ttype).collect::<Vec<Type>>(),
            (vec![Type::String(String::from("str")), Type::Semicolon])
        );
    }
}
```

The counter part `test_group_fail!` for `empty_input!` produces the code below.
The main difference being the assertion of the resulting token vector to be
empty and the `Lexer.errors` field to contain at least on error.

```rust
mod empty_input {
    use crate::lexer;

    #[test]
    fn empty() {
        let source = "".as_bytes().to_vec();
        let mut l = lexer::Lexer::new(&source, "lexer_tests_fail");
        let toks = l.run();
        assert_eq!(toks.len(), 0);
        assert_ne!(l.errors.len(), 0);
    }

    #[test]
    fn empty_with_escaped() {
        let source = "\\".as_bytes().to_vec();
        let mut l = lexer::Lexer::new(&source, "lexer_tests_fail");
        let toks = l.run();
        assert_eq!(toks.len(), 0);
        assert_ne!(l.errors.len(), 0);
    }

    #[test]
    fn empty_with_space() {
        let source = " \t\n\r".as_bytes().to_vec();
        let mut l = lexer::Lexer::new(&source, "lexer_tests_fail");
        let toks = l.run();
        assert_eq!(toks.len(), 0);
        assert_ne!(l.errors.len(), 0);
    }
}
```

Lets take a look at the macros itself, I will not go into detail around the
macro definition - simply because I explained the meta variable declaration in
the previous [chapter](#code-deduplication-with-macros). The first macro is
uesd for the assertions of test with valid inputs - `test_group_pass_assert!`:

```rust
macro_rules! test_group_pass_assert {
    ($group_name:ident,$($ident:ident:$input:literal=$expected:expr),*) => {
    mod $group_name {
        use crate::{lexer, types::Type};

        $(
            #[test]
            fn $ident() {
                let input = $input.as_bytes().to_vec();
                let mut l = lexer::Lexer::new(&input, "lexer_tests_pass");
                let toks = l.run();
                assert_eq!(l.errors.len(), 0);
                assert_eq!(toks.into_iter().map(|tok| tok.ttype).collect::<Vec<Type>>(), $expected);
            }
        )*
        }
    };
}
```

While the second is used for invalid inputs and edge case testing with expected
errors - `test_group_fail!`:

```rust
macro_rules! test_group_fail {
    ($group_name:ident,$($name:ident:$value:literal),*) => {
        mod $group_name {
        use crate::lexer;
        $(
            #[test]
            fn $name() {
                let source = $value.as_bytes().to_vec();
                let mut l = lexer::Lexer::new(&source, "lexer_tests_fail");
                let toks = l.run();
                assert_eq!(toks.len(), 0);
                assert_ne!(l.errors.len(), 0);
            }
         )*
        }
    };
}
```


#### Parser Tests

I use the same concepts and almost the same macros in the `parser` module to
test the results the parser produces, but this time focussing on edge cases and
full sql statements. For instance the tests expected to pass and to fail for
the `EXPLAIN` sql statement:

```rust
#[cfg(test)]
mod should_pass {
    test_group_pass_assert! {
        sql_stmt_prefix,
        explain: r#"EXPLAIN VACUUM;"#=vec![Type::Keyword(Keyword::EXPLAIN)],
        explain_query_plan: r#"EXPLAIN QUERY PLAN VACUUM;"#=vec![Type::Keyword(Keyword::EXPLAIN)]
    }
}

#[cfg(test)]
mod should_fail {
    test_group_fail! {
        sql_stmt_prefix,
        explain: r#"EXPLAIN;"#,
        explain_query_plan: r#"EXPLAIN QUERY PLAN;"#
    }
}
```

Both macros get the `sql_stmt_prefix` as their module names, because thats the
function, in the parser, responsible for the `EXPLAIN` statement. The failing
tests check wheter the parser correctly asserts the conditions the sql standard
lays out, see [sqlite - sql-stmt](https://www.sqlite.org/syntax/sql-stmt.html).
Specifically, either that a statement follows after the `EXPLAIN` identifier or
the `QUERY PLAN` and a statement follow.

The difference between these tests and the tests for the lexer are in the way
the assertions are made. Take a look at the code the macros produce:

```rust
#[cfg(test)]
mod should_pass {
    mod sql_stmt_prefix {
        use crate::{lexer, parser::Parser, types::Keyword, types::Type};

        #[test]
        fn explain() {
            let input = r#"EXPLAIN VACUUM;"#.as_bytes().to_vec();
            let mut l = lexer::Lexer::new(&input, "parser_test_pass");
            let toks = l.run();
            assert_eq!(l.errors.len(), 0);
            let mut parser = Parser::new(toks, "parser_test_pass");
            let ast = parser.parse();
            assert_eq!(parser.errors.len(), 0);
            assert_eq!(
                ast.into_iter()
                    .map(|o| o.unwrap().token().ttype.clone())
                    .collect::<Vec<Type>>(),
                (vec![Type::Keyword(Keyword::EXPLAIN)])
            );
        }

        #[test]
        fn explain_query_plan() {
            let input = r#"EXPLAIN QUERY PLAN VACUUM;"#.as_bytes().to_vec();
            let mut l = lexer::Lexer::new(&input, "parser_test_pass");
            let toks = l.run();
            assert_eq!(l.errors.len(), 0);
            let mut parser = Parser::new(toks, "parser_test_pass");
            let ast = parser.parse();
            assert_eq!(parser.errors.len(), 0);
            assert_eq!(
                ast.into_iter()
                    .map(|o| o.unwrap().token().ttype.clone())
                    .collect::<Vec<Type>>(),
                (vec![Type::Keyword(Keyword::EXPLAIN)])
            );
        }
    }
}
```

As shown, the `test_group_pass_assert!` macro in the `parser` module starts
with the same `Lexer` initialisation and empty error vector assertion. However,
the next step is to initialise the `Parser` structure and after parsing assert
the outcome - i.e. no errors and nodes with the correct types.

```rust
#[cfg(test)]
mod should_fail {
    mod sql_stmt_prefix {
        use crate::{lexer, parser::Parser};
        #[test]
        fn explain() {
            let input = r#"EXPLAIN;"#.as_bytes().to_vec();
            let mut l = lexer::Lexer::new(&input, "parser_test_fail");
            let toks = l.run();
            assert_eq!(l.errors.len(), 0);
            let mut parser = Parser::new(toks, "parser_test_fail");
            let _ = parser.parse();
            assert_ne!(parser.errors.len(), 0);
        }

        #[test]
        fn explain_query_plan() {
            let input = r#"EXPLAIN QUERY PLAN;"#.as_bytes().to_vec();
            let mut l = lexer::Lexer::new(&input, "parser_test_fail");
            let toks = l.run();
            assert_eq!(l.errors.len(), 0);
            let mut parser = Parser::new(toks, "parser_test_fail");
            let _ = parser.parse();
            assert_ne!(parser.errors.len(), 0);
        }
    }
}
```

The `test_group_fail!` macro also extends the same macro from the `lexer`
module and appends the check for errors after parsing. Both `macro_rules!`:

```rust
macro_rules! test_group_pass_assert {
    ($group_name:ident,$($ident:ident:$input:literal=$expected:expr),*) => {
    mod $group_name {
        use crate::{lexer, parser::Parser, types::Type, types::Keyword};
        $(
            #[test]
            fn $ident() {
                let input = $input.as_bytes().to_vec();
                let mut l = lexer::Lexer::new(&input, "parser_test_pass");
                let toks = l.run();
                assert_eq!(l.errors.len(), 0);

                let mut parser = Parser::new(toks, "parser_test_pass");
                let ast = parser.parse();
                assert_eq!(parser.errors.len(), 0);
                assert_eq!(ast.into_iter()
                    .map(|o| o.unwrap().token().ttype.clone())
                    .collect::<Vec<Type>>(), $expected);
            }
        )*
        }
    };
}

macro_rules! test_group_fail {
    ($group_name:ident,$($ident:ident:$input:literal),*) => {
    mod $group_name {
        use crate::{lexer, parser::Parser};
        $(
            #[test]
            fn $ident() {
                let input = $input.as_bytes().to_vec();
                let mut l = lexer::Lexer::new(&input, "parser_test_fail");
                let toks = l.run();
                assert_eq!(l.errors.len(), 0);

                let mut parser = Parser::new(toks, "parser_test_fail");
                let _ = parser.parse();
                assert_ne!(parser.errors.len(), 0);
            }
        )*
        }
    };
}
```

### Macro Pitfalls

- `rust-analyzer` plays badly inside `macro_rules!`
    - no real intellisense
    - no goto definition
    - no hover for signatures of literals and language constructs
- `cargo fmt` does not format or indent inside of `macro_rules!` and macro invokations
- `treesitter` (yes I use neovim, btw 😼) and `chroma` (used on this site)
  sometimes struggle with syntax highlighting of `macro_rules!`
- documentation is sparse at best

## Matching characters

When writing a lexer, comparing characters is the part everything else depends
on. Rust makes this enjoyable via the `matches!` macro and the patterns the
`match` statement accepts. For instance, checking if the current character is
a valid sqlite number can be done by a simple `matches!` macro invocation:

```rust
/// Specifically matches https://www.sqlite.org/syntax/numeric-literal.html
fn is_sqlite_num(&self) -> bool {
    matches!(self.cur(), 
             // exponent notation with +-
             '+' | '-' |
             // sqlite allows for separating numbers by _
             '_' |
             // floating point
             '.' |
             // hexadecimal
             'a'..='f' | 'A'..='F' |
             // decimal
             '0'..='9')
}
```

Similarly testing for identifiers is as easy as the above:

```rust
fn is_ident(&self, c: char) -> bool {
    matches!(c, 'a'..='z' | 'A'..='Z' | '_' | '0'..='9')
}
```

Symbol detection in the main loop of the lexer works exactly the same:

```rust
pub fn run(&mut self) -> Vec<Token> {
    let mut r = vec![];
    while !self.is_eof() {
        match self.cur() {
            // skipping whitespace
            '\t' | '\r' | ' ' | '\n' => {}
            '*' => r.push(self.single(Type::Asteriks)),
            ';' => r.push(self.single(Type::Semicolon)),
            ',' => r.push(self.single(Type::Comma)),
            '%' => r.push(self.single(Type::Percent)),
            _ => {
                // actually there is error handling here, but its omitted for the
                // next chapter
                panic!();
            } 
        }
        self.advance();
    }
    r
}
```

Patterns in `match` statement and `matches` blocks are arguably the most
useful feature of Rust.

## Matching tokens
## Lexer and parser error handling
## Pretty errors
