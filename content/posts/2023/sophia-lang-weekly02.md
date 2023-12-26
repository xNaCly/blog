---
title: "Sophia Lang Weekly - 02"
summary: "Again, new object/array index + function + loop syntax, built-in functions, a License and lambdas"
date: 2023-12-24
tags:
  - sophia
---

First of all, Merry Christmas, second of all - This week I rewrote the array
and object index syntax, again (yes again). I also improved (I think) the way
functions and loops are defined. I introduced three new built-in functions and
added a license.

## New and improved function and for loop notation

Due to outside feedback and my own thoughts on the previously employed
`function` and `for` loop parameter notation, I decided to switch from:

```lisp
(for (_ i) 5 (println i))
(fun square (_ n) (* n n))
```

To:

```lisp
(for [i] 5 (println i))
(fun square [n] (* n n))
```

## Reworked Array and Object indexing (V3)

Due to the aforementioned changes the currently not context aware parser
required a change for object and array indexing, this means prefixing the index
syntax with `#`:

```lisp
(let person { array: [1 2 3] })
(println person#["array"][0])
```

## New built-in functions

This week I introduced some eagerly awaited built-in functions, such as
mapping, filtering and asserting.

### Map

This built-in allows for applying a function to every element of an array and
returning a new array containing the result of each function application.

```lisp
(fun square [n] (* n n))
(map (square) [1 2 3 4 5])
;; [1 4 9 16 25]
```

### Filter

The `filter` built-in applies the function to every item in the array and keeps
the element in the resulting array if the function returns true, otherwise the
element is skipped in the result.

```lisp
(fun isEven [num] (= 0 (% num 2)))
(filter (isEven) [1 2 3 4 5])
;; [2 4]
```

### Assert

Asserting makes sure state is correct in the program with a fast way for
feedback:

```lisp
(assert (= 2 2))
```

`assert` checks if the argument expression evaluates to true, otherwise it
panics. The built-in also panics when provided with more than one argument or
the argument evaluating to a non boolean value.

## Finally, a License

I plan on implementing the embedding of sophia scripts into fully featured go
application to improve the way these applications can be configured and
scripted. I chose the permissive [MIT
license](https://en.wikipedia.org/wiki/MIT_License), due to me wanting to pave
the way for almost all projects to use sophia if they desire to do so.

## Planned features

### Thinking about lambdas

Both `map` and `filter` require a previously defined function to apply to array
elements. This can be cumbersome and verbose to type, thus I thought a lot
about a clean and concise syntax approach to anonymous functions, specifically
for usage in the `map` and `filter` built-ins:

```lisp
(map (lambda [n] (* n n)) [1 2 3 4 5])
(filter (lambda [n] (= 0 (% n 2))) [1 2 3 4 5])
```

This notation allows for omitting the function definition.

### Array ranges

A previously very badly implemented feature was ranges for array creation, such as:

```lisp
(let zeroToThree [0..3]) ;; [0 1 2 3]
(let oneToThree [1..3]) ;; [1 2 3]
```

I plan to reimplement this in a clean and efficient way.

### Deconstructing objects

The last feature I thought about was deconstructing values from objects into variables:

```lisp
(let person { name: "anon" age: 25 })
(let [name age] person)
(let [name] person)
;; shorthand for
(let name person#["name"])
(let age person#["age"])
(let name person#["name"])
```
