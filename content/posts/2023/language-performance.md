---
title: Improving programming language performance
summary: Reducing the execution time of a benchmark by 703% or 7.03x
date: 2023-12-06
tags:
  - sophia
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
    Token token.Token
}

func (s *String) Eval() any {
    return s.Token.Raw
}

// expr.Put dispatches a .Eval call
// to each of its child nodes
type Put struct {
    Token    token.Token
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

### Example benchmark

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

### Naive first estimates

Executing this on my machine without any optimizations applied takes a whooping
6.5s:

![benchmark](/programming-lang-performance/benchmark_first.png)

Anyway, lets start setting up the profiler.

### Project and Profiler setup

{{<callout type="Tip">}}
This is somewhat of a guide to setting up a go project and running a profiler
with the application. You can follow along if your want :^).
{{</callout>}}

Lets first clone the repo and move back in git history untill we are before the optimizations took place:

```bash
git clone https://github.com/xnacly/sophia oldsophia
cd oldsophia
git reset --hard 024c69d
```

Lets modify our application to collect runtime metrics via the
[runtime/pprof](https://pkg.go.dev/runtime/pprof) package:

```go {hl_lines=["6-7", "11-16"]}
// oldsophia/main.go
package main

import (
	"os"
	"runtime/pprof"
	"sophia/core/run"
)

func main() {
	f, err := os.Create("cpu.pprof")
	if err != nil {
		panic(err)
	}
	pprof.StartCPUProfile(f)
	defer pprof.StopCPUProfile()

	run.Start()
}
```

The next step is to compile, run and start the profile of our application with
the example benchmark script we created before:

```shell
$ go build.
$ ./sophia leetcode.phia
$ go tool pprof -http=":8080" ./sophia ./cpu.pprof
```

We are not interested in the graph view, so lets switch to _Top_.

![profiler](/programming-lang-performance/profiler.png)

The most interesting for us in this new view are the _Flat_ and _Flat%_ columns:

![profiler-top-15](/programming-lang-performance/profiler_top15.png)

## Archiving Easy Performance Gains

### Doing less is more (performance)

Especially in hot paths, such as nodes that are accessed or evaluated a lot,
reducing the amount of instructions or operations is crucial to improving
performance.

#### Constant parsing

Previously both `expr.Boolean` & `expr.Float` did heavy operations on each
`Eval()` call:

```go
func (f *Float) Eval() any {
	float, err := strconv.ParseFloat(f.Token.Raw, 64)
	if err != nil {
		serror.Add(&f.Token, "Float parse error", "Failed to parse float %q: %q", f.Token.Raw, err)
		serror.Panic()
	}
	return float
}

func (b *Boolean) Eval() any {
	return b.Token.Raw == "true"
}
```

Both these functions can and will be executed multiple times throughout running
a script, thus computing these values at parse time improves performance be
reducing operations in hot paths.

```go
// core/parser/parser.go:
func (p *Parser) parseArguments() expr.Node {
    // [...]
	} else if p.peekIs(token.FLOAT) {
		t := p.peek()
		value, err := strconv.ParseFloat(t.Raw, 64)
		if err != nil {
			serror.Add(&t, "Failed to parse number", "%q not a valid floating point integer", t.Raw)
			value = 0
		}
		child = &expr.Float{
			Token: t,
			Value: value,
		}
        //[...]
	} else if p.peekIs(token.BOOL) {
		child = &expr.Boolean{
			Token: p.peek(),
			// fastpath for easy boolean access, skipping a compare for each eval
			Value: p.peek().Raw == "true",
		}
	}
    // [...]
}

// core/expr/float.go:
type Float struct {
	Token token.Token
	Value float64
}

func (f *Float) Eval() any {
	return f.Value
}

// core/expr/bool.go:
type Boolean struct {
	Token token.Token
	Value bool
}

func (b *Boolean) Eval() any {
	return b.Value
}
```

#### Type casts!?

A prominent function in the profiler output is `core/expr.castPanicIfNotType`,
which is a generic function and in this case present for `float64`:

![typecasts](/programming-lang-performance/typecasts.png)

The implementation for `castPanicIfNotType` is as follows:

```go
func castPanicIfNotType[T any](in any, t token.Token) T {
	val, ok := in.(T)
	if !ok {
		var e T
		serror.Add(&t, "Type error", "Incompatiable types %T and %T", in, e)
		serror.Panic()
	}
	return val
}
```

This function increases the load on the garbage collector because `val` is
almost always escaping to the heap. I tried mitigate the need for a generic
function by implementing two helper functions for casting to `bool` and to
`float64`, both functions make use of type switches and proved to be faster /
being not represented in the top 15 of the profiler:

```go
// fastpath for casting bool, reduces memory allocation by skipping allocation
func castBoolPanic(in any, t token.Token) bool {
	switch v := in.(type) {
	case bool:
		return v
	default:
		serror.Add(&t, "Type error", "Incompatiable types %T and bool", in)
		serror.Panic()
	}
	// technically unreachable
	return false
}

// fastpath for casting float64, reduces memory allocation by skipping allocation
func castFloatPanic(in any, t token.Token) float64 {
	switch v := in.(type) {
	case float64:
		return v
	default:
		serror.Add(&t, "Type error", "Incompatiable types %T and float64", in)
		serror.Panic()
	}
	// technically unreachable
	return 0
}
```

### Resulting benchmark and pprof

Putting these optimisation together, rebuilding and rerunning the app +
profiler results in our new top 15 functions we can use for optimising the
interpreter further:

![profile-after-first-opts](/programming-lang-performance/profiler_after_first_opts.png)

We reduced the time `castPanicIfNotType` took from 0.24s to 0.16s, furthermore
we reduced `expr.(*Lt).Eval` from 0.37s to 0.27s. Our big issue with garbage
collection (red square at the top right) still remains.

We started of with a hyperfine naive benchmark for total time taken to run the
script, thus I will continue comparing via the profiler and hyperfine:

![benchmark-after-first-ops](/programming-lang-performance/benchmark_pc_after_first_ops.png)

Our easy to implement changes already decreased the runtime by ~750ms from
6.553s to 5.803s in comparison to the not optimised state.

## Less Easy Performance Gains

### Less allocations, less frees

The most eye-catching function is definitely the `runtime.mallocgc` function.
Our program spends 0.76s of its whole execution allocating memory - Remember we
are writing an interpreter, the lexical analysis and the parser are creating a
lot of memory.

Currently each AST node stores a copy of its token, this could be a potential
cause for massive allocation activities, simply due to the fact that we have a
lot of tokens and AST nodes.

```go
type Float struct {
    // copied by the parser, essentially duplicating GC load
	Token token.Token
	Value float64
}
```

Our first optimization is therefore to stop copying tokens into AST nodes and
instead keep references to them. Theoretically we should reduce the amount of
memory for the garbage collector to allocate and free from `n^2` to `n`, where
`n` is the amount of tokens \* the size of a token:

```go
type Float struct {
	Token *token.Token
	Value float64
}
```

This optimization took some time to implement, I had to rewrite parts of the
parser and all expression definitions.

### Fast paths

{{<callout type="Tip">}}
Fast paths in interpreter or compiler design commonly refers to a shorter path
of instructions or operations to get to the same result, see [Fast path -
wikipedia](https://en.wikipedia.org/wiki/Fast_path).
{{</callout>}}

The sophia language contains a whole lot of instructions that accept two or
more instructions, such as:

- addition
- subtraction
- division
- multiplication
- modulus
- and
- or
- equal

`expr.Add` and the other above expressions were implemented by simply iterating
the children of the node and applying the operation to them:

```go
func (a *Add) Eval() any {
	if len(a.Children) == 0 {
		return 0.0
	}
	res := 0.0
	for i, c := range a.Children {
		if i == 0 {
			res = castFloatPanic(c.Eval(), a.Token)
		} else {
			res += castFloatPanic(c.Eval(), a.Token)
		}
	}
	return res
}
```

The new and improved way includes checking if there are two children, thus
being able to apply the operation for the two children directly:

```go
func (a *Add) Eval() any {
	if len(a.Children) == 2 {
		// fastpath for two children
		f := a.Children[0]
		s := a.Children[1]
		return castFloatPanic(f.Eval(), f.GetToken()) + castFloatPanic(s.Eval(), s.GetToken())
	}

	res := 0.0
	for i, c := range a.Children {
		if i == 0 {
			res = castFloatPanic(c.Eval(), c.GetToken())
		} else {
			res += castFloatPanic(c.Eval(), c.GetToken())
		}
	}
	return res
}
```

### Reinvent the wheel (sometimes)

This is an optimization that i could not exactly measure, but I knew having to
parse a format string for each `put` instruction is too heavy of an operation:

```go
func (p *Put) Eval() any {
	b := strings.Builder{}
	for i, c := range p.Children {
		if i != 0 {
			b.WriteRune(' ')
		}
		b.WriteString(fmt.Sprint(c.Eval()))
	}
	fmt.Printf("%s\n", b.String())
	return nil
}
```

Thus I not only removed the `fmt.Printf` call but also wrapped it for common prints:

```go
func (p *Put) Eval() any {
	buffer.Reset()
	formatHelper(buffer, p.Children, ' ')
	buffer.WriteRune('\n')
	buffer.WriteTo(os.Stdout)
	return nil
}

// core/expr/util.go
func formatHelper(buffer *bytes.Buffer, children []Node, sep rune) {
	for i, c := range children {
		if i != 0 && sep != 0 {
			buffer.WriteRune(sep)
		}
		v := c.Eval()
		switch v := v.(type) {
		case string:
			buffer.WriteString(v)
		case float64:
			buffer.WriteString(strconv.FormatFloat(v, 'g', 12, 64))
		case bool:
			if v {
				buffer.WriteString("true")
			} else {
				buffer.WriteString("false")
			}
		default:
			fmt.Fprint(buffer, v)
		}
	}
}
```

This new function omits the need for parsing format strings, calling to the
runtime to use reflection for simple cases such as strings, float64 and
booleans. The same `formatHelper` function is reused for format strings.

### Resulting benchmark and pprof

Again we restart the profiler and check our top 15 functions:

![profiler_after_second_opts](/programming-lang-performance/profiler_after_second_opts.png)

We moved `runtime.mallocgc` and `runtime.nextFreeFast` down by a whole lot, the
first from 0.74s of the application run time to 0.12s, the second from 0.28s to
0.05s.

![benchmark-second-first-ops](/programming-lang-performance/benchmark_pc_after_second_ops.png)

Our slightly less easy to implement changes decreased the runtime by 3.795s
from 5.803s to 2.009s in comparison to the not optimised state - that is really
good, really really good, we are talking a 65.38% runtime decrease.

## A tale of hash table key performance

Our last optimization requires an introduction. The sophia programming language
stores all user defined variables in a map called `consts.SYMBOL_TABLE` and all
user defined functions in `consts.FUNC_TABLE`. Both are maps using strings as
keys.

```go
var FUNC_TABLE = make(map[string]any, 16)
var SYMBOL_TABLE = make(map[string]any, 64)
```

Map key hashing is so expensive the program spends 0.23s/12.5% of its total
runtime on assigning keys to a map (`runtime.mapassign_faststr`), 0.23s/12.5%
on hashing strings (`runtime.aeshashbody`) and 0.16s/8.7% on accessing maps
(`runtime.mapaccess2_faststr`). Cumulated these add up to 0.62s or 33.7% of the
application runtime, thus definitely worth investigating.

![hashmap](/programming-lang-performance/hashmap.png)

Hashing strings with for example
[FNV-1a](https://en.wikipedia.org/wiki/Fowler%E2%80%93Noll%E2%80%93Vo_hash_function)
is as expensive as the string is long, because the hash has to take every
character into account. Integers are inherently easier to hash and therefore
require less computational effort. This prompted me to test if the maps would
perform better with `uint32` as keys.

Replacing this was hard, because I had to find a way of keeping track of unique
variables and functions while assigning them an identifier (this of course had
to be more efficient than strings as keys for maps).

I solved this by creating the
[sophia/core/alloc](https://github.com/xNaCly/Sophia/blob/master/core/alloc/allocator.go)
package and hooking it up to the parser. This package keeps track of variables,
functions and their unique id while parsing. While evaluating, the map access
for identifiers is done with their new fields called `Key` the parser fills
with the help of the `alloc` package:

```go {hl_lines=[4, "30-32"]}
// core/expr/ident.go
type Ident struct {
	Token *token.Token
	Key   uint32
	Name  string
}

func (i *Ident) Eval() any {
	val, ok := consts.SYMBOL_TABLE[i.Key]
	if !ok {
		serror.Add(i.Token, "Undefined variable", "Variable %q is not defined.", i.Name)
		serror.Panic()
	}
	return val
}

// core/parser/parser.go
func (p *Parser) parseStatement() expr.Node {
    // [...]
    case token.LET:
		if len(childs) == 0 {
			serror.Add(op, "Not enough arguments", "Expected at least one argument for variable declaration, got %d.", len(childs))
			return nil
		}
		ident, ok := childs[0].(*expr.Ident)
		if !ok {
			serror.Add(childs[0].GetToken(), "Wrong parameter", "Expected identifier, got %T.", childs[0])
			return nil
		}
		if _, ok := alloc.Default.Variables[ident.Name]; !ok {
			ident.Key = alloc.NewVar(ident.Name)
		}
		stmt = &expr.Var{
			Token: op,
			Ident: ident,
			Value: childs[1:],
		}
}
```

### Resulting benchmark and pprof

{{<callout type="Tip">}}
Hashing seems to be a lot faster on my beefy computer, the benchmarks from my macbook resulted in the following:

Map key hashing for string is expensive, the program spends 1.03s of its
execution (20.93%) in the function `aeshashbody`, 0.62s in
`runtime.mapassign_faststr` (12.6%) and 0.46s in `runtime.mapaccess2_faststr`
(9.35%). Moving from strings to uint32 for map keys replaced these with
spending 0.62s in `runtime.memhash32` (15.7%), 0.31s in `runtime.mapassign_fast32`
(7.85%) and 0.36s in `runtime.mapaccess2_fast32` (9.11%). The cumulated map
interactions previously took 3.11s (42.88%) of the total execution time. With
the key change from string to uint32, the total map interaction time went down
to 1.29s (32.66%).
{{</callout>}}

So lets benchmark this drastic change and take a look what happened in comparison to the previous change:

![profiler-final](/programming-lang-performance/profiler_final.png)

We replaced the expensive map access via string keys and replaced them with
their respective `32` variants. This changed the cumulated amount of
application runtime for map access from previously 0.62s or 33.7% to 0.66s or
40%, however our hyperfine benchmark tells us we decreased the total runtime by
~400ms from previously 2s to 1.6s:

![benchmark-final](/programming-lang-performance/benchmark_final.png)

## Final benchmarks

Lets compare the previous stage with the optimised stage of the project via hyperfine:

![benchmark_pc](/programming-lang-performance/benchmark_pc.png)

{{<callout type="Pc Specs">}}
_Hit em with the neofetch_:

![neofetch](/programming-lang-performance/neofetch.png)

{{</callout>}}

This of course being my beefy machine, if I run the same benchmark on my
macbook from 2012, I mainly develop on while in university (and i first ran the
benchmark on), the delta is a lot more impressive:

{{<callout type="Macbook Specs">}}
_Hit em with the (second) neofetch_:

![neofetch_macbook](/programming-lang-performance/neofetch_macbook.png)

{{</callout>}}

![benchmark_macbook](/programming-lang-performance/benchmark_macbook.png)

Compared to a ~4x improvement a ~7x improvement is a lot more impressive.
