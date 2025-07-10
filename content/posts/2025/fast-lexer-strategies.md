---
title: "Strategies for very fast Lexers"
summary: "Making compilation pipelines fast, starting with the tokenizer"
date: 2025-07-11
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


## Abstracting allocations via the Allocator interface

I want to allow the user of purple-garden to choose between allocation
strategies like my garbage collectors and a bump allocator. For this I need an
interface to marry several backing implementations into a singular api:

```c
#ifndef MEM_H
#define MEM_H

#include <stddef.h>

#ifdef DEBUG
#if DEBUG
#define VERBOSE_ALLOCATOR 1
#endif
#else
#define VERBOSE_ALLOCATOR 0
#endif

// 1MB
#define GC_MIN_HEAP 1024 * 1024

typedef struct {
  size_t current;
  size_t allocated;
} Stats;

// CALL is used to emulate method calls by calling a METHOD on SELF with
// SELF->ctx and __VA_ARGS__, this is useful for interface interaction, such as
// Allocator, which reduces alloc_bump.request(alloc_bump.ctx, 64); to
// CALL(alloc_bump, request, 64), removing the need for passing the context in
// manually
#if VERBOSE_ALLOCATOR
#include <stdio.h>
#define CALL(SELF, METHOD, ...)                                                \
  (fprintf(stderr, "[ALLOCATOR] %s@%s::%d: %s->%s(%s)\n", __FILE__, __func__,  \
           __LINE__, #SELF, #METHOD, #__VA_ARGS__),                            \
   (SELF)->METHOD((SELF)->ctx, ##__VA_ARGS__))
#else
#define CALL(SELF, METHOD, ...) (SELF)->METHOD((SELF)->ctx, ##__VA_ARGS__)
#endif

// Allocator defines an interface abstracting different allocators, so the
// runtime of the virtual machine does not need to know about implementation
// details, can be used like this:
//
//
//  #define ALLOC_HEAP_SIZE = 1024
//  Allocator alloc_bump = bump_init(ALLOC_HEAP_SIZE);
//
//  size_t some_block_size = 16;
//  void *some_block = alloc_bump.request(alloc_bump.ctx, some_block_size);
//
//  alloc_bump.destroy(alloc_bump.ctx);
//
typedef struct {
  // Allocator::ctx refers to an internal allocator state and owned memory
  // areas, for instance, a bump allocator would attach its meta data (current
  // position, cap, etc) here
  void *ctx;

  // Allocator::stats is expected to return the current statistics of the
  // underlying allocator
  Stats (*stats)(void *ctx);
  // Allocator::request returns a handle to a block of memory of size `size`
  void *(*request)(void *ctx, size_t size);
  // Allocator::destroy cleans state up and deallocates any owned memory areas
  void (*destroy)(void *ctx);
} Allocator;

Allocator *bump_init(size_t size);
Allocator *xcgc_init(size_t size, void *vm);

#endif
```

For instance: this allocator is then passed to the virtual machine. The vm uses
`Allocator->request(Allocator->ctx, sizeof(Value))` to allocate a new runtime
value.

I included a `CALL` macro for cleaning this duplicated context passing up:

```c
Allocator *a = bump_init(1024);

// before:
void *block = a->request(a->ctx, 512);
a->destroy(a->ctx)

// after:
void *block = CALL(a, request, 512);
CALL(a, destroy)
```

This macro also enables verbose allocation insights for debugging purposes:

```text
[ALLOCATOR] vm.c@freelist_preallocate::59: fl->alloc->request(sizeof(Frame))
[ALLOCATOR] main.c@main::245: vm.alloc->stats()
[ALLOCATOR] main.c@main::255: pipeline_allocator->destroy()
[ALLOCATOR] vm.c@Vm_destroy::283: vm->alloc->destroy()
```

The implementation of said interface is straightforward:

