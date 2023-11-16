---
title: "Tokenizing Arithmetic expressions - calculator p.1"
summary: "In depth explaination around writing a simple interpreter"
date: 2023-10-16
tags:
  - go
  - bytecode-series
---

## Introduction

This is the first post of a four part series around implementing and
understanding the steps for interpreting [arithmetic
expressions](https://en.wikipedia.org/wiki/Arithmetic). The series is meant for
explaining key concepts such as [lexical
analysis](https://en.wikipedia.org/wiki/Lexical_analysis), parsing / building
the [ast](https://en.wikipedia.org/wiki/Abstract_syntax_tree), walking the ast
/ flatting it to byte code, [bytecode virtual
machines](https://en.wikipedia.org/wiki/Bytecode) and
[TDD](https://en.wikipedia.org/wiki/Test-driven_development) centered around
compilers and interpreters.

{{<callout type="Info">}}
The corresponding GitHub repository can be found [here](https://github.com/xNaCly/calculator).
{{</callout>}}

1. This first article contains the introduction to our problem domain, the setup
   of our project, the basics of TDD and the first steps towards interpreting
   arithmetic expressions: tokenizing our input / performing lexical analysis

2. The second article will be centered around converting the list of tokens we
   created in the first article to an abstract syntax tree, short ast

3. The third article will be focused on walking the abstract syntax tree and
   converting nodes into a list of instructions for our virtual machine

4. The fourth and last article will be consisting of implementing the bytecode
   virtual machine and executing expressions compiled to bytecode

All posts in this series will include an extensive amount of resources for the
readers deeper understanding of the matter. The following books and articles
are commonly referenced in the compiler and interpreter space:

- [Writing An Interpreter in Go by Thorsten Ball](https://interpreterbook.com/)
  (go) - TDD, scratches the surface
- [Crafting Interpreters by Robert Nystrom](https://craftinginterpreters.com/)
  (java & c) - very detailed, includes data structures and in depth topics,
  such as grammars, hashing, etc
- [Compilers: Principles, Techniques, and
  Tools](https://en.wikipedia.org/wiki/Compilers:_Principles,_Techniques,_and_Tools)
  (java) - very theoretic

We will be using the [go programming language](https://go.dev/) in this series.
All concepts can be applied to any programming language. Some level of
proficiency with go is assumed, I will not explain syntax.

## Problem domain

The expression we want to be able to execute with our interpreter is the
smallest subset of a programming language i could imagine thus our problem
domain is defined by a subset of arithmetic expressions:

- addition
- subtraction
- multiplication
- division

We will also support braces that can be used to indicate precedence, which we
will talk about in the second post of this series.

### Expressions

Some examples of expression we will accept:

```python
# comments

# addition
1029+0.129
# =1029.129

# subtraction
5_120_129-5_120_128
# =1

# multiplication
5e12*3
# =150000

# division
1/2
# =0.5

# braces
(1+1)/2
# =1
```

## Interpreter design

There are several well established ways of interpreting programming languages.
Lets take a look at the stages an interpreter commonly performs before the
passed in source code is interpreted.

### Interpreter Stages

1. **Lexical analysis** -> the process of recognizing structures such as
   numbers, identifiers or symbols in the source code , converts recognized
   structures into a list of token, often referred to as _scanning_, _lexing_
   or _tokenizing_.

2. **Parsing** -> refers to the process of detecting precedence and checking
   whether the input conforms to the defined grammar. In our case the parser
   analyses the output of our previous stage and builds an abstract syntax tree
   while taking operator precedence into account.

3. **Evaluating** -> commonly means walking the tree starting from the leafs,
   computing a value for each node and exiting on computing the value of the
   root, see [tree walk interpreter](). While this is the simplest way to
   implement an interpreter, it introduces performance issues due to requiring
   recursion and the overhead of traversing many pointers. There are [multiple
   ways of implementing this
   step](<https://en.wikipedia.org/wiki/Interpreter_(computing)#Variations>),
   each one with different pros and cons:
   - [Tree walk / Abstract syntax tree
     interpreters](https://en.wikipedia.org/wiki/Abstract_syntax_tree): too
     slow, too much overhead
   - [Just-in-time
     compiler](https://en.wikipedia.org/wiki/Just-in-time_compilation): too
     complex / too hard to implement
   - [bytecode interpreter](https://en.wikipedia.org/wiki/Bytecode): medium
     hard to implement, faster than tree walk interpreter

For our interpreter we decide to use the idea of bytecode interpreters, thus
splitting the third step into two sub steps::

1. **Compiling to bytecode** -> Walking the tree and compiling each node into bytecode
2. **Executing bytecode** -> Iterating over the list of bytecode instructions and executing them

### Example

Consider the following statement and lets visualize the stages using the example:

```python
1.025*3+1
```

#### Lexical analysis

Performing the first stage converts the input from a character stream into a
list of structures:

```go
token := []Token{
    Token{Type: NUMBER, Raw: "1.025"},
    Token{Type: ASTERIKS, Raw: "*"},
    Token{Type: NUMBER, Raw: "3"},
    Token{Type: PLUS, Raw: "+"},
    Token{Type: NUMBER, Raw: "3"},
}
```

#### Parsing

We now build an abstract syntax tree out of the list of token we get from the previous stage:

```go
ast := Addition{
    Token: Token{Type: PLUS, Raw: "+"},
    Left: Multiplication{
        Token: Token{Type: ASTERIKS, Raw: "*"},
        Left: Number{
            Token: Token{Type: NUMBER, Raw: "1.025"},
        },
        Right: Number{
            Token: Token{Type: NUMBER, Raw: "3"}
        },
    },
    Right: Number{Token: NUMBER, Raw: "1"},
}
```

Notice the depth of the tree, the deeper the node sits the earlier it is
compiled to bytecode, thus considering operator precedence, see below for a
visual explanation:

1. Initial ast

   ```text
   +
   │
   ├─ 1
   │
   └─ *
      │
      ├─ 1.025
      │
      └─ 3
   ```

2. `Multiplication` evaluated:

   ```text
   +
   │
   ├─ 1
   │
   └─ 3.075
   ```

3. `Addition` evaluated:

   ```text
   4.075
   ```

#### Compiling to bytecode

We use the AST we got from the previous step to compile each node to a list of
bytecode instructions. The bottom most node, commonly referred to as leafs are
all numbers, thus we will start there.

The bytecode VM we want to implement has a list of registers, comparable to the
CPU registers on a real machine. We can load and manipulate values in these
registers. In the third and fourth part of this series, we will go into great
depth on registers, bytecode and virtual machines. For now simply know there
are registers, we can manipulate them, our VM accepts an instruction and an
argument.

Lets now take a look at the bytecode our previous example compiles to:

```asm
;; multiplication
    ;; loading 1.025 into register 0
    OP_LOAD    :: 1.025000
    ;; moving 1.025 from register 0 to register 1
    OP_STORE   :: 1.000000

    ;; loading 3 into register 0
    OP_LOAD    :: 3.000000
    ;; multiplying the value of register 0
    ;; with the value of register 1
    OP_MULTIPY :: 1.000000

    ;; storing the result of the
    ;; multiplication in register 1
    OP_STORE   :: 1.000000

;; addition
    ;; loading 1 into register 0
    OP_LOAD    :: 1.000000
    ;; adding the value of register 1
    ;; to the value of register 0
    OP_ADD     :: 1.000000
```

The left hand side of each line is the operation the virtual machine is
executing, the right hand side is the argument of the operation, sides are
separated with `::`.

This should suffice as a high level overview over the steps we want to take
until we reach the integer result of our expression, starting from the source
code, tokenizing, parsing, compiling and executing bytecode.

## Project setup

{{<callout type="Tip">}}
All code snippets used in this series start with a comment specifying the file
it points to. Code not relevant to the current topic is omitted but still
notated using `[...]`.

```go
// main.go
package main

// [...]

func main() { }
```

If a new file should be created it will be explicitly stated.

Code snippets starting with a `$` must be executed in a shell:

```text
$ echo "This is a shell"
```

{{</callout>}}

1. Creating a directory for our project:

   ```text
   $ mkdir calc
   ```

2. Entry point

   Using go we can start with the bare minimum a project requires:

   ```go
   // main.go
   package main

   import "fmt"

   func main() {
       fmt.Println("Hello World!")
   }
   ```

   Running the above via `go run .` requires the creation of the projects
   `go.mod` file:

3. Initialising the project

   ```text
   $ go mod init calc
   ```

4. Building and running the source code

   ```text
   $ go run .
   Hello World!
   ```

All of our source code will live in the root of the project. Currently we have
`main.go` and `go.mod` in the root of our project.

## Test driven development

{{<callout type="Info">}}
Test driven development refers to the process of defining a problem domain for
a function, creating the corresponding test, preferably with as much edge cases
as possible and incrementing the implementation of the function to satisfy all
test cases.
{{</callout>}}

As we are implementing an interpreter both the input to our function and the
output of our function is known and therefore easily representable with tests
which screams we should use TDD and iterate until all tests are passing. We
will create our tests once we defined the different kinds a token can represent
and the `Token` structure.

## Tokenising

Leaving the above behind, lets now get to the gist of this part of the series:
the tokeniser. Our main goal is to step through the source code we input and
convert it to different tokens and afterwards spitting out this list of tokens.

Lets get started, create a new file in the projects directory, beside `main.go`
and `go.sum` called `lexer.go`:

```go
// lexer.go
package main

import (
	"bufio"
	"io"
	"log"
	"strings"
)
```

For now this will be enough, we will fill this file with content in the
following sections.

### Token and Types of Token

In the classical sense a lexical token refers to a list of characters with an
assigned meaning, see [lexical token and lexical
tokenisation](https://en.wikipedia.org/wiki/Lexical_analysis#Lexical_token_and_lexical_tokenization)
and remember the first step of the [example](#lexical-analysis).

To define the meaning we attach to this list of characters we will define a
list of possible meanings we want to support in our interpreter, remember our
[problem domain](#problem-domain).

```go
// lexer.go
package main

const (
    TOKEN_UNKNOWN = iota + 1

    TOKEN_NUMBER

    // symbols
	TOKEN_PLUS
	TOKEN_MINUS
	TOKEN_ASTERISK
	TOKEN_SLASH

    // structure
	TOKEN_BRACE_LEFT
	TOKEN_BRACE_RIGHT

	TOKEN_EOF
)
```

{{<callout type="Iota - the Go way of doing enums">}}
Go does not have enums, it has `iota`, see the go spec
[here](https://go.dev/ref/spec#Iota). Its not a particularly good system but
its good enough for our use case - it basically increments all consts by 1 in a
const block starting from 0. Therefore `TOKEN_UNKNOWN` is set to 1 and
`TOKEN_EOF` to 9.
{{</callout>}}

We will now define the structure holding the detected structure, its type and its raw value:

```go
// lexer.go
package main

// [...] token kind definition

type Token struct {
    Type int
    Raw  string
}
```

We defined the structure to hold tokens we found in the source code and their types.

### Tests

Now lets get started with writing tests. Per [go
convention](https://pkg.go.dev/testing) we create a new file postfixed with
`_test.go`. This `lexer_test.go` file contains all tests for the tokeniser and
exists beside all previously created files in the root of the directory.

So lets create the foundation for our tests - we will make use of an idea
called [table driven
tests](https://dave.cheney.net/2019/05/07/prefer-table-driven-tests):

```go
// lexer_test.go
package main

import (
    "testing"
    "strings"

    "github.com/stretchr/testify/assert"
)

func TestLexer(t *testing.T) {
    tests := []struct{
        Name string
        In   string
        Out  []Token
    }{}
    for _, test := range tests {
        t.Run(test.Name, func(t *testing.T) {
            in := strings.NewReader(test.In)
			out := NewLexer(in).Lex()
            assert.EqualValues(t, test.Out, out)
        })
    }
}
```

We use the `assert.EqualValues` function to compare our expected and the actual
resulting arrays.

{{<callout type="Tip">}}
Including external packages in our project is a simple as running the following command:

```text
$ go get <repo>
```

For our example we want the `github.com/stretchr/testify/assert` package, thus we execute:

```text
$ go get github.com/stretchr/testify/assert
```

{{</callout>}}

Lets add our first test - an edge case - specifically the case of an empty
input for which we expect only one structure `Token` with `Token.Type:
TOKEN_EOF` in the resulting token list.

```go {hl_lines=["17-23"]}
// lexer_test.go
package main

import (
    "testing"
    "strings"

    "github.com/stretchr/testify/assert"
)

func TestLexer(t *testing.T) {
    tests := []struct{
        Name string
        In   string
        Out  []Token
    }{
        {
            Name: "empty input",
            In: "",
            Out: []Token{
                {Type: TOKEN_EOF, Raw: "TOKEN_EOF"},
            },
        },
    }
    for _, test := range tests {
        t.Run(test.Name, func(t *testing.T) {
            in := strings.NewReader(test.In)
			out := NewLexer(in).Lex()
            assert.EqualValues(t, test.Out, out)
        })
    }
}
```

Running our tests with `go test ./... -v` will result in an error simply
because we have not yet defined our Lexer:

```text
$ go test ./... -v
# calc [calc.test]
./lexer_test.go:35:11: undefined: NewLexer
FAIL    calc [build failed]
FAIL
```

### Debugging

If we try to print our `Token` structure we will see the `Token.Type` as an
integer, for example:

```go
package main

func main() {
    t := Token{Type: TOKEN_NUMBER, Raw: "12"}
    fmt.Printf("Token{Type: %d, Raw: %s}\n", t.Type, t.Raw)
}
```

This would of course not result in the output we want, due to the enum defining
token types as integers:

```text
$ go run .
Token{Type: 2, Raw: 12}
```

Therefore we add the `TOKEN_LOOKUP` hash map:

```go
// lexer.go
package main

// [...] imports

// [...] token types generation

var TOKEN_LOOKUP = map[int]string{
	TOKEN_UNKNOWN:     "UNKNOWN",
	TOKEN_NUMBER:      "TOKEN_NUMBER",
	TOKEN_PLUS:        "TOKEN_PLUS",
	TOKEN_MINUS:       "TOKEN_MINUS",
	TOKEN_ASTERISK:    "TOKEN_ASTERISK",
	TOKEN_SLASH:       "TOKEN_SLASH",
	TOKEN_BRACE_LEFT:  "TOKEN_BRACE_LEFT",
	TOKEN_BRACE_RIGHT: "TOKEN_BRACE_RIGHT",
	TOKEN_EOF:         "EOF",
}
```

{{<callout type="Tip">}}
With vim the above is extremely easy to generate, simply copy the before defined
types of tokens, paste them into the map, remove `= iota +1`, white space and
comments. Afterwards mark them again with `Shift+v`. Now regex all over the
place by typing `:'<,'>s/\([A-Z_]\+\)/\1: "\1",`, this creates a capture group
for all upper case characters found one or more times, this group is reused in
the substitute replace part of the command (second part of the command,
infix split by `/`) and replaces all `\1` with the captured name, thus
filling the map.
{{</callout>}}

If we were to now update our previous example to using the new `TOKEN_LOOKUP`
map we notice it now works correctly:

```go
package main

import "fmt"

func main() {
	t := Token{Type: TOKEN_NUMBER, Raw: "12"}
	fmt.Printf("Token{Type: %s, Raw: %s}\n", TOKEN_LOOKUP[t.Type], t.Raw)
}
```

```text
$ go run .
Token{Type: TOKEN_NUMBER, Raw: 12}
```

### Lexer overview

After establishing our debug capabilities we now can move on to creating the
`Lexer` and defining our tokenisers API:

```go
// lexer.go
package main

// [...] Imports, token types, token struct, TOKEN_LOOKUP map

type Lexer struct {
	scanner bufio.Reader
	cur     rune
}

func NewLexer(reader io.Reader) *Lexer { }

func (l *Lexer) Lex() []Token { }

func (l *Lexer) number() Token { }

func (l *Lexer) advance() { }
```

The `Lexer` structure holds a scanner we will create in the `NewLexer` function
this function accepts an unbuffered reader which we will wrap into a buffered
reader for stepping trough the source in an optimized fashion. The function
returns a Lexer structure. The `cur` field holds the current character.

The heart of the tokeniser is the `Lexer.Lex` method. It iterates over all
characters in the buffered reader and tries to recognize structures.

The `Lexer.number` method is called when an number is detected, it then
iterates until the current character is no longer a part of a number and
returns a `Token` structure.

`Lexer.advance` requests the next character from the buffered scanner and sets
`Lexer.cur` to the resulting character.

{{<callout type="Tip">}}

#### Definitions

- Method vs function -> I refer to standalone functions as functions - to
  functions attached to structures as methods Thus `NewLexer` is a function and
  `Lexer.Lex` is a method. But to each their own - I don't really care 😼.

- Number vs integer vs digit -> Here I define a number as 1 or more characters
  between 0 and 9, I extend this definition with `e`, `.` and `_` in between
  the first number and all following numbers. Thus I consider the following numbers as valid for this interpreter:
  - `1e5`
  - `12.5`
  - `0.5`
  - `5_000_000`

{{</callout>}}

### Creating the lexer

As introduced before the `NewLexer` function creates the lexer:

```go
// lexer.go
package main

// [...] Imports, token types, token struct, TOKEN_LOOKUP map

type Lexer struct {
	scanner bufio.Reader
	cur     rune
}

func NewLexer(reader io.Reader) *Lexer {
	l := &Lexer{
		scanner: *bufio.NewReader(reader),
	}
	l.advance()
	return l
}
```

This function accepts a reader, creates a new `Lexer` structure, converts the
reader to a [buffered `Reader`](https://pkg.go.dev/bufio#Reader), assigns it to
the `Lexer` structure and afterwards invokes the `Lexer.advance` function we
will discuss in the next chapter.

### Advancing in the Input

Stepping through the source code is as easy as requesting a new character from
our buffered reader via the `bufio.Reader.ReadRune()` method:

```go
// lexer.go
package main

// [...]

func (l *Lexer) advance() {
	r, _, err := l.scanner.ReadRune()
	if err != nil {
        l.cur = 0
    } else {
        l.cur = r
    }
}
```

The `ReadRune` function returns an error once the end of the file is hit, to
indicate this to our `Lexer.Lex` function we will set the `Lexer.cur` field to
`0`.

{{<callout type="Tip">}}
End of file is often referred to as `EOF`.
{{</callout>}}

We will now focus on the heart of the tokeniser: `Lexer.Lex()`:

```go
// lexer.go
package main

// [...]

func (l *Lexer) Lex() []Token {
	t := make([]Token, 0)
	for l.cur != 0 {
        l.advance()
	}
	t = append(t, Token{
		Type: TOKEN_EOF,
		Raw:  "TOKEN_EOF",
	})
	return t
}
```

We firstly create a new slice of type `[]Token`, we will fill with tokens we
find while stepping through the source code. The while loop iterates until we
hit the `EOF` by calling `*Lexer.advance()`. To indicate the ending of our
token list we append a token of type `TOKEN_EOF` to the slice `t`.

After defining the `NewLexer` and the `*Lexer.Lex` we can try running our tests
again:

```text
$ go test ./... -v
=== RUN   TestLexer
=== RUN   TestLexer/empty_input
--- PASS: TestLexer (0.00s)
    --- PASS: TestLexer/empty_input (0.00s)
PASS
ok      calc    0.002s
```

Thus we know our lexer works correctly for empty inputs.

### Ignoring white space

Every good programming language ignores white space and so do we (looking at
you [Python](https://peps.python.org/pep-0008/#code-lay-out)). White space is
commonly defined as a new line: `'\n'` / `'\r'`, a tab `'\t'` or a space `' '`.

Lets add a new test case called `whitespace` to our white space tests:

```go{hl_lines=["13-19"]}
// lexer_test.go
package main

// [...]

func TestLexer(t *testing.T) {
	tests := []struct {
		Name string
		In   string
		Out  []Token
	}{
        // [...]
		{
			Name: "whitespace",
			In:   "\r\n\t             ",
			Out: []Token{
				{TOKEN_EOF, "TOKEN_EOF"},
			},
		},
	}
    // [...]
}
```

Having defined what we want as the output, lets get started with ignoring white space:

To check if the current character matches any of the above we introduce
a [switch case statement](https://go.dev/tour/flowcontrol/9):

```go{hl_lines=["9-13"]}
// lexer.go
package main

// [...]

func (l *Lexer) Lex() []Token {
	t := make([]Token, 0)
	for l.cur != 0 {
		switch l.cur {
		case ' ', '\n', '\t', '\r':
			l.advance()
			continue
        }

        l.advance()
	}
	t = append(t, Token{
		Type: TOKEN_EOF,
		Raw:  "TOKEN_EOF",
	})
	return t
}
```

Lets run our tests and check if everything worked out the way we wanted it to:

```text
$ go test ./... -v
=== RUN   TestLexer
=== RUN   TestLexer/empty_input
=== RUN   TestLexer/whitespace
--- PASS: TestLexer (0.00s)
    --- PASS: TestLexer/empty_input (0.00s)
    --- PASS: TestLexer/whitespace (0.00s)
PASS
ok      calc    0.001s
```

Seems like we ignored whitespace the right way 😼.

### Support for comments

Lets add a very similar test as we added in the previous chapter to check if we ignore comments correctly:

```go{hl_lines=["13-19"]}
// lexer_test.go
package main

// [...]

func TestLexer(t *testing.T) {
	tests := []struct {
		Name string
		In   string
		Out  []Token
	}{
        // [...]
		{
			Name: "comment",
			In:   "# this is a comment\n# this is a comment without a newline at the end",
			Out: []Token{
				{TOKEN_EOF, "TOKEN_EOF"},
			},
		},
	}
    // [...]
}
```

To ignore comments, we add a new case to our switch statement:

```go{hl_lines=["10-14"]}
// lexer.go
package main

// [...]

func (l *Lexer) Lex() []Token {
    // [...]
	for l.cur != 0 {
		switch l.cur {
        case '#':
			for l.cur != '\n' && l.cur != 0 {
				l.advance()
			}
			continue
		case ' ', '\n', '\t', '\r':
			l.advance()
			continue
		}
		l.advance()
	}
    // [...]
}
```

We want our comments to start with `#`, therefore we enter the case if the
current character is a `#`. Once in the case we call `*Lexer.advance()` until
we either hit a newline or `EOF` - both causing the loop to stop.

Lets again run our tests:

```text
$ go test ./... -v
=== RUN   TestLexer
=== RUN   TestLexer/empty_input
=== RUN   TestLexer/whitespace
=== RUN   TestLexer/comment
--- PASS: TestLexer (0.00s)
    --- PASS: TestLexer/empty_input (0.00s)
    --- PASS: TestLexer/whitespace (0.00s)
    --- PASS: TestLexer/comment (0.00s)
PASS
ok      calc    0.001s
```

### Detecting special symbols

Having added tests for empty input, ignoring white space and comments, we will
now add a new test for the symbols we want to recognize in out input:

```go{hl_lines=["14-26"]}
// lexer_test.go
package main


// [...]

func TestLexer(t *testing.T) {
	tests := []struct {
		Name string
		In   string
		Out  []Token
	}{
        // [...]
        {
			Name: "symbols",
			In:   "+-/*()",
			Out: []Token{
				{TOKEN_PLUS, "+"},
				{TOKEN_MINUS, "-"},
				{TOKEN_SLASH, "/"},
				{TOKEN_ASTERISK, "*"},
				{TOKEN_BRACE_LEFT, "("},
				{TOKEN_BRACE_RIGHT, ")"},
				{TOKEN_EOF, "TOKEN_EOF"},
			},
		},
	}
    // [...]
}
```

Running our tests including the above at the current state of out
implementation will result in the following `assert` Error:

```text
$ go test ./...
--- FAIL: TestLexer (0.00s)
    --- FAIL: TestLexer/symbols (0.00s)
        lexer_test.go:56:
                Error Trace:    ./lexer_test.go:56
                Error:          Not equal:
                                expected: []main.Token{main.Token{Type:3, Raw:"+"}, main.Token{Type:4, Raw:"-"}, main.Token{Type:6, Raw:"/"}, main.Token{Type:5, Raw:"*"}, main.Token{Type:7, Raw:"("}, main.Token{Type:8, Raw:")"}, main.Token{Type:9, Raw:"TOKEN_EOF"}}
                                actual  : []main.Token{main.Token{Type:9, Raw:"TOKEN_EOF"}}
// [...]
                Test:           TestLexer/symbols
FAIL
FAIL    calc    0.004s
FAIL
```

Implementing support for the symbols we want should fix this issue.

Our first step towards this goal is to define a new variable called `ttype`
holding the type of token we recognized:

```go{hl_lines=["10"]}
// lexer.go
package main

// [...]

func (l *Lexer) Lex() []Token {
    // [...]
	for l.cur != 0 {
        // [...]
        ttype := TOKEN_UNKNOWN
        // [...]
		l.advance()
	}
    // [...]
}
```

We use this variable to insert detected tokens into our `t` array, if the value
of `ttype` didn't change and is still `TOKEN_UNKNOWN` we display an error and exit:

```go{hl_lines=["16-23"]}
// lexer.go
package main

import (
    // [...]
    "log"
)
// [...]

func (l *Lexer) Lex() []Token {
    // [...]
	for l.cur != 0 {
        // [...]
        ttype := TOKEN_UNKNOWN
        // [...]
		if ttype != TOKEN_UNKNOWN {
			t = append(t, Token{
				Type: ttype,
				Raw:  string(l.cur),
			})
		} else {
			log.Fatalf("unknown %q in input", l.cur)
		}

		l.advance()
	}
    // [...]
}
```

For now this concludes our error handling, not great - i know. Our next step is
to add cases to our switch to react to differing characters:

```go{hl_lines=["12-23"]}
// lexer.go
package main

// [...]

func (l *Lexer) Lex() []Token {
    // [...]
	for l.cur != 0 {
        // [...]
		switch l.cur {
            // [...]
        case '+':
			ttype = TOKEN_PLUS
		case '-':
			ttype = TOKEN_MINUS
		case '/':
			ttype = TOKEN_SLASH
		case '*':
			ttype = TOKEN_ASTERISK
		case '(':
			ttype = TOKEN_BRACE_LEFT
		case ')':
			ttype = TOKEN_BRACE_RIGHT
        }
        // [...]
		l.advance()
	}
    // [...]
}
```

We can now once again run our tests:

```text
$ go test ./... -v
calc master M :: go test ./... -v
=== RUN   TestLexer
=== RUN   TestLexer/empty_input
=== RUN   TestLexer/whitespace
=== RUN   TestLexer/comment
=== RUN   TestLexer/symbols
--- PASS: TestLexer (0.00s)
    --- PASS: TestLexer/empty_input (0.00s)
    --- PASS: TestLexer/whitespace (0.00s)
    --- PASS: TestLexer/comment (0.00s)
    --- PASS: TestLexer/symbols (0.00s)
PASS
ok      calc    0.003s
```

And we pass our tests, the only feature missing from our tokeniser is detecting
numbers.

### Support for integers and floating point numbers

As introduced before i want to support numbers with several infixes, such as `_`, `e` and `.`.

Go ahead and add some tests for these cases:

```go
// lexer_test.go
package main


// [...]

func TestLexer(t *testing.T) {
	tests := []struct {
		Name string
		In   string
		Out  []Token
	}{
        // [...]
        {
			Name: "number",
			In:   "123",
			Out: []Token{
				{TOKEN_NUMBER, "123"},
				{TOKEN_EOF, "TOKEN_EOF"},
			},
		},
		{
			Name: "number with underscore",
			In:   "10_000",
			Out: []Token{
				{TOKEN_NUMBER, "10_000"},
				{TOKEN_EOF, "TOKEN_EOF"},
			},
		},
		{
			Name: "number with e",
			In:   "10e5",
			Out: []Token{
				{TOKEN_NUMBER, "10e5"},
				{TOKEN_EOF, "TOKEN_EOF"},
			},
		},
		{
			Name: "number with .",
			In:   "0.005",
			Out: []Token{
				{TOKEN_NUMBER, "0.005"},
				{TOKEN_EOF, "TOKEN_EOF"},
			},
		},
	}
    // [...]
}
```

Lets add a `default`-case to our switch statement:

```go{hl_lines=["12-15"]}
// lexer.go
package main

// [...]

func (l *Lexer) Lex() []Token {
    // [...]
	for l.cur != 0 {
        // [...]
		switch l.cur {
            // [...]
        default:
			if (l.cur >= '0' && l.cur <= '9') || l.cur == '.' {
				t = append(t, l.number())
				continue
			}
        }
        // [...]
	}
    // [...]
}
```

As one should notice we have yet to define the `*Lexer.number` function:

```go
// lexer.go
package main

// [...]

func (l *Lexer) number() Token {
	b := strings.Builder{}
	for (l.cur >= '0' && l.cur <= '9') || l.cur == '.' || l.cur == '_' || l.cur == 'e' {
		b.WriteRune(l.cur)
		l.advance()
	}
	return Token{
		Raw:  b.String(),
		Type: TOKEN_NUMBER,
	}
}
```

The function makes use of the `strings.Builder` structure. This is used to omit
copying the string which we would have to do if we simply used `string+string`.
We iterate while our character matches what we want and write to the
`strings.Builder` structure. Upon hitting a character we do not accept the loop
stops and the function returns a `Token`-Structure with the result of the
`strings.Builder` we defined and wrote to previously.

Combining the previously added `default`-case and our new `*Lexer.number()`
function we added support for numbers starting with `0-9` or `.`. We support
infixes such as `_`, `.`, `_` and `e` - exactly matching our test cases, thus
we can now once again check if our tests pass:

```text{hl_lines=["6-9", "15-18"]}
=== RUN   TestLexer
=== RUN   TestLexer/empty_input
=== RUN   TestLexer/whitespace
=== RUN   TestLexer/comment
=== RUN   TestLexer/symbols
=== RUN   TestLexer/number
=== RUN   TestLexer/number_with_underscore
=== RUN   TestLexer/number_with_e
=== RUN   TestLexer/number_with_.
--- PASS: TestLexer (0.00s)
    --- PASS: TestLexer/empty_input (0.00s)
    --- PASS: TestLexer/whitespace (0.00s)
    --- PASS: TestLexer/comment (0.00s)
    --- PASS: TestLexer/symbols (0.00s)
    --- PASS: TestLexer/number (0.00s)
    --- PASS: TestLexer/number_with_underscore (0.00s)
    --- PASS: TestLexer/number_with_e (0.00s)
    --- PASS: TestLexer/number_with_. (0.00s)
PASS
ok      calc    0.003s
```

## Calling our Tokeniser

Out tests pass - we can finally move on to my favorite part of every
programming project: passing input via the command line to our program and
seeing the output. Doing so requires some packages. We need `os` to access the
command line arguments our program was called with, we need `strings` to create
a `io.Reader` for the parameter our tokeniser requires. Furthermore we include
the `log` package and promptly disable all prefixes, timestamps, etc. by
invoking `log.SetFlags` with 0 as the argument.

```go
package main

import (
	"log"
	"os"
	"strings"
)

func main() {
    log.SetFlags(0)
	if len(os.Args) != 2 {
		log.Fatalln("missing input")
	}

	input := os.Args[1]

	token := NewLexer(strings.NewReader(input)).Lex()
}
```

{{<callout type="Tip">}}
When an executable build with go is started it can access the arguments passed to it via the `os.Args` slice:

```go
// main.go
package main

import (
    "fmt"
    "os"
)

func main() {
    fmt.Println(os.Args)
}
```

```text
$ go build .
$ ./main arg1 arg2 arg3
[./main arg1 arg2 arg3]
```

The 0 index is always the name of the executable.

{{</callout>}}

We got our tokens but we haven't printed them yet, so we create a helper method
called `debugToken` - we first print the header of our table and afterwards
iterate through our list of `Token` structures, printing them one by one.

```go{hl_lines=["6-11", 2, "21"]}
// main.go
package main

// [...]

func debugToken(token []Token) {
	log.Printf("%5s | %20s | %15s \n\n", "index", "type", "raw")
	for i, t := range token {
		log.Printf("%5d | %20s | %15s \n", i, TOKEN_LOOKUP[t.Type], t.Raw)
	}
}

func main() {
    log.SetFlags(0)
	if len(os.Args) != 2 {
		log.Fatalln("missing input")
	}

	input := os.Args[1]

	token := NewLexer(strings.NewReader(input)).Lex()
	debugToken(token)
}
```

Running our program with an expression of our choice results in a table of lexemes we recognized

```text
$ go run . "100_000+.5*(42-3.1415)/12"
index |                 type |             raw

    0 |         TOKEN_NUMBER |         100_000
    1 |           TOKEN_PLUS |               +
    2 |         TOKEN_NUMBER |              .5
    3 |       TOKEN_ASTERISK |               *
    4 |     TOKEN_BRACE_LEFT |               (
    5 |         TOKEN_NUMBER |              42
    6 |          TOKEN_MINUS |               -
    7 |         TOKEN_NUMBER |          3.1415
    8 |    TOKEN_BRACE_RIGHT |               )
    9 |          TOKEN_SLASH |               /
   10 |         TOKEN_NUMBER |              12
   11 |                  EOF |       TOKEN_EOF
```

{{<callout type="Closing Words">}}
We did it, we read our input, recognized lexemes in it, stored theses in
structures and attached meaning we require for further processing to them. All
while employing TDD and tests the way the go god fathers intended us to.

The next part will probably take a while longer to make, this one already took
me a week to write. Keep an eye on my [RSS feed](https://xnacly.me/index.xml) -
I'm very excited to finally fully understand precedence parsing and writing the
next blog article.
{{</callout>}}
