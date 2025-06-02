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

## VM Architecture, Bytecode and Disassembly

Since some consider programming languages and implementing one as modern day
magic, I'll introduce some basic concepts while going over the architecture of
purple gardens interpretation pipeline. 

### Building a register based bytecode virtual machine

### Building a bytecode compiler

### Calling a function

### Calling a builtin

## Calling and defining Functions

Since every good language needs a way to structure and reuse code, purple
garden (pg) needs functions.

```scheme
; (@function <name> [<list of arguments>] <s-expr body>)
(@function no-args [] (@None))
(@function one-arg [a] (@Some a))
(@function two-args [a b] (@Some a))
(@function three-args [a b c] (@Some a))
(@function four-args [a b c d] (@Some a))
; ...
```

And we just call them in the

```scheme
(no-args)
(one-arg 1)
(two-args 1 2)
(three-args 1 2 3)
(four-args 1 2 3 4)
```

## Generating Definition Bytecode

Once a function is defined the compiler emits bytecode for said function
including its body and the setup for all params, this differs for 0, 1 and n
arguments:

### No argument

```scheme
(@function no-args [] (@None))
```

No argument, thus we can omit prep for argument passing:

```asm
__globals:
        False; {idx=0}
        True; {idx=1}
        Option(None); {idx=2}

__entry:
__0x000000[01EC]: no-args
        JMP 6
        ARGS 0
        BUILTIN 1019: <@None>
        LEAVE
```

### Single Argument

```scheme
(@function one-arg [a] (@Some a))
```

A singular argument is passed by a pointer to its value being stored in `r0`,
this makes calling functions with a single argument way faster than using the
stack based method for enabling n arguments:

```asm
__0x000008[02B6]: one-arg
        JMP 20
        ; function head / parameter creation
        STORE 1 ; 1. move &Value from r0 to r1
        LOAD 4: Str(`a`) ; 2. load name of variable into r0
        VAR 1   ; 3. create an entry in variable table with the hash of its name
                ; (computed at compile time) and its &Value in r1

        ; function body
        LOADV 796972: $a
        BUILTIN 145: <@Some>
        LEAVE
```

### n Arguments

```scheme
(@function three-args [a b c] (@Some a))
```

This is where the mix of registers and stack is used. Since the value for the
last argument is always in `r0`. Any further arguments are stored on the stack:

```text
args: a b c
vals: 1 2 3

stack: 1 2
r0: 3
```

In the disassembled bytecode this results in simply one `POP` before comencing
with the already known argument setup:

```asm
__entry:
__0x000000[02CB]: three-args
        JMP 28

        ; function head

        ; create variable 'c' pointing to &Value
        STORE 1
        LOAD 3: Str(`c`)
        VAR 1

        ; pop &Value for variable 'b' from the stack top
        POP
        STORE 1
        LOAD 4: Str(`b`)
        VAR 1

        ; pop &Value for variable 'a' from the stack top
        POP
        STORE 1
        LOAD 5: Str(`a`)
        VAR 1

        ; function body
        LOADV 796972: $a
        BUILTIN 145: <@Some>
        LEAVE
```

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

### n Arguments

## Defining Functions in the Virtual Machine

## Executing Functions in the Virtual Machine

## Putting all examples together

```asm
__globals:
        False; {idx=0}
        True; {idx=1}
        Option(None); {idx=2}
        Str(`a`); {idx=3,hash=796972}
        Str(`b`); {idx=4,hash=798181}
        Str(`c`); {idx=5,hash=797778}
        Str(`d`); {idx=6,hash=795763}
        Int(1); {idx=7}
        Int(1); {idx=8}
        Int(2); {idx=9}
        Int(1); {idx=10}
        Int(2); {idx=11}
        Int(3); {idx=12}
        Int(1); {idx=13}
        Int(2); {idx=14}
        Int(3); {idx=15}
        Int(4); {idx=16}

__entry:
__0x000000[01EC]: no-args
        JMP 6
        ARGS 0
        BUILTIN 1019: <@None>
        LEAVE


__0x000008[02B6]: one-arg
        JMP 20
        STORE 1
        LOAD 3: Str(`a`)
        VAR 1
        LOADV 796972: $a
        BUILTIN 145: <@Some>
        LEAVE


__0x000016[00A1]: two-args
        JMP 42
        STORE 1
        LOAD 4: Str(`b`)
        VAR 1
        POP
        STORE 1
        LOAD 3: Str(`a`)
        VAR 1
        LOADV 796972: $a
        BUILTIN 145: <@Some>
        LEAVE


__0x00002C[02CB]: three-args
        JMP 72
        STORE 1
        LOAD 5: Str(`c`)
        VAR 1
        POP
        STORE 1
        LOAD 4: Str(`b`)
        VAR 1
        POP
        STORE 1
        LOAD 3: Str(`a`)
        VAR 1
        LOADV 796972: $a
        BUILTIN 145: <@Some>
        LEAVE


__0x00004A[0075]: four-args
        JMP 110
        STORE 1
        LOAD 6: Str(`d`)
        VAR 1
        POP
        STORE 1
        LOAD 5: Str(`c`)
        VAR 1
        POP
        STORE 1
        LOAD 4: Str(`b`)
        VAR 1
        POP
        STORE 1
        LOAD 3: Str(`a`)
        VAR 1
        LOADV 796972: $a
        BUILTIN 145: <@Some>
        LEAVE

        CALL 0: <no-args>
        LOAD 7: Int(1)
        CALL 8: <one-arg>
        PUSHG 8
        LOAD 9: Int(2)
        ARGS 2
        CALL 22: <two-args>
        PUSHG 10
        PUSHG 11
        LOAD 12: Int(3)
        ARGS 3
        CALL 44: <three-args>
        PUSHG 13
        PUSHG 14
        PUSHG 15
        LOAD 16: Int(4)
        ARGS 4
        CALL 74: <four-args>
```

## Extra Section for Flexing Micro Benchmarks

### The function calling example

{{<shellout lang="scheme">}}
$ head -n10 examples/bench.garden
%SEPARATOR%
(@function no-args [] (@None))
(@function one-arg [a] (@Some a))
(@function two-args [a b] (@Some a))
(@function three-args [a b c] (@Some a))
(@function four-args [a b c d] (@Some a))
(no-args)
(one-arg 1)
(two-args 1 2)
(three-args 1 2 3)
(four-args 1 2 3 4)
{{</shellout>}}

{{<shellout>}}
$ wc -l examples/bench.garden
%SEPARATOR%
25010 examples/bench.garden
{{</shellout>}}

{{<shellout>}}
$ make bench PG=examples/bench.garden
%SEPARATOR%
// [...]
[    0.0000ms] main::Args_parse: Parsed arguments
[    0.0360ms] io::IO_read_file_to_string: mmaped input of size=380261B
[    0.0080ms] mem::init: Allocated memory block of size=612368384B
[    3.8690ms] lexer::Lexer_all: lexed tokens count=125085
[    5.1560ms] parser::Parser_next created AST with node_count=25010
[    3.4340ms] cc::cc: Flattened AST to byte code/global pool length=180148/50017
[    4.1530ms] vm::Vm_run: executed byte code
[    3.7390ms] mem::Allocator::destroy: Deallocated memory space
[    0.0000ms] vm::Vm_destroy: teared vm down
[    0.0000ms] munmap: unmapped input
{{</shellout>}}
