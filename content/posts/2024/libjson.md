---
title: "Making libjson RFC 8259 compliant"
date: 2024-09-12
summary: "Giving lots of edge cases attention, so I can call my json parser RFC 8259 compliant"
tags:
  - json
  - go
---

I [wrote a json parser in go](https://github.com/xNaCly/libjson), because I
wanted to do some language developement, write a lexer and a parser while doing
a lot of performance work. So here i am, almost at the performance of
`encoding/json`[^performance], but I expose a different way of interacting with
the json object via the `xnacly/libjson` [package
api](https://pkg.go.dev/github.com/xnacly/libjson).

[^performance]:
    1.4ms slower for 1MB inputs, 7.9ms slower for 5MB and 13ms
    slower for 10MB (on my machine, see
    [Benchmarks](https://github.com/xNaCly/libjson?tab=readme-ov-file#benchmarks))

Consider the following example:

```go
type Structure struct {
    Field []float64
}
var s Structure
input := []byte(`{ "field": [1, 2]}`)
if err := json.Unmarshal(input, &s); err != nil {
    panic(err)
}
fmt.Println(s.Field[1])
```

The `encoding/json` package would use reflection to map JSON key-value pairs to
the correct fields of the structure. I wanted to skip this and just thought to
myself, why not make the access of the JavaScript Object Notation just as we
would with JavaScript - so I did just that, you can be the judge whether it
fits into go.

```go
obj, err := libjson.New(`{ "field": [1, 2]}`)
if err != nil {
    panic(err)
}
out, err := libjson.Get[[]float64](obj, ".field")
if err != nil {
    panic(err)
}
fmt.Println(out)
```

{{<callout type="Tip">}}
Please do not mind the toplevel function `libjson.Get` to access values from an
object, go does not support generics for methods of a non generic struct, so I
had to implement it like this.
{{</callout>}}

The downside of my implementation is twofold:

1. access is slower, because `libjson.Get` computes the access, while
   `struct.field` is very fast and can be optimised by the go compiler - I plan
   to implement `libjson.Compile` to mitigate this
2. a second potential error cause, specifically the object access can fail, if
   the types do not match or the field can not be accessed.

## JSONTestSuite Project

I stumbled upon the [JSONTestSuite](https://github.com/nst/JSONTestSuite)
project - the project prides itself with being

> A comprehensive test suite for RFC 8259 compliant JSON parsers

So i wanted to test my parser against it, because up until now I simply read
the RFC and decided its easiest to support all floating point integers the
`strconv` package supports. If i remember correctly, my lexer does not even
support escaping quotes (`"`). Adding the parser to the project was fairly
easy, see [xnacly/JSONTestSuite
a20fc56](https://github.com/xNaCly/JSONTestSuite/commit/a20fc5621c82f07f42b19548bee86c41afe79077),
so I ran the suite and was promply surprised with a lot of passing tests and a
lot of tests that were not passing.

Exactly 35 passing and 43 not passing, a good 45% are already passing, thats a
good quota. Below an image with all tests that should fail and didn't.

![legend](/libjson/legend.png)
![failing tests](/libjson/failing_tests.png)

Lets define a test function and work through each and every case:

```go
func TestStandardFail(t *testing.T) {
	input := []string{
		`{"a":"b"}/**/`,
	}
	for _, i := range input {
		t.Run(i, func(t *testing.T) {
			p := parser{l: lexer{r: bufio.NewReader(strings.NewReader(i))}}
			_, err := p.parse()
			assert.Error(t, err)
		})
	}
}
```

libjson has a lot of tests already, thus i will narrow our tests down to only `TestStandardFail`:

```text
libjson master M :: go test ./... -run=StandardFail -v
?       github.com/xnacly/libjson/cmd   [no test files]
?       github.com/xnacly/libjson/test  [no test files]
=== RUN   TestStandardFail
=== RUN   TestStandardFail/{"a":"b"}/**/
    object_test.go:63:
                Error Trace:    /home/teo/programming/libjson/object_test.go:63
                Error:          An error is expected but got nil.
                Test:           TestStandardFail/{"a":"b"}/**/
--- FAIL: TestStandardFail (0.00s)
    --- FAIL: TestStandardFail/{"a":"b"}/**/ (0.00s)
FAIL
FAIL    github.com/xnacly/libjson       0.002s
FAIL
```

Ill append this blog every once in a while if I have time and wil republish it :), below is my first day

### Day 1 - Objects and trash

I don't care about cases with numbers, simply because `strconv` does my number
parsing. I also will merge similar cases, thus i will start with the first five
comment and thrash tests, and you can read about how I fixed each and every
case:

```go
func TestStandardFail(t *testing.T) {
	input := []string{
		`{"a":"b"}/**/`,
		`{"a":"b"}/**//`,
		`{"a":"b"}//`,
		`{"a":"b"}/`,
		`{"a":"b"}#`,
	}
	for _, i := range input {
		t.Run(i, func(t *testing.T) {
			p := parser{l: lexer{r: bufio.NewReader(strings.NewReader(i))}}
			_, err := p.parse()
			assert.Error(t, err)
		})
	}
}
```

All of these fail:

```text
--- FAIL: TestStandardFail (0.00s)
    --- FAIL: TestStandardFail/{"a":"b"}/**/ (0.00s)
    --- FAIL: TestStandardFail/{"a":"b"}/**// (0.00s)
    --- FAIL: TestStandardFail/{"a":"b"}// (0.00s)
    --- FAIL: TestStandardFail/{"a":"b"}/ (0.00s)
    --- FAIL: TestStandardFail/{"a":"b"}# (0.00s)
FAIL
FAIL    github.com/xnacly/libjson       0.002s
FAIL
```

Lets figure out why these do not fail, as they should. The first step is to
take a look at the tokens generated by the lexer, for this I simply log them
once the parser requests them in the `(*parser).advance()` function in the
`parser.go` file:

```go
func (p *parser) advance() error {
	t, err := p.l.next()
	fmt.Printf("|type=%-6s|value=%-5s|err=%q\n", tokennames[t.Type], string(t.Val), err)
	p.t = t
	if p.t.Type == t_eof {
		return nil
	}
	return err
}
```

`tokenname` is a hashmap in the `types.go` file mapping the token types
returned by the lexer to their names, this really helps with debugging, believe
me:

```go
var tokennames = map[t_json]string{
	t_string:       "string",
	t_number:       "number",
	t_true:         "true",
	t_false:        "false",
	t_null:         "null",
	t_left_curly:   "{",
	t_right_curly:  "}",
	t_left_braket:  "[",
	t_right_braket: "]",
	t_comma:        ",",
	t_colon:        ":",
	t_eof:          "EOF",
}
```

Anyways, executing our first test again we can clearly see there are no more
tokens requested after the closing curly brace, but there is an error the
parser simply not passes up the chain.

```text
=== RUN   TestStandardFail
=== RUN   TestStandardFail/{"a":"b"}/**/
|type={     |value=     |err=%!q(<nil>)
|type=string|value=a    |err=%!q(<nil>)
|type=:     |value=     |err=%!q(<nil>)
|type=string|value=b    |err=%!q(<nil>)
|type=}     |value=     |err=%!q(<nil>)
|type=EOF   |value=     |err="Unexpected character '/' at this position."
    object_test.go:70:
                Error Trace:    /home/teo/programming/libjson/object_test.go:70
                Error:          An error is expected but got nil.
                Test:           TestStandardFail/{"a":"b"}/**/
--- FAIL: TestStandardFail (0.00s)
    --- FAIL: TestStandardFail/{"a":"b"}/**/ (0.00s)
FAIL
FAIL    github.com/xnacly/libjson       0.002s
FAIL
```

This is because the `(*parser).advance()` function returns nil if the token is
`t_eof` to handle the case of the input ending. We have to add another
condition to this if, specifically add `&& err != nil` to check if the input is
really done or we have an error from the lexer.

```go
func (p *parser) advance() error {
	t, err := p.l.next()
	p.t = t
	if p.t.Type == t_eof && err != nil {
		return err
	}
	return nil
}
```

This makes not only the first test pass, but all of them:

```text
libjson master M :: go test ./... -run=StandardFail -v
?       github.com/xnacly/libjson/cmd   [no test files]
?       github.com/xnacly/libjson/test  [no test files]
=== RUN   TestStandardFail
=== RUN   TestStandardFail/{"a":"b"}/**/
=== RUN   TestStandardFail/{"a":"b"}/**//
=== RUN   TestStandardFail/{"a":"b"}//
=== RUN   TestStandardFail/{"a":"b"}/
=== RUN   TestStandardFail/{"a":"b"}#
--- PASS: TestStandardFail (0.00s)
    --- PASS: TestStandardFail/{"a":"b"}/**/ (0.00s)
    --- PASS: TestStandardFail/{"a":"b"}/**// (0.00s)
    --- PASS: TestStandardFail/{"a":"b"}// (0.00s)
    --- PASS: TestStandardFail/{"a":"b"}/ (0.00s)
    --- PASS: TestStandardFail/{"a":"b"}# (0.00s)
PASS
ok      github.com/xnacly/libjson       0.002s
```
