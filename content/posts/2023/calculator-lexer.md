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

This is the first post of a four part series around implementing and understanding
the steps for interpreting arithmetic expressions[^arithmetic]. The series is meant for
explaining key concepts such as lexical analysis[^lexical-analysis], parsing / building the ast[^ast],
walking the ast / flatting it to byte code, bytecode virtual machines[^bytecode-vm] and TDD[^tdd]
centered around compilers and interpreters.

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

We will be using the go programming language[^go] in this series. All concepts
here can be applied to almost any programming language. Some level of
proficiency with go is assumed, I will not explain syntax.

[^arithmetic]: Arithmetic expressions: https://en.wikipedia.org/wiki/Expression_(mathematics)
[^lexical-analysis]: Lexical analysis / Scanning / Tokenizing: https://en.wikipedia.org/wiki/Lexical_analysis
[^ast]: Abstract Syntax Tree: https://en.wikipedia.org/wiki/Abstract_syntax_tree
[^bytecode-vm]: Bytecode virtual machine: https://en.wikipedia.org/wiki/Bytecode
[^tdd]: Test Driven Development: https://en.wikipedia.org/wiki/Test-driven_development
[^go]: The go programming language 💕: https://go.dev/

## Arithmetic expressions

## Why Tokenize

## Project setup

## Test driven development

## Tokenizing

### Token and Types of Tokens

### Debugging

### Creating the Lexer

### Advancing in the Input

### Ignoring white space

### Support for comments

### Detecting special symbols

### Support for integers and floating point numbers

## Wrapping up
