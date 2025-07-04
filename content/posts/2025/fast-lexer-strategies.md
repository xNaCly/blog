---
title: "Strategies for very fast Lexers"
summary: ""
date: 2025-07-03
draft: true
tags:
- C
---


{{<callout type="Warning">}}
In this blog post I'll explain strategies I used to make the purple garden
lexer really fast, that doesnt mean all approaches are feasible for your
usecase and architecture.
{{</callout>}}

# Introduction to Lexing

A lexer (often also a tokenizer) is the easiest part of any compilation and
language pipeline. The idea is to convert a list of characters into a list of
tokens in which each token conveys some meaning. This list of tokens can then
be used by the parser to generate an abstract syntax tree (AST), which the
compiler consumes, converting it to bytecode, which the vm executes.

## A compilation pipeline

As an overview:

```
┌───────────────────┐
│                   │
│       Lexer       │ <- we are here
│                   │
└─────────┬─────────┘
          │          
          │ Tokens <- and here
          │          
┌─────────▼─────────┐
│                   │
│       Parser      │
│                   │
└─────────┬─────────┘
          │          
          │ AST          
          │          
┌─────────▼─────────┐
│                   │
│      Compiler     │
│                   │
└─────────┬─────────┘
          │          
          │ Bytecode          
          │          
┌─────────▼─────────┐
│                   │
│  Virtual Machine  │
│                   │
└───────────────────┘
```

For a list of characters, lets say `(@std.fmt.println "my pi is: " 3.1415)`:

1. Input to the lexer:

    ```text
    (@std.fmt.println "my pi is: " 3.1415)
    ```

2. As characters:

    ```text
    (
    @
    s
    t
    d
    .
    f
    m
    t
    // ....
    )
    ```

3. As pseudo tokens:

    ```text
    (
    @std
    .
    fmt
    .
    println
    "my pi is: "
    3.1415
    )
    ```

The above is just an example and I'll go into detail below:

## Defining Tokens

A token is not only a set characters it can be mapped to, but it also holds:

- A token type, to easily distinguish between tokens
- Positional information:
    - start point
    - end or length
    - line number

Purple garden keeps it as minimal as possible and just has a String and a token type:

```c
typedef enum {
  // (
  T_DELIMITOR_LEFT = 1,
  // +
  T_PLUS = 2,
  // -
  T_MINUS = 3,
  // *
  T_ASTERISKS = 4,
  // /
  T_SLASH = 5,
  // =
  T_EQUAL = 6,
  // )
  T_DELIMITOR_RIGHT,
  // [
  T_BRAKET_LEFT,
  // ]
  T_BRAKET_RIGHT,
  // anything between ""
  T_STRING,
  // true
  T_TRUE,
  // false
  T_FALSE,
  // floating point numbers
  T_DOUBLE,
  // whole numbers
  T_INTEGER,
  // builtins in the format @<builtin>
  T_BUILTIN,
  // any identifier
  T_IDENT,
  // end marker
  T_EOF,
} TokenType;

typedef struct {
  TokenType type;
  // stores all values for T_STRING,T_IDENT,T_INTEGER and T_DOUBLE
  Str string;
} Token;
```

## Architecting a minimal Lexer

