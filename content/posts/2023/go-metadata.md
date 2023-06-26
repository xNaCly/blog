---
title: "Removing metadata from Go binaries"
date: 2023-06-26
summary: Stripping metadata and debug information
tags:
  - go
---

The go compiler includes a lot of information about the system the binary was
compiled on in the resulting executable.
In some cases, this is not desirable; therefore, I will introduce several
types of information embedded by the compiler and how to remove or replace them.

To visualize the following chapters, I created a simple go project via the `go
mod init metadata_example` command with a singular module named `logger`:

```text
$ exa --tree
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

We can see the unique `buildid` the go compiler generated[^buildid_generation] for this build using `file`:

```text
$ file metadata_example
metadata_example: ELF 64-bit LSB executable, x86-64, version 1 (SYSV),
statically linked, Go
BuildID=EeK2FDOWyG6IGg5mazlg/ENHyunFNhP8fxN7Y3QPV/12qIzndxNxBtjs7mhfY7/RRZcvOGD57KThfaaOCUV,
with debug_info, not stripped
```

The binary contains debug information and can therefore be objdumped fairly easy:

```text
$ go tool objdump metadata_example | tail -n 26
TEXT main.main(SB) /home/teo/programming/test/main.go
  main.go:5             0x482820                493b6610                CMPQ 0x10(R14), SP
  ....
```

[^ripgrep]: https://github.com/BurntSushi/ripgrep
[^buildid_generation]: https://go.dev/src/cmd/go/internal/work/buildid.go

# Removing Metadata

The following three types of information are fairly easy to remove: Each one
will have an explanation and a removal example.

## Removing Debug information

Technically the go tool chain includes the following information via the linker
not the compiler. [^go_linker_docs]

[^go_linker_docs]: https://pkg.go.dev/cmd/link

### omitting DWARF symbol table

The DWARF symbol table [^dwarf_wikipedia] is used for debugging. It can be
stripped by passing the `-w` flag to the go linker.

```bash
go build -ldflags="-w"
```

[^dwarf_wikipedia]: https://en.wikipedia.org/wiki/DWARF

### omitting symbol table and debug information

The go symbol table and the debug information embedded in the binary enable and
enhance the usage of the `gosym`-package [^gosym] and the `objdump` go tool
[^go_objdump]. Omitting both the symbol table and debug information can be achieved
by invoking the go linker with the `-s` flag.

```bash
go build -ldflags="-s"
```

Running the go `objdump` tool on the resulting binary returns an error:

```text
$ go tool objdump metadata_example
objdump: disassemble metadata_example: no symbol section
```

[^gosym]: https://go.dev/src/debug/gosym/symtab.go
[^go_objdump]: https://pkg.go.dev/cmd/objdump

## Trimming module paths

As showcased before, the compiled binary contains all the files included in the
resulting binary. The go compiler exposes the `-trimpath` to strip common
prefixes from these files, which almost always contain compromising information
such as the name of the compiling user.

The compiler does the above when invoked with the flag, as follows:

```bash
go build -trimpath
```

Using the flag when compiling results in the binary not including the absolute
paths but project root relative paths:

```text
$ go build
$ go tool objdump metadata_example | rg "main.main"
TEXT main.main(SB) /home/teo/programming/test/main.go
  main.go:5             0x482898                eb86                    JMP main.main(SB)
$ go build -trimpath
$ go tool objdump metadata_example | rg "main.main"
TEXT main.main(SB) metadata_example/main.go
  main.go:5             0x482898                eb86                    JMP main.main(SB)
```

Comparing the `strings` output from the start of this post, the binary now
no longer contains the given example:

```text
$ strings metadata_example | rg "teo"
$ strings metadata_example | rg "logger"
metadata_example/logger.Print
metadata_example/logger/logger.go
```

## Replacing the buildid

The `buildid` can not be removed but it can be replaced with the `-buildid`
linker flag:

```bash
go build -ldflags="-buildid="
```

Which results in the following `file` output:

```text
$ go build -ldflags="-buildid="
$ file metadata_example
metadata_example: ELF 64-bit LSB executable, x86-64, version 1 (SYSV),
statically linked, with debug_info, not stripped
```

## Compile command example

Putting all of the above together, we arrive at the following build command:

```bash
go build -ldflags="-w -s -buildid=" -trimpath
```

This build does not include the DWARF symbol table, the go symbol table, debug
information, the unique `buildid` or compromising file paths.

Difference in file size[^binary_size]:

```text
  33 go.mod
   - logger
  93 main.go
1.2M metadata_example
1.9M metadata_example_full
```

The `metadata_example_full` was build with `go build` and the
`metadata_example` was build with all flags included in this post.

[^binary_size]: 37% size reduction

## Further options

### Stripping binaries

Its always possible to strip binaries using the gnu coreutils `strip` tool,
this is however strongly advised against when stripping go binaries due to
random panics.[^stripping_binaries]

[^stripping_binaries]: https://github.com/moby/moby/blob/2a95488f7843a773de2b541a47d9b971a635bfff/project/PACKAGERS.md#stripping-binaries

### Obfuscation

There are several go modules out there for replacing strings with computations
that evaluate to strings at runtime or replacing paths to modules with hashes.
[^garble] [^mumbojumbo]

These can be useful for creating more obscure binaries, which are hard to
reverse engineer.

[^garble]: https://github.com/burrowers/garble
[^mumbojumbo]: https://github.com/jeromer/mumbojumbo
