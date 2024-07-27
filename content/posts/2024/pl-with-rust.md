---
title: "Build a programming language with me"
date: 2024-07-27
summary: "Build a registerbased, interpreted pl with me and learn some rust on the way"
draft: true
tags:
  - rust
---

## The plan & the features

The main idea of this post is to:

- implement the most basic programming language
- lex, parse and compile the input to bytecode
- implement a virtual machine for this input
- attempt to improve performance
- do the whole thing in rust while learning all the language features i need for this project

With most basic I refer to the following features:

- arithmetics with `+-*/`
- line comments starting with `#`
- register based virtual machine with a constant pool

{{<callout type="Warning">}}
As I mentioned above, I'm new to Rust and this is my third(ish) attempt at
learning and using the language (for more than one project or two weeks). Thus,
if you have any improvements, either [raise an
issue](https://github.com/xNaCly/calculator/issues/new), [open a
pr](https://github.com/xNaCly/calculator/pulls) or send me an
[email](mailto://contact@xnacly.me).
{{</callout>}}

## Tokenizer/Lexer

You know the drill, we want to convert a stream of chars (in the rust or go,
see runes, sense) into a list of tokens we can then pass to the parser, see
below for an example:

```text
3.1415/2
```

We throw this into our lexer and get the following out:

```text
[
    {type: Type::NUMBER(3.1415), pos: 0},
    {type: Type::DIV, pos: 6},
    {type: Type::NUMBER(2), pos: 7},
]
```

Lets implement this in Rust. Im going to omit the file opening, the buffering
of contained lines, etc and jump right into the Lexer struct:

```rust

```
