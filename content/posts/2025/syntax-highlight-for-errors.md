---
title: "Syntax Highlight for SQL in Diagnostic errors"
summary: "Adding syntax highlighting to SQL snippets in sqleibniz diagnostics"
date: 2025-02-04
draft: true
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

1. Pass a line of text to a `highlight` function
2. Split line into chunks of text
3. Assign types of tokens to colors escape codes
4. Insert color escape code before chunk of text and color reset after the chunk
5. Write into string builder
6. Print to stdout

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

## Attaching to diagnostic display
