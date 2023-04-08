---
title: Lexical analysis of Markdown in Go
summary: How to tokenize markdown without regular expressions
date: 2023-04-05
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
    {
        Pos:    13,
        Kind:   NEWLINE,
        Line:   0,
        Value:  "",
    },
}
```

Notice how ` Heading 3` is completely encapsulated in the last `Token` object of Kind `TEXT`.

### Scanner setup

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

#### Instantiation

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

#### Adding a new Token

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

#### Moving through the line

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

#### Moving through the file

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

#### Pretty Printing the Tokens

To debug and take a look at our processed tokens we implement the `scanner.Scanner.PrintTokens` function:

```go
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) PrintTokens() {
	for _, token := range s.tokens {
		fmt.Printf("[ '%s' | %d | %d | '%s' ]\n",
			TOKEN_LOOKUP_MAP[token.Kind],
			token.Pos,
			token.Line,
			token.Value,
		)
	}
}
```

The function simply loops over every token in the `tokens` array field of the `Scanner` structure and formats the token values according to our format string.

An attentive reader has already noticed the `TOKEN_LOOKUP_MAP` in line 9 of the snippet.
This map simply binds the enums we created as our token kinds to their name, because who likes looking at numbers if they can instead look at names 😴.
This map is defined in the `scanner/tokens.go` file and looks like this:

```go
// scanner/tokens.go
package scanner

// ...

var TOKEN_LOOKUP_MAP = map[uint]string{
	HASH:               "HASH",
	UNDERSCORE:         "UNDERSCORE",
	STAR:               "STAR",
	NEWLINE:            "NEWLINE",
	DASH:               "DASH",
	STRAIGHTBRACEOPEN:  "STRAIGHTBRACEOPEN",
	STRAIGHTBRACECLOSE: "STRAIGHTBRACECLOSE",
	PARENOPEN:          "PARENOPEN",
	PARENCLOSE:         "PARENCLOSE",
	GREATERTHAN:        "GREATERTHAN",
	BACKTICK:           "BACKTICK",
	TEXT:               "TEXT",
	BANG:               "BANG",
}
```

This means whenever we lex a hash (`#`) and we want to check if it is a hash using our eyes, we can simply do the following:

```go
fmt.Println(TOKEN_LOOKUP_MAP[HASH])
```

Running the `scanner.Scanner.PrintTokens` function for our example `### Heading 3`, results in the following output:

```text
[ 'HASH' | 0 | 0 | '' ]
[ 'HASH' | 1 | 0 | '' ]
[ 'HASH' | 2 | 0 | '' ]
[ 'TEXT' | 3 | 0 | ' Heading 3' ]
[ 'NEWLINE' | 13 | 0 | '' ]
```

#### Getting our scanned Tokens

To access the token we scanned, we create a new function called `scanner.Scanner.Tokens`, which returns the `scanner.Scanner.tokens` structure field:

```go
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) Tokens() []Token {
    return s.tokens
}
```

### Single character tokens

A single character token in Markdown can be any of:

```text
 # (Hash)
 _ (Underscore)
 * (Star)
\n (New Line)
 - (Dash)
 [ (Open Square Bracket)
 ] (Close Square Bracket)
 ( (Open Paren)
 ) (Close paren)
 > (Bigger than)
 ! (Bang / exclamation mark)
 ` (Backtick)
```

To parse these we simply check if the value of the `curChar` field is equal to them and call `addToken` with the tokens kind in the `scanner.Scanner.Lex` function.

Doing this requires a for loop over all the characters in the current line while we aren't at the end of the file:

```go
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) Lex() {
	for !s.isAtEnd {

    }
}
```

{{<callout type="Tip">}}
Remember, the `isAtEnd` field of the `Scanner` struct indicates that we left the last line of the file behind us and are therefore done with the file.
{{</callout>}}

To pave the way for matching characters we create a switch case statement for the `curChar` field of the `Scanner` structure and a variable `tokenKind`:

```go {hl_lines=["8-11"]}
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) Lex() {
	for !s.isAtEnd {
        var tokenKind uint
        switch s.curChar {

        }
    }
}
```

We use the `tokenKind` variable to store the kind of token we found.
This allows us to write the call to `s.addToken` after the switch case not in each case statement:

```go {hl_lines=["12"]}
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) Lex() {
	for !s.isAtEnd {
        var tokenKind uint
        switch s.curChar {

        }
        s.addToken(tokenKind, "")
    }
}
```

After adding the token the current character matches we need to move on to the next character - remember we implemented `scanner.Scanner.advance` exactly for this use case.:

```go {hl_lines=["13"]}
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) Lex() {
	for !s.isAtEnd {
        var tokenKind uint
        switch s.curChar {

        }
        s.addToken(tokenKind, "")
        s.advance()
    }
}
```

I am now going to show you how to match the hash in detail and afterwards we are going to fast forward the process for the remaining symbols.

```go {hl_lines=["10-11"]}
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) Lex() {
	for !s.isAtEnd {
        var tokenKind uint
        switch s.curChar {
            case '#':
			tokenKind = HASH
        }
        s.addToken(tokenKind, "")
        s.advance()
    }
}
```

Everything we had to do was add the case to match `#` and assign the kind of token (`HASH`) to the `tokenKind` variable.

