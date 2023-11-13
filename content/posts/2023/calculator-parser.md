---
title: "Parsing Arithmetic expressions - calculator p.2"
summary: "In depth guide on parsing expressions and building an ast"
date: 2023-11-13
draft: true
tags:
  - go
  - bytecode vm
  - parser
---

{{<callout type="Tip">}}
This is the second post of a four part series around implementing and
understanding the steps for interpreting [arithmetic
expressions](https://en.wikipedia.org/wiki/Arithmetic). The series is meant for
explaining key concepts such as [lexical
analysis](https://en.wikipedia.org/wiki/Lexical_analysis), parsing / building
the [ast](https://en.wikipedia.org/wiki/Abstract_syntax_tree), walking the ast
/ flatting it to byte code, [bytecode virtual
machines](https://en.wikipedia.org/wiki/Bytecode) and
[TDD](https://en.wikipedia.org/wiki/Test-driven_development) centered around
compilers and interpreters.

1. [This first article contains the introduction to our problem domain, the
   setup of our project, the basics of TDD and the first steps towards
   interpreting arithmetic expressions: tokenizing our input / performing
   lexical analysis](/calculator-lexer)

2. The second article will be centered around converting the list of tokens we
   created in the first article to an abstract syntax tree, short ast (this post)

3. The third article will be focused on walking the abstract syntax tree and
   converting nodes into a list of instructions for our virtual machine (coming soon)

4. The fourth and last article will be consisting of implementing the bytecode
   virtual machine and executing expressions compiled to bytecode (coming soon)

The corresponding GitHub repository can be found
[here](https://github.com/xNaCly/calculator).
{{</callout>}}

<!-- TODO: introduction -->
<!-- TODO: explain parsing -->
<!-- TODO: showcase grammar -->

## Parsing

## Abstract syntax tree

Our abstract syntax tree will consist of a bunch of nodes attached to each
other, each element will at most contain two child nodes.

### Node Representation, interfaces and structures

We will represent an element of our ast with the `Node` interface. A structure
satisfies the interface by implementing all defined functions:

```go
// expr.go (create a new file)
package main

import (
    "fmt"
    "strings"
)

type Node interface {
    Compile() []Operation
}
```

The `Compile` function will recursively call `Compile` on all its child nodes
and return the resulting byte code operations.

### Laying Groundwork for compilation

We have not yet defined the `Operation` structure. This structure is used to
store a singular instruction for our virtual machine. Lets define this structure:

```go
// vm.go (create a new file)
package main

// represents an operation the virtual machine performs
type OpCode uint8

// represents an operation and its argument
type Operation struct {
    Code OpCode // type of operation
    Arg float64 // operation argument
}
```

### Debugging Nodes and their values

We want to look at our resulting abstract syntax tree and notice the operator
precedence and node depth as easily as possible. I deemed the following format
suitable.

Lets for example take `2+2*2`, this expression requires `2*2` having
a higher precedence as `2+2`, thus we represent the expression as follows:

```text
+
  2
  *
    2
    2
```

The further right the node sits the earlier it gets compiled to bytecode, thus
resulting in our desired precedence.

To implement this feature we add a new function called `String` to our `Node` interface:

```go{hl_lines=["4"]}
// expr.go
type Node interface {
    Compile() []Operation
    String(ident int) string
}
```

This function accepts the amount of spaces to indent itself with, calls the
`String` function on its child nodes and returns a formatted string containing
its and its child nodes content.

### Numbers

Numbers are the simplest to implement. At first, we define a new `Number`
structure:

```go
// expr.go

// [...]

type Number struct {
    token Token
}
```

To satisfy the `Node` interface we add the following two functions:

```go
// expr.go

// [...]

type Number struct {
    token Token
}

func (n *Number) Compile() []Operation {
    return nil
}

func (n *Number) String(ident int) []Operation {
    return fmt.Sprint(strings.Repeat(" ", ident), n.token.Raw)
}
```

We return `nil` from the `Number.Compile` function because we cover flatting
and compiling the abstract syntax tree to byte code in the next post of this
series.

### Binary operations

Lets now take a look at the next expression. We will describe all operations
with two child nodes as binary, such as `+`, `-`, `*` and `/`. The
corresponding structure reflects that:

```go
// expr.go

// [...]

type Binary struct {
	token Token
	left  Node
	right Node
}
```

As we did with the `Number` structure we now satisfy the `Node` structure by implementing its functions:

```go

// expr.go

// [...]

func (b *Binary) Compile() []Operation {
	return nil
}

func (b *Binary) String(ident int) string {
	identStr := strings.Repeat(" ", ident)
	return fmt.Sprint(identStr, b.token.Raw, "\n ", identStr, b.left.String(ident+1), "\n ", identStr, b.right.String(ident+1))
}
```

The `String` function for binary expressions is a bit more complex than its
counterpart in the `Number` structure. We indent the value of the binary
expressions token, a newline, call the `String` function on the left child
while incrementing the indent and thus moving the child one space to the right.
We then do the same for the right. This results in the output we want:

```text
ast     depth
------  -----------------------

+                           <-0
  +              <-1          |
    +    <-2       |          |
      2    |       |          |
      2    |       |          |
    2    <-2     <-1          |
  2                         <-0
```

### Unary operations

We will categorise operations with one child as unary. Our calculator only
supports negating numbers, thus we allow: `-1`, `--5` and `--------10`, seems
idiotic but we want to support it 😼.

```go
// expr.go

// [...]

type Unary struct {
	token Token
	right Node
}

func (u *Unary) Compile() []Operation {
    return nil
}

func (u *Unary) String(ident int) string {
	identStr := strings.Repeat(" ", ident)
	return fmt.Sprint(identStr, "\n ", identStr, "-", u.right.String(ident+1))
}
```

The `Unary.String` function closely resembles the `Binary.String` function but
has one child.

## Tests

## Parsing the List of Tokens

### Skeleton and utilities

### Binary

### Unary

### Primary and Grouped expressions
