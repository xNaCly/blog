---
title: "Sophia Lang Weekly - 01"
summary: "New object/array index syntax, use Go functions from sophia"
date: 2023-12-15
tags:
  - sophia
---

This week I added support for `-` in identifiers, reworked the array and object
index notation (again, but this time with an even better reasoning than last
weeks), introduced something i call _known function interface_ - `KFI` for
short for exposing go functions into the sophia runtime and I have a lot of
features and improvements planned some of which I will outline at the end.

## Support for '-' in identifiers

I like the possibilites S-Expressions bring to language expression, such as
allowing `-` in identifiers. Therefore I added support for `-` in identifiers to the lexer:

```lisp
;; mock hash
(fun fnv-1a (_ string)
    (len string))
(println (fnv-1a "Hello World")) ;; 11
```

## Reworked array and object index notation (V2)

Read about my second try of getting array and object indexing right - hopefully the last time :^).

### The First Problem

Last week I introduced a pretty nasty bug, caused by the lexer not being able
to correctly tokenize `(println array.2.0)` (maybe correct, but not in the way
we want it to):

The expression results in the following token stream:

| Tokentype         | Raw     |
| ----------------- | ------- |
| TOKEN_LEFT_BRACE  | (       |
| TOKEN_IDENT       | println |
| TOKEN_IDENT       | array   |
| TOKEN_DOT         | .       |
| TOKEN_FLOAT       | 2.0     |
| TOKEN_RIGHT_BRACE | )       |

This is absolutly not what we want, our parser now thinks we want to access the
array at position 2 instead of accessing the first element of the array element
at position 2 of the original `array`.

### The Second Problem

The simple solution is to use a different way of indexing into arrays, I mean
it works for objects right?

Sadly it doesn't - consider the following:

```lisp
(let object { name: "xnacly" skill: 0 })
(let keys "name" "skill")
(for (_ i) keys
;; how do we dynamically access the keys of the object?
    (println "what am i doing?"))
```

The catch being - we can't use our previous object index notation for accessing
object fields dynamically and thats a feature i really want.

Even if we were to change the notation for array indexing we would still not be
able to access objects in a nice way and we would have two notations for a
pretty similar operation, like JavaScript does it:

```js
let arr = [1, 2, 3, 4];
console.log(arr[0]);
let object = { name: "xnacly", skill: 0 };
console.log(object.name);
// or
console.log(object["name"]);
```

I do not want two ways to do the same thing, thus I though about ways to make
indexing as intuitive as possible and came to the conclusion: Why not simply
discard the `object.field` notation and only use `object["field"]` and
`array[index]`? That way the language has a consistent feel for indexing and we
solved our lexer issues.

{{<callout type="Tip">}}
The cautios reader will have noticed this syntax change will cause some
problems regarding array creation. Don't worry, I will lay out the mitigation
in the following chapter.
{{</callout>}}

### The solution

I took inspiration from the previous mentioned dynamic JavaScript object index
syntax and of course took a look at python, that uses the same syntax but also
omits the `object.field` notation, similar to what i want to implement:

```py
obj = {
    "name": "xnacly",
    "skill": 0,
}
print(obj["name"])
```

So I changed the parser and now object and array index notation is awesome and
id say more redable than before:

```lisp
(let object {
    workers: #[ ;; new array declaration syntax
        { name: "drone1" efficiency: 0.25 }
        { name: "drone2" efficiency: 0.55 }
    ]
})

;; accessing an object field by a known key:
(println object["workers"])

;; accessing an object field dynamically:
(let field "whatever")
(println object[field]) ;; results in <nil>

;; nested array and object access:
(println object["workers"][1]["name"]) ;; results in "drone2"
```

