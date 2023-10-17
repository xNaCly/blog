---
title: "Tokenizing Arithmetic expressions - calculator p.1"
summary: "In depth explaination around writing a simple interpreter"
date: 2023-10-16
tags:
  - go
  - bytecode vm
draft: true
---

## Introduction

This is the first post of a four part series around implementing and
understanding the steps for interpreting [arithmetic
expressions](https://en.wikipedia.org/wiki/Arithmetic). The series is meant for
explaining key concepts such as [lexical
analysis](https://en.wikipedia.org/wiki/Lexical_analysis), parsing / building
the [ast](https://en.wikipedia.org/wiki/Abstract_syntax_tree), walking the ast
/ flatting it to byte code, [bytecode virtual
machines](https://en.wikipedia.org/wiki/Bytecode) and
[TDD](https://en.wikipedia.org/wiki/Test-driven_development) centered around
compilers and interpreters.

1. This first article contains the introduction to our problem domain, the setup
   of our project, the basics of TDD and the first steps towards interpreting
   arithmetic expressions: tokenizing our input / performing lexical analysis

2. The second article will be centered around converting the list of tokens we
   created in the first article to an abstract syntax tree, short ast

3. The third article will be focused on walking the abstract syntax tree and
   converting nodes into a list of instructions for our virtual machine

4. The fourth and last article will be consisting of implementing the bytecode
   virtual machine and executing expressions compiled to bytecode

All posts in this series will include an extensive amount of resources for the
readers deeper understanding of the matter. The following books and articles
are commonly referenced in the compiler and interpreter space:

- [Writing An Interpreter in Go by Thorsten Ball](https://interpreterbook.com/)
  (go) - TDD, scratches the surface
- [Crafting Interpreters by Robert Nystrom](https://craftinginterpreters.com/)
  (java & c) - very detailed, includes data structures and in depth topics,
  such as grammars, hashing, etc
- [Compilers: Principles, Techniques, and
  Tools](https://en.wikipedia.org/wiki/Compilers:_Principles,_Techniques,_and_Tools)
  (java) - very theoretic

We will be using the [go programming language](https://go.dev/) in this series.
All concepts can be applied to any programming language. Some level of
proficiency with go is assumed, I will not explain syntax.

## Problem domain

The expression we want to be able to execute with our interpreter is the
smallest subset of a programming language i could imagine thus our problem
domain is defined by a subset of arithmetic expressions:

- addition
- subtraction
- multiplication
- division

We will also support braces that can be used to indicate precedence, which we
will talk about in the second post of this series.

Some examples of expression we will accept:

```python
# comments

# addition
1029+0.129
# =1029.129

# subtraction
5_120_129-5_120_128
# =1

# multiplication
5e12*3
# =150000

# division
1/2
# =0.5

# braces
(1+1)/2
# =1
```

## Interpreter design

There are several well established ways of interpreting programming languages.
Lets take a look at the stages an interpreter commonly performs before the
passed in source code is interpreted.

### Interpreter Stages

1. **Lexical analysis** -> the process of recognizing structures such as
   numbers, identifiers or symbols in the source code , converts recognized
   structures into a list of token, often referred to as _scanning_, _lexing_
   or _tokenizing_.

2. **Parsing** -> refers to the process of detecting precedence and checking
   whether the input conforms to the defined grammar. In our case the parser
   analyses the output of our previous stage and builds an abstract syntax tree
   while taking operator precedence into account.

3. **Evaluating** -> commonly means walking the tree starting from the leafs,
   computing a value for each node and exiting on computing the value of the
   root, see [tree walk interpreter](). While this is the simplest way to
   implement an interpreter, it introduces performance issues due to requiring
   recursion and the overhead of traversing many pointers. There are [multiple
   ways of implementing this
   step](<https://en.wikipedia.org/wiki/Interpreter_(computing)#Variations>),
   each one with different pros and cons:
   - [Tree walk / Abstract syntax tree
     interpreters](https://en.wikipedia.org/wiki/Abstract_syntax_tree): too
     slow, too much overhead
   - [Just-in-time
     compiler](https://en.wikipedia.org/wiki/Just-in-time_compilation): too
     complex / too hard to implement
   - [bytecode interpreter](https://en.wikipedia.org/wiki/Bytecode): medium
     hard to implement, faster than tree walk interpreter

For our interpreter we decide to use the idea of bytecode interpreters, thus
splitting the third step into two sub steps::

1. **Compiling to bytecode** -> Walking the tree and compiling each node into bytecode
2. **Executing bytecode** -> Iterating over the list of bytecode instructions and executing them

### Example

Consider the following statement and lets visualize the stages using the example:

```python
1.025*3+1
```

#### Lexical analysis

Performing the first stage converts the input from a character stream into a
list of structures:

```go
token := []Token{
    Token{Type: NUMBER, Raw: "1.025"},
    Token{Type: ASTERIKS, Raw: "*"},
    Token{Type: NUMBER, Raw: "3"},
    Token{Type: PLUS, Raw: "+"},
    Token{Type: NUMBER, Raw: "3"},
}
```

#### Parsing

We now build an abstract syntax tree out of the list of token we get from the previous stage:

```go
ast := Addition{
    Token: Token{Type: PLUS, Raw: "+"},
    Left: Multiplication{
        Token: Token{Type: ASTERIKS, Raw: "*"},
        Left: Number{
            Token: Token{Type: NUMBER, Raw: "1.025"},
        },
        Right: Number{
            Token: Token{Type: NUMBER, Raw: "3"}
        },
    },
    Right: Number{Token: NUMBER, Raw: "1"},
}
```

Notice the depth of the tree, the deeper the node sits the earlier it is
compiled to bytecode, thus considering operator precedence, see below for a
visual explanation:

1. Initial ast

   ```text
   +
   │
   ├─ 1
   │
   └─ *
      │
      ├─ 1.025
      │
      └─ 3
   ```

2. `Multiplication` evaluated:

   ```text
   +
   │
   ├─ 1
   │
   └─ 3.075
   ```

3. `Addition` evaluated:

   ```text
   4.075
   ```

#### Compiling to bytecode

We use the ast we got from the previous step to compile each node to a list of
bytecode instructions. The bottom most node, commonly referred to as leafs are
all numbers, thus we will start there.

The bytecode vm we want to implement has a list of registers, comparable to the
cpu registers on a real machine. We can load and manipulate values in these
registers. In the third and fourth part of this series, we will go into great
depth on registers, bytecode and virtual machines. For now simply know there
are registers, we can manipulate them, our vm accepts an instruction and an
argument.

Lets now take a look at the bytecode our previous example compiles to:

```asm
;; multiplication
    ;; loading 1.025 into register 0
    OP_LOAD    :: 1.025000
    ;; moving 1.025 from register 0 to register 1
    OP_STORE   :: 1.000000

    ;; loading 3 into register 0
    OP_LOAD    :: 3.000000
    ;; multiplying the value of register 0
    ;; with the value of register 1
    OP_MULTIPY :: 1.000000

    ;; storing the result of the
    ;; multiplication in register 1
    OP_STORE   :: 1.000000

;; addition
    ;; loading 1 into register 0
    OP_LOAD    :: 1.000000
    ;; adding the value of register 1
    ;; to the value of register 0
    OP_ADD     :: 1.000000
```

The left hand side of each line is the operation the virtual machine is
executing, the right hand side is the argument of the operation, sides are
separated with `::`.

This should suffice as a high level overview over the steps we want to take
until we reach the integer result of our expression, starting from the source
code, tokenizing, parsing, compiling and executing bytecode.

## Project setup

{{<callout type="Tip">}}
All code snippets used in this series start with a comment specifying the file
it points to. Code not relevant to the current topic is omitted but still
notated using `[...]`.

```go
// main.go
package main

// [...]

func main() { }
```

If a new file should be created this will be explicitly stated.

Code snippets starting with a `$` must be executed in a shell:

```text
$ echo "This is a shell"
```

{{</callout>}}

1. Creating a directory for our project:

   ```text
   $ mkdir calc
   ```

2. Entry point

   Using go we can start with the bare minimum a project requires:

   ```go
   // main.go
   package main

   import "fmt"

   func main() {
       fmt.Println("Hello World!")
   }
   ```

   Running the above via `go run .` requires the creation of the projects
   `go.mod` file:

3. Initialising the project

   ```text
   $ go mod init calc
   ```

4. Building and running the source code

   ```text
   $ go run .
   Hello World!
   ```

All of our source code will live in the root of the project. Currently we have
`main.go` and `go.mod` in the root of our project.

## Test driven development

{{<callout type="Info">}}
Test driven development refers to the process of defining a problem domain for
a function, creating the corresponding test, preferably with as much edge cases
as possible and incrementing the implementation of the function to satisfy all
test cases.
{{</callout>}}

As we are implementing an interpreter both the input to our function and the
output of our function is known and therefore easily representable with tests
which screams we should use TDD and iterate until all tests are passing.

### Test setup

### Table driven tests

## Tokenizing

### Token and Types of Token

### Debugging

### Creating the Lexer

### Advancing in the Input

### Ignoring white space

### Support for comments

### Detecting special symbols

### Support for integers and floating point numbers

## Wrapping up
