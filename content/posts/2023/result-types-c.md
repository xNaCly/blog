---
title: "Implementing Result Types for C"
date: 2023-09-05
summary: "Implementing a Rust like Result type for and in c"
tags:
  - c
  - SeaScript
---

While working on [SeaScript](https://github.com/xNaCly/SeaScript) - a small
programming language that compiles to c, I wanted to add result types to allow
functions to return errors and values without a big hussle. This in turn
enables nice and clean error handling for functions such as:

```text
sqrt [n:number]: Result[number] -> {
    if n < 0 {
        return Result{
            error: "can't compute sqrt for negative numbers"
        }
    }
    res = sqrt(n)
    if res < 0 {
        return Result{error: "couldn't compute sqrt of {n}"}
    }
    return Result{value: res}
}
```

Because seascript compiles to c, i have to implement this in a way that its not
a compile time feature only. So i sat down and implemented Result types in C.

```c
#ifndef RESULT_H
#define RESULT_H

#include <stdint.h>

typedef struct {
  // if the Result holds no error, this contains the success value
  void *value;
  // if the Result holds an error, this contains the error message
  const char *error;
  // this indicates if the Result holds an error
  int8_t hasError;
} SeaScriptResult;

// allocates a new Result, sets ->hasError to 0 and ->value to the given value
SeaScriptResult *SeaScriptResultNewSuccess(void *value);

// allocates a new Result, sets ->hasError to 1 and ->error to the given error
SeaScriptResult *SeaScriptResultNewError(const char *error);

// returns the value of the Result and destroys it. If the Result contains an
// error the error message is printed to stderr and the process exists with
// EXIT_FAILURE
void *SeaScriptResultUnwrap(SeaScriptResult *result);

// returns the value of the Result and destroys it. If the Result contains an
// error the provided error message is printed to stderr and the process exists
// with EXIT_FAILURE
void *SeaScriptResultExpect(SeaScriptResult *result, const char *error);

// frees the allocated memory region for the given Result, sets the
// pointer to point to NULL
void SeaScriptResultFree(SeaScriptResult *result);

#endif
```

The API manages its allocations by itself and exposes
`SeaScriptResultNewSuccess` and `SeaScriptResultNewError` for creating results.
It also exposes `SeaScriptResultUnwrap` and `SeaScriptResultExpect` for
consuming the result.

The best example is the before defined `sqrt` method written in in seascript
but translated to c:

```c
#include <stdio.h>
#include <stdlib.h>
#include "sealib/result.h"

SeaScriptResult *squareRoot(double n) {
    if (n < 0) {
      return SeaScriptResultNewError(
          "can't compute square root of negative integer");
    }
    double res = sqrt(n);
    if (res < 0) {
      return SeaScriptResultNewError(
          "failed to compute square root");
    }
    double *r = malloc(sizeof(double))
    *r = res;
    return SeaScriptResultNewSuccess(r);
}
```

The `SeaScriptResultNewSuccess` function requires a pointer to be passed in,
therefore the consumer of the `SeaScriptResult` has to free the embedded
pointer after consuming the result.

```c
int main(void) {
    SeaScriptResult* res = squareRoot(-5);
    double res = (double *) SeaScriptResultUnwrap(res);
    printf("%f\n", *res);
    free(res);
    return EXIT_SUCCESS;
}
```

Both `SeaScriptResultUnwrap` and `SeaScriptResultExpect` consume the Result,
write to stderr and exit the process, therefore the library consumer does not
need to free these Results.

{{<callout type="Tip">}}
Interested in the implementation of this API? View the source code
[here](https://github.com/xNaCly/SeaScript/blob/master/sealib/result.c).
{{</callout>}}
