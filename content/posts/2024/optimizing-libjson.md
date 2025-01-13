---
title: "Optimizing libjson, or: beating encoding/json by at least 2.5x"
date: 2025-01-10
summary: "Benchmarking, analysing and improving JSON parsing performance"
tags:
  - go
---

Libjson is a JSON parsing/interaction library for which I attempted to go the
not so gopher way: disregarding interoperability and backwards compatibility:

1. libjson does not support writing json into structure fields via reflection
2. libjson does not support accessing json via a structure, because: see point 1.
3. libjson instead uses a Javascript like object access syntax

The three points above result in the following api:

```go
package main

import (
    "github.com/xnacly/libjson"
)

func main() {
	input := `{ "hello": {"world": ["hi"] } }`
	jsonObj, _ := New(input) // or libjson.NewReader(r io.Reader)

	// accessing values
	fmt.Println(Get[string](jsonObj, ".hello.world.0")) // hi
}
```

Libjson is fast, but I want to make it even faster, thus i established a
baseline of the current results via `./bench.sh | rg "faster` - it already is
about 2x faster than `encoding/json`.

```text
2.10 ± 0.11 times faster than ./test -libjson=false ./1MB.json
2.33 ± 0.07 times faster than ./test -libjson=false ./5MB.json
2.37 ± 0.03 times faster than ./test -libjson=false ./10MB.json
```

## Benchmark setup

I use:

- python to generate large json files for avoiding microbenchmarks
- hyperfine to compare the execution time of the program
- bash to put everything together

### Generating input

