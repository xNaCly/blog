---
title: "Rethinking How I Deal With CLI Arguments (replacing getopt)"
summary: "Shortcomings of getopt, parsing CLI arguments into flags, no POSIX and a lot of implementation details"
date: 2025-05-10
tags:
    - C
draft: true
---

This article covers the issues I found myself having while using `getopt.h` for
a programming language bytecode interpreter pipeline I am currently working on
([`purple-garden`](https://github.com/xNaCly/purple-garden)[^pg]),
implementation details for the replacement I wrote, examples of how to use the
new solution and how I replaced the previous implementation with the new one
using `6cl`[^6cl].

[^pg]: purple-garden is a WIP of a lisp like high performance scripting language


{{<callout type="Tip or: TL;DR">}}

#### `getopt.h` kinda sucks to use, because:

- You have to write the help page and the usage page yourself
- You have to keep track of all flags and their handling at least twice (once
  in your flag definitions, once for short option names and once in their
  handling)
- Flags aren't typed, so all option arguments are just C strings accessible via
  global state `optarg`
- Default values aren't really a thing
- Option prefix is hardcoded to `-` for short options and `--` for long options
  (thanks for that [UNIX and POSIX](https://www.man7.org/linux/man-pages/man3/getopt.3.html))

#### I solved these issues by:

- Generating help and usage pages from the list of options
- Single flag list, no short and long definition in multiple places
- Typing flag options with seven types, range validation (`float.h`,
  `limits.h`) and default values:
  - string
  - boolean
  - character
  - integer and long
  - float and double
- Defaults and types are just fields of the flag struct in the flag definition
- Macro for setting the prefix and single prefix for all options 

{{</callout>}}

I wrote [`6cl`](https://github.com/xNaCly/6cl) to fill the gaps I encountered.
6cl is an opiniated command line option parsing library for 6wm[^6wm] and
purple garden

[^6cl]: named after the 6 looking like the G of garden. Combined with cl, which
is short for command line

[^6wm]: a planned fork of dwm to replace the `config.h` driven configuration
    with a purple garden script

## Current state

The purple-garden (pg), interpreter accepts a number of options:

```text
$ ./purple_garden -h
usage: purple_garden [-v | --version] [-h | --help]
                     [-d | --disassemble] [-b<size> | --block-allocator=<size>]
                     [-a | --aot-functions] [-m | --memory-usage]
                     [-V | --verbose] [-r<input> | --run=<input>] <file.garden>

Options:
        -v, --version
                display version information

        -h, --help
                extended usage information

        -d, --disassemble
                readable bytecode representation with labels,
                globals and comments

        -b=<size>, --block-allocator=<size>
                use block allocator instead of garbage collection

        -a, --aot-functions
                compile all functions to machine code

        -m, --memory-usage
                display the memory usage of parsing,
                compilation and the virtual machine

        -V, --verbose
                verbose logging

        -r=<input>, --run=<input>
                executes the argument as if an input file was given
```

### Command line argument parsing using getopt

I handle these by first defining a struct to hold all options, for later reference:

```c
typedef struct {
  // options - int because getopt has no bool support

  // use block allocator instead of garbage collection
  size_t block_allocator;
  // compile all functions to machine code
  int aot_functions;
  // readable bytecode representation with labels, globals and comments
  int disassemble;
  // display the memory usage of parsing, compilation and the virtual machine
  int memory_usage;

  // executes the argument as if an input file was given
  char *run;

  // verbose logging
  int verbose;

  // options in which we exit after toggle
  int version;
  int help;

  // entry point - last argument thats not an option
  char *filename;
} Args;
```

After that I define the list of options so I can keep track of them once getopt
does its stuff:

```c
typedef struct {
  const char *name_long;
  const char name_short;
  const char *description;
  const char *arg_name;
} cli_option;

// WARN: DO NOT REORDER THIS - will result in option handling issues
static const cli_option options[] = {
    {"version", 'v', "display version information", ""},
    {"help", 'h', "extended usage information", ""},
    {"disassemble", 'd', "readable bytecode representation with labels, globals and comments", ""},
    {"block-allocator", 'b', "use block allocator instead of garbage collection", "<size>"},
    {"aot-functions", 'a', "compile all functions to machine code", ""},
    {"memory-usage", 'm', "display the memory usage of parsing, compilation and the virtual machine", ""},
    {"verbose", 'V', "verbose logging", ""},
    {"run", 'r', "executes the argument as if an input file was given", "<input>"},
};
```

The heavy lifting is of course done in the `Args_parse` function:

```c
Args Args_parse(int argc, char **argv) {
    // [...] 1.-6.
}
```

1. Convert the array of `cli_option`'s to `getopt`'s `option`

    ```c
        Args a = (Args){0};
        // MUST be in sync with options, otherwise this will not work as intended
        struct option long_options[] = {
          {options[0].name_long, no_argument, &a.version, 1},
          {options[1].name_long, no_argument, &a.help, 1},
          {options[2].name_long, no_argument, &a.disassemble, 1},
          {options[3].name_long, required_argument, 0, 'b'},
          {options[4].name_long, no_argument, &a.aot_functions, 1},
          {options[5].name_long, no_argument, &a.memory_usage, 1},
          {options[6].name_long, no_argument, &a.verbose, 1},
          {options[7].name_long, required_argument, 0, 'r'},
          {0, 0, 0, 0},
        };
    ```

2. Pass the array to `getopt_long` with the matching short flag definition `vhdb:amVr:` (third location to define flags)

    ```c
        int opt;
        while ((opt = getopt_long(argc, argv, "vhdb:amVr:", long_options, NULL)) !=
             -1) {
            //  [...]
        }
    ```

3. Handle short options separately from long option "automatic" handling (touching every flag twice)

    ```c
            switch (opt) {
            case 'v':
              a.version = 1;
              break;
            case 'V':
              a.verbose = 1;
              break;
            case 'h':
              a.help = 1;
              break;
            case 'd':
              a.disassemble = 1;
              break;
            case 'r':
              a.run = optarg;
              break;
            case 'b':
              char *endptr;
              size_t block_size = strtol(optarg, &endptr, 10);
              ASSERT(endptr != optarg, "args: Failed to parse number from: %s", optarg);
              a.block_allocator = block_size;
              break;
            case 'a':
              a.aot_functions = 1;
              break;
            case 'm':
              a.memory_usage = 1;
              break;
            case 0:
              break;
            default:
              usage();
              exit(EXIT_FAILURE);
            }
    ```

4. Store all non flags as rest, representing the entry file (`filename`)

    ```c
        if (optind < argc) {
            a.filename = argv[optind];
        }
    ```

5. Act on commands, like `--version`, `--help` and their short variants

    ```c
        if (a.version) {
            // [...]
        } else if (a.help) {
            usage();
            // [...]
        }
    ```

6. Error if no input to the interpreter is detected

    ```c
      if (a.filename == NULL && a.run == NULL) {
        usage();
        fprintf(stderr, "error: Missing a file? try `-h/--help`\n");
        exit(EXIT_FAILURE);
      };
    ```

## 6cl Design, API and Examplary Usage

The API design is a inspired by go's [flag](https://pkg.go.dev/flag) package,
google's [gflag](https://gflags.github.io/gflags/), my general experience with
programming languages (Go, Rust, C, etc.) and my attempt to create an ergonomic
interface around the constraints of the C programming language.

By ergnomic I mean:

- single location for defining flags (no setting and handling them multiple times)
- merged short and long options (no `-s`, `--save`, but `-s` and `-save`)
- no combined options (no `-xvf` or `-lah`, but `-x -v -f` and `-l -a -h`)
- type safe and early errors if types can't be to parsed or over-/underflows occur
- type safe default values if flags aren't specified

### Defining Flags

### Accessing Flags

### Fusing into an Example

## Internals and Implementation Details

From here on out, I'll show how I implemented the command line parser and the
API surface.

### Generating Documentation

If the user passes a malformed input to a well written application, it should
provide a good error message, a usage overview and a note on how to get in
depth help. Since we have options with short names, long names, types, default
values and a description - I want to display all of the aforementioned in the
help and a subset in the usage page.

#### Usage

The usage page is displayed if the application is invoked with either `+h` or
`+help` or the 6cl parser hits an error (for the former two just as a prefix to
the help page):

```text
$ ./examples/dice.out +k
Unkown short option 'k'
usage ./examples/dice.out: [ +n / +rolls <int=2>] [ +m / +sides <int=6>]
                           [ +l / +label <string=`=> `>] [ +v / +verbose]
                           [ +h / +help]
```

After every two options there is a newline inserted to make the output more readable.

#### Examples

To generate two examples (one with long names and one with short names), the default values are used:

```text
Examples:
        ./examples/dice.out +n 2 +m 6 \
                            +l "=> " +v

        ./examples/dice.out +rolls 2 +sides 6 \
                            +label "=> " +verbose
```

As with the usage, after every two options there is a newline inserted.

#### Help page

The help page merges the usage, the extended option display (with description)
and the example sections:

```text
$ ./examples/dice.out +help
usage ./examples/dice.out: [ +n / +rolls <int=2>] [ +m / +sides <int=6>]
                           [ +l / +label <string=`=> `>] [ +v / +verbose]
                           [ +h / +help]

Option:
          +n / +rolls <int=2>
                times to roll

          +m / +sides <int=6>
                sides the dice has

          +l / +label <string=`=> `>
                prefix for the dice roll result

          +v / +verbose
                print all rolls, not only the result

          +h / +help
                help page and usage

Examples:
        ./examples/dice.out +n 2 +m 6 \
                            +l "=> " +v

        ./examples/dice.out +rolls 2 +sides 6 \
                            +label "=> " +verbose
```

### Detecting Short Flags
### Detecting Long Flags
### Parsing, Validating and Setting Flag Values
## Migrating Purple Garden from getopt to 6cl