```c
// Bump allocator header
typedef struct {
  // points to the start of the allocated block from which Allocator::request
  // will hand out aligned chunks
  void *block;
  // the size of said allocated block
  size_t len;
  // the current amount of bytes in use
  size_t pos;
} BumpCtx;

void *bump_request(void *ctx, size_t size) {
  BumpCtx *b_ctx = (BumpCtx *)ctx;
  size_t align = sizeof(void *);
  b_ctx->pos = (b_ctx->pos + align - 1) & ~(align - 1);
  ASSERT(b_ctx->pos + size <= b_ctx->len, "OOM :( with %zu", b_ctx->len);
  void *block_entry = (char *)b_ctx->block + b_ctx->pos;
  b_ctx->pos += size;
  return block_entry;
}

void bump_destroy(void *ctx) {
  ASSERT(ctx != NULL, "bump_destroy on already destroyed allocator");
  BumpCtx *b_ctx = (BumpCtx *)ctx;
  // madvise(2):
  // The  application  no  longer requires the pages in the range
  // specified by addr and len. The kernel can thus  free  these
  // pages,  but  the freeing could be delayed until memory pres‐
  // sure occurs.
  madvise(b_ctx->block, b_ctx->len, MADV_FREE);
  int res = munmap(b_ctx->block, b_ctx->len);
  ASSERT(res == 0, "munmap failed");
  free(ctx);
}

Stats bump_stats(void *ctx) {
  BumpCtx *b_ctx = (BumpCtx *)ctx;
  return (Stats){.allocated = b_ctx->len, .current = b_ctx->pos};
}

Allocator *bump_init(size_t size) {
  long page_size = sysconf(_SC_PAGESIZE);
  size = (size + page_size - 1) & ~(page_size - 1);

  void *b = mmap(NULL, size, PROT_READ | PROT_WRITE,
                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  ASSERT(b != MAP_FAILED, "failed to mmap allocator buffer");

  BumpCtx *ctx = malloc(sizeof(BumpCtx));
  ASSERT(ctx != NULL, "failed to bump allocator context");
  ctx->len = size;
  ctx->pos = 0;
  ctx->block = b;

  Allocator *a = malloc(sizeof(Allocator));
  ASSERT(ctx != NULL, "failed to alloc bump allocator");
  a->ctx = (void *)ctx;
  a->destroy = bump_destroy;
  a->request = bump_request;
  a->stats = bump_stats;

  return a;
}
```


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

Doubles are represented differently, specifcally by their mantiassa and
exponent, requiring a slightly more sophisticated conversion algorithm. In the
same vain as `Str_to_int64_t`, validating is already done by the lexer to the
extend of only allowing any of `.1234567890`.

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

I want to distinguish atoms (strings, numbers, idents) from other atoms for
interning purposes and faster comparisons in the pipeline. This can be done via
hashes, especially since we already "visit" each member of said atoms while
converting them to tokens. Hashing them is therefore just a matter of
computations while walking the atoms underlying bytes.

For instance strings: before this, the lexer just advanced until it hit the closing delimitor or EOF:

```c
size_t Lexer_all(Lexer *l, Allocator *a, Token **out) {

    // ...

string: {
  // skip "
  l->pos++;
  size_t start = l->pos;
  for (char cc = cur(l); cc > 0 && cc != '"'; l->pos++, cc = cur(l)) {}

  if (UNLIKELY(cur(l) != '"')) {
    Str slice = Str_slice(&l->input, l->pos, l->input.len);
    fprintf(stderr, "lex: Unterminated string near: '%.*s'", (int)slice.len,
            slice.p);
    out[count++] = INTERN_EOF;
  } else {
    Token *t = CALL(a, request, sizeof(Token));
    t->type = T_STRING;
    t->string = (Str){
        .p = l->input.p + start,
        .len = l->pos - start,
    };
    out[count++] = t;
    // skip "
    l->pos++;
  }
  JUMP_TARGET;
}

    // ...

}
```

Adding hashing to this is fairly easy:

```diff
diff --git a/lexer.c b/lexer.c
index 316a494..2280a6b 100644
--- a/lexer.c
+++ b/lexer.c
@@ -286,10 +286,7 @@ string: {
   // skip "
   l->pos++;
   size_t start = l->pos;
+  size_t hash = FNV_OFFSET_BASIS;
   for (char cc = cur(l); cc > 0 && cc != '"'; l->pos++, cc = cur(l)) {
+    hash ^= cc;
+    hash *= FNV_PRIME;
   }

   if (UNLIKELY(cur(l) != '"')) {
@@ -303,7 +300,6 @@ string: {
     t->string = (Str){
         .p = l->input.p + start,
         .len = l->pos - start,
+        .hash = hash,
     };
     out[count++] = t;
     // skip "
```

Numbers, identifiers and builtins are all also being hashed, I omitted this
here for clearity and since we will revisit this topic again in this article. 

## Interning Tokens

Most of the tokens we will encounter are constant, we know:

- their size
- their type

We can use this knowledge, statically allocate these and use their pointers to
reduce memory pressure:

