---
title: "Embedding the Sophia runtime into Go applications"
summary: "Guide for embedding the sophia runtime, Go interoperability and error handling"
date: 2024-01-09
tags:
  - go
  - sophia
---

{{<callout type="Tip">}}
Suppose you want to create a webserver and make it scriptable via a minimal,
fast and go interoperability supporting language -
[Sophia](https://github.com/xNaCly/Sophia) is here for you and makes it as easy
as possible.
{{</callout>}}

## Installing the runtime

Install sophia as a project dependency:

```shell
$ go get github.com/xnacly/sophia
```

## Initial embedding

The skeleton imports the embed package - this package provides abstractions over
configuring, instantiating and starting the sophia runtime.

```go
package main

import (
	"os"

	"github.com/xnacly/sophia/embed"
)

func main() {
	embed.Embed(embed.Configuration{})
	file, err := os.Open("config.phia")
	if err != nil {
		panic(err)
	}
	embed.Execute(file, nil)
}
```

{{<callout type="Tip">}}
The `embed.Configuration` structure allows for a more in depth configuration,
such as enabling the linkage of the go standard library into the sophia
language via `embed.Configuration.EnableGoStd` or toggling the debug mode via
`embed.Configuration.Debug`.

On the other hand the `embed.Execute` function takes `*os.File` and
`io.Writer`, is the writer nil the runtime prints error message to `os.Stdout`,
otherwise the writer is used. The `embed.Execute` function also returns an
error if the execution was faulty.
{{</callout>}}

## Configuration script

Lets add a structure we want to configure with a sophia script:

```go
package main

import (
	"fmt"
	"os"

	"github.com/xnacly/sophia/embed"
)

type Configuration struct {
	Port int
}

var config = &Configuration{}

func main() {
	embed.Embed(embed.Configuration{})
	file, err := os.Open("config.phia")
	if err != nil {
		panic(err)
	}
	embed.Execute(file, nil)
}
```

And write the corresponding sophia script, named `config.phia`:

```lisp
(let port 8080)
(set-port port)
```

## Interfacing with go

Sophia supports interoperability with go by allowing the declaration and
injection of functions written in go into its runtime, this can be done by
adding a function of type `type.KnownFunctionInterface` to the
`embed.Configuration.Functions` map:

```go
package main

import (
	"fmt"
	"os"

	"github.com/xnacly/sophia/core/token"
	"github.com/xnacly/sophia/core/types"
	"github.com/xnacly/sophia/embed"
)

type Configuration struct {
	Port int
}

var config = &Configuration{}

func main() {
	embed.Embed(embed.Configuration{
		Functions: map[string]types.KnownFunctionInterface{
			"set-port": func(t *token.Token, n ...types.Node) any {
				return nil
			},
		},
	})
	file, err := os.Open("config.phia")
	if err != nil {
		panic(err)
	}
	embed.Execute(file, nil)
}
```

## Input validation

We only want exactly one parameter, thus we check for the length and use the
`serror` package (short for sophia error) for creating an error with the given
token (the first element after our desired argument length).

```go
package main

import (
	"fmt"
	"os"

	"github.com/xnacly/sophia/core/serror"
	"github.com/xnacly/sophia/core/token"
	"github.com/xnacly/sophia/core/types"
	"github.com/xnacly/sophia/embed"
)

type Configuration struct {
	Port int
}

var config = &Configuration{}

func main() {
	embed.Embed(embed.Configuration{
		Functions: map[string]types.KnownFunctionInterface{
			"set-port": func(t *token.Token, n ...types.Node) any {
				if len(n) > 1 {
					serror.Add(n[1].GetToken(), "Too many arguments", "Expected 1 argument for set-port, got %d", len(n))
					serror.Panic()
				}
				return nil
			},
		},
	})
	file, err := os.Open("config.phia")
	if err != nil {
		panic(err)
	}
	embed.Execute(file, nil)
	fmt.Println("port:", config.Port)
}
```

If we pass two ports to our `set-port` function we will get the following error message:

```shell
$ cat config.phia
(let port 8080)
(set-port port port)
$ go run .
error: Too many arguments

        at: /home/teo/programming/embedding_sophia/config.phia:3:16:

            1| ;; vim: syntax=lisp
            2| (let port 8080)
            3| (set-port port port)
             |                ^^^^

Expected 1 argument for set-port, got 2
```

## Type validation

Lets evaluate the result of the argument passed to our function, cast it to a float64 and assign it to `config.Port`:

```go
package main

import (
	"fmt"
	"os"

	"github.com/xnacly/sophia/core/serror"
	"github.com/xnacly/sophia/core/token"
	"github.com/xnacly/sophia/core/types"
	"github.com/xnacly/sophia/embed"
)

type Configuration struct {
	Port int
}

var config = &Configuration{}

func main() {
	embed.Embed(embed.Configuration{
		Functions: map[string]types.KnownFunctionInterface{
			"set-port": func(t *token.Token, n ...types.Node) any {
				if len(n) > 1 {
					serror.Add(n[1].GetToken(), "Too many arguments", "Expected 1 argument for set-port, got %d", len(n))
					serror.Panic()
				}
				res := n[0].Eval()
				port, ok := res.(float64)
				if !ok {
					serror.Add(n[0].GetToken(), "Type error", "Expected float64 for port, got %T", res)
					serror.Panic()
				}

				config.Port = int(port)

				return nil
			},
		},
	})
	file, err := os.Open("config.phia")
	if err != nil {
		panic(err)
	}
	embed.Execute(file, nil)
	fmt.Println("port:", config.Port)
}
```

Again, lets check the error handling:

```shell
$ cat config.phia
(let port "8080")
(set-port port)
$ go run .
error: Type error

        at: /home/teo/programming/embedding_sophia/config.phia:3:11:

            1| ;; vim: syntax=lisp
            2| (let port "8080")
            3| (set-port port)
             |           ^^^^

Expected float64 for port, got string
```

## Resulting embedding of Sophia

Simply running our script with valid inputs according to our previous checks will result in the following output:

```shell
$ cat config.phia
(let port 8080)
(set-port port)
$ go run .
port: 8080
```

Thats it, a simple configuration structure and two method calls, can't really
get shorter than that - I am now going to migrate my package manager
[mehr](https://github.com/xNaCly/mehr) to be configured with sophia.