As explained in [A compilation pipeline](#a-compilation-pipeline), the lexer
iterates over the characters in the input and attempts to match found
characters to sets of characters, like keywords, numbers and symbols. For this
we will need to keep some state, even if though its not much:

```c
typedef struct {
  Str input; // <- String view over the input
  size_t pos; // <- current position in the input
} Lexer;
```

> `Str` as an abstraction is introduced in [Operating on zero copy, zero alloc string windows](#operating-on-zero-copy-zero-alloc-string-windows).

A naive approach would be:

```c
#define SINGLE_TOK(t) ((Token){.type = t})

Lexer Lexer_new(Str str) {
    return {
        .input=str,
        .pos=0
    };
}

Token Lexer_next(Lexer *l) {
    if (l->input.len == 0 || l->pos >= l->input.len) {
        return SINGLE_TOK(T_EOF)
    }

    Token t;
    switch(Str_get(l->input, l->pos)) {
        case '+':
            t = SINGLE_TOK(T_PLUS);
            break;
        case '-':
            t = SINGLE_TOK(T_MINUS);
            break;
        case '*':
            t = SINGLE_TOK(T_ASTERISKS);
            break;
        case '/':
            t = SINGLE_TOK(T_SLASH);
            break;
        // ... thinks like strings, quoted symbols, numbers, comments, whitespace :^)
        default:
            t = SINGLE_TOK(T_EOF);
            break;
    }
    l->pos++;
    return t;
}
```

And one could consume the api as follows (even with a little type->string
lookup for debugging):

```c
const char* TOKEN_TYPE_MAP[] = {
    [T_PLUS] = "T_PLUS",
    [T_MINUS] = "T_MINUS",
    [T_ASTERISKS] = "T_ASTERISKS",
    [T_SLASH] = "T_SLASH",
    [T_EOF] = "T_EOF"
};

Str s = STRING("+-*/");
Lexer l = Lexer_new(s);
while(l.pos < l.input.len) {
    Token t = Lexer_next(&l);
    puts(TOKEN_TYPE_MAP[t.type]);
}
```

{{<callout type="Tip - Designated initializers">}}
Designated initializers (`[<int>] = <value>`) are allowed by ISO C99, while
designated initializers with ranges (`[<int> .. <int>] = <value>`) are a gnu
extension, see [6.2.11 Designated Initializers
](https://gcc.gnu.org/onlinedocs/gcc/Designated-Inits.html).
{{</callout>}}

# Making it fast

Lets get into some optimisations and strategies for creating a clean, minimal
and especially fast lexer.

## Computed gotos, or: Threaded Lexing

`Threaded Lexing` is a reference to _Threaded code_, see
[wikipedia](https://en.wikipedia.org/wiki/Threaded_code). The idea is to
replace the switch statement with a jump to a block inside of the lexer. The
easiest way I could think of implementing this was to:

1. Define a jump table mapping lexeme start characters to their respective blocks

    ```c
    static void *jump_table[256] = {
      // first bind all possible bytes to the unkown label, so there are no out
      // of bound reads
      [0 ... 255] = &&unknown,

      // replace all known bytes with correct jump labels
      ['('] = &&delimitor_left,
      [')'] = &&delimitor_right,
      ['['] = &&braket_left,
      [']'] = &&braket_right,
      ['@'] = &&builtin,
      ['+'] = &&plus,
      ['-'] = &&minus,
      ['/'] = &&slash,
      ['*'] = &&asterisks,
      ['='] = &&equal,
      [' '] = &&whitespace,
      ['\t'] = &&whitespace,
      ['\n'] = &&whitespace,
      [';'] = &&comment,
      ['.'] = &&number,
      ['0' ... '9'] = &&number,
      ['a' ... 'z'] = &&ident,
      ['A' ... 'Z'] = &&ident,
      ['\''] = &&quoted,
      ['_'] = &&ident,
      ['"'] = &&string,

      // handle the edgecase of being at the end of the input
      [0] = &&end,
    };
    ```

2. Create a macro for jumping to the label

    ```c
    #define JUMP_TARGET goto *jump_table[(int8_t)l->input.p[l->pos]]
    ```

3. At the start of the lexer, call the macro

    ```c
    JUMP_TARGET
    ```

Putting it all together lets us build the following threaded lexer:

```c
size_t Lexer_all(Lexer *l, Allocator *a, Token **out) {
  ASSERT(out != NULL, "Failed to allocate token list");

  // empty input
  if (l->input.len == 0) {
    return 1;
  }

  static void *jump_table[256] = {
      [0 ... 255] = &&unknown,
      ['('] = &&delimitor_left,
      [')'] = &&delimitor_right,
      ['['] = &&braket_left,
      [']'] = &&braket_right,
      ['@'] = &&builtin,
      ['+'] = &&plus,
      ['-'] = &&minus,
      ['/'] = &&slash,
      ['*'] = &&asterisks,
      ['='] = &&equal,
      [' '] = &&whitespace,
      ['\t'] = &&whitespace,
      ['\n'] = &&whitespace,
      [';'] = &&comment,
      ['.'] = &&number,
      ['0' ... '9'] = &&number,
      ['a' ... 'z'] = &&ident,
      ['A' ... 'Z'] = &&ident,
      ['\''] = &&quoted,
      ['_'] = &&ident,
      ['"'] = &&string,
      [0] = &&end,
  };

#define JUMP_TARGET goto *jump_table[(int8_t)l->input.p[l->pos]]

  JUMP_TARGET;

delimitor_left:
  JUMP_TARGET;

delimitor_right:
  JUMP_TARGET;

braket_left:
  JUMP_TARGET;

braket_right:
  JUMP_TARGET;

builtin:
  JUMP_TARGET;

plus:
  JUMP_TARGET;

minus:
  JUMP_TARGET;

slash:
  JUMP_TARGET;

equal:
  JUMP_TARGET;

asterisks:
  JUMP_TARGET;

number:
  JUMP_TARGET;

ident:
  JUMP_TARGET;

quoted:
  JUMP_TARGET;

string:
  JUMP_TARGET;

comment:
  JUMP_TARGET;

whitespace:
  JUMP_TARGET;

unknown: 
  return 1;

end:
  return 0;
}
```

Replacing the switch with an array index and a jump. The latter is
significantly faster than the former due to:

- Better [code density](https://en.wikipedia.org/wiki/Instruction_set_architecture#Code_density)
- Less cache misses, better branch prediction


{{<callout type="Warning">}}
There are two downsides to this approach:

1. It is not supported by MSVC toolchain (clang, gcc only)
2. It makes reading and debugging the lexer far more complicated
{{</callout>}}


## Operating on zero copy, zero alloc string windows

Our lexer doesn't require mutable strings, C does not come with a string
abstraction out of the box and I wanted to attach metadata to strings - so I
came up with a small string abstraction:

```c
// str is a simple stack allocated wrapper around C char arrays, providing
// constant time length access and zero allocation+copy interactions for all
// methods except Str_to
typedef struct {
  // store the pointer to the underlying char
  const uint8_t *p;
  // hash of the input, do not expect it to be filled, has to be computed via
  // Str_hash or inline in the lexer
  uint64_t hash;
  // length of the input without a zero terminator
  size_t len;
} Str;
```

```c
#define STRING(str) ((Str){.len = sizeof(str) - 1, .p = (const uint8_t *)str})
#define STRING_EMPTY ((Str){.len = 0, .p = NULL})

```

Creating a `Str` from a c style `const char*` can be done by passing it into
the `STRING` macro, gcc can evaluate all operations inside of it at compile
time. Since the view doesnt own its underlying data, its cheap to copy and
create slices by just pointing new views to the underlying buffer.

I use this struct throughout the whole codebase, but specifically inside of the
lexer to create views over the original input that point to the contents of
some tokens:

```c
// example inside of handling strings in the lexer:

// dummy values for start and hash
size_t start = 3;
size_t hash = 0xAFFEDEAD;

Token *t = &(Token){};
t->type = T_STRING;
t->string = (Str){
    .p = l->input.p + start,
    .len = l->pos - start,
    .hash = hash,
};
```

Due to the window nature of this struct I had to reimplement some things
myself, such as slicing, concatination, equality checking, hashing and
converting to `int64` and `double`:

```c
char Str_get(const Str *str, size_t index);
Str Str_from(const char *s);
Str Str_slice(const Str *str, size_t start, size_t end);
Str Str_concat(const Str *a, const Str *b, Allocator *alloc);
bool Str_eq(const Str *a, const Str *b);
void Str_debug(const Str *str);
size_t Str_hash(const Str *str);
int64_t Str_to_int64_t(const Str *str);
double Str_to_double(const Str *str);
```

Lets quickly go over the interesting ones, specifically slicing and converting
to other data types. Slicing is super easy, since we just move the start and
the end to the new slice start and end.

```c
Str Str_slice(const Str *str, size_t start, size_t end) {
  ASSERT(end >= start, "Str_slice: Invalid slice range: end must be >= start");
  ASSERT(end <= str->len, "Str_slice: Slice range exceeds string length");

  return (Str){
      .p = str->p + start,
      .len = end - start,
  };
}
```

Converting to `int64` is also fairly uncomplicated, since the lexer is expected
to make sure all characters are in the integer set. The algorithm consists of
converting the character representation of an integer component into its
literal value by subtracting `'0'` from it. The resulting value is added to the
product of the previous iteration and 10, since we are working in the decimal
system.

```c
int64_t Str_to_int64_t(const Str *str) {
  int64_t r = 0;
  ASSERT(str->len > 0, "Cant convert empty string into int64_t");

  for (size_t i = 0; i < str->len; i++) {
    int digit = str->p[i] - '0';
    ASSERT(r < (INT64_MAX - digit) / 10,
           "int64_t number space overflow: `%.*s`", (int)str->len, str->p)
    r = r * 10 + digit;
  }

  return r;
}
```

Doubles are represented differently. By their mantiassa and exponent, which
requires a slightly more sophisticated conversion algorithm. In the same vain
as `Str_to_int64_t`, validating 

```c
double Str_to_double(const Str *str) {
  ASSERT(str->len > 0, "Can't convert empty string into double");

  const char *p = (const char *)str->p;
  size_t len = str->len;

  uint64_t mantissa = 0;
  int exponent = 0;
  bool seen_dot = false;
  bool has_digits = false;

  // we dont check that all chars are numbers here, since the lexer already does
  // that
  for (size_t i = 0; i < len; i++) {
    char c = p[i];

    if (c == '.') {
      seen_dot = true;
      continue;
    }

    has_digits = true;
    short digit = c - '0';
    ASSERT(mantissa <= (UINT64_MAX - digit) / 10, "Mantissa overflow");
    mantissa = mantissa * 10 + digit;
    if (seen_dot) {
      exponent -= 1;
    }
  }

  // if there were no digits after the '.'
  ASSERT(has_digits, "Can't parse `%.*s` into a double", (int)len, p);

  double result = (double)mantissa;
  // skip exponent computation for <mantissa>.0, since these are just the
  // mantissa
  if (exponent != 0) {
    result *= pow(10.0, exponent);
  }

  return result;
}
```

## Hashing everything
## Lazy conversions and number parsing
## Interning Tokens
## Prehashing keywords for comparisons 
## Abstracting allocations via the Allocator interface
## Extra: memory mapping the input

# Combining select strategies with later compiliation pipeline stages
## With the parser
## With the compiler

# Micro and Macrobenchmarks
