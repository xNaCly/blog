---
title: "Sophia Lang Weekly - 02"
summary: "Again, new object/array index + function + loop syntax, built-in functions, a License and lambdas"
date: 2023-12-24
draft: true
tags:
  - sophia
---

First of all, merry christmas, second of all - This week I rewrote the array
and object index syntax, again (yes again). I also improved (I think) the way
functions and loops are defined. I introduced three new built-in functions and
added a license.

### New and improved function and for loop notation

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

### Reworked Array and Object indexing (V3)

Due to the aforementioned changes the currently not context aware parser
required a change for object and array indexing, this means prefixing the index
syntax with `#`:

```lisp
(let person { array: [1 2 3] })
(println person#["array"][0])
```

### New built-in functions

This week I introduced some eagerly awaited built-in functions, such as
mapping, filtering and asserting.

#### Map

This built-in allows for applying a function to every element of an array and
returing a new array containing the result of each function application.

```lisp
(fun square [n] (* n n))
(map (square) [1 2 3 4 5])
;; [1 4 9 16 25]
```

#### Filter

#### Assert

### Finally, a License

### Thinking about lambdas
