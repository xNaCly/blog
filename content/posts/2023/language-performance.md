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

I started developing the sophia programming language in july 2023 to learn all
about lexical analysis, parsing and evaluation in a real world setting. Thus i
decided on the (in)famous lisp S-expressions. A very early stage of the project
can be seen
[here](https://xnacly.me/posts/2023/write-your-own-programming-language/).

Currently the syntax is as follows:

```lisp
;; power of n
(fun square (_ n)
    (* n n))

(let n 12)
(let res
    (square a))
(put '{n}*{n} is {res}') ;; 12*12 is 144

;; fizzbuzz 0-15
(for (_ i) 15
    (let mod3 (eq 0 (% i 3)))
    (let mod5 (eq 0 (% i 5)))
    (match
        (if (and mod3 mod5) (put "FizzBuzz"))
        (if mod3 (put "Fizz"))
        (if mod5 (put "Buzz"))
        (put i)))

;; efficient binomial computation
(fun bin (_ n k)
    (if (gt k n)
        (return -1))
    (if (and (eq k n) (eq k 0))
        (return 1))

    ;; Due to the symmetry of the binomial coefficient with regard to k and n −
	;; k, calculation may be optimised by setting the upper limit of the
	;; product above to the smaller of k and n − k, see
	;; https://en.wikipedia.org/wiki/Binomial_coefficient#Computing_the_value_of_binomial_coefficients
    (let kn (- n k))
    (if (lt kn k)
        (let k kn))

    ;; see https://en.wikipedia.org/wiki/Binomial_coefficient#Multiplicative_formula
    (let r 1)
    (for (_ i) k
        (let r
            (/ (* r (- n i)) (+ i 1)))
        )
    r)

(put (bin 1 1)) ;; 1
(put (bin 6 3)) ;; 20
(put (bin 49 6)) ;; 20
(put (bin 20 15)) ;; 15504
```

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

{{<callout type="Tip">}}
_Both the lexer and the parser do not really do that much, thus i focus on the
evaluation stage of the interpreter in this blog post._
{{</callout>}}

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

> _The real problem is that programmers have spent far too much time worrying
> about efficiency in the wrong places and at the wrong times; premature
> optimization is the root of all evil (or at least most of it) in programming._
>
> **Donald E. Knuth**, [Turing Award Lecture](https://dl.acm.org/doi/pdf/10.1145/361604.361612) (1974)

The first step in the process of optimisation is to know where to look. I
didn't have any previous experience with benchmarks and interpreter performance -
therefore I did the only responsible thing and fired up a profiler.

### Example source

Before we do that we want to quickly hack up a script using a big enough set of
the instructions of our programming language that takes long enough for us to
gain an insight on whats going on inside the interpreter. I chose a leetcode
problem and want to execute it around 500k times - this should really give us a
big enough of a sample.

```lisp
;; leetcode 327 Maximum Count of positive integer and negative integer
(let example1
    (not 2) ;; negated: (not 2) -> -2
    (not 1)
    (not 1) 1 2 3)
(let example2 (not 3) (not 2) (not 1) 0 0 1 2)
(let example3 5 20 66 1314)

;; returns a if bigger than b, otherwise b
;; max: float, float -> float
(fun max (_ a b)
    (let max a) ;; created as nil
    (if (lt a b) (let max b))
    max) ;; return without extra statement

;; counts negative and positve numbers in arr, returns the higher amount
(fun solve (_ arr)
    (let pos 0)
    (let neg 0)
    (for (_ i) arr
        (match
            (if (lt i 0) (let pos (+ pos 1)))
            (let neg (+ neg 1))))
    (max neg pos))


(for (_ i) 500_000
    (solve example1) ;; 3
    (solve example3) ;; 4
    (solve example2) ;; 4
)
```

Executing this on my machine without any optimizations applied takes a whooping
6.5s -> compared to 1.6s the executable containing all applied optimizations takes:

{{<callout type="Pc Specs">}}
_Hit em with the neofetch_:

![neofetch](/programming-lang-performance/neofetch.png)

{{</callout>}}

![benchmark_pc](/programming-lang-performance/benchmark_pc.png)

This of course being my beefy machine, if I run the same benchmark on my
macbook from 2012, I mainly develop on while in university (and i first ran the
benchmark on), the delta is a lot more impressive:

{{<callout type="Macbook Specs">}}
_Hit em with the (second) neofetch_:

![neofetch_macbook](/programming-lang-performance/neofetch_macbook.png)

{{</callout>}}

![benchmark_macbook](/programming-lang-performance/benchmark_macbook.png)

Compared to a ~4x improvement a ~7x improvement is a lot more impressive.
Anyway, lets start setting up the profiler.

### Project and Profiler setup

{{<callout type="Tip">}}
This is somewhat of a guide to setting up a go project and running a profiler
with the application. You can follow along if your want :^).
{{</callout>}}

### Identifying Hot Spots

## Archiving Performance gains

### Doing less is more (performance)

#### Constant values

<!-- TODO: boolean no longer compares token raw value to "true", done once by parser -->
<!-- TODO: float no longer parse floats on each eval, done once by parser -->

#### Type casts!?

<!-- TODO: Replace a generic function for casting values to specific functions
leveraging type switches for values of type float or boolean -->

#### Function scopes

### Fast paths

### Less allocations, less frees

### Reinvent the wheel (sometimes)

### A tale on hash table keys

## Future work

<!-- TODO: Byte code interpreter-->
