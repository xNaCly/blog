---
title: "Abusing C to implement JSON Parsing with Struct Methods"
summary: "Json parsing in C using function pointers attached to a struct"
date: 2025-02-26
draft: true
tags:
  - json
  - c
---

## Idea

1. Build a JSON parser in c
2. Instead of using by itself functions: attach functions to a struct and use
   these as methods
3. make it C issue family free (segfaults, leaks, stack overflows, etc...)
4. provide an ergonomic API

### Usage

```c
#include "json.h"
#include <stdlib.h>

int main(void) {
  struct json json = json_new(JSON({
    "object" : {},
    "array" : [ [], {}],
    "atoms" : [ "string", 0.1, true, false, null ],
  }));
  struct json_value json_value = json.parse(&json);
  // json_type_map returns the json_type as char*
  printf("type: %s\n", json_type_map[json_value.type]);
  json_free_value(&json_value);
  return EXIT_SUCCESS;
}
```

{{<callout type="Tip - Compiling C projects the easy way">}}

> Dont take this as a guide for using make, in my projects I just use it as a
> command runner.

#### Compiler flags

> These flags can be specific to `gcc`, I use `gcc (GCC) 14.2.1 20250207`, so
> take this with a grain of salt.

I use these flags in almost every c project I ever started.

```sh
gcc -std=c23 \
	-O2 \
	-Wall \
	-Wextra \
	-Werror \
	-fdiagnostics-color=always \
	-fsanitize=address,undefined \
	-fno-common \
	-Winit-self \
	-Wfloat-equal \
	-Wundef \
	-Wshadow \
	-Wpointer-arith \
	-Wcast-align \
	-Wstrict-prototypes \
	-Wstrict-overflow=5 \
	-Wwrite-strings \
	-Waggregate-return \
	-Wswitch-default \
	-Wno-discarded-qualifiers \
	-Wno-aggregate-return \
    main.c
```

| Flag                            | Description                                                                                               |
| ------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `-std=c23 `                     | set lang standard, i use ISO C23                                                                          |
| `-O2 `                          | optimize more than `-O1`                                                                                  |
| `-Wall `                        | enable a list of warnings                                                                                 |
| `-Wextra `                      | enable more warnings than -Wall                                                                           |
| `-Werror `                      | convert all warnings to errors                                                                            |
| `-fdiagnostics-color=always `   | use color in diagnostics                                                                                  |
| `-fsanitize=address,undefined ` | enable AddressSanitizer and UndefinedBehaviorSanitizer                                                    |
| `-fno-common `                  | place uninitialized global variables in the BSS section                                                   |
| `-Winit-self `                  | warn about uninitialized variables                                                                        |
| `-Wfloat-equal `                | warn if floating-point values are used in equality comparisons.                                           |
| `-Wundef `                      | warn if an undefined identifier is evaluated                                                              |
| `-Wshadow `                     | warn whenever a local variable or type declaration shadows another variable, parameter, type              |
| `-Wpointer-arith `              | warn about anything that depends on the “size of” a function type or of void                              |
| `-Wcast-align `                 | warn whenever a pointer is cast such that the required alignment of the target is increased.              |
| `-Wstrict-prototypes `          | warn if a function is declared or defined without specifying the argument types                           |
| `-Wstrict-overflow=5 `          | warns about cases where the compiler optimizes based on the assumption that signed overflow does not occu |
| `-Wwrite-strings `              | give string constants the type `const char[length]`, warns on copy into non const char\*                  |
| `-Wswitch-default `             | warn whenever a switch statement does not have a default case                                             |
| `-Wno-discarded-qualifiers `    | do not warn if type qualifiers on pointers are being discarded.                                           |
| `-Wno-aggregate-return `        | do not warn if any functions that return structures or unions are defined or called.                      |

#### Sourcing source files

I generally keep my header and source files in the same directory as the
makefile, so i use `find` to find them:

```shell
shell find . -name "*.c"
```

#### Make and Makefiles

