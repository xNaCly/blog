---
title: "Syntax Highlight for SQL in Diagnostic errors"
summary: "Adding syntax highlighting to SQL snippets in sqleibniz diagnostics"
date: 2025-02-12
tags:
    - rust
    - sqleibniz
    - sql
---

This is the third article of my quest for improving the developer experience
around using sql:

1. [Making SQL Keyword Suggestions Work](/posts/2024/making-sql-keyword-suggestions-work/)
2. [Embedding Lua in sqleibniz with Rust](/posts/2024/embed-lua-in-rust/)

{{<callout type="TLDR">}}
I added syntax highlight to sqleibniz diagnostic output:

![sqleibniz diagnostic with syntax highlight](/syntax-highlight/sqleibniz.png)
{{</callout>}}

This time I was annoyed by tools like rustc for not applying syntax highlighting to diagnostics:

![rustc compilation error without syntax highlight](/syntax-highlight/rustc.png)

sqleibniz is also missing this feature:

![sqleibniz diagnostic without syntax highlight](/syntax-highlight/old_sqleibniz.png)

## The Idea

1. Pass a line of sql text to a `highlight` function
2. Have it generate color escape codes for lexemes
3. Write color escape codes and lexemes to a string builder / buffer
4. Dump builder content to stdout

## A String Builder

