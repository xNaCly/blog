---
title: "Intertwining Registers and Stack for Fast Function Calls"
summary: " Designing a calling convention by merging registers and a stack in my bytecode VM"
date: 2025-06-01
tags:
  - C
  - pldev
draft: true
---

I'm building another programming language, this time less lispy, but still
S expression based. It's not inherently functional, but has pure functions. I wanted
to make a fast programming language that's fun to implement and fun for me to
program in. So far, this is the result.

## Calling and defining Functions

Since every good language needs a way to structure and reuse code, purple
garden (pg) needs functions.

```scheme
; (@function <name> [<list of arguments>] <s-expr body>)
(@function no-args-no-return [] (@None))
(@function one-arg [a] (@Some a))
(@function two-args [a b] (@Some a))
(@function three-args [a b c] (@Some a))
(@function four-args [a b c d] (@Some a)
; ...
```

And we just call them in the 

```scheme
(no-args-no-return)
(one-arg 1)
(two-args 1 2)
(three-args 1 2 3)
(four-args 1 2 3 4)
```

## Generating Definition Bytecode

### No argument

```scheme
(@function no-args [])
```

No argument, means no prep for 

```asm
__entry:
__0x000000[01EC]: no-args
        JMP 2
        LEAVE

        ; ...
```

### Single Argument

### Multiple Arguments

## Generating Call site Bytecode

### No argument

```scheme
(@function no-args [])
(no-args)
```

Since we don't pass any arguments, the call is just the `OP_CALL` and bytecode
index for the function definition, here `0`:

```asm
__entry:
        ; ...

        CALL 0: <no-args>
```

### Single Argument

### Multiple Arguments


## Defining Functions in the Virtual Machine

## Executing Functions in the Virtual Machine

## Extra Section for Flexing Micro Benchmarks
