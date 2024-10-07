---
title: "Fun with Go Iterators"
date: 2024-10-07
summary: "Go 1.23 added Iterators, so lets build a js like streaming api"
tags:
    - go
---

Go version 1.23 added iterator support [^language] and the `iter` package
[^iterators]. We can now loop
 over constants, containers (maps, slices,
arrays,
 strings) and functions. At first I found the iterator creation clunky,
while consuming the iterator seems straightforward.

[^language]: https://go.dev/doc/go1.23#language
[^iterators]: https://go.dev/doc/go1.23#iterators

My issue with the go way of iterators is, you can't chain them like you would in JavaScript:

```js
[1,2,3,4]
    .reverse()
    .map(e => e*e)
    .filter(e => e % 2 == 0)
    .forEach(e => console.log(e)) 
```

## The Annoyance

Writing this in go would require us to chain 5 function calls:

```go
slices.ForEach(
    slices.Filter(
        slices.Map(
            slices.Reverse(slices.All([]int{1,2,3,4})), 
            func(i int) int { return i * i},
        ),
        func(i int) bool { return i % 2 == 0 }
    ),
    func(i int) { fmt.Println(i) }
)
```

This is an example, there are are no `Map`, `Filter` or `ForEach` functions in the `slices` package [^slices].

[^slices]: https://pkg.go.dev/slices


## The Solution (sort of)

