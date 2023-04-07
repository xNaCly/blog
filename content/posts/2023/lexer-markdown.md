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

A scanner / lexer / tokeniser takes an input without any sense, such as a stream of characters and converts it into a stream of tokens with information attached to them, such as their position, their kind or their value.

For example, take a look at the following markdown:

```markdown
### Heading 3
```

After throwing it into our scanner, the scanner converts it internally into a stream of tokens, representable by using an array of characters, like so:

```go
input := []rune{
    '#',
    '#',
    '#',
    ' ',
    'H',
    'e',
    'a',
    'd',
    'i',
    'n',
    'g',
    ' ',
    '3',
    '\n',
}
```

{{<callout type="Tip">}}
Notice the `'\n'` line break after the `3`.
A line in terms of a file always ends in a line break on linux, this means a line is composed of all the characters between the last `\n` and the next `\n`.
{{</callout>}}

After the scanner did its job it should spit out a stream of tokens, again representable as an array, only this time of objects:

```go
result := []Token{
    {
        Pos:    0,
        Kind:   HASH,
        Line:   0,
        Value:  "",
    },
    {
        Pos:    1,
        Kind:   HASH,
        Line:   0,
        Value:  "",
    },
    {
        Pos:    2,
        Kind:   HASH,
        Line:   0,
        Value:  "",
    },
    {
        Pos:    3,
        Kind:   TEXT,
        Line:   0,
        Value:  " Heading 3",
    },
}
```

Notice how ` Heading 3` is completely encapsulated in the last `Token` object of Kind `TEXT`.

#### Scanner setup

Our first step is to create a new `Scanner` structure:

```go
// scanner/scanner.go
package scanner

type Scanner struct {
	scan    *bufio.Scanner
	isAtEnd bool
	curLine []rune
	curChar rune
	linePos uint
	line    uint
	tokens  []Token
}
```

The fields in the structure can be explained as follows:

| Field     | usage                                                                               |
| --------- | ----------------------------------------------------------------------------------- |
| `scan`    | contains the buffered scanner which is used to iterate over the file we want to lex |
| `isAtEnd` | indicates if the scanner lexed the whole file and is at the end of it (EOF)         |
| `curLine` | array of runes containing the characters of the current line                        |
| `curChar` | the character which can be found at the current index on the current line           |
| `linePos` | indicates the scanners position on the current line                                 |
| `line`    | holds the line position of the scanner in the file                                  |
| `tokens`  | contains the lexed token objects                                                    |

##### Instantiation

To instantiate we define a new exported function (a function of a module is exported if its first character is uppercase) in the package:

```go
// scanner/scanner.go
package scanner

// ...

func New(fileName string) Scanner {
    file, err := os.Open(fileName)
	if err != nil {
		log.Fatalln("couldn't open file", err)
	}

	scan := bufio.NewScanner(file)
    // scan.Scan reads the first line
    // of the given file into the scanner
	scan.Scan()

    // scan.Text returns
    // the string value of the previously read line
	firstLine := []rune(scan.Text())

	return Scanner{
		scan:    scan,
		curLine: firstLine,
		curChar: firstLine[0],
		line:    0,
		linePos: 0,
	}
}
```

The `scanner.New` function returns an instance of the `Scanner` structure we defined before.

##### Adding a new Token

To write less repetitive code, we create the `scanner.Scanner.addToken` function:

```go
// scanner/scanner.go
package scanner

//...

func (s *Scanner) addToken(kind uint, value string) {
    pos := s.linePos
	if len(value) != 0 {
		pos = s.linePos - uint(len(value))
	}
	s.tokens = append(s.tokens, Token{
		Pos:   pos,
		Kind:  kind,
		Value: value,
		Line:  s.line,
	})
}
```

This function allows us to add a token after scanning it simply by calling the function like so:

```go
s.addToken(HASH, "")
```

{{<callout type="Info">}}
Lines 7 till 10 are a bit unintuitive, so lets go into detail and explore their use:

```go
pos := s.linePos
```

Line 7 is simply assigning the value of the current position the lexer is at to the `pos` variable.

```go {hl_lines=[2]}
pos := s.linePos
if len(value) != 0 {
    pos = s.linePos - uint(len(value))
}
```

The `if` statement in line 8 checks if the function parameter `value` of type `string` we are receiving contains a value, this is done by comparing its length with not null.

