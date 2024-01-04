---
title: "Extract Metadata From HTML with GO"
date: 2024-01-03
summary: "Guide to extracting data from HTML using GO"
tags:
  - go
---

## Scope of this article

I am currently in the process of writing a local first search engine by
extracting the site map of a given webpage and indexing all listed sites. The
index scope is currently limited to the following meta data:

- page title (contained in `<title>...</title>`)
- description of the page (encoded in `<meta>`)
- favicon of the webpage (`<link type="image/x-icon">`)

## Thinking about tests

The first task is to establish test data we can use for extracting the
aforementioned tags. I am going to use a recent post of mine
([https://xnacly.me/posts/2023/sophia-lang-weekly02/](https://xnacly.me/posts/2023/sophia-lang-weekly02/))
to throw against the extractor we are going to write:

```go
package main

import (
	"net/http"
	"testing"
	"time"
)

func TestExtractor(t *testing.T) {
	client := http.Client{
		Timeout: time.Millisecond * 250,
	}
	resp, err := client.Get("https://xnacly.me/posts/2023/sophia-lang-weekly02/")
	if err != nil {
		t.Error(err)
	} else if resp.StatusCode > http.StatusPermanentRedirect {
		t.Error(err)
	}

	site := Extract(resp.Body)
	err = resp.Body.Close()
	if site.Title != "Sophia Lang Weekly - 02 | xnacly - blog" {
		t.Errorf("Title doesnt match, got %q", site.Title)
	}

	if site.Description != "Again, new object/array index + function + loop syntax, built-in functions, a License and lambdas" {
		t.Errorf("Description doesnt match, got %q", site.Description)
	}

	if site.IconUrl != "https://xnacly.me/images/favicon.ico" {
		t.Errorf("IconUrl doesnt match, got %q", site.IconUrl)
	}
}
```

This test case is straight forward, we make a request, pass the body to the
`Extract` function (we are going to write in the next section) and afterwards
check if the resulting data structure contains the correct values.

## Setup, Types and Packages

Lets take a look at the signature of the `Extract` function:

```go
package main

type Site struct {
	Title       string
	Description string
	IconUrl     string
}

func Extract(r io.Reader) Site {
    site := Site{}
    return site
}
```

Lets now add the dependency to our imports and get started with creating a new tokenizer:

{{<callout type="Tip">}}
We are using the [x/net/html](https://pkg.go.dev/golang.org/x/net/html)
package, you can add it to your projects go mod via

```shell
$ go get golang.org/x/net/html
```

{{</callout>}}

```go{hl_lines=["3-5", "15"]}
package main

import (
    "io"
    "golang.org/x/net/html"
)

type Site struct {
	Title       string
	Description string
	IconUrl     string
}

func Extract(r io.Reader) Site {
    site := Site{}
    lexer := html.NewTokenizer(r)
    return site
}
```

### Lets think content (using our heads)

All our extraction targets are contained in the `<head></head>` tag of a HTML
document. Considering we are going to use my recent blog article, I will use
the same to highlight the structure of the data we want to extract:

```html {hl_lines=["25-29", "5", "11-14"]}
<!DOCTYPE html>
<html lang="en-us" data-lt-installed="true">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <title>Sophia Lang Weekly - 02 | xnacly - blog</title>
    <meta charset="utf-8" />
    <meta http-equiv="x-ua-compatible" content="IE=edge,chrome=1" />
    <meta name="viewport" content="width=device-width,minimum-scale=1" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Sophia Lang Weekly - 02" />
    <meta
      property="og:description"
      content="Again, new object/array index + function + loop syntax, built-in functions, a License and lambdas"
    />
    <meta
      name="description"
      content="Again, new object/array index + function + loop syntax, built-in functions, a License and lambdas"
    />
    <meta property="article:author" content="xnacly" />
    <meta
      property="article:published_time"
      content="2023-12-24 00:00:00 +0000 UTC"
    />
    <meta name="generator" content="Hugo 0.119.0" />
    <link
      rel="shortcut icon"
      href="https://xnacly.me/images/favicon.ico"
      type="image/x-icon"
    />
  </head>
  <!-- body -->
</html>
```

We can safely assume our content is contained in the `head` tag, thus we will
at first create a bit of context in our extractor and get our hands on the
current token and its type:

```go
package main

import (
    "io"
    "golang.org/x/net/html"
)

type Site struct {
	Title       string
	Description string
	IconUrl     string
}

func Extract(r io.Reader) Site {
    site := Site{}
    lexer := html.NewTokenizer(r)

    var inHead bool
    for {
		tokenType := lexer.Next()
		tok := lexer.Token()
        switch tokenType {
		case html.EndTagToken: // </head>
			if tok.Data == "head" {
				return site
			}
		case html.StartTagToken: // <head>
			if tok.Data == "head" {
				inHead = true
			}

			// keep lexing if not in head of document
			if !inHead {
				continue
			}
        }
    }
    return site
}
```

{{<callout type="Tip">}}
`html.Token` exports the `Data`-field that is either filled with the name of
the current tag or its content (for text).
{{</callout>}}

We use this snippet to detect if we are currently in the `head` tag, if not we
simply skip the current token. If we hit the `</head>` we do not care about the
rest of the document, thus we exit the function.

### The title and its text contents

Lets add the logic for detecting and storing the `title` tag content:

```go {hl_lines=["18", "37-39", "40-44"]}
package main

import (
    "io"
    "golang.org/x/net/html"
)

type Site struct {
	Title       string
	Description string
	IconUrl     string
}

func Extract(r io.Reader) Site {
    site := Site{}
    lexer := html.NewTokenizer(r)

    var inHead bool
    var inTitle bool
    for {
		tokenType := lexer.Next()
		tok := lexer.Token()
        switch tokenType {
		case html.EndTagToken: // </head>
			if tok.Data == "head" {
				return site
			}
		case html.StartTagToken: // <head>
			if tok.Data == "head" {
				inHead = true
			}

			// keep lexing if not in head of document
			if !inHead {
				continue
			}

            if tok.Data == "title" {
				inTitle = true
			}
        case html.TextToken:
			if inTitle {
				site.Title = tok.Data
				inTitle = false
			}
        }
    }
    return site
}
```

This enables us to check if we are between a `<title>` and a `</title>` tag, if
we are we write the content of the `html.TextToken` to `site.Title`.

### The problematic part of the problem

We want to extract the `<meta>` tag with both `property="og:description"` and
`name="description"`. This requires us to check if a given tag is of type
`meta`, has the property `property="whatever"` and write it to our `site`
structure.

```html
<meta
  property="og:description"
  content="Again, new object/array index + function + loop syntax, built-in functions, a License and lambdas"
/>
<meta
  name="description"
  content="Again, new object/array index + function + loop syntax, built-in functions, a License and lambdas"
/>
```

The issue being the `html.Attribute` structure we will use to access these
attributes returns an array, not particularly efficient to search multiple
times for multiple pages to index, therefore we need a helper function for
converting this array into a hash table mapping keys to values:

```go
// [...]
func attrToMap(attr []html.Attribute) map[string]string {
	r := make(map[string]string, len(attr))
	for _, a := range attr {
		r[a.Key] = a.Val
	}
	return r
}
```

We will use this function in combination with `hasKeyWithValue` - a function we
will implement in a second:

```go {hl_lines=["26-35"]}
// [...]
func Extract(r io.Reader) Site {
    site := Site{}
    lexer := html.NewTokenizer(r)

    var inHead bool
    var inTitle bool
    for {
		tokenType := lexer.Next()
		tok := lexer.Token()
        switch tokenType {
		case html.EndTagToken: // </head>
			if tok.Data == "head" {
				return site
			}
		case html.StartTagToken: // <head>
			if tok.Data == "head" {
				inHead = true
			}

			// keep lexing if not in head of document
			if !inHead {
				continue
			}

            var attrMap map[string]string
			if tok.Data == "meta" {
				if attrMap == nil {
					attrMap = attrToMap(tok.Attr)
				}
				if hasKeyWithValue(attrMap, "property", "og:description") || hasKeyWithValue(attrMap, "name", "description") {
					// we have the check above, thus we skip error handling here
					site.Description, _ = attrMap["content"]
				}
			}

            if tok.Data == "title" {
				inTitle = true
			}
        case html.TextToken:
			if inTitle {
				site.Title = tok.Data
				inTitle = false
			}
        }
    }
    return site
}
```

The usage of the new `hasKeyWithValue` function may not be intuitive, therefore
lets first take a look at the implementation:

```go
// [...]
func hasKeyWithValue(attributes map[string]string, key, value string) bool {
	if val, ok := attributes[key]; ok {
		if val == value {
			return true
		}
	}
	return false
}
```

The function just checks if the key is contained in the map and the passed in
value matches the value found in the attribute map.

### My favorite icon - a favicon

Lets employ the previously introduced helper functions for extracting the favicon:

```go {hl_lines=["35-42"]}
// [...]
func Extract(r io.Reader) Site {
    site := Site{}
    lexer := html.NewTokenizer(r)

    var inHead bool
    var inTitle bool
    for {
		tokenType := lexer.Next()
		tok := lexer.Token()
        switch tokenType {
		case html.EndTagToken: // </head>
			if tok.Data == "head" {
				return site
			}
		case html.StartTagToken: // <head>
			if tok.Data == "head" {
				inHead = true
			}

			// keep lexing if not in head of document
			if !inHead {
				continue
			}

            var attrMap map[string]string
			if tok.Data == "meta" {
				if attrMap == nil {
					attrMap = attrToMap(tok.Attr)
				}
				if hasKeyWithValue(attrMap, "property", "og:description") || hasKeyWithValue(attrMap, "name", "description") {
					// we have the check above, thus we skip error handling here
					site.Description, _ = attrMap["content"]
				}
			} else if tok.Data == "link" {
				if attrMap == nil {
					attrMap = attrToMap(tok.Attr)
				}
				if hasKeyWithValue(attrMap, "type", "image/x-icon") {
					site.IconUrl, _ = attrMap["href"]
				}
			}


            if tok.Data == "title" {
				inTitle = true
			}
        case html.TextToken:
			if inTitle {
				site.Title = tok.Data
				inTitle = false
			}
        }
    }
    return site
}
```

Here we check if a `link` tag contains the property-value pair
`type="image/x-icon"` and store the value of the `href` attribute.

## Running our tests

If we run our very cool test now, we should get no errors and everything should
be fine:

```text
tmp.nSnzQqKFL3 :: go test ./... -v
=== RUN   TestExtractor
--- PASS: TestExtractor (0.09s)
PASS
ok  	test	0.093s
```

## Conclusion?

This may not be the fastest, cleanest or most efficient way, but it works and its robust.