I also again improved the error messages for indexing, see
[4ed459e](https://github.com/xNaCly/Sophia/commit/4ed459ef58ae881fb9c7d6547a17a2a334acc1d3).

## Reworked array creation

I reworked array declaration because I need the `[]` for the previously
introduced syntax feature, thus I switched from

```lisp
(let arr [1 2 3 4])
```

To prefixing array creation with `#`:

```lisp
(let arr #[1 2 3 4])
```

Arrays are now treated as primitives and can be included in object definitions:

```lisp
(let person {
    name: "xnacly"
    skill: 0.0
    stats: #[
        {
            name: "health"
            value: 0.75
        }
        {
            name: "saturation"
            value: 0.75
        }
    ]
})
(println person["name"] "stats:")
(for (_ stat) person["stats"]
    (println stat["name"] stat["value"]))
```

This enables the parser to distinguish between array access and array declaration.

## Somewhat of a foreign function interface

[pims](https://lobste.rs/~pims) on [lobster](https://lobste.rs) asked for a
very cool feature:

> [...]
>
> _Not sure if you’re open to feature requests, but exposing host functions,
> similar to wasm/lua/etc. would be great. One could write most of the logic in
> Sophia but hook into the extensive go ecosystem when needed._
>
> ~ pims, [link](https://lobste.rs/s/gvjeve/sophia_lang_weekly_00#c_muyhox)

As I am always open to suggestions and didn't even think about exposing
functions written in Go into the sophia runtime before, I got to work.

{{<callout type="Tip">}}
_KFI is a pun on FFI, because we know our functions, their signature and their
body and they must be defined in the same binary the sophia language runtime is
embedded in._
{{</callout>}}

For starters I rewrote the `expr.Call.Eval()` method to include a fast path for
executing built ins, simply because Go manages argument assignment, stack
management, scoping, etc. thus we can omit that:

```go
// core/expr/Call.go
func (c *Call) Eval() any {
	storedFunc, ok := consts.FUNC_TABLE[c.Key]
	if !ok {
		serror.Add(c.Token, "Undefined function", "Function %q not defined", c.Token.Raw)
		serror.Panic()
	}

	def, ok := storedFunc.(*Func)
	if !ok {
        // this branch is hit if a function is not of type *Func which only
        // happens for built ins, thus the cast can not fail
		function, _ := storedFunc.(func(token *token.Token, args ...types.Node) any)
		return function(c.Token, c.Params...)
	}
    // [...]
}
```

Then I reused my allocator for faster map keys and create the first built-in
replacing the `put` keyword and the `expr.Put` structure:

```go
// builtin provides functions that are built into the sophia language but are
// written in pure go, they may interface with the sophia lang via AST
// manipulation and by accepting AST nodes and returning values or nodes.
//
// See docs/Embedding.md for more information.
package builtin

import (
	"os"
	"sophia/core/alloc"
	"sophia/core/consts"
	"sophia/core/serror"
	"sophia/core/shared"
	"sophia/core/token"
	"sophia/core/types"
	"strings"
)

var sharedPrintBuffer = &strings.Builder{}

func init() {
    // [...]
	consts.FUNC_TABLE[alloc.NewFunc("println")] = func(tok *token.Token, args ...types.Node) any {
		sharedPrintBuffer.Reset()
		shared.FormatHelper(sharedPrintBuffer, args, ' ')
		sharedPrintBuffer.WriteRune('\n')
		os.Stdout.WriteString(sharedPrintBuffer.String())
		return nil
	}
}
```

### Usage Examples

Now some examples taken from
[docs/Embedding](https://xnacly.github.io/Sophia/Embedding.html).

#### Linking strings.Split

```go
func init() {
	// [...]
	consts.FUNC_TABLE[alloc.NewFunc("strings-split")] = func(tok *token.Token, args ...types.Node) any {
		if len(args) != 2 {
			serror.Add(tok, "Argument error", "Expected exactly 2 argument for strings-split built-in")
			serror.Panic()
		}
		v := args[0].Eval()
		str, ok := v.(string)
		if !ok {
			serror.Add(tok, "Error", "Can't split target of type %T, use a string", v)
			serror.Panic()
		}

		v = args[1].Eval()
		sep, ok := v.(string)
		if !ok {
			serror.Add(tok, "Error", "Can't split string with anything other than a string (%T)", v)
			serror.Panic()
		}

		out := strings.Split(str, sep)

		// sophia lang runtime only sees arrays containing
		// elements whose types were erased as an array.
		r := make([]any, len(out))
		for i, e := range out {
			r[i] = e
		}

		return r
	}
}
```

This maps the `strings.Split` function from the go standard library to the
`strings-split` sophia function. All functions defined with the KFI have access
to the callees token and all its arguments, for instance:

```lisp
(strings-split "Hello World" "")
;; token: strings-split
;; n: "Hello World", " "
```

The `token` parameter points to `strings-split`, `n` contains 0 or more
arguments to the call, here its `["Hello World", " "]`.

#### typeof

We can do whatever go and the sophia lang type system allow. You can print an
expressions type without evaluating it:

```go
consts.FUNC_TABLE[alloc.NewFunc("typeof")] = func(tok *token.Token, n ...types.Node) any {
    if len(n) != 1 {
        serror.Add(tok, "Argument error", "Expected exactly 1 argument for typeof built-in")
        serror.Panic()
    }
    return fmt.Sprintf("%T", n[0])
}
```

And call this function from sophia:

```text
$ cat test.phia; echo "------"; sophia test.phia
(println (typeof #[1 "test" test 25.0]))
(println (typeof true))
(println (typeof "test"))
(println (typeof 12))
(println (typeof { key: "value" }))
------
*expr.Array
*expr.Boolean
*expr.String
*expr.Float
*expr.Object
```

### Consequences

- calling built-in functions is less expensive than calling sophia functions,
  simply because the go runtime manages the callstack, scope, etc... => high
  performance for often used operationes, very nice
- removal of the `expr.Put` structure

## Removing the JavaScript target

I removed the JavaScript target because I grew tired of maintaining a secondary
backend while not using it for anything. Thus I stripped the `Node.CompileJs(b
*strings.Builder)` function from the `Node` interface and removed the function
from all expressions.

In the same breath I cleaned the configuration and cli flags up: I removed the
`-ast` and `-tokens` flags and merged them under the `-dbg` flag. I also
removed the `-target` flag, simply because its not used anymore. All of these
were also removed from the `core.Config` structure.

## Planned features

{{<callout type="Regarding Modules">}}
Do not worry, i havent forgotten about [last weeks planned
feature](https://xnacly.me/posts/2023/sophia-lang-weekly00/#planned-feature-modules).
Its a big feature and I'm still experimenting with the way i want to implement
and design syntax.
{{</callout>}}

### Embedding the sophia programming language

I plan to enable the embedding of the sophia programming language runtime into
go application by a singular call and make it configurable to include links to
functions written in go via the new KFI feature, this will look something like:

```go
package main

import (
    "sophia"
    "sophia/core/types"
    "sophia/core/token"
)

func fib(n float64) float64 {
	bLast := 0.0
	last := 1.0
	for i := 0.0; i < n-1; i++ {
		t := bLast + last
		bLast = last
		last = t
	}
	return last
}

func main() {
    sophia.Embed(sophia.Configuration{
        Kfi: map[string]func(*token.Token, ...types.Node) any {
            "fib": func(tok *token.Token, args ...types.Node) any {
                if len(args) != 1 {
                    serror.Add(tok, "Argument error", "Expected exactly 1 argument")
                    serror.Panic()
                }
                ev := args[0].Eval()
                in, ok := ev.(float64)
                if !ok {
                    serror.Add(args[0].GetToken(), "Type error", "Expected float64 got %T", ev)
                    serror.Panic()
                }
                return fib(in)
            }
        }
    })
}
```