Now the other symbols:

```go {hl_lines=["12-33"]}
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) Lex() {
	for !s.isAtEnd {
        var tokenKind uint
        switch s.curChar {
        case '#':
            tokenKind = HASH
        case '!':
            tokenKind = BANG
        case '>':
            tokenKind = GREATERTHAN
        case '_':
            tokenKind = UNDERSCORE
        case '*':
            tokenKind = STAR
        case '-':
            tokenKind = DASH
        case '[':
            tokenKind = STRAIGHTBRACEOPEN
        case ']':
            tokenKind = STRAIGHTBRACECLOSE
        case '(':
            tokenKind = PARENOPEN
        case ')':
            tokenKind = PARENCLOSE
        case '`':
            tokenKind = BACKTICK
        }
        s.addToken(tokenKind, "")
        s.advance()
    }
}
```

Notice the missing line break (`\n`)?
As i mentioned while discussing the `scanner.Scanner.advance` function, we need to add the line breaks to the end of the line ourselfs to keep track if we are at the end of the current line.

To move to the next line we need to call the `scanner.Scanner.advanceLine` function if the scanner encounters the line break symbol:

```go {hl_lines=["20-23"]}
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) Lex() {
	for !s.isAtEnd {
        var tokenKind uint
        switch s.curChar {
        case '#':
            tokenKind = HASH
        case '!':
            tokenKind = BANG
        case '>':
            tokenKind = GREATERTHAN
        case '_':
            tokenKind = UNDERSCORE
        case '*':
            tokenKind = STAR
        case '\n':
			s.addToken(NEWLINE, "")
			s.advanceLine()
			continue
        case '-':
            tokenKind = DASH
        case '[':
            tokenKind = STRAIGHTBRACEOPEN
        case ']':
            tokenKind = STRAIGHTBRACECLOSE
        case '(':
            tokenKind = PARENOPEN
        case ')':
            tokenKind = PARENCLOSE
        case '`':
            tokenKind = BACKTICK
        }
        s.addToken(tokenKind, "")
        s.advance()
    }
}
```

As one can see we add a new token with the `NEWLINE` kind and afterwards advance to the next line and continue onward to the next iteration of the loop

If we again look at our example we can see our lexer can already tokenize four of our five tokens - the three hashes and the line break at the end of the line.

Scanning the rest of the paragraph as a token of kind `TEXT` is going to be slightly more complex.

### Multi character tokens

Lets talk lexing texts. We want our scanner to categorize everything between the special symbols we are already scanning for as a token of kind `TEXT`.
To accomplish this we will need to add a default case to our switch statement:

```go {hl_lines=["36-48"]}
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) Lex() {
	for !s.isAtEnd {
        var tokenKind uint
        switch s.curChar {
        case '#':
            tokenKind = HASH
        case '!':
            tokenKind = BANG
        case '>':
            tokenKind = GREATERTHAN
        case '_':
            tokenKind = UNDERSCORE
        case '*':
            tokenKind = STAR
        case '\n':
			s.addToken(NEWLINE, "")
			s.advanceLine()
			continue
        case '-':
            tokenKind = DASH
        case '[':
            tokenKind = STRAIGHTBRACEOPEN
        case ']':
            tokenKind = STRAIGHTBRACECLOSE
        case '(':
            tokenKind = PARENOPEN
        case ')':
            tokenKind = PARENCLOSE
        case '`':
            tokenKind = BACKTICK
        default:
            var res strings.Builder

        out:
            for {
                switch s.curChar {
                case '\n', '!', '#', '_', '*', '-', '[', ']', '(', ')', '`', '>', '?':
                    break out
                }

                res.WriteRune(s.curChar)
                s.advance()
            }
        }
        s.addToken(tokenKind, "")
        s.advance()
    }
}
```

In this default statement we create a new variable of type `strings.Builder` on which we will append the characters of the text to.
This is considerably faster than just concatenating two strings using the `+=` operator.

The next line defines a label for our following loop (`out:`).
We will use this label to break the outer loop if we find a character which matches any special character.

In this while loop we check if the current character matches a special character (lines 41-44), if it does we break at the `out` label (line 43).
This stops the loop labeled as `out`.
If it isn't a special character the scanner writes the current character to the `strings.Builder` and advances to the next character.

We want our scanner to skip empty lines, therefore we add the following snippet at the end of the default case:

```go {hl_lines=["50-52", 54]}
// scanner/scanner.go
package scanner

