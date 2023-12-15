---
title: "Sophia Lang Weekly - 00"
summary: "Performance, nested objects/arrays & better errors"
date: 2023-12-09
tags:
  - sophia
---

{{<callout type="Tip">}}
This series will be a continuous somewhat weekly newsletter about my progress,
changes and anything around the [sophia](https://github.com/xnacly/sophia)
programming language. I will try to publish one post of the series containing
the changes and ideas for every week I have time to work on the project, so
expect around 2-3 a month, mostly on Sundays. These posts will be short,
concise. Basic knowledge of interpreter and programming language
design is assumed.
{{</callout>}}

This weeks changes include improvements to the performance of certain
benchmarks, clearer errors for illegal index operations, reworked index syntax
for arrays and objects (with shortcomings) and a big planned feature.

## Performance improvements

This and last week we saw a lot of drastic performance improvements and there
is already a post going into detail on several optimizations on my blog:

> Excerpts from [Improving programming language performance](https://xnacly.me/posts/2023/language-performance/):
>
> _How I improved my programming language runtime [...] for a specific
> benchmark by reducing its execution time by 7.03 times or 703%. The benchmark
> script previously took 22.2 seconds. I reduced it to 3.3s!_
>
> _[...]_
>
> _Our slightly less easy to implement changes decreased the runtime by 3.795s
> from 5.803s to 2.009s in comparison to the not optimised state - that is
> really good, really really good, we are talking a 65.38% runtime decrease._

## Deep array and index access

Previously the parser did not support nested array or object index notation
such as `[object.field.field]` or `[array.index.field]` both required a wrapper
variable:

```lisp
(let person {
    name: "anon"
    bank: {
        money: 2500
        institute: {
            name: "western union"
        }
    }
    age: 25
})

;; (put [person.bank.money]) <-- parser error

(let bankOfPerson [person.bank])
(put [bankOfPerson.money]) ;; 2500

(let bankOfPersonInstititue [person.institute])
(put [bankOfPerson.name]) ;; western union
```

Having reworked the parser for nested array and index notation the following is
now supported:

```lisp
(put [person.bank.money]) ;; 2500
(put [person.bank.institute.name]) ;; "western union"
```

## Reworked array and object index notation

I really disliked the way I implemented indexing into arrays or objects,
therefore I reworked the notation. Previously accessing array or object
contents was done inside of `[]`:

```lisp
(let person {
    name: "anon"
    bank: {
        money: 2500
        institute: {
            name: "western union"
        }
    }
    age: 25
})

(put [person.bank.money]) ;; 2500
(put [person.bank.institute.name]) ;; "western union"

(let arr person 1 2 3 4 5)
(put [arr.0.name]) ;; "anon"
```

The improved way is obviously inspired by C, Go, JavaScript, etc:

```lisp
(let person {
    name: "anon"
    bank: {
        money: 2500
        institute: {
            name: "western union"
        }
    }
    age: 25
})

(put person.bank.money) ;; 2500
(put person.bank.institute.name) ;; "western union"

(let arr person 1 2 3 4 5)
(put arr.0.name) ;; "anon"
```

This removes the need for writing even more braces in a brace dominated environment :^).

## More precise illegal index error feedback

While reworking the index notation I also improved the way errors for indexing
are displayed. Previously the `expr.Index` AST node would simply complain about
not containing logic for indexing into the given type.

![old-index-feedback](/sophia-weekly/old-index-feedback.png)

Now it includes more precise feedback:

![new-index-feedback](/sophia-weekly/new-index-feedback.png)

## New implementation example

This week i added the computation of the [binomial
coefficient](https://en.wikipedia.org/wiki/Binomial_coefficient) to the
[examples](https://github.com/xNaCly/Sophia/blob/master/examples):

```lisp
(fun bin (_ n k)
    (if (gt k n)
        (return -1))
    (if (and (eq k n) (eq k 0))
        (return 1))

    ;; Due to the symmetry of the binomial coefficient with regard to k and n −
	;; k, calculation may be optimised by setting the upper limit of the
	;; product above to the smaller of k and n − k, see
	;; https://en.wikipedia.org/wiki/Binomial_coefficient#Computing_the_value_of_binomial_coefficients
    (let kn (- n k))
    (if (lt kn k)
        (let k kn))

    ;; see https://en.wikipedia.org/wiki/Binomial_coefficient#Multiplicative_formula
    (let r 1)
    (for (_ i) k
        (let r
            (/ (* r (- n i)) (+ i 1)))
        )
    r)

(put (bin 1 1)) ;; 1
(put (bin 6 3)) ;; 20
(put (bin 49 6)) ;; 20
(put (bin 20 15)) ;; 15504
```

It makes use of a symmetry of `k` and `n-k`, thus reducing the amount of
iterations required to compute the coefficient. Implementation inspired by
[statlib.BinomialCoefficient](https://github.com/xNaCly/statlib/blob/master/bin.go).

## Planned feature: modules

My plan for the sophia language is to not include any object orientation due to
the fact that I am a vivid Java hater (unless its the right tool for the job -
which it rarely is). I also do not want to allow myself to attach functions
onto objects. My idea is to create modules in a rust like fashion (multiple in
one file are allowed) and to define static functions in these. The resulting
syntax will look something like:

```lisp
;; custom module
(module person
    (fun str (_ p) (++ "person: " p.name)

    (module extract ;; modules can be nested
        (fun name (_ p) p.name)
    )
)

;; using a custom module
(use person)
(let pers { name: "anon" })
(put (person::string pers))

;; using nested modules
(use person::extract)
(put (person::extract::name pers))
```

I also want to mirror go's extensive standard library into the sophia language
via modules and static functions:

```lisp
(use strings)
;; results in ["192", "168", "0", "217"]
(put (strings::split "192.168.0.217" "."))

(use fmt)
(fmt::printf "Hello %q" "traveler")
(put (fmt::sprintf "Hello %q" "Space"))
```

I also long for a better type system in the sophia language, so maybe thats an
idea.