I want to write the resulting string of the diagnostic display to more buffers
than stdout. This means i need a temporary buffer i can write `String`, `&str`,
`char`, `byte` and `Vec<u8>` to. My string builder is just a struct holding a
vector of bytes. _The source can be found
[here](https://github.com/xNaCly/sqleibniz/blob/master/src/highlight/builder.rs)_.

```rust
pub struct Builder {
    buffer: Vec<u8>,
}

impl Builder {
    // [...]
    
    pub fn string(self) -> String {
        match String::from_utf8(self.buffer) {
            Ok(string) => string,
            Err(_) => String::from("<failed to stringify Builder::buffer"),
        }
    }
}
```

Creating the string representation of the byte vector consumes the whole builder.
The other methods for appending bytes:

```rust
impl Builder {
    pub fn new() -> Self {
        Builder { buffer: Vec::new() }
    }

    pub fn with_capacity(cap: usize) -> Self {
        Builder {
            buffer: Vec::with_capacity(cap),
        }
    }

    pub fn write_char(&mut self, char: char) {
        self.buffer.push(char as u8);
    }

    pub fn write_byte(&mut self, byte: u8) {
        self.buffer.push(byte);
    }

    pub fn write_str(&mut self, str: &str) {
        self.buffer.append(&mut str.as_bytes().to_vec());
    }

    pub fn write_string(&mut self, string: String) {
        self.buffer.append(&mut string.into_bytes())
    }

    pub fn write_buf(&mut self, buf: Vec<u8>) {
        let mut b = buf;
        self.buffer.append(&mut b)
    }

    // [...]
}
```

## ANSI Color Escape Codes, or: I don't care about Windows

Wikipedia has a nice list of ANSI color escape codes: [ANSI escape
code#Colors](https://en.wikipedia.org/wiki/ANSI_escape_code#Colors). 

> I do know these can be wonky on the windows cmd, but i simply dont care, i do
> not own a device with windows on it and i do not develop for windows or with
> windows in mind.

So I created an enum and just added a `&str` representation:

```rust
#[derive(Debug)]
pub enum Color {
    Reset,

    // used for error display
    Red,
    Blue,
    Cyan,
    Green,
    Yellow,

    // used for syntax highlighting
    Grey,
    Magenta,
    Orange,
    White,
}

impl Color {
    pub fn as_str(&self) -> &str {
        match self {
            Self::Reset => "\x1b[0m",
            Self::Red => "\x1b[31m",
            Self::Blue => "\x1b[94m",
            Self::Green => "\x1b[92m",
            Self::Yellow => "\x1b[93m",
            Self::Cyan => "\x1b[96m",
            Self::Grey => "\x1b[90m",
            Self::Magenta => "\x1b[35m",
            Self::Orange => "\x1b[33m",
            Self::White => "\x1b[97m",
        }
    }
}
```

## Mapping Tokens to Colors

Since I only need this mapping in the `highlight` module, i created a private
`Highlight` trait:

```rust
trait Highlight {
    fn lookup(ttype: &Type) -> Color;
    fn as_bytes(&self) -> Vec<u8>;
}

impl Highlight for Color {
    fn lookup(ttype: &Type) -> Color {
        match ttype {
            Type::Keyword(_) => Self::Magenta,
            // atoms
            Type::String(_) 
            | Type::Number(_) 
            | Type::Blob(_) 
            | Type::Boolean(_) => Self::Orange,
            // special symbols
            Type::Dollar
            | Type::Colon
            | Type::Asterisk
            | Type::Question
            | Type::Param(_)
            | Type::Percent
            | Type::ParamName(_) => Self::Red,
            // symbols
            Type::Dot
            | Type::Ident(_)
            | Type::Semicolon
            | Type::Comma
            | Type::Equal
            | Type::At
            | Type::BraceLeft
            | Type::BraceRight
            | Type::BracketLeft
            | Type::BracketRight => Self::White,
            _ => Self::Grey,
        }
    }

    fn as_bytes(&self) -> Vec<u8> {
        self.as_str().as_bytes().to_vec()
    }
}
```

## Highlighting module

As introduced before, the `highlight` module contains the `Highlight` trait,
the string builder and the logic for highlighting a singular line of sql input,
in the form of the `highlight` function:


```rust
pub fn highlight(builder: &mut builder::Builder, token_on_line: &[&Token], line: &str) {
    // no tokens on a line means: either comment or empty line
    if token_on_line.len() == 0 {
        builder.write_str(Color::Grey.as_str());
        builder.write_str(line);
        builder.write_str(Color::Reset.as_str());
        return;
    }

    let reset = Color::Reset.as_bytes();

    let mut buf = line
        .split("")
        .map(|s| s.as_bytes().to_vec())
        .skip(1)
        .take(line.len())
        .collect::<Vec<Vec<u8>>>();

    let original_length = buf.len();
    for tok in token_on_line {
        let offset = buf.len() - original_length;
        let color = Color::lookup(&tok.ttype);
        buf.insert(tok.start + offset, color.as_bytes());
        if tok.start == tok.end {
            buf.insert(tok.end + offset, reset.clone());
        } else {
            buf.insert(tok.end + offset + 1, reset.clone());
        }
    }

    // INFO: used to inspect the text
    // dbg!(&buf
    //     .iter()
    //     .map(|s| String::from_utf8(s.to_vec()).unwrap())
    //     .collect::<Vec<String>>());

    for element in buf {
        builder.write_buf(element.to_vec());
    }
}
```

The basic idea behind the highlighting is to split the input string into a list
of characters as strings (specifically strings, because I want to insert color
escape codes before the start of a lexeme and at its end). Consider the
following lines:

```sql
-- causes a diagnostic,
-- because VACUUM does not allow a literal at this point
VACUUM ' ';
```

The first line will be filtered out by the first condition in the function -
because the lexer does not output any tokens for that line. Thus, we focus on
`VACUUM ' ';`. First we fill the `buf` variable:

```rust
let mut buf = line 
    // "VACUUM ' ';"
    .split("")
    // vec!["", "V", "A", "C", "U", "U", "M", "'", " ", "'", ";", ""]
    .skip(1)
    // we skip the first empty string
    .take(line.len())
    // we skip the last empty string
    .map(|s| s.as_bytes().to_vec())
    // same as before, but as vector of bytes
    .collect::<Vec<Vec<u8>>>();
```

Now we have the input split into characters and are able to insert the correct
color code and escape codes, as shown below:

1. `Type::Keyword(VACUUM)` is a keyword, thus we use the `Highlight::lookup` method to get `Color::Magenta`
2. `Type::String` is an atom, and resolves to `Color::Orange`
3. `Type::Semicolon` is a symbol, thus we use `Color::White`
4. after each lexeme, we must insert the `Color::Reset` enum variant to
  correctly highlight all the following text

```sql
   VACUUM ' ';
-- ^    ^ ^ ^^
-- |    | | ||
-- |    | | |+-- before this we insert Color::White and after Color::Reset
-- |    | | |
-- |    | | +-- after this, we insert Color::Reset
-- |    | | 
-- |    | +-- before this, we insert Color::Orange
-- |    |
-- |    +-- after this point, we insert Color::Reset
-- |
-- +-- before this point, we need to insert Color::Making
```

Since we are inserting into the `buf` variable, we need to keep track of its
`original_length` to compute the offset for all future insertions. We then
iterate over the tokens the caller passed into the function (`token_on_line`,
which should only contain tokens that were on the line we want to highlight):

```rust
let original_length = buf.len();
for tok in token_on_line {
    let offset = buf.len() - original_length;
    let color = Color::lookup(&tok.ttype);
    buf.insert(tok.start + offset, color.as_bytes());
    if tok.start == tok.end {
        buf.insert(tok.end + offset, reset.clone());
    } else {
        buf.insert(tok.end + offset + 1, reset.clone());
    }
}
```

Once we computed the offset, we use `Highlight::lookup` to get the color of the
current token and write the color escape code we got via `Highlight::as_bytes`
at the start of the token plus the offset into the buffer. However, if the
token is not one character long, we have to add move `Color::reset` one
position to the right.

After this, all elements of `buf` are written into the string builder passed
into the function.

> Dont mind the performance, it works and it is fast enough, I know inserting
> into an vector is slow and there are faster solutions.

## Attaching to diagnostic display

![final syntax highlighting](/syntax-highlight/final.png)

As shown above and below, the highlight function is called with the shared string
builder, all tokens found on the current line and the offending line itself:

```rust

#[derive(Debug, Clone, PartialEq)]
pub struct Error {
    pub file: String,
    pub line: usize,
    pub rule: Rule,
    pub note: String,
    pub msg: String,
    pub start: usize,
    pub end: usize,
    pub doc_url: Option<&'static str>,
}

pub fn print_str_colored(b: &mut builder::Builder, s: &str, c: Color) {
    b.write_str(c.as_str());
    b.write_str(s);
    b.write_str(Color::Reset.as_str());
}

impl Error {
    pub fn print(&mut self, b: &mut builder::Builder, content: &Vec<u8>, tokens: &[Token]) {
        // [...]
        let offending_line = String::from(lines.get(self.line).unwrap());
        print_str_colored(b, &format!(" {:02} | ", self.line + 1), Color::Blue);
        highlight(
            b,
            &tokens
                .iter()
                .filter(|t| t.line == self.line)
                .collect::<Vec<&Token>>(),
            &offending_line,
        );
        print_str_colored(b, "\n    |", Color::Blue);
        // [...]
    }
}
```

The `Error::print` function itself is called from the `main` function of the sqleibniz crate:

```rust
    // [...]

    if !processed_errors.is_empty() && !args.silent {
        error::print_str_colored(
            &mut error_string_builder,
            &format!("{:=^72}\n", format!(" {} ", file.name)),
            error::Color::Blue,
        );
        let error_count = processed_errors.len();
        for (i, e) in processed_errors.iter().enumerate() {
            (**e)
                .clone()
                .print(&mut error_string_builder, &content, &toks);

            if i + 1 != error_count {
                error_string_builder.write_char('\n');
            }
        }
    }

    // [...]
```

Please just ignore the ugly double dereference in line 11, this is needed
because I want to further use the `processed_errors` array and not clone it -
simply because there is a lot of data in each error structure.