// ...

func (s *Scanner) Lex() {
	for !s.isAtEnd {
        var tokenKind uint
        switch s.curChar {
        case '#':
            tokenKind = HASH
        case '!':
            tokenKind = BANG
        case '>':
            tokenKind = GREATERTHAN
        case '_':
            tokenKind = UNDERSCORE
        case '*':
            tokenKind = STAR
        case '\n':
			s.addToken(NEWLINE, "")
			s.advanceLine()
			continue
        case '-':
            tokenKind = DASH
        case '[':
            tokenKind = STRAIGHTBRACEOPEN
        case ']':
            tokenKind = STRAIGHTBRACECLOSE
        case '(':
            tokenKind = PARENOPEN
        case ')':
            tokenKind = PARENCLOSE
        case '`':
            tokenKind = BACKTICK
        default:
            var res strings.Builder

        out:
            for {
                switch s.curChar {
                case '\n', '!', '#', '_', '*', '-', '[', ']', '(', ')', '`', '>':
                    break out
                }

                res.WriteRune(s.curChar)
                s.advance()
            }

			if res.Len() != 0 {
				s.addToken(TEXT, res.String())
			}

			continue
        }
        s.addToken(tokenKind, "")
        s.advance()
    }
}
```

This change skips all scanned token which have a string of length 0.
The `continue` at the end skips adding the token again in line 56, due to the fact that we already added the token in line 51 if it is not empty.

## Tests

While lexing we need to check if we get the output right and correct. Go supports testing code with a built-in module.
To test simply create a new file in the `scanner` directory, named `scanner_test.go`.:

```go
// scanner/scanner_test.go
package scanner

import "testing"

func TestExample(t *testing.T) {
    s := New("./markdown.md")
    s.Lex()
    tokens := s.Tokens()
}
```

The `_test` suffix is important, otherwise the `go test` command won't recognize the file and therefore the tests in it.

For this test to work the `markdown.md` file needs to be created in the `scanner/` directory. Fill it with the example we already used before:

```markdown
### Heading 3
```

Now we can append the following to our `TestExample` function:

```go {hl_lines=["11-21"]}
// scanner/scanner_test.go
package scanner

import "testing"

func TestExample(t *testing.T) {
    s := New("./markdown.md")
    s.Lex()
    tokens := s.Tokens()

    expectedTokens := []uint {
        HASH,
        HASH,
        HASH,
        TEXT,
        NEWLINE,
    }

    if len(tokens) != len(expectedTokens) {
		t.Errorf("expected %d tokens, got: %d", len(expectedTokens), len(tokens))
	}
}
```

We define the token kinds we expect in the `expectedTokens` array, after that we compare the length of the tokens we got after scanning and the length of the array we just defined. If they didn't match we did something wrong.

To check if all tokens we matched are correct we need to loop over them to check if the current token we expect matches the current token we scanned:

```go {hl_lines=["23-29"]}
// scanner/scanner_test.go
package scanner

import "testing"

func TestExample(t *testing.T) {
    s := New("./markdown.md")
    s.Lex()
    tokens := s.Tokens()

    expectedTokens := []uint {
        HASH,
        HASH,
        HASH,
        TEXT,
        NEWLINE,
    }

    if len(tokens) != len(expectedTokens) {
		t.Errorf("expected %d tokens, got: %d", len(expectedTokens), len(tokens))
	}

    for i, token := range tokens {
		if expectedTokens[i] != token.Kind {
			t.Errorf("expected %d [%s], got %d [%s] for token %d",
				expectedTokens[i], TOKEN_LOOKUP_MAP[expectedTokens[i]], token.Kind, TOKEN_LOOKUP_MAP[token.Kind], i,
			)
		}
	}
}
```

So thats it, now you are able to write a lexer for markdown and test if everything worked out correctly.
