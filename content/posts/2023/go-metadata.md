---
title: "Removing metadata from Go binaries"
date: 2023-06-25
draft: true
tags:
  - go
---

The go compiler includes a lot of information about the system the binary was
compiled on in the resulting executable.
In some cases this is not desirable, therefore I will introduce several
types of information embedded by the compiler and how to remove or replace them.

# Example project

To visualize the following chapters I created a simple go project via the `go
init` command with a singular module named `logger`:

```text
teo@MacBookPro:~/programming/test$ exa --tree
.
├── go.mod
├── logger
│  └── logger.go
└── main.go
```

The `main.go` file contains the following call to the exported `Print()` function
of the `logger` module:

```go
package main

import "metadata_example/logger"

func main() {
	logger.Print("Hello World")
}
```

The `logger` module contains as previously mentioned the `Print()` function:

```go
package logger

import "fmt"

func Print(s string) {
	fmt.Printf("Printing: %s", s)
}
```

Compiling the given source files via `go build` creates a binary called
`metadata_example` which can now be examined with the gnu coreutils: `strings`,
`file` and the go tool `objdump`.

Simply running `strings` on the `metadata_example` binary and filtering the
output via `ripgrep`[^ripgrep] allows us to view paths to included modules and
the name of the compiling user:

```text
$ strings metadata_example | rg "teo"
/home/teo/programming/test/main.go
/home/teo/programming/test/logger/logger.go
```

And the function we defined in the `logger` module:

```text
$ strings metadata_example | rg "logger"
metadata_example/logger.Print
/home/teo/programming/test/logger/logger.go
metadata_example/logger..inittask
```

[^ripgrep]: https://github.com/BurntSushi/ripgrep

# Removing Metadata

## Removing Debug information

Technically the go tool chain includes the following information via the linker
not the compiler. [^go_linker_docs]

[^go_linker_docs]: https://pkg.go.dev/cmd/link

### omitting DWARF symbol table

[^dwarf_wikipedia]: https://en.wikipedia.org/wiki/DWARF

### omitting symbol table and debug information

The go symbol table and the debug information embed in the binary enable and
enhance the usage of the `gosym`-package [^gosym] and the `objdump` go tool
[^go_objdump].

[^gosym]: https://go.dev/src/debug/gosym/symtab.go
[^go_objdump]: https://pkg.go.dev/cmd/objdump

## Trimming module paths

## Replacing the buildId

## Compile command example

## Further options
