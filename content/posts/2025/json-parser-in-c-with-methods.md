---
title: "Abusing C to implement JSON Parsing with Struct Methods"
summary: "Json parsing in C using function pointers attached to a struct"
date: 2025-02-26
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
    "array" : [[]],
    "atoms" : [ "string", 0.1, true, false, null ]
  }));
  struct json_value json_value = json.parse(&json);
  json_print_value(&json_value);
  puts("");
  json_free_value(&json_value);
  return EXIT_SUCCESS;
}
```

{{<callout type="Tip - Compiling C projects the easy way">}}

> Don't take this as a guide for using make, in my projects I just use it as a
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

> I don't define the `build` target as `.PHONY` because i generally never have
> a `build` directory.

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

This doesn't really deserve its own section, but I use `#<expression>` to
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

I need a structure to hold a parsed JSON value, their types and their values.

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
      free(json_value->object_keys[i]);
      json_free_value(&json_value->values[i]);
    }
    if (json_value->object_keys != NULL) {
      free(json_value->object_keys);
      json_value->object_keys = NULL;
    }
    if (json_value->values != NULL) {
      free(json_value->values);
      json_value->values = NULL;
    }
    break;
  case json_array:
    for (size_t i = 0; i < json_value->length; i++) {
      json_free_value(&json_value->values[i]);
    }
    if (json_value->values != NULL) {
      free(json_value->values);
      json_value->values = NULL;
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

As simple as that, we ignore stack allocated JSON value variants, such as
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
  json_print_value(&json_value);
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
  size_t length;
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
      .length = strlen(input) - 1,
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
  return json->is_eof(json) ? -1 : json->input[json->pos];
}

static bool is_eof(struct json *json) {
  ASSERT(json != NULL, "corrupted internal state");
  return json->pos > json->length;
}