```go {hl_lines=[3]}
pos := s.linePos
if len(value) != 0 {
    pos = s.linePos - uint(len(value))
}
```

The magic happens in the 9th line of the snippet.
This line calculates the position of the token by subtracting the length of the function parameter `value` of type string from the cursors position on the current line.

This is very dry and hard to understand without an example, so lets go back to the example we used before. Consider we have the following line to lex:

```markdown
### Heading 3
```

As we explored before we scan each hash as its own token and would add it using the `addToken` function. We will call the function like so:

```go
s.addToken(HASH, "")
```

This means the `addToken` function gets an empty string (length is 0) as the content of the parameter `value`, therefore the if statement in its body is not executed.

However, if we lexed a text and want to add it using the `addToken` function we would call it like this:

```go
s.addToken(TEXT, " Heading 3")
```

As one can see we supplied the function call with the value `" Heading 3"` which is in fact not of length 0.
This means the if statement in the function body is executed and tries to calculate a different position for the `TEXT` token than the `HASH` token.

To explain this behaviour we need to think about how we would lex a token of type `TEXT`.
When encountering a `#` we can simply call the `s.addToken(HASH, "")` function, advance to the next token and lex again.
We can't do this when we encounter non format specific characters (everything not `#_*\n-[]()>!`).
To store everything else in a neat way we iterate over the rest of the line until we hit any of the before mentioned special characters and then add the text with its content using the `addToken(TEXT, " Heading 3")` function.

This however means the scanners position is at the end of the text we want to scan:

```text
             scanner is positioned here (pos: 13)
             ↓↓
### Heading 3\n
   ↑
   but the text starts here (pos: 3)
```

To compensate this offset, we subtract the length of the text we lexed from the position the scanner is currently on:

```text
end_of_text - length_of_text = beginning_of_the_text
```

{{</callout>}}

##### Moving through the line

After lexing a character we want to take a look at the next one.
Therefore we need to somehow advance to the next character and position on the line, the following function does exactly that:

```go
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) advance() {
	if s.linePos+1 >= uint(len(s.curLine)) {
		s.curChar = '\n'
		s.linePos++
		return
	}

	s.linePos++
	s.curChar = s.curLine[s.linePos]
}
```

The function increments the `linePos` field of the `Scanner` struct and sets the `curChar` field to the next character if the scanner wouldn't be at the end of the line when incrementing.

Due to the fact that the `bufio.Scanner` removes line breaks from the read lines we need to set the current character to a line break if we are at the end of the line. ([Source](https://pkg.go.dev/bufio#Scanner))
This enables us to check if we are at the end of the line while iterating through the current line.

##### Moving through the file

After hitting a line break (`\n`) we of course need to advance to the next line.
The following function allows us to do exactly this:

```go
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) advanceLine() {
	ok := s.scan.Scan()

	if s.scan.Err() != nil || !ok {
		s.isAtEnd = true
		return
	}

	s.curLine = []rune(s.scan.Text())
	s.line++
	s.linePos = 0
	for len(s.curLine) == 0 {
		s.scan.Scan()
		s.curLine = []rune(s.scan.Text())
		s.line++
	}
	s.curChar = s.curLine[s.linePos]
}
```

The above function calls the `scan` field of the `Scanner` structure to get the next line of the file,
if this failed or the `bufio.Scanner` has an error the `isAtEnd` flag on the `Scanner` structure is set.

If the scanner is still in the bounds of the file it sets the current line to the string result of the line the `bufio.Scanner` just scanned.
After that it increments the `line` field of the `Scanner` structure and sets the field `linePos` to 0.

If the current line is of length 0 or simply empty, the function loops until it finds a line which isn't empty.

At the end the function assigns the first character of the new line to the `curChar` field of the `Scanner` structure.

##### Printing the Tokens

### Single char tokens

A single character token in Markdown can be any of:

- \# (Hash)
- \_ (Underscore)
- \* (Star)
- \n (New Line)
- \- (Dash)
- \[ (Open Square Bracket)
- \] (Close Square Bracket)
- \( (Open Paren)
- \) (Close paren)
- \> (Bigger than)
- \! (Bang / exclamation mark)
- \` (Backtick)

To parse these we simply

### Multi char tokens

- explain how to lex
- show how to lex

## Tests

- tests to check if our result is consistent
- start small, go bigger