> I dont define the `build` target as `.PHONY` because i generally never have a `build` dir.

Putting it all together as a makefile:

```make
CFLAGS := -std=c23 \
	-O2 \
	-Wall \
	-Wextra \
	-Werror \
	-fdiagnostics-color=always \
	-fsanitize=address,undefined \
	-fno-common \
	-Winit-self \
	-Wfloat-equal \
	-Wundef \
	-Wshadow \
	-Wpointer-arith \
	-Wcast-align \
	-Wstrict-prototypes \
	-Wstrict-overflow=5 \
	-Wwrite-strings \
	-Waggregate-return \
	-Wcast-qual \
	-Wswitch-default \
	-Wno-discarded-qualifiers \
	-Wno-aggregate-return

FILES := $(shell find . -name "*.c")

build:
	$(CC) $(CFLAGS) $(FILES) -o jsoninc
```

{{</callout>}}

## Variadic macros to write inline raw JSON

This doesnt really deserve its own section, but I use `#<expression>` to
stringify C expressions in conjunction with `__VA_ARGS__`:

```c
#define JSON(...) #__VA_ARGS__
```

To enable:

```c
char *raw_json = JSON({ "array" : [ [], {}] });
```

Inlines to:

```c
char *raw_json = "{ \"array\" : [[]], }";
```

## Representing JSON values in memory

I need a structure to hold a parsed json value, their types and their values.

### Types of JSON values

JSON can be either one of:

1. null
2. true
3. false
4. number
5. string
6. array
7. object

In C i use an enum to represent this:

```c
// json.h
enum json_type {
  json_number,
  json_string,
  json_boolean,
  json_null,
  json_object,
  json_array,
};

extern char *json_type_map[];
```

And i use `json_type_map` to map all `json_type` values to their `char*` representation:

```c
char *json_type_map[] = {
    [json_number] = "json_number",   [json_string] = "json_string",
    [json_boolean] = "json_boolean", [json_null] = "json_null",
    [json_object] = "json_object",   [json_array] = "json_array",
};
```

### json_value & unions for atoms, array elements or object values and object keys

The `json_value` struct holds the type, as defined above, a union sharing
memory space for either a boolean, a string or a number, a list of `json_value`
structures as array children or object values, a list of strings that are
object keys and the length for the three aforementioned fields.

```c
struct json_value {
  enum json_type type;
  union {
    bool boolean;
    char *string;
    double number;
  } value;
  struct json_value *values;
  char **object_keys;
  // length is filled for json_type=json_array|json_object
  size_t length;
};
```

### Tearing values down

Since some of the fields in `json_value` are heap allocated, we have to destroy
/ free the structure upon either no longer using it or exiting the process.
`json_free_value` does exactly this:

```c
void json_free_value(struct json_value *json_value) {
  switch (json_value->type) {
  case json_string:
    free(json_value->value.string);
    break;
  case json_object:
    for (size_t i = 0; i < json_value->length; i++) {
      free(&json_value->object_keys[i]);
      json_free_value(&json_value->values[i]);
    }
    break;
  case json_array:
    for (size_t i = 0; i < json_value->length; i++) {
      json_free_value(&json_value->values[i]);
    }
    break;
  case json_number:
  case json_boolean:
  case json_null:
  default:
    break;
  }
  json_value->type = json_null;
}
```

As simple as that, we ignore stack allocated json value variants, such as
`json_number`, `json_boolean` and `json_null`, while freeing allocated memory
space for `json_string`, each `json_array` child and `json_object` keys and
values.

### Printing json_values

Only a memory representation and no way to inspect it has no value to us, thus
I dumped `print_json_value` into `main.c`:

