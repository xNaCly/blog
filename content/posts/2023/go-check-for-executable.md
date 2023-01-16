---
title: "Go: check if executable is in path"
summary: "Quick guide with snippet on how to check if a executable is in the systems path"
date: 2023-01-16
tags:
  - Go
---

To check if an executable is in the path we use the `exec` package and its exported `LookPath()` function.

## Docs and Resources:

- [go doc os/exec package, LookPath](https://pkg.go.dev/os/exec#LookPath)

{{<callout type="Info">}}

- output of `go doc exec.LookPath`:

```go
package exec // import "os/exec"
func LookPath(file string) (string, error)`
```

LookPath searches for an executable named file in the directories named by
the PATH environment variable. If file contains a slash, it is tried
directly and the PATH is not consulted. LookPath also uses PATHEXT
environment variable to match a suitable candidate. The result may be an
absolute path or a path relative to the current directory.
{{</callout>}}

## Snippet

```go
// declare file as in package main
package main

// import formatting and executable packages
import (
	"fmt"
	"os/exec"
)

// checks if executable 'e' is in path
func checkIfExecInPath(e string) bool {
	// ignore output, only use error
	_, err := exec.LookPath(e)
	// return true if error nil, else false
	return err == nil
}

func main() {
	fmt.Println(checkIfExecInPath("git")) // returns: true
	fmt.Println(checkIfExecInPath("gut")) // returns: false
}
```

{{<callout type="Hint">}}

For a realworld application of this, take a look at my [git auto sync](https://github.com/xNaCly/git-auto-sync) project,
which uses git to periodically update a repository. For this to work it checks if git is installed before running:

```go {hl_lines=[2]}
// taken from: https://github.com/xNaCly/git-auto-sync/blob/579276f62a0d30b45a3c2b01634bfff9703ce1ea/main.go#L14-L16
if !checkForGit(conf) {
	log.Fatalln("[FATAL ERROR] 'git' executable not found, gas requires git to work properly - exiting.")
}
```

```go {hl_lines=[4,5]}
// taken from: https://github.com/xNaCly/git-auto-sync/blob/579276f62a0d30b45a3c2b01634bfff9703ce1ea/util.go#L101-L105
func checkForGit(conf Config) bool {
	DebugLog(conf, "checking for git executable in path...")
	_, err := exec.LookPath("git")
	return err == nil
}
```

{{</callout>}}
