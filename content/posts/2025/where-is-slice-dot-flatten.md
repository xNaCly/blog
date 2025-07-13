---
title: "Where The FUCK Are slice.Flatten And slice.Map"
summary: "Go iterators are too minimalist and iter.Seq/iter.Seq2 suck"
date: 2025-06-22
tags:
    - go
---

I recently found myself having to work with some 2d slices in Go, when it hit
me, go's `slices` package has no `Flatten` or `Map` functions. I mainly needed to extract
these slices from `map`'s, sort them, filter and pass them to other iterator
based `slice` functions ([`iter`](https://pkg.go.dev/iter) and
[`slices`](https://pkg.go.dev/slices)). 

```go
var sets = map[string][]string{
	"nato": {
		"Alfa",
        "Bravo",
        // ...
		"Zulu",
	},
	"german": {
		"Anton",
		"Berta",
        // ...
		"Zacharias",
	},
}

func main() {
	// phonetic alphabet stuff

	// there are 26 chars in an alphabet and each set is an alphabet
	flattend := make([]int, len(sets)*26)
	idx := 0
	for inner := range maps.Values(sets) {
		for _, innerVal := range inner {
			l := len(innerVal)
			if l != 0 {
				flattend[idx] = l
				idx += 1
			}
		}
	}
	sum := 0
	slices.Sort(flattend)
	for _, v := range flattend {
		sum += v
	}
	fmt.Println(sum)
}
```

{{<shellout>}}
$ go run .
%SEPARATOR%
300
{{</shellout>}}

# Where is Flatten (+Map) and Why even Flatten

Most, if not all, `slice` functions accept
[`iter.Seq`](https://cs.opensource.google/go/go/+/refs/tags/go1.24.4:src/iter/iter.go;l=221):

```go
// Seq is an iterator over sequences of individual values.
// When called as seq(yield), seq calls yield(v) for each value v in the sequence,
// stopping early if yield returns false.
// See the [iter] package documentation for more details.
type Seq[V any] func(yield func(V) bool)
```

The issue is: converting any 2d slice (`[][]T`) to an iterator is generally
done via `slices.All`, which yields
[`iter.Seq2`](https://cs.opensource.google/go/go/+/refs/tags/go1.24.4:src/iter/iter.go;l=227)


```go
// All returns an iterator over index-value pairs in the slice
// in the usual order.
func All[Slice ~[]E, E any](s Slice) iter.Seq2[int, E] {
	return func(yield func(int, E) bool) {
		for i, v := range s {
			if !yield(i, v) {
				return
			}
		}
	}
}
```


```go
// Seq2 is an iterator over sequences of pairs of values, most commonly key-value pairs.
// When called as seq(yield), seq calls yield(k, v) for each pair (k, v) in the sequence,
// stopping early if yield returns false.
// See the [iter] package documentation for more details.
type Seq2[K, V any] func(yield func(K, V) bool)
```

For instance, passing `[][]string` to `slices.All` computes the following
generic:

```go
// func[Slice ~[]E, E any](s Slice) iter.Seq2[int, E]
func slices.All(s [][]string) iter.Seq2[int, []string] 
```


And none of the below functions accept the above `iter.Seq2`:

```go
func Collect[E any](seq iter.Seq[E]) []E
func AppendSeq[Slice ~[]E, E any](s Slice, seq iter.Seq[E]) Slice
func Sorted[E cmp.Ordered](seq iter.Seq[E]) []E
func SortedFunc[E any](seq iter.Seq[E], cmp func(E, E) int) []E
func SortedStableFunc[E any](seq iter.Seq[E], cmp func(E, E) int) []E
```


So I would need to consume each iterator value and consume all its elements
before moving the resulting temporary container into yet another iterator to
pass into all other, iterator consuming functions.

Rust has `Iterator.flatten` and every other "functional like" language
constructs in not so functional languages (JavaScript, etc.) contain them too.

```rust
// [5, 5]
vec![vec!["hello"], vec!["world"]]
    .iter()
    .flatten()
    .map(|word| word.len())
    .collect::<Vec<_>>();
```

```js
[["hello"], ["world"]].flat().map(word => word.length);
```

So I'm asking: Where the fuck are `slices.Flatten` and `slices.Map`?:

```go
// []string{"hello", "world"}
slices.Collect(
    slices.Map(
        slices.Flatten(
            slices.All([][]string{{"hello"}, {"world"}}),
        ),
        func(in string) int {
            return len(in)
        },
    ),
)
```

On an whole other note: `map.Values` from the example returns `iter.Seq`
while `slices.All` returns `iter.Seq2`, so we will need to write two
`Flatten` implementations due to Go having a not really generic
generic system.

> Also this sucks to look at, but I already wrote an article about that:
> [Fun with Go Iterators](/posts/2024/fun-with-iterators/).


# A Flatten, a simpler Flatten and an even simpler Map

Answering the above question:

Even though Go iterators are really weird to write, but easy to consume,
these are trivial to understand:

```go
// Map takes a Seq[T] and applies fn to each element, producing a Seq[V].
func Map[T any, V any](seq iter.Seq[T], fn func(T) V) iter.Seq[V] {
	return func(yield func(V) bool) {
		seq(func(t T) bool {
			v := fn(t)
			return yield(v)
		})
	}
}

// Flatten flattens Seq[[]T] into Seq[T]
func Flatten[T any](outer iter.Seq[[]T]) iter.Seq[T] {
	return func(yield func(T) bool) {
		outer(func(inner []T) bool {
			for _, val := range inner {
				if !yield(val) {
					return false
				}
			}
			return true
		})
	}
}

// FlattenSeq2 flattens Seq2[K, []T] into Seq[T]
func FlattenSeq2[T any, K any](outer iter.Seq2[K, []T]) iter.Seq[T] {
	return func(yield func(T) bool) {
		outer(func(_ K, inner []T) bool {
			for _, val := range inner {
				if !yield(val) {
					return false
				}
			}
			return true
		})
	}
}
```

Reworking the example we started out with with the new `Flatten`
and `Map` iterator functions:

```go
func main() {
	sum := 0
	for _, v := range slices.Sorted(
		Map(
			Flatten(maps.Values(sets)),
			func(in string) int {
				return len(in)
			},
		),
	) {
		sum += v
	}
	fmt.Println(sum)
}
```

And using `Flatten` with `slices.All` via 

```go
FlattenSeq2(slices.All([][]string{}))
```

For example:

```go {hl_lines=[4]}
// gen produces `amount` of tuples of len `tupleSize` with unique
// members of sets
func gen(sets [][]string, amount int, tupleSize int) [][]string {
	allWords := slices.Collect(FlattenSeq2(slices.All(sets)))
	allWordsLen := len(allWords)
	r := make([][]string, amount)
	for i := range amount {
		allWordsLocal := make([]string, allWordsLen)
		copy(allWordsLocal, allWords)
		r[i] = make([]string, toupleSize)
		for j := range toupleSize {
			idx := rand.Intn(len(allWordsLocal) - 1)
			r[i][j] = allWordsLocal[idx]
			allWordsLocal[idx] = allWordsLocal[len(allWordsLocal)-1]
			allWordsLocal = allWordsLocal[:len(allWordsLocal)-1]
		}
	}
	return r
}
```

# Where are the other iterator helpers and why are Go iterators like this?

Go iterators are probably a good idea? I don't think they fit into the language
at all and they lack so many features that I perceive them to be somewhat
unfinished. Especially compared to something like the interface system and how
most packages feel designed around the idea of plug and play `Writer` and
`Reader` interaction. Maybe I am too spoiled by rust and pre generic Go.

Since I'm already here, where are:

1. `Filter`
2. `FlatMap`
3. `FilterMap`
4. `Sum`
5. ...


Also, I don't have (or want) a google account so I won't contribute any
of these, nor `Flatten` or `Map`, to the Go project - even disregarding
the fact that they probably wouldn't be accepted as part of `slices`.