> View the source for the benchmarking code at [xnacly/libjson/test](https://github.com/xNaCly/libjson/tree/master/test)

I decided on the following json object, to simulate the real world
usage:

```json
[
  {
    "key1": "value",
    "array": [],
    "obj": {},
    "atomArray": [11201, 1e112, true, false, null, "str"]
  }
]
```

I then write a small python script to generate three different file sizes (1mb,
5mb and 10mb) with the amount of objects in them to arrive at around these
sizes:

```python
from os.path import exists
import math

sizes = [1,5,10]

line = """\t{
        "key1": "value",
        "array": [],
        "obj": {},
        "atomArray": [11201,1e112,true,false,null,"str"]
    }"""

def write_data(size: int):
    name = f"{size}MB.json"
    if not exists(name):
        with open(name, mode="w", encoding="utf8") as f:
            f.write("[\n")
            size = math.floor((size*1000000)/len(line))
            f.write(",\n".join([line for _ in range(0, size)]))
            f.write("\n]")

[write_data(size) for size in sizes]
```

### Creating a program

To call a program with hyperfine, we need to write one:

```go
package main

import (
	"encoding/json"
	"flag"
	"log"
	"os"

	"github.com/xnacly/libjson"
)

func main() {
	lj := flag.Bool("libjson", true, "benchmark libjson or gojson")
	flag.Parse()
	args := flag.Args()
	if len(args) == 0 {
		log.Fatalln("Wanted a file as first argument, got nothing, exiting")
	}
	file, err := os.Open(args[0])
	if err != nil {
		log.Fatalln(err)
	}
	if *lj {
		_, err := libjson.NewReader(file)
		if err != nil {
			log.Fatalln(err)
		}
	} else {
		v := []struct {
			Key1      string
			Array     []any
			Obj       any
			AtomArray []any
		}{}
		d := json.NewDecoder(file)
		err := d.Decode(&v)
		if err != nil {
			log.Fatalln(err)
		}
	}
}
```

This program takes a flag (`-libjson`) to control whether it should use
`libjson` or `encoding/json` as a backend.

### Calling hyperfine

Putting the above together, i came up with the following shell script:

```sh
#!/bin/bash
echo "generating example data"
python3 gen.py

echo "building executable"
rm ./test
go build ./test.go

hyperfine "./test ./1MB.json" "./test -libjson=false ./1MB.json"
hyperfine "./test ./5MB.json" "./test -libjson=false ./5MB.json"
hyperfine "./test ./10MB.json" "./test -libjson=false ./10MB.json"
```

### Preciser benchmarks

The benchmarking via a whole program serves as a good comparison between
different implementations and their total speeds, however it is very imprecise
regarding the allocations and time in the functions we are interested in. To
create a more precise and relevant benchmark, I will also include the results
of the following benchmarks which are using the `testing.B` tooling:

```go
package libjson

import (
	"encoding/json"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

const amount = 50_000

func BenchmarkLibJson(b *testing.B) {
	data := strings.Repeat(`{"key1": "value","array": [],"obj": {},"atomArray": [11201,1e112,true,false,null,"str"]},`, amount)
	d := []byte("[" + data[:len(data)-1] + "]")
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := New(d)
		assert.NoError(b, err)
	}
	b.ReportAllocs()
}

func BenchmarkEncodingJson(b *testing.B) {
	data := strings.Repeat(`{"key1": "value","array": [],"obj": {},"atomArray": [11201,1e112,true,false,null,"str"]},`, amount)
	d := []byte("[" + data[:len(data)-1] + "]")
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		v := []struct {
			Key1      string
			Array     []any
			Obj       any
			AtomArray []any
		}{}
		err := json.Unmarshal(d, &v)
		assert.NoError(b, err)
	}
	b.ReportAllocs()
}
```

Taking both benchmarks into account, the total baseline is as follows:

```text
$ cd test && ./bench.sh
generating example data
building executable
Benchmark 1: ./test ./1MB.json
  Time (mean ± σ):      12.4 ms ±   0.6 ms    [User: 16.0 ms, System: 4.8 ms]
  Range (min … max):    11.1 ms …  14.3 ms    217 runs

Benchmark 2: ./test -libjson=false ./1MB.json
  Time (mean ± σ):      24.9 ms ±   0.6 ms    [User: 25.2 ms, System: 3.5 ms]
  Range (min … max):    23.7 ms …  26.4 ms    117 runs

Summary
  ./test ./1MB.json ran
    2.01 ± 0.11 times faster than ./test -libjson=false ./1MB.json
Benchmark 1: ./test ./5MB.json
  Time (mean ± σ):      51.8 ms ±   1.5 ms    [User: 77.5 ms, System: 12.4 ms]
  Range (min … max):    49.4 ms …  54.8 ms    57 runs

Benchmark 2: ./test -libjson=false ./5MB.json
  Time (mean ± σ):     116.7 ms ±   1.2 ms    [User: 133.1 ms, System: 9.8 ms]
  Range (min … max):   114.1 ms … 119.6 ms    25 runs

Summary
  ./test ./5MB.json ran
    2.25 ± 0.07 times faster than ./test -libjson=false ./5MB.json
Benchmark 1: ./test ./10MB.json
  Time (mean ± σ):      97.9 ms ±   1.2 ms    [User: 142.4 ms, System: 22.7 ms]
  Range (min … max):    95.0 ms … 100.4 ms    29 runs

Benchmark 2: ./test -libjson=false ./10MB.json
  Time (mean ± σ):     228.8 ms ±   1.7 ms    [User: 257.9 ms, System: 17.7 ms]
  Range (min … max):   226.2 ms … 231.4 ms    13 runs

Summary
  ./test ./10MB.json ran
    2.34 ± 0.03 times faster than ./test -libjson=false ./10MB.json


$ go test ./... -bench=.
goos: linux
goarch: amd64
pkg: github.com/xnacly/libjson
cpu: AMD Ryzen 7 3700X 8-Core Processor
BenchmarkLibJson-16                   21          53156910 ns/op        34744407 B/op     500024 allocs/op
BenchmarkEncodingJson-16               8         134535103 ns/op        39723750 B/op     650033 allocs/op
PASS
ok      github.com/xnacly/libjson       2.404s
?       github.com/xnacly/libjson/cmd   [no test files]
?       github.com/xnacly/libjson/test  [no test files]
```

Or as tables:

| backend       | 1mb              | 5mb              | 10mb            |
| ------------- | ---------------- | ---------------- | --------------- |
| encoding/json | 24.9ms           | 116.7ms          | 225.9ms         |
| libjson       | 12.4ms (-12.5ms) | 51.8ms (-64.9ms) | 97.9ms (-128ms) |

| backend       | ns/op                   | B/op                    | allocs/op          |
| ------------- | ----------------------- | ----------------------- | ------------------ |
| encoding/json | 134_535_103             | 39_723_750              | 650_033            |
| libjson       | 53_156_910 (-8_137_819) | 34_744_407 (-4_979_343) | 500_024 (-150_009) |

## Previous improvements

Since I made most of these before thinking about this blog article, i will just
mention them and their relative impact (-ms for improvement, +ms for
regression) in a tuple of the input sizes:

| change                                                                                             | impact 1mb | impact 5mb | impact 10mb |
| -------------------------------------------------------------------------------------------------- | ---------- | ---------- | ----------- |
| disabled unique key checking for objects, duplicates just overwrite the previous value             | not tested | not tested | not tested  |
| lex on demand, instead of before starting the parser                                               | -4ms       | -14ms      | not tested  |
| use `*(*string)(unsafe.Pointer(&l.buf))` instead of `string()` to skip an allocation               | -0.4ms     | -2ms       | -4ms        |
| move allocations and string/number parsing to the parser                                           | -1ms       | -2ms       | -4ms        |
| fast paths for `true`, `false` and `null` & byte slices instead of strings for string/number token | -6ms       | -25ms      | -60ms       |
| =                                                                                                  | -11.4ms    | -43ms      | -68ms       |

## Replacing byte slices with offsets and lengths

Currently a `token`-structure is defined as:

```go
type token struct {
	Type t_json
    Val  []byte
}
```

While `t_json` defines all possible types of tokens a json document can
contain, and `token.Val` is only filed for `t_json::t_number` and
`t_json::t_string`:

```go
const (
	t_string       t_json = iota // anything between ""
	t_number                     // floating point, hex, etc
	t_true                       // true
	t_false                      // false
	t_null                       // null
	t_left_curly                 // {
	t_right_curly                // }
	t_left_braket                // [
	t_right_braket               // ]
	t_comma                      // ,
	t_colon                      // :
	t_eof                        // for any non structure characters outside of strings and numbers
)
```

Replacing `token.Val` with `token.Start` and `token.End` does not exactly
remove an allocation, see [Go Slices: usage and
internals](https://go.dev/blog/slices-intro), but reduces the size the `token`
struct occupies in memory. The new `token` structure:

```go
type token struct {
	Type t_json
	// only populated for number and string
	Start int
	End   int
}
```

Switching the lexer and the parser from byte slices
to this wasn't that hard and results in the following runtimes:

| backend        | 1mb              | 5mb              | 10mb            |
| -------------- | ---------------- | ---------------- | --------------- |
| encoding/json  | 24.9ms           | 116.7ms          | 225.9ms         |
| libjson before | 12.4ms (-12.5ms) | 51.8ms (-64.9ms) | 97.9ms (-128ms) |
| libjson        | 12ms (-0.4ms)    | 49.8ms (-2ms)    | 93.8ms (-4.1ms) |

And the following `Benchmark*` output:

| backend        | ns/op                    | B/op                    | allocs/op          |
| -------------- | ------------------------ | ----------------------- | ------------------ |
| encoding/json  | 134_535_103              | 39_723_750              | 650_033            |
| libjson before | 53_156_910 (-81_378_193) | 34_744_407 (-4_979_343) | 500_024 (-150_009) |
| libjson        | 50_504_689 (-2_652_221)  | 34_744_392 (-15)        | 500_024            |

## Manually inlining parser::expect

Currently the parser uses the `parser::expect` method to throw an error if the
current `token.Type` does not match the expected `t_json`:

```go
func (p *parser) expect(t t_json) error {
	if p.cur_tok.Type != t {
		return fmt.Errorf("Unexpected %q at this position, expected %q", tokennames[p.cur_tok.Type], tokennames[t])
	}
	return p.advance()
}
```

It is, for example, used in `parser::array`:

```go
func (p *parser) array() ([]any, error) {
	err := p.expect(t_left_braket)
	if err != nil {
		return nil, err
	}

	if p.cur_tok.Type == t_right_braket {
		err = p.advance()
		return []any{}, err
	}

	a := make([]any, 0, 8)

	for p.cur_tok.Type != t_eof && p.cur_tok.Type != t_right_braket {
		if len(a) > 0 {
			err := p.expect(t_comma)
			if err != nil {
				return nil, err
			}
		}
		node, err := p.expression()
		if err != nil {
			return nil, err
		}
		a = append(a, node)
	}

	return a, p.expect(t_right_braket)
}
```

This change replaces every `parser::expect` invocation with the body of the function:

```go
func (p *parser) array() ([]any, error) {
    if p.cur_tok.Type != t_left_braket {
        return nil, fmt.Errorf("Unexpected %q at this position, expected %q", tokennames[p.cur_tok.Type], tokennames[t_left_braket])
    }
    err := p.advance()
    if err != nil {
        return nil, err
    }

    if p.cur_tok.Type == t_right_braket {
            return []any{}, p.advance()
    }

    a := make([]any, 0, 8)

    for p.cur_tok.Type != t_eof && p.cur_tok.Type != t_right_braket {
        if len(a) > 0 {
            if p.cur_tok.Type != t_comma {
                return nil, fmt.Errorf("Unexpected %q at this position, expected %q", tokennames[p.cur_tok.Type], tokennames[t_comma])
            }
            err := p.advance()
            if err != nil {
                return nil, err
            }
        }
        node, err := p.expression()
        if err != nil {
            return nil, err
        }
        a = append(a, node)
    }

    if p.cur_tok.Type != t_right_braket {
        return nil, fmt.Errorf("Unexpected %q at this position, expected %q", tokennames[p.cur_tok.Type], tokennames[t_right_braket])
    }

    return a, p.advance()
}
```

The results of this change:

| backend        | 1mb             | 5mb              | 10mb              |
| -------------- | --------------- | ---------------- | ----------------- |
| encoding/json  | 24.9ms          | 116.7ms          | 225.9ms           |
| libjson before | 12ms (-12.9ms)  | 49.8ms (-66.9ms) | 93.8ms (-134.1ms) |
| libjson        | 11.5ms (-0.5ms) | 48.5ms (-1.3ms)  | 91ms (-2.3ms)     |

| backend        | ns/op                    | B/op                    | allocs/op          |
| -------------- | ------------------------ | ----------------------- | ------------------ |
| encoding/json  | 134_535_103              | 39_723_750              | 650_033            |
| libjson before | 50_504_689 (-84_030_414) | 34_744_392 (-4_979_358) | 500_024 (-150_009) |
| libjson        | 49_262_503 (-1_242_186)  | 34_744_160 (-232)       | 500_024            |

## Parallelising lexer::next and parser::parse

Moving from lexing on demand to possibly prelexing in paralell did not
result a decrease in runtime, but regressed the performance towards the
`encoding/json` results.

> I tested buffered channel sizes from 2,8,16,32 up until 50k (because thats
> the number i use for the amount of objects for the benchmarks) and none of
> these tests yielded any runtime improvements.

Currently said on demand lexing is attached to the parser as follows:

```go
type parser struct {
	l       lexer
	cur_tok token
}

func (p *parser) advance() error {
	t, err := p.l.next()
	p.cur_tok = t
	if p.cur_tok.Type == t_eof && err != nil {
		return err
	}
	return nil
}
```

Replacing this with a channel and moving the tokenisation to a go routine:

```go
type parser struct {
	l       lexer
	c       <-chan token
	cur_tok token
}

func (p *parser) advance() {
	p.cur_tok = <-p.c
}
```

Previously, the lexer and parser invocation worked as shown below:

```go
func New(data []byte) (JSON, error) {
	p := parser{l: lexer{data: data}}
	obj, err := p.parse()
	if err != nil {
		return JSON{}, err
	}
	return JSON{obj}, nil
}
```

Now we have to manage error handling, channel creation, etc:

```go
const chanSize = 64

func New(data []byte) (JSON, error) {
	l := lexer{data: data}
	c := make(chan token, chanSize)
	var lexerErr error
	go func() {
		for {
			if tok, err := l.next(); err == nil {
				if tok.Type == t_eof {
					break
				}
				c <- tok
			} else {
				lexerErr = err
				break
			}
		}
		close(c)
		c = nil
	}()
	p := parser{l: l, c: c}
	obj, err := p.parse()
	if lexerErr != nil {
		return JSON{}, lexerErr
	}
	if err != nil {
		return JSON{}, err
	}
	return JSON{obj}, nil
}
```

> The changes are kept in the
> [`paralell-lexer-and-parser`](https://github.com/xNaCly/libjson/tree/parallel-lexer-and-parser)
> branch.

Benchmarking this sadly did not satisfy my search for better performance, but I
wanted to include it either way:

| backend        | 1mb              | 5mb              | 10mb               |
| -------------- | ---------------- | ---------------- | ------------------ |
| encoding/json  | 24.9ms           | 116.7ms          | 225.9ms            |
| libjson before | 11.5ms (-13.4ms) | 48.5ms (-68.2ms) | 91ms (-136.4ms)    |
| libjson        | 24.3ms (+12.8ms) | 112.5ms (+64ms)  | 218.6ms (+127.6ms) |

| backend        | ns/op                     | B/op                    | allocs/op          |
| -------------- | ------------------------- | ----------------------- | ------------------ |
| encoding/json  | 134_535_103               | 39_723_750              | 650_033            |
| libjson before | 50_504_689 (-85_272_600)  | 34_744_392 (-4_979_590) | 500_024 (-150_009) |
| libjson        | 125_533_704 (+75_029_015) | 35_949_392 (+1_205_000) | 500_031 (+7)       |

## Results

Again, these result from design choices, benchmarking, profiling and
exploration of many things similar to the parallelisation attempt above.

| backend        | 1mb              | 5mb              | 10mb            |
| -------------- | ---------------- | ---------------- | --------------- |
| encoding/json  | 24.9ms           | 116.7ms          | 225.9ms         |
| libjson before | 11.5ms (-13.4ms) | 48.5ms (-68.2ms) | 91ms (-136.4ms) |

| backend       | ns/op                    | B/op                    | allocs/op          |
| ------------- | ------------------------ | ----------------------- | ------------------ |
| encoding/json | 134_535_103              | 39_723_750              | 650_033            |
| libjson       | 50_504_689 (-85_272_600) | 34_744_392 (-4_979_590) | 500_024 (-150_009) |

Summing up, libjson is currently around 2.5x faster than `encoding/json`. For
50k objects in a json array, it uses 5MB less memory and makes 150k less
allocations - pretty good.
