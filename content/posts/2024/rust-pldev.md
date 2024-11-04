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

## Iterating characters
## Matching characters
## Lexer and parser error handling
## Pretty errors
## Matching tokens
