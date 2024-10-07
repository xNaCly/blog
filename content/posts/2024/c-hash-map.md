---
title: "HashMap in 25 lines of C"
summary: "Minimal hash table implementation"
date: 2024-08-29
tags:
    - c
---

This post shows how to implement a simple hash table of arbitrary length,
allowing to store all values c knows and doing so while being as minimal as
possible. It does however not include collision handling, to implement this,
simply swap the `Map.buckets` array with an array of linked list and insert
into the linked lists instead of only into the bucket array and you should be
good to go.

```c
#include <assert.h>

typedef struct Map { size_t size; size_t cap; void **buckets; } Map;
const size_t BASE = 0x811c9dc5;
const size_t PRIME = 0x01000193;
size_t hash(Map *m, char *str) {
    size_t initial = BASE;
    while(*str) {
        initial ^= *str++;
        initial *= PRIME;
    }
    return initial & (m->cap - 1);
}

Map init(size_t cap) {
    Map m = {0,cap};
    m.buckets = malloc(sizeof(void*)*m.cap);
    assert(m.buckets != NULL);
    return m;
}

void put(Map *m, char *str, void *value) {
    m->size++;
    m->buckets[hash(m, str)] = value;
}

void* get(Map *m, char *str) {
    return m->buckets[hash(m, str)];
}
```

## Hashing

For the hashing I decided to go with
[FNV1a](https://en.wikipedia.org/wiki/Fowler%E2%80%93Noll%E2%80%93Vo_hash_function#FNV-1a_hash),
simply because its easy to implement and very fast. We are only using strings
as keys, thus we could use the [java way of hashing
strings](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html#hashCode--).
The idea is to start with an initial value (`BASE`) and assign this to the
xored value of itself and the data (current character). This is then assigned
to its multiplication with the `PRIME`.

The last line of the `hash`-function includes an optimisation for quicker
modulus computation, it is equivalent to `initial % m->cap` but is a lot
faster. It does however only work for the cap being powers of two.

## Storing and accessing everything

c allows for storage of all and any values via `void*`, I abuse this to only
store the pointers to values, thus allowing the values to be of any kind, the
only downside being, the user of the map has to allocate, ref, deref and cast
the values to the expected types.

```c
#include <stdio.h>
#include <stdlib.h>

// ... Map implementation

int main(void) {
    Map m = init(1024);
    double d1 = 25.0;
    double d2 = 50.0;
    put(&m, "key1", (void*)&d1);
    put(&m, "key2", (void*)&d2);

    printf("key1=%f;key2=%f\n", *(double*)get(&m, "key1"), *(double*)get(&m, "key2"));

    free(m.buckets);
    return EXIT_SUCCESS;
}
```

This showcases the casting and the ref + deref necessary to interact with the
hash table and of course the user has to free the memory used for the table
buckets.
