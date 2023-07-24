---
title: "You Should Write Your Own Programming Language"
summary: "Why i think you should write your own programming language"
date: 2023-07-24
tags:
  - lisp
  - go
---

I recently started writing an interpreted [programming language inspired by
lisp](https://github.com/xNaCly/Sophia). Mainly because its easy to parse the
expressions :^). I named it after my girlfriend and got started. Its designed
around single character operators, such as `.:+-*/^%`.

After implementing the first few features I wanted to somewhat express the fun
i had while writing this obscure language in this post while explaining why I
think everyone should at least try to implement a subset of a programming
language. Even if the language is, like mine, a little bit esoteric.

Without going into too much detail, here is a short showcase of the language:

```clojure
;; print arguments to stdout
[. "hello world"]

[.
    [+
        [* 2 2]
        2
        3
    ]
    [^ 5
        [- 2 1]
    ]
]
;; 9 10

[: pi 3.1415]
[.
    [* pi 5]
]
;; 15.7075000000000001
```

I know its a pain to read or write. It also has a lot of quirks and weird design decisions:

- [so many braces](https://wiki.c2.com/?LispLacksVisualCues)
- no [S-Expressions](https://en.wikipedia.org/wiki/S-expression), but [M-Expressions](https://en.wikipedia.org/wiki/M-expression)
- no functions
- somehow everything is an array and simultaneously isn't
- lisp without linked lists
- only pretty errors in the lexer, everything else is just an error message:

```fish
sophia -exp '[. "hello world]'
# 13:47:45 err: Unterminated String at [l 1:3]
#
# 001 |   [. "test]
#            ^^^^^^
# 13:49:47 lexer error

sophia -exp '[? "test"]'
# 13:48:37 err: Unknown token '?' at [l 1:1]
#
# 001 |   [? "test"]
#          ^
# 13:49:47 lexer error

sophia -exp '[. "test"'
# 13:49:47 err: Missing statement end
#   - Expected Token ']' got 'EOF' [l: 0:0]
# 13:49:47 parser error

sophia -exp '[+ 1 "b"]'
# 13:50:46 err: can not use variable
#   of type string in current operation (+)
#   , expected float64 for value "b"
# 13:50:46 runtime error
```

- no control flow
- only strings and floats (float64)
- variables only store the first argument after the identifier (don't @me, the parser isn't done yet)
- [i stole the `.` from forth](<https://en.wikipedia.org/wiki/Forth_(programming_language)#%E2%80%9CHello,_World!%E2%80%9D>)
- expressions (everything between `[]`) are evaluated right to left, for
  instance the power operator is evaluated like so:
  1. Assign first child of the power expression to a variable called `result`
  2. Raise the `result` to the power of the next child and assign the result to `result`
  3. Profit (not really)
- all operators (the first token in `[]`) are single character

As one can see my to-do list is full for the next few months.

## Why should i write a programming language

I think the benefit of implementing a programming language or even a subset like I did can be categorized into the following chapters.

Of course lets not forget the joy of writing a programming language, you
provide your idea of an instruction set and the computer executes and prints
what you specified.

### Programming language experience

In my opinion i learned a lot about go and java (yeah i know 🤢) while working
on several interpreters. You can learn a lot about iterators, the standard
library, string and character manipulation as well as i/o when implementing
your own programming language.

Some books and resources i found very helpful for learning go:

- [The Go Programming Language by Brian W. Kernighan](https://www.gopl.io/)
- [Go by example](https://gobyexample.com/)
- [Go documentation](https://go.dev/doc/)

### Data structures

You will need to store a list of tokens in a list which size you can't know at
compile time, therefore you will need a variable size list, such as a
[Slice](https://gobyexample.com/slices) or an
[ArrayList](https://www.programiz.com/java-programming/arraylist).

You also have to keep track of built-in keywords or variables you encounter
while parsing, both of these use cases cry for a
[map](https://gobyexample.com/maps) or a
[HashMap](https://www.programiz.com/java-programming/hashmap).

You probably are implementing a tree walk interpreter, for this to work you are
building a tree out of scanned tokens, which also is a data structure.

Not only will you have to use data structures when implementing your
programming language, but you will have to understand and use them to have a
somewhat good time.

For data structures I can recommend the course [The Last Algorithms Course
You'll Need](https://frontendmasters.com/courses/algorithms/) by
[ThePrimeagen](https://frontendmasters.com/teachers/the-primeagen/) or [A
Programmer's Guider to Computer Science
Vol.1](https://www.goodreads.com/book/show/51185374-a-programmer-s-guide-to-computer-science)

### Design patterns

No I am not talking about [SOLID](https://en.wikipedia.org/wiki/SOLID),
dependency injection or implementing the abstract `BuilderFactory`, I'm
referring to the useful design patters, such as:

- [Iterators](https://refactoring.guru/design-patterns/iterator)
- [Visitor](https://refactoring.guru/design-patterns/visitor)

I use the iterator pattern to iterate over tokens and
[ast](https://en.wikipedia.org/wiki/Abstract_syntax_tree)-Nodes. I make use of
the visitor pattern to invoke the `.Eval()` function on the root of the AST,
which will then evaluate all nodes until the leaf is hit. This creates a clean
and nice looking code base and keeps the mental overhead low by separating
creation and evaluation.

### Understanding the basics

The thing I love most about tinkering with implementing a programming language
is the theory behind it. Lexical and syntax analysis, parsing the
token stream to an abstract syntax tree and evaluating it is just a lot of fun.

When implementing a programming language you will learn about:

- lexical analysis (assigning meaning to characters)
- syntax analysis (checking if the lexed / scanned stream matches the grammar you desire)
- building a tree of nodes which represent the structure of your source program
- tree traversal to evaluate this structure
- a lot of error handling
  - errors when lexing (unknown characters, not terminated strings, etc)
  - errors when parsing (braces at the wrong place, missing semicolon, etc.)
  - errors when evaluating (trying to do arithmetics with strings, calling undefined functions or using undefined variables)

For writing interpreters i can recommend:

- [Writing An Interpreter in Go by Thorsten Ball](https://interpreterbook.com/) (go)
- [Crafting Interpreters by Robert Nystrom](https://craftinginterpreters.com/) (java & c)

For reading about the theory behind writing programming languages i can recommend the dragon book:

- [Compilers: Principles, Techniques, and Tools](https://en.wikipedia.org/wiki/Compilers:_Principles,_Techniques,_and_Tools)