Because i have a big distaste for writing chained "functional" operations like this, looking at you python (don't come at me haskell bros) - I wanted to use the new iterators and the `iter` package and wrap it with a structure to allow the nice and clean chaining JavaScript provides. Below are the same operations, but instead of using the `iter` and `slices` package, I use my abstraction:

```go
func TestIterator(t *testing.T) {
	From([]int{1, 2, 3, 4}).
		Reverse().
		Map(func(i int) int { return i * i }).
		Filter(func(i int) bool { return i%2 == 0 }).
		Each(func(a int) { println(a) })
    // 16
    // 4
}
```

## The Logic

Lets take a look a the implementation and let me introduce the `Iterator`struct.
It wraps the iterator `(*Iterator).iter` and thus allows me to callfunctions on
this structure, instead of having to use each iterator functionas a param to the
next one.

```go
type Iterator[V any] struct {
	iter iter.Seq[V]
}
```

Lets take a look at the first functions coming to mind when talking about iterators, creating one from a slice and collection one into a slice:

```go
func (i Iterator[V]) Collect() []V {
	collect := make([]V, 0)
	for e := range i.iter {
		collect = append(collect, e)
	}
	return collect
}

func From[V any](slice []V) *Iterator[V] {
	return &Iterator[V]{
		iter: func(yield func(V) bool) {
			for _, v := range slice {
				if !yield(v) {
					return
				}
			}
		},
	}
}
```

The first one is as straight forward as possible - create a slice, consume the
iterator, append each element, return the slice. The second highlights the weird
way iterators are created in go. Lets first take a look at the signature, we are
returning a pointer to the struct, so the callee can invoke all methods without
having to use a temporary variable for each. In the function itself, the
iterator is created by returning a closure, that loops over the param and
returning, which stops the iterator, when the `yield` function returns `false`.

### Each

The `ForEach` / `Each` method is the next function I want, It simply executes
the passed in function for every element of the iterator.

```go
func (i *Iterator[V]) Each(f func(V)) {
	for i := range i.iter {
		f(i)
	}
}
```

It can be used like this:

```go
From([]int{1, 2, 3, 4}).Each(func(a int) { println(a) })
// 1
// 2
// 3
// 4
```

### Reverse

A way to reverse the iterator, we first need to collect all elements and after that construct a new iterator from the collected slice, luckily we have functions for exactly this:

```go
func (i *Iterator[V]) Reverse() *Iterator[V] {
	collect := i.Collect()
	counter := len(collect) - 1
	for e := range i.iter {
		collect[counter] = e
		counter--
	}
	return From(collect)
}
```

Again, useful to reverse a slice:

```go
From([]int{1, 2, 3, 4}).Reverse().Each(func(a int) { println(a) })
// 4
// 3
// 2
// 1
```

### Map

Mutating every element of the iterator is a necessity, too:

```go
func (i *Iterator[V]) Map(f func(V) V) *Iterator[V] {
	cpy := i.iter
	i.iter = func(yield func(V) bool) {
		for v := range cpy {
			v = f(v)
			if !yield(v) {
				return
			}
		}
	}
	return i
}
```

At first we copy the previous iterator, by doing this, we skip causing a stack
overflow by referencing the `i.iter` iterator in the iterator itself. `Map` is
works by overwriting the `i.iter` with a new iterator thats consuming every
field of the `cpy` iterator and overwriting the iterator value with the result
of passing `v` to `f`, thus mapping over the iterator.

### Filter

After mapping, possibly the most used streaming / functional api method is
`Filter`. So lets take a look at our final operation:

```go
func (i *Iterator[V]) Filter(f func(V) bool) *Iterator[V] {
	cpy := i.iter
	i.iter = func(yield func(V) bool) {
		for v := range cpy {
			if f(v) {
				if !yield(v) {
					return
				}
			}
		}
	}
	return i
}
```

Similar to `Map`, we consume the copied iterator and invoke `f` with `v` as the
param for each one, if `f` returns true, we keep it in the new iterator. 

## Examples and Thoughts

The `slices` and the `iter` package both play very good together with the generic system introduced in go 1.18 [^go1.18].

[^go1.18]: https://go.dev/doc/go1.18

While this API is easier to use, I understand the reasoning of the go team for
not implementing iterators like this. Below are some tests that serve as
examples and the result of running them.

```go
package iter1

import (
	"fmt"
	"testing"
	"unicode"
)

func TestIteratorNumbers(t *testing.T) {
	From([]int{1, 2, 3, 4}).
		Reverse().
		Map(func(i int) int { return i * i }).
		Filter(func(i int) bool { return i%2 == 0 }).
		Each(func(a int) { println(a) })
}

func TestIteratorRunes(t *testing.T) {
	r := From([]rune("Hello World!")).
		Reverse().
		// remove all spaces
		Filter(func(r rune) bool { return !unicode.IsSpace(r) }).
		// convert every rune to uppercase
		Map(func(r rune) rune { return unicode.ToUpper(r) }).
		Collect()
	fmt.Println(string(r))
}

func TestIteratorStructs(t *testing.T) {
	type User struct {
		Id   int
		Name string
		Hash int
	}

	u := []User{
		{0, "xnacly", 0},
		{1, "hans", 0},
		{2, "gedigedagedeio", 0},
	}

	From(u).
		// computing the hash for each user
		Map(func(u User) User {
			h := 0
			for i, r := range u.Name {
				h += int(r)*31 ^ (len(u.Name) - i - 1)
			}
			u.Hash = h
			return u
		}).
		Each(func(u User) { fmt.Printf("%#+v\n", u) })
}
```

Running these, results in:

```text
$ go test ./... -v
=== RUN   TestIteratorNumbers
16
4
--- PASS: TestIteratorNumbers (0.00s)
=== RUN   TestIteratorRunes
!DLROWOLLEH
--- PASS: TestIteratorRunes (0.00s)
=== RUN   TestIteratorStructs
&iter1.User{Id:0, Name:"xnacly", Hash:20314}
&iter1.User{Id:1, Name:"hans", Hash:13208}
&iter1.User{Id:2, Name:"gedigedagedeio", Hash:44336}
--- PASS: TestIteratorStructs (0.00s)
PASS
ok      iter1   0.263s
```

So there u have it, a wrapper around `iter` and `slices` to mirror the way
JavaScript provides streaming, only in go.