```c
// we can "intern" these, since all of them are the same, regardless of position
Token *INTERN_DELIMITOR_LEFT = &SINGLE_TOK(T_DELIMITOR_LEFT);
Token *INTERN_DELIMITOR_RIGHT = &SINGLE_TOK(T_DELIMITOR_RIGHT);
Token *INTERN_BRAKET_LEFT = &SINGLE_TOK(T_BRAKET_LEFT);
Token *INTERN_BRAKET_RIGHT = &SINGLE_TOK(T_BRAKET_RIGHT);
Token *INTERN_MINUS = &SINGLE_TOK(T_MINUS);
Token *INTERN_PLUS = &SINGLE_TOK(T_PLUS);
Token *INTERN_ASTERISKS = &SINGLE_TOK(T_ASTERISKS);
Token *INTERN_SLASH = &SINGLE_TOK(T_SLASH);
Token *INTERN_FALSE = &SINGLE_TOK(T_FALSE);
Token *INTERN_TRUE = &SINGLE_TOK(T_TRUE);
Token *INTERN_EQUAL = &SINGLE_TOK(T_EQUAL);
Token *INTERN_EOF = &SINGLE_TOK(T_EOF);

// size_t Lexer_all(Lexer *l, Allocator *a, Token **out) 
```

`SINGLE_TOK` is just: 

```c
#define SINGLE_TOK(t) ((Token){.type = t})
```

## Prehashing keywords for comparisons

As introduced in the previous chapters, all identifers are hashed, thus we can
also hash the known keywords at startup and make comparing them very fast.

Lets take a look at `true` and `false`, both are known keywords and we will
need to compare found identifers to them. 

```c {hl_lines=[12]}
ident: {
  size_t start = l->pos;
  size_t hash = FNV_OFFSET_BASIS;
  for (char cc = cur(l); cc > 0 && is_alphanum(cc); l->pos++, cc = cur(l)) {
    hash ^= cc;
    hash *= FNV_PRIME;
  }

  size_t len = l->pos - start;
  Token *t;

  // comparing to the keywords is now just a number comparison
  if (hash == true_hash) {
    t = INTERN_TRUE;
  } else if (hash == false_hash) {
    t = INTERN_FALSE;
  } else {
    t = CALL(a, request, sizeof(Token));
    t->type = T_IDENT;
    t->string = (Str){
        .p = l->input.p + start,
        .len = len,
        .hash = hash,
    };
  }
  out[count++] = t;
  JUMP_TARGET;
}
```

{{<callout type="Tip - is_alphanum deep dive">}}

> I know this function shouldn't be called `is_alphanum` because it allows `[A-Za-z0-9_-]`

A naive check of `is_alphanum` can be:

```c
bool is_alphanum(char cc) {
    return (cc >= 'a' && cc <= 'z') || (cc >= 'A' && cc <= 'Z') 
        || (cc >= '0' && cc <= '9') || cc == '_' || cc == '-'
}
```

We know we can omit the uppercase check by converting the character to its
lowercase representation, so lets fold the character, since ASCII upper and
lowercase characters only differ by a single bit: 

```c
bool is_alphanum(char cc) {
  uint8_t lower = cc | 0x20;
  bool is_alpha = (lower >= 'a' && lower <= 'z');
  bool is_digit = (cc >= '0' && cc <= '9');
  return is_alpha || is_digit || cc == '_' || cc == '-';
}
```

In benchmarks I was able to measure `inline` and parameter type `uint8_t` have a
reproducible impact of reducing the runtime by 1-5% for identifier heavy
inputs, so I marked the function as "private" `static inline`:

```c
inline static bool is_alphanum(uint8_t cc) {
  uint8_t lower = cc | 0x20;
  bool is_alpha = (lower >= 'a' && lower <= 'z');
  bool is_digit = (cc >= '0' && cc <= '9');
  return is_alpha || is_digit || cc == '_' || cc == '-';
}
```

There are some other ways that could be more efficient, but I haven't benchmarked them:

1. statically allocated lookup table like:

    ```c
    static const bool is_alphanum_lookup[128] = {
        ['0' ... '9'] = true,
        ['A' ... 'Z'] = true,
        ['a' ... 'z'] = true,
        ['_'] = true,
        ['-'] = true,
    };
    inline static bool is_alphanum(uint8_t cc) {
        return cc < 128 && is_alphanum_lookup[cc];
    }
    ```


2. weird bit sets:

    > I don't fully understand this one and it sucks to read, so no thanks

    ```c
    static const uint64_t table1 = 0x03ff000000000000
    static const uint64_t table2 = 0x07fffffe07fffffe


    inline static bool is_alphanum(uint8_t cc) {
        if (cc >= 128) return false;
        return cc < 64 ? (table1 >> cc) & 1 : (table2 >> (cc - 64)) & 1;
    }
    ```

{{</callout>}}

## Lazy conversions and number parsing

## Extra: memory mapping the input

# Combining select strategies with later compiliation pipeline stages

## With the parser

## With the compiler

## Putting it all together

# Micro and Macrobenchmarks