```c
void print_json_value(struct json_value *json_value) {
  switch (json_value->type) {
  case json_null:
    printf("null");
    break;
  case json_number:
    printf("%f", json_value->value.number);
    break;
  case json_string:
    printf("\"%s\"", json_value->value.string);
    break;
  case json_boolean:
    printf(json_value->value.boolean ? "true" : "false");
    break;
  case json_object:
    printf("{");
    for (size_t i = 0; i < json_value->length; i++) {
      printf("\"%s\": ", json_value->object_keys[i]);
      print_json_value(&json_value->values[i]);
      if (i < json_value->length - 1) {
        printf(", ");
      }
    }
    printf("}");
    break;
  case json_array:
    printf("[");
    for (size_t i = 0; i < json_value->length; i++) {
      print_json_value(&json_value->values[i]);
      if (i < json_value->length - 1) {
        printf(", ");
      }
    }
    printf("]");
    break;
  default:
    ASSERT(0, "Unimplemented json_value case");
    break;
  }
}

```

Calling this function:

```c
int main(void) {
  struct json_value json_value = {
      .type = json_array,
      .length = 4,
      .values =
          (struct json_value[]){
              (struct json_value){.type = json_string, .value.string = "hi"},
              (struct json_value){.type = json_number, .value.number = 161},
              (struct json_value){
                  .type = json_object,
                  .length = 1,
                  .object_keys =
                      (char *[]){
                          "key",
                      },
                  .values =
                      (struct json_value[]){
                          (struct json_value){.type = json_string,
                                              .value.string = "value"},
                      },
              },
              (struct json_value){.type = json_null},
          },
  };
  print_json_value(&json_value);
  puts("");
  return EXIT_SUCCESS;
}
```

Results in:

```text
["hi", 161.000000, {"key": "value"}, null]
```

### `json` Parser struct, Function pointers and how to use them (they suck)

As contrary as it sounds, one can attach functions to structures in c very
easily, just define a field of a struct as a function pointer, assign a
function to it and you got a method, as you would in Go or Rust.

```c
struct json {
  char *input;
  size_t pos;
  char (*cur)(struct json *json);
  bool (*is_eof)(struct json *json);
  void (*advance)(struct json *json);
  struct json_value (*atom)(struct json *json);
  struct json_value (*array)(struct json *json);
  struct json_value (*object)(struct json *json);
  struct json_value (*parse)(struct json *json);
};
```

Of course you have to define a function the c way (`<return type> <name>(<list
of params>);`) and assign it to your method field - but I is not that
complicated:

```c
struct json json_new(char *input) {
  ASSERT(input != NULL, "corrupted input");
  struct json j = (struct json){
      .input = input,
  };

  j.cur = cur;
  j.is_eof = is_eof;
  j.advance = advance;
  j.parse = parse;
  j.object = object;
  j.array = array;
  j.atom = atom;

  return j;
}
```

`cur`, `is_eof` and `advance` are small helper functions:

```c
static char cur(struct json *json) {
  ASSERT(json != NULL, "corrupted internal state");
  char cc = json->input[json->pos];
  return cc ? cc : -1;
}

static bool is_eof(struct json *json) {
  ASSERT(json != NULL, "corrupted internal state");
  return json->input[json->pos] == 0;
}

static void advance(struct json *json) {
  ASSERT(json != NULL, "corrupted internal state");
  if (!json->is_eof(json)) {
    json->pos++;
  }
}
```

`ASSERT` is a simple assertion macro:

```c
#define ASSERT(EXP, context)                                                   \
  if (!(EXP)) {                                                                \
    fprintf(stderr,                                                            \
            "jsoninc: ASSERT(" #EXP "): `" context                             \
            "` failed at %s, line %d\n",                                       \
            __FILE__, __LINE__);                                               \
    exit(EXIT_FAILURE);                                                        \
  }
```

Failing for instance if the argument to the `json_new` function is a null pointer:

```c
int main(void) {
  struct json json = json_new(NULL);
  return EXIT_SUCCESS;
}
```

Even with a descriptive comment:

```text
jsoninc: ASSERT(input != NULL): `corrupted input` failed at ./json.c, line 16
```

## Parsing JSON with methods

### Ignoring Whitespace

### Parsing Arrays

### Parsing Objects

### Parsing Atoms

#### numbers

#### null

#### true

#### false

#### strings

## Accessing values