static void advance(struct json *json) {
  ASSERT(json != NULL, "corrupted internal state");
  json->pos++;
  skip_whitespace(json);
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

Since we now have the whole setup out of the way, we can start with the crux of
the project: parsing JSON. Normally I would have done a lexer and parser, but
for the sake of simplicity - I combined these passes into a single parser
architecture.

{{<callout type="Warning">}}
Also please don't even think about standard compliance - I really cant be
bothered, see [Parsing JSON is a
Minefield 💣](https://seriot.ch/projects/parsing_json.html).
{{</callout>}}

### Ignoring Whitespace

As far as we are concerned, JSON does not say anything about whitespace - so we
just use the `skip_whitespace` function to ignore all and any whitespace:

```c
static void skip_whitespace(struct json *json) {
  while (!json->is_eof(json) &&
         (json->cur(json) == ' ' || json->cur(json) == '\t' ||
          json->cur(json) == '\n')) {
    json->pos++;
  }
}
```

### Parsing Atoms

Since JSON has five kinds of an atom, we need to parse them into our
`json_value` struct using the `json->atom` method:

```c
static struct json_value atom(struct json *json) {
    ASSERT(json != NULL, "corrupted internal state");

    skip_whitespace(json);

    char cc = json->cur(json);
    if ((cc >= '0' && cc <= '9') || cc == '.' || cc == '-') {
        return number(json);
    }

    switch (cc) {
        // ... all of the atoms ...
    default:
        printf("unknown character '%c' at pos %zu\n", json->cur(json), json->pos);
        ASSERT(false, "unknown character");
        return (struct json_value){.type = json_null};
    }
}
```

#### numbers

{{<callout type="Info">}}
Technically numbers in JSON should include scientific notation and other fun
stuff, but lets just remember the projects simplicity and my sanity, see
[json.org](www.json.org/).
{{</callout>}}

```c
static struct json_value number(struct json *json) {
  ASSERT(json != NULL, "corrupted internal state");
  size_t start = json->pos;
  // i don't give a fuck about scientific notation <3
  for (char cc = json->cur(json);
       ((cc >= '0' && cc <= '9') || cc == '_' || cc == '.' || cc == '-');
       json->advance(json), cc = json->cur(json))
    ;

  char *slice = malloc(sizeof(char) * json->pos - start + 1);
  ASSERT(slice != NULL, "failed to allocate slice for number parsing")
  memcpy(slice, json->input + start, json->pos - start);
  slice[json->pos - start] = 0;
  double number = strtod(slice, NULL);
  free(slice);

  return (struct json_value){.type = json_number, .value = {.number = number}};
}
```

We keep track of the start of the number, advance as far as the number is still
considered a number (any of `0-9 | _ | . | -`). Once we hit the end we allocate
a temporary string, copy the chars containing the number from the input string
and terminate the string with `\0`. `strtod` is used to convert this string to
a double. Once that is done we free the slice and return the result as a
`json_value`.

#### null, true and false

`null`, `true` and `false` are unique atoms and easy to reason about, regarding
constant size and characters, as such we can just assert their characters:

```c
static struct json_value atom(struct json *json) {
  ASSERT(json != NULL, "corrupted internal state");

  skip_whitespace(json);

  char cc = json->cur(json);
  if ((cc >= '0' && cc <= '9') || cc == '.' || cc == '-') {
    return number(json);
  }

  switch (cc) {
  case 'n': // null
    json->pos++;
    ASSERT(json->cur(json) == 'u', "unknown atom 'n', wanted 'null'")
    json->pos++;
    ASSERT(json->cur(json) == 'l', "unknown atom 'nu', wanted 'null'")
    json->pos++;
    ASSERT(json->cur(json) == 'l', "unknown atom 'nul', wanted 'null'")
    json->advance(json);
    return (struct json_value){.type = json_null};
  case 't': // true
    json->pos++;
    ASSERT(json->cur(json) == 'r', "unknown atom 't', wanted 'true'")
    json->pos++;
    ASSERT(json->cur(json) == 'u', "unknown atom 'tr', wanted 'true'")
    json->pos++;
    ASSERT(json->cur(json) == 'e', "unknown atom 'tru', wanted 'true'")
    json->advance(json);
    return (struct json_value){.type = json_boolean,
                               .value = {.boolean = true}};
  case 'f': // false
    json->pos++;
    ASSERT(json->cur(json) == 'a', "invalid atom 'f', wanted 'false'")
    json->pos++;
    ASSERT(json->cur(json) == 'l', "invalid atom 'fa', wanted 'false'")
    json->pos++;
    ASSERT(json->cur(json) == 's', "invalid atom 'fal', wanted 'false'")
    json->pos++;
    ASSERT(json->cur(json) == 'e', "invalid atom 'fals', wanted 'false'")
    json->advance(json);
    return (struct json_value){.type = json_boolean,
                               .value = {.boolean = false}};
  // ... strings ...
  default:
    printf("unknown character '%c' at pos %zu\n", json->cur(json), json->pos);
    ASSERT(false, "unknown character");
    return (struct json_value){.type = json_null};
  }
}
```

#### strings

{{<callout type="Info">}}
Again, similarly to JSON numbers, JSON strings should include escapes for
quotation marks and other fun stuff, but lets again just remember the projects
simplicity and my sanity, see [json.org](www.json.org/).
{{</callout>}}

```c
static char *string(struct json *json) {
  json->advance(json);
  size_t start = json->pos;
  for (char cc = json->cur(json); cc != '\n' && cc != '"';
       json->advance(json), cc = json->cur(json))
    ;

  char *slice = malloc(sizeof(char) * json->pos - start + 1);
  ASSERT(slice != NULL, "failed to allocate slice for a string")

  memcpy(slice, json->input + start, json->pos - start);
  slice[json->pos - start] = 0;

  ASSERT(json->cur(json) == '"', "unterminated string");
  json->advance(json);
  return slice;
}
```

Pretty easy stuff, as long as we are inside of the string (before `\"`,`\n` and
`EOF`) we advance, after that we copy it into a new slice and return that slice
(this function is especially useful for object keys - that's why it is a
function).

### Parsing Arrays

Since arrays a any amount of JSON values between `[]` and separated via `,` -
this one is not that hard to implement too:

```c
struct json_value array(struct json *json) {
  ASSERT(json != NULL, "corrupted internal state");
  ASSERT(json->cur(json) == '[', "invalid array start");
  json->advance(json);

  struct json_value json_value = {.type = json_array};
  json_value.values = malloc(sizeof(struct json_value));

  while (!json->is_eof(json) && json->cur(json) != ']') {
    if (json_value.length > 0) {
      if (json->cur(json) != ',') {
        json_free_value(&json_value);
      }
      ASSERT(json->cur(json) == ',',
             "expected , as the separator between array members");
      json->advance(json);
    }
    struct json_value member = json->parse(json);
    json_value.values = realloc(json_value.values,
                                sizeof(json_value) * (json_value.length + 1));
    json_value.values[json_value.length++] = member;
  }

  ASSERT(json->cur(json) == ']', "missing array end");
  json->advance(json);
  return json_value;
}
```

We start with a array length of one and reallocate for every new child we find.
We also check for the `,` between each child.

> A growing array would probably be better to minimize allocations, but here we
> are, writing unoptimized C code - still, it works :)

### Parsing Objects

```c
struct json_value object(struct json *json) {
  ASSERT(json != NULL, "corrupted internal state");
  ASSERT(json->cur(json) == '{', "invalid object start");
  json->advance(json);

  struct json_value json_value = {.type = json_object};
  json_value.object_keys = malloc(sizeof(char *));
  json_value.values = malloc(sizeof(struct json_value));

  while (!json->is_eof(json) && json->cur(json) != '}') {
    if (json_value.length > 0) {
      if (json->cur(json) != ',') {
        json_free_value(&json_value);
      }
      ASSERT(json->cur(json) == ',',
             "expected , as separator between object key value pairs");
      json->advance(json);
    }
    ASSERT(json->cur(json) == '"',
           "expected a string as the object key, did not get that")
    char *key = string(json);
    ASSERT(json->cur(json) == ':', "expected object key and value separator");
    json->advance(json);

    struct json_value member = json->parse(json);
    json_value.values = realloc(json_value.values, sizeof(struct json_value) *
                                                       (json_value.length + 1));
    json_value.values[json_value.length] = member;
    json_value.object_keys = realloc(json_value.object_keys,
                                     sizeof(char **) * (json_value.length + 1));
    json_value.object_keys[json_value.length] = key;
    json_value.length++;
  }

  ASSERT(json->cur(json) == '}', "missing object end");
  json->advance(json);
  return json_value;
}
```

Same as arrays, only instead of a single atom we have a string as the key, `:`
as a separator and a `json_value` as the value. Each pair is separated with
`,`.
