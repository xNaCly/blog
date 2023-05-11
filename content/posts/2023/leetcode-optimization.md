---
title: Leetcode Optimization and Go
summary: Solving and optimizing a leetcode puzzle in three ways
date: 2023-05-11
tags:
  - go
  - leetcode
  - performance
---

{{<callout type="Info">}}
While i dislike the whole idea around grinding leetcode puzzles as much as possible,
i still like the challenge of thinking about a problem and correcting the implementation with a [TDD](https://en.wikipedia.org/wiki/Test-driven_development) approach.

The third implementation runs with 0ms runtime and 2.1MB memory usage, this beats 100% and 80% of all solutions, [source](https://leetcode.com/problems/replace-all-s-to-avoid-consecutive-repeating-characters/submissions/948070040/).
{{</callout>}}

This article highlights three different approaches to solving the puzzle [1576](https://leetcode.com/problems/replace-all-s-to-avoid-consecutive-repeating-characters/).

The puzzle is fairly easy, the expected input is a string made up of lowercase alphabetical characters, as well as containing a question mark (`?`). This character should be replaced with an alphabetical character and should not be repeated consecutively.

For example:

```text
"?zs" -> "azs"
"ubv?w" -> "ubvaw"
"j?qg??b" -> "jaqgacb"
```

To implement this, we loop over the characters, check if the current character is a question mark, choose the `a` as a replacement, check if the previous character is `a` or the following character is `a`, if so we move on to the next character.

The logic in the loop can be visualized via a flow chart:

![flow-chart](/leetcode/flow.png)

## Setup

We already have three test cases taken from the leetcode puzzle, so lets create the skeleton for running our implementation:

```go
// main.go
package main

import (
	"fmt"
)

var i = []string{
	"?zs",
	"ubv?w",
	"j?qg??b",
}

func modifyString(s string) string {
    return ""
}

func main() {
	for _, s := range i {
        fmt.Printf("%s -> %s\n", s, modifyString(s))
	}
}
```

## First implementation

Our first implementation is straight forward. We define a string to perform a character lookup on.

```go
// ...
const alphabet = "abcdefghijklmnopqrstuvwxyz"

func modifyString(s string) string {
	b := strings.Builder{}
	for i, r := range s {
		if r == '?' {
			rr := 0
			for (b.Len() > 0 && alphabet[rr] == b.String()[b.Len()-1]) ||
                    (len(s) > i+1 && alphabet[rr] == s[i+1]) {
				rr++
			}
			b.WriteByte(alphabet[rr])
		} else {
			b.WriteRune(r)
		}
	}
	return b.String()
}
// ...
```

We then create a [strings.Builder](https://pkg.go.dev/strings#Builder) in the function body, which is an incredibly faster way to concatenate strings than simply adding them together (`s += "test"`).

The next step is to iterate of the given string `s` and checking if the current rune (`r`) is a question mark.

```go
// ...
for i, r := range s {
    if r == '?'{ /* ...*/ }
}
// ...
```

In the else statement, we simply write the current rune to the string builder `b`.

```go {hl_lines=[7]}
// ...
b := strings.Builder{}
for i, r := range s {
    if r == '?'{
        /* ...*/
    } else {
        b.WriteRune(r)
    }
}
// ...
```

To calculate a new character we define a new variable `rr` which we will use to index the `alphabet` constant, as well as a for loop to iterate over possible characters.

```go {hl_lines=["5-8"]}
// ...
b := strings.Builder{}
for i, r := range s {
    if r == '?'{
        rr := 0
        for (b.Len() > 0 && alphabet[rr] == b.String()[b.Len()-1]) ||
            (len(s) > i+1 && alphabet[rr] == s[i+1]) {
        }
    } else {
        b.WriteRune(r)
    }
}
// ...
```

The heart of this approach is the for loop condition inside of the if statement, so lets take this apart:

```text
(b.Len() > 0 && alphabet[rr] == b.String()[b.Len()-1])
||
(len(s) > i+1 && alphabet[rr] == s[i+1])
```

Our for loops iterates as long as one of the conditions is met.

```text {hl_lines=[1]}
(b.Len() > 0 && alphabet[rr] == b.String()[b.Len()-1])
||
(len(s) > i+1 && alphabet[rr] == s[i+1])
```

The first condition checks if the string builders `b` length is bigger than 0, because we want to index it with possibly zero if we are at the start of the string `s`. And after doing so compares the last character in the string build with the currently computed character.

```text
(b.Len() > 0 && alphabet[rr] == b.String()[b.Len()-1])
 ^^^^^^^^^^^    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 |              |
 |              + checks if the last character
 |                in the string builder
 |                is the same as the currently
 |                computed character
 |
 + checks if the string builder can be indexed
```

The second condition does almost the same thing, but instead of checking the previous character it checks the next character.

```text {hl_lines=[3]}
(b.Len() > 0 && alphabet[rr] == b.String()[b.Len()-1])
||
(len(s) > i+1 && alphabet[rr] == s[i+1])
```

We again start of by checking if the length of the input string is longer than the number we want to index, if true, check if the currently computed character matches the next character in the input string.

```text
(len(s) > i+1 && alphabet[rr] == s[i+1])
 ^^^^^^^^^^^^    ^^^^^^^^^^^^^^^^^^^^^^
 |               |
 |               + compare the computed
 |                 rune to the next
 |                 rune in the input
 |
 + check if the string is long enough
   for us to index the next character
```

Both of these conditions rely on [lazy evaluation](https://en.wikipedia.org/wiki/Short-circuit_evaluation), otherwise indexing the string builder would throw an error.

In the for loop body, we simply increment the alphabet index by one. After computing the new character, we write it to the string builder via a lookup on the `alphabet` string constant.

```go {hl_lines=[8, 10]}
// ...
	b := strings.Builder{}
	for i, r := range s {
		if r == '?' {
			rr := 0
			for (b.Len() > 0 && alphabet[rr] == b.String()[b.Len()-1]) ||
                    (len(s) > i+1 && alphabet[rr] == s[i+1]) {
				rr++
			}
            b.WriteByte(alphabet[rr])
		} else {
			b.WriteRune(r)
		}
	}
}
// ...
```

At the very end of the implementation, we return the string builders `.String()` method:

```go {hl_lines=[16]}
// ...
func modifyString(s string) string {
	b := strings.Builder{}
	for i, r := range s {
		if r == '?' {
			rr := 0
			for (b.Len() > 0 && alphabet[rr] == b.String()[b.Len()-1]) ||
                    (len(s) > i+1 && alphabet[rr] == s[i+1]) {
				rr++
			}
            b.WriteByte(alphabet[rr])
		} else {
			b.WriteRune(r)
		}
	}
    return b.String()
}
// ...
```

Running our application via `go run main.go`, yields the following result:

```bash
go run .
# ?zs -> azs
# ubv?w -> ubvaw
# j?qg??b -> jaqgacb
```

{{<callout type="Tip">}}
We have some obvious performance issues in this version of the code:

- using a string to lookup characters
- calling len functions multiple times
- computing values in the loop, which could be precomputed

{{</callout>}}

## Second implementation

```go
func modifyStringSecond(s string) string {
	b := strings.Builder{}
	for i, r := range s {
		if r == '?' {
			rr := 0
			for (b.Len() > 0 && rr+97 == int(b.String()[b.Len()-1])) ||
				(len(s) > i+1 && rr+97 == int(s[i+1])) {
				rr++
			}
			b.WriteRune(rune(rr + 97))
		} else {
			b.WriteRune(r)
		}
	}
	return b.String()
}
```

This approach differs from the first approach, by replacing the lookup of a character from the alphabet by adding an offset to the current character.

Due to the fact, that we start our computation of the character we want to replace the question mark with, we can add `97` to this value.
This works, because the lowercase `a` is located at the Decimal value 97 in the [ascii standard](https://www.asciitable.com/).
Go uses [UTF-8](https://en.wikipedia.org/wiki/UTF-8) for encoding runes / characters, which is ascii compatible and does therefore support our idea.

> For example:
>
> Suppose we have the value 10 stored in `rr`.
> Comparing this value to the previous or next character can be done by simply adding 97 to this value.
>
> ```go
> fmt.Println(10+97 == int('k'))
> // true
> fmt.Println(0+97 == int('a'))
> // true
> fmt.Println(1+97 == int('a'))
> // false
> ```

Simply removing the character lookup via index of the `alphabet` constant and replacing this with adding an offset to the computed value should increase the performance right? - _as it turns out that is not the case_ 🤣

{{<callout type="Tip">}}
We have some obvious performance issues in this version of the code:

- 3 type conversions per iteration
- computing functions in the loop, which could be precomputed

{{</callout>}}

## Third implementation

The third and heavly optimized version decreases the time taken for every operation by a factor of 2 compared to the first implementation.

```go
func modifyStringThird(s string) string {
	ls := len(s)
	b := make([]byte, 0)
    // input loop
	for i, r := range s {
		by := byte(r)
		lb := len(b)
		if r == '?' {
			var rr byte
            // rune computation loop
			for (lb > 0 && rr+97 == b[lb-1]) ||
				(ls > i+1 && rr+97 == s[i+1]) {
				rr++
			}
			by = rr + 97
		}
		b = append(b, by)
	}
	return string(b)
}
```

This version uses the optimization we already applied in the second approach (offset instead of rune lookup) plus computing the length of the input and the byte array outside of the rune computing loop.

This approach reduces the type conversions inside of the computing loop from 3 to 0, and inside the input loop to 1.
It also does not call any functions inside the computation loop, such as the `strings.Builder.Len()` or the `len(s)` methods.

## Benchmarks

To show the difference between the approaches, i created three benchmarks via the [testing](https://pkg.go.dev/testing@go1.20.4#hdr-Benchmarks) framework included in gos std lib:

```go
package main

import (
	"strings"
	"testing"
)

var inputSizes = map[string]int{
	"size10":    10,
	"size100":   100,
	"size1000":  1000,
	"size10000": 10000,
}

func BenchmarkFirst(b *testing.B) {
	for size, v := range inputSizes {
		b.Run(size, func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				modifyStringFirst(strings.Repeat("j?qg??b", v))
			}
		})
	}
}

func BenchmarkSecond(b *testing.B) {
	for size, v := range inputSizes {
		b.Run(size, func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				modifyStringSecond(strings.Repeat("j?qg??b", v))
			}
		})
	}
}

func BenchmarkThird(b *testing.B) {
	for size, v := range inputSizes {
		b.Run(size, func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				modifyStringThird(strings.Repeat("j?qg??b", v))
			}
		})
	}
}
```

Running this via the `go test` tool, prints interesting results:

```bash
go test ./... -bench=.
# goos: linux
# goarch: amd64
# pkg: leetcode
# cpu: AMD Ryzen 7 3700X 8-Core Processor
# BenchmarkFirst/size10-16                 2185942               547.2 ns/op
# BenchmarkFirst/size100-16                 337184              3487 ns/op
# BenchmarkFirst/size1000-16                 35896             33587 ns/op
# BenchmarkFirst/size10000-16                 3548            322588 ns/op
# BenchmarkFirst/size100000-16                 352           3424906 ns/op

# BenchmarkSecond/size10-16                1998387               601.3 ns/op
# BenchmarkSecond/size100-16                298550              3909 ns/op
# BenchmarkSecond/size1000-16                32400             37335 ns/op
# BenchmarkSecond/size10000-16                3280            356697 ns/op
# BenchmarkSecond/size100000-16                318           3777205 ns/op

# BenchmarkThird/size10-16                 3076419               393.0 ns/op
# BenchmarkThird/size100-16                 576669              1978 ns/op
# BenchmarkThird/size1000-16                 64304             18599 ns/op
# BenchmarkThird/size10000-16                 7867            156845 ns/op
# BenchmarkThird/size100000-16                 636           1938507 ns/op

# PASS
# ok      leetcode        21.463s
```

Comparing the output shows us that the second implementation is a bit slower than the first and the third implementation is around 2x faster than the first implementation:

![benchmark](/leetcode/Benchmark.png)
