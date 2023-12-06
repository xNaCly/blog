---
title: Improving programming language performance
summary: Reducing the execution time of a benchmark by 703% or 7.03x
date: 2023-12-06
draft: true
tags:
    - lisp
    - performance
    - go
---

{{<callout type="Introduction">}}
How I improved my programming language runtime (see
[sophia](https://github.com/xnacly/Sophia)) for a specific benchmark by
reducing its execution time by 7.03 times or 703%. The benchmark script
previously took 22.2 seconds. I reduced it to 3.3s!
{{</callout>}}


I started developing the sophia programming language to learn all about
lexical analysis, parsing and evaluation in a real world setting. Thus i
decided on the (in)famous lisp S-expressions. A very early stage of the
project can be seen
[here](https://xnacly.me/posts/2023/write-your-own-programming-language/).

{{<callout type="Tip">}}
In the future i will highlight the part of the implementation responsible for
error handling and display - not only because i think its a very interesting
topic, but due to me being very proud of the final result. Here a small sneak peek.

![sophia-errors](/programming-lang-performance/errors.png)

If you're interested in a more extensive overview, visit [Sophia - Internal
Documentation - Error
Handling](https://xnacly.github.io/Sophia/Internal.html#error-handling).
{{</callout>}}

## Lets Talk Architecture

The interpreter follows the same rudimentary stages of interpretation most interpreters make use of:

1. Lexical analysis: character stream to token stream
2. Parsing: token stream to abstract syntax tree
3. Evalulation: abstract syntax tree to values (Tree walk interpreter)

I did not develop the interpreter with performance in mind.

### AST and Eval

The evaluation is the most interesting part of the interpreter, I chose the
[Interpreter pattern](https://en.wikipedia.org/wiki/Interpreter_pattern) -
simply because it was the first time I was implementing an interpreter. 


The AST in sophia consists of `Node`'s that can contain child `Node`'s. The
evaluation process starts at the root of the AST and dispatches a
`Node.Eval()` call. The root node dispatches this call to its children and its
children to their children, thus walking the tree and moving the work to the
`Node`'s:

```go
// expr/node.go
type Node interface {
    // [...]
    Eval() any
}

// expr.String statisfies expr.Node
type String struct {
    Token *token.Token
}

func (s *String) Eval() any {
    return s.Token.Raw
}

// expr.Put dispatches a .Eval call 
// to each of its child nodes
type Put struct {
    Token    *token.Token
    Children []Node
}
```

Due to the interpreter holding all token, all ast nodes and possibly walking
and calling `Eval()` on most of them multiple times, the memory and cpu
footprint is large for a minimal language like this. This can be mitigated
with reworking the evaluation into a byte code compiler and vm.

## Benchmarking

### Project and Profiler setup

### Identifying Hot Spots

## Archiving Performance gains

## Future work

