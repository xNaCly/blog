---
title: Lexical analysis of Markdown in Go
summary: How to tokenize markdown without regular expressions
date: 2023-04-05
draft: true
tags:
  - go
  - markdown
---

{{<callout type="Info">}}
This is a partial write-up of the lexer I implemented while working on my markdown to html converter.
The repository can be found [here](https://github.com/xnacly/fleck).

Today's goal is to implement a simple enough scanner / lexer to understand the basics of converting a stream of characters without sense into a stream of tokens with a **lot** of sense. 😉
{{</callout>}}

## Tokens

Our output consists of a lot of tokens which are strings with an identified meaning, contrary to our input stream, which has no meaning whatsoever.

### Defining a Markdown subset

To keep the scanner small and simple we restrict ourself to a subset of Markdown.

- Headings

  ```text
  # h1

  ## h2

  ### h3

  #### h4

  ##### h5

  ###### h6
  ```

- Lists

  ```markdown
  - [ ] list
  - [x] list
  - list
  ```

- Links

  ```markdown
  [cool website](https://xnacly.me)
  ```

- Images

  ```markdown
  ![very cool avatar](https://xnacly/images/avatar.webp)
  ```

- Emphasis

  ```markdown
  **this is bold**
  ```

- Italics

  ```markdown
  _this is italic_
  ```

- Horizontal rulers

  ```markdown
  ---
  ```

- Quotes

  ```markdown
  > Opinion is the medium between knowledge and ignorance.
  > ~ Plato
  ```

- code blocks

  ````markdown
  ```javascript
  console.log("test");
  ```
  ````

- inline code

  ```markdown
  `this is inline code`
  ```

### Defining Tokens

The parser will do the job of putting our tokens together in a well structured way (AST).
Our job is to tell the parser exactly which token its currently looking at.
To do this we need to create a structure for each Token which holds information such as position, value, kind of token, etc.

In go the above looks something like the following:

```go
// scanner/tokens.go
package scanner

type Token struct {
    Pos uint
    Kind uint
    Line uint
    Value string
}
```

The position, kind and line structure values are all of type unsigned integer, simply because it doesn't make sense for them to be negative.
To indicate where the scanner encountered the token, the token struct contains the `Line` and the `Position` on the line on which the token was found.
To store text we find while lexing, we use the `Value` field.

For example lets take a look at the following:

```text
## Tokens

### Defining Tokens
```

Imagine we are at the second position of the third line, our fictional cursor (indicated using `^`) is therefore located under the second hash (`#`) in the heading `Defining Tokens`:

```text
## Tokens

### Defining Tokens
 ^
 |
 cursor, located at: [line: 2, position 1]
```

{{<callout type="Tip">}}
Remember, arrays start at the index `0`, therefore we are located at the line `2`, even though the numbers on the left indicate we are in line `3` of the file.
{{</callout>}}

If we were to lex this character and store it somewhere we would create the following go structure:

```go
// main.go
package main

import "github.com/xnacly/fleck/scanner"

func main() {
    t := scanner.Token {
        Pos:    1,
        Kind:   0, // ? We don't know yet
        Line:   2,
        Value:  "",
    }
}
```

### Categorizing Tokens

To distinguish tokens from one another, we define a bucket load of constants:

```go
// scanner/tokens.go
package scanner
// ...

const (
	TEXT = iota + 1 // everything else
	HASH // #
	UNDERSCORE // _
	STAR // *
	NEWLINE // \n
	DASH // -
	STRAIGHTBRACEOPEN // [
	STRAIGHTBRACECLOSE // ]
	PARENOPEN // (
	PARENCLOSE // )
	BACKTICK // `
	GREATERTHAN // >
	BANG // !
)
```

`iota` is used to auto increment constants and is therefore providing something like an enum in go. ([source](https://go.dev/ref/spec#Iota))

We can now extend our example using our newly created enum:

```go
// main.go
package main

import "github.com/xnacly/fleck/scanner"

func main() {
    t := scanner.Token {
        Pos:    1,
        Kind:   HASH,
        Line:   2,
        Value:  "",
    }
}
```

Remember, the character is a hash (`#`). Therefore we added the `HASH` constant from above as the `Kind` field in the resulting structure.

## Scanner

- what does a scanner do

### Single char tokens

- explain how to lex
- show how to lex

### Multi char tokens

- explain how to lex
- show how to lex

## Tests

- tests to check if our result is consistent
- start small, go bigger

## Benchmarks

- why benchmark

### Built-in

- how to use built in benchmarks

### Pprof

- why use pprof
- how to view result in the browser
- use flamecharts

## Performance

- steps i took to improve the Performance
