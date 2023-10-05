---
title: "Implementing growing arrays for C"
date: 2023-10-05
summary: "Implementing a go like slice type for and in c"
tags:
  - go
  - c
---

{{<callout type="Background">}}
A few weeks ago I posted the [Implementing Result Types for
C](/posts/2023/result-types-c/) article. With the same purpose and reasoning I
required a list type which grows depending on the size of the input. Because i
like the way [slices](https://go.dev/tour/moretypes/7) work and their
[implementation](https://go.dev/blog/slices-intro) in the go programming
language i decided to port a rudimentary version to C for my
[SeaScript](https://github.com/xNaCly/SeaScript) programming language project.
{{</callout>}}

The concept of slices is build around wrapping array access and therefore
enabling bounds checking, dynamic resizing and better memory alignment than for
example a linked list.

Lets take a look at a simple example of using go slices and compare it to my
ported version:

```go
package main

import "fmt"

func main() {
    s := make([]int)
    for i := 0; i < 100; i++ {
        s = append(s, i)
    }
    for i := 0; i < 100; i++ {
        fmt.Println(s[i])
    }
}
```

```c
#include <stdio.h>
#include <stdlib.h>

#include "slice.h"

int main(void) {
    CsSlice *s = CsSliceNew(0);
    for (int i = 0; i < 100; i++) {
        int *j = (int *)malloc(sizeof(int));
        *j = i;
        CsSliceAppend(s, j);
    }
    for (size_t i = 0; i < 100; i++) {
        int *r = (int *)CsUnwrap(CsSliceGet(s, i));
        printf("%d\n", *r);
        free(r)
    }
    CsSliceFree(s)
    return EXIT_SUCCESS;
}
```

The main difference between c and go here, is the required allocation for
storing arbitrary data in the slice, which is needed because the only way i
know of to include generic data in c structures is to use `void *`, which
requires an allocation. We also deallocate the stored memory in line 16,
because we free the whole slice in line 18.

Memory Ownership for both stored values and the slice itself is required of the
library consumer, the slice however doubles in size if insertion requires
bigger capacity than currently available.

The following is the header file for the `slice` package:

```c
#ifndef SLICE_H
#define SLICE_H

#include "result.h"
#include <stddef.h>

typedef struct CsSlice {
  // list of elements
  void **elements;
  // count of elements currenlty in list
  size_t len;
  // maxium size of Slice
  size_t cap;
} CsSlice;

// creates and returns a new slice, if initial_size is less than
// SLICE_MIN_SIZE, initial_size gets set to SLICE_MIN_SIZE.
CsSlice *CsSliceNew(size_t initial_size);

// inserts element at the given index, if s.len would be bigger than s.cap
// after insertion, doubles the size of the underlying array
void CsSliceAppend(CsSlice *s, void *element);

// returns the given element if 0 <= index < s.len
CsResult *CsSliceGet(CsSlice *s, int index);

// returns pointer to the underlying array
void **CsSliceGetArray(CsSlice *s);

// frees the allocated memory region for the given Slice, sets the
// pointer to point to NULL
void CsSliceFree(CsSlice *s);

#endif
```

{{<callout type="Tip">}}
Interested in the implementation of this API? View the source code
[here](https://github.com/xNaCly/SeaScript/blob/master/sealib/slice.c).
{{</callout>}}
