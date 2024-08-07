---
title: "Calling Go Functions from c++"
summary: "Interacting with the Go runtime with c++ (or c, i think)"
date: 2024-07-20
tags:
  - go
  - c++
---

As programmers we sometimes need to do weird stuff or make two systems work
together that really should not interoperate. As is the case with c++ and go in
the way of calling functions written in go from c++. But I didnt ask if i
should, i just asked if i could and the result is documented in the form of
this blog post and the repo
[here](https://github.com/respondchat/c-go-interop/).

## Project setup

The flow of our project will be to compile the go file to an archive with the
go toolchain. We will then use the gnu c++ compiler to link our c++ code
calling functions from the go library with the compiled archive.

Compiling a go file to an archive:

```shell
go build -buildmode=c-archive -o lib.a lib.go
```

Compiling a c++ file and linking it against the afore compiled archive:

```shell
g++ -Wall main.cpp lib.a -o main
```

To make our iteration loop faster we will use `make` and insert the invocation
of the resulting binary to our `example` target:

```make
example:
	go build -buildmode=c-archive -o lib.a lib.go
	g++ -Wall main.cpp lib.a -o main
	./main
```

## Simple example

{{<callout type="Tip">}}

If you are interested in the code without any explanations, take a look
[here](https://github.com/respondchat/c-go-interop/). For documentation around
the way one can interact with the go runtime from c or c++, check out [Go Wiki:
cgo](https://go.dev/wiki/cgo) and [cgo command](https://pkg.go.dev/cmd/cgo).
{{</callout>}}

We will start with some easy stuff and wrap the go standard library methods for
the square root and the n-th power, export them and call them from c++.

The first step is to create both `lib.go` and `main.cpp` and fill them with the
following boilerplate:

```go
// lib.go
package main

import "C"
import ()

func main() {}
```

```c++
// main.cpp
#include "lib.h"
int main() {}
```

We can now check if our project setup works:

```text
$ make
go build -buildmode=c-archive -o lib.a lib.go
g++ -Wall main.cpp lib.a -o main
./main
```

Lets now wrap both `math.Sqrt` and `math.Pow` in go functions, export them and
invoke them from c++ to get a feel for the interaction logic. Starting of with
the definition in `lib.go`:

```go{hl_lines=[5, "8-11", "13-16"]}
package main

import "C"
import (
	"math"
)

//export Sqrt
func Sqrt(n float64) float64 {
	return math.Sqrt(n)
}

//export Pow
func Pow(x float64, y float64) float64 {
	return math.Pow(x, y)
}

func main() {}
```

All exported functions need to start with an uppercase letter (as defined in
the [go spec](https://go.dev/ref/spec#Exported_identifiers)) and require a
comment above them with the name of the function it should be invoked by from
the c++ context.

We can now modify our c++ and create a small function to call the functions we
defined above:

```c++{hl_lines=[2, "4-9", 12]}
#include "lib.h"
#include <iostream>

void maths() {
  GoFloat64 sqrt = Sqrt(25.0);
  std::cout << "sqrt(25.0)=" << sqrt << std::endl;
  GoFloat64 pow = Pow(5, 3);
  std::cout << "power(5, 3)=" << pow << std::endl;
}

int main() {
  maths();
}
```

{{<callout type="Go types in c">}}

We use `GoFloat64` to interact with the result of the invoked go function.
`GoFloat64` is defined as:

```c++
typedef double GoFloat64;
```

Other types are:

```c++
// ...
typedef signed char GoInt8;
typedef unsigned char GoUint8;
typedef short GoInt16;
typedef unsigned short GoUint16;
typedef int GoInt32;
typedef unsigned int GoUint32;
typedef long long GoInt64;
typedef unsigned long long GoUint64;
typedef GoInt64 GoInt;
typedef GoUint64 GoUint;
typedef size_t GoUintptr;
typedef float GoFloat32;
// ...
```

These definitions are generated by the go toolchain for the archive build in
the `lib.h` file, upon first compiling the archive. After 70 lines of
boilerplate we can see the output generated for our `lib.go` file:

```c++
#ifdef __cplusplus
extern "C" {
#endif

extern GoFloat64 Sqrt(GoFloat64 n);
extern GoFloat64 Pow(GoFloat64 x, GoFloat64 y);

#ifdef __cplusplus
}
#endif
```

{{</callout>}}

Running our example via `make`:

```text{hl_lines=[5,6]}
$ make
go build -buildmode=c-archive -o lib.a lib.go
g++ -Wall main.cpp lib.a -o main
./main
sqrt(25.0)=5
power(5, 3)=125
```

## Web requests and passing strings to go

Lets take a look at the possibility of making a get request to an URL. For that
we implement the `Request` method in `lib.go`:

```go{hl_lines=[6,7]}
package main

import "C"
import (
	"math"
	"net/http"
	"time"
)

// ...

//export Request
func Request(str string) int {
	client := http.Client{
		Timeout: time.Millisecond * 200,
	}
	resp, _ := client.Get(str)
	return resp.StatusCode
}

// ...
```

However the conventional string used in the go runtime differs from the string
used in c++. To help us with this, the toolchain generated a type definition in `lib.h`:

```c++
#ifndef GO_CGO_GOSTRING_TYPEDEF
typedef struct { const char *p; ptrdiff_t n; } _GoString_;
#endif
// ...
#ifndef GO_CGO_GOSTRING_TYPEDEF
typedef _GoString_ GoString;
#endif
```

We can create an instance of this structure and pass it to our `Request` function:

```c++
#include "lib.h"
#include <cstring>

// ...

void request(const char *s) {
  GoString str;
  str.p = s;
  str.n = strlen(str.p);
  int r = Request(str);
  std::cout << "http.Get(" << str.p << ")=" << r << std::endl;
}

int main() {
  // ...
  request("https://xnacly.me/5");
  request("https://xnacly.me/about");
}
```

`GoString.n` is the length of the string and `GoString.p` refers to the pointer
to the string. Lets test the request to an invalid page and the request to a valid page:

```text{hl_lines=[5,6]}
$ make
go build -buildmode=c-archive -o lib.a lib.go
g++ -Wall main.cpp lib.a -o main
./main
http.Get(https://xnacly.me/5)=404
http.Get(https://xnacly.me/about)=200
```

## Go routines

Probably the most unique feature of go in comparison to other largely used
programming languages is its concurrency model. Therefore lets add the ability
to spawn go routines to c++.

```go{hl_lines=[8]}
package main

import "C"
import (
	"fmt"
	"math"
	"net/http"
	"sync"
	"time"
)

// ...

//export Routines
func Routines(n int) {
	wg := sync.WaitGroup{}
	for i := range n {
		wg.Add(1)
		fmt.Printf("Spawning go routine %d\n", i)
		go func() {
			defer wg.Done()
			time.Sleep(time.Millisecond * 10)
		}()
	}
	wg.Wait()
}

// ...
```

Lets just add the `Routines` call to the c++ `main` function and invoke 1024 go routines:

```c++
// ...
int main() {
  // ...
  Routines(1024);
}
```

After building and executing the binary we get:

```text
$ make
go build -buildmode=c-archive -o lib.a lib.go
g++ -Wall main.cpp lib.a -o main
./main
Spawning go routine 0
...
Spawning go routine 1023
```

Very many go routines `:^)`.

There you have it, a nice and short explanation for calling go functions from
c++ (if you need to). The same should work for c, but I didnt bother to test
this one.
