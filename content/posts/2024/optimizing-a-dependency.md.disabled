---
title: "Optimizing a go package by 38147125738.8x"
summary: "Investigating performance issues in a go package for open port lookup"
date: 2024-11-18
tags:
  - go
  - linux
---

> I am using a project of a friend of mine to get a list of currently open
> ports on a system:
> [linux-open-ports](https://github.com/Intevel/linux-open-ports/tree/main).
>
> I noticed the implemention is a little slower than i expected, so i went to
> investigate. I cached the inode to pid mapping for a open port lookup dependency and made
> the whole process `38147125738.8x` faster.

## A Baseline

Go provides the tooling for establishing a baseline via benchmarks, so lets
make use of this and write one:

```go
package linuxopenports

import "testing"

func BenchmarkGetOpenPorts(b *testing.B) {
	ports, err := GetOpenPorts()
	if err != nil {
		b.Fatal(err)
	}
	if len(ports) == 0 {
		b.Fatal("no ports detected")
	}
}
```

This yields a not too fast result on my system:

```text
goos: linux
goarch: amd64
pkg: github.com/intevel/linux-open-ports
cpu: AMD Ryzen 7 PRO 7840U w/ Radeon 780M Graphics
BenchmarkGetOpenPorts
BenchmarkGetOpenPorts-16               1        1570580328 ns/op
PASS
ok      github.com/intevel/linux-open-ports     1.588s
```

## Concept of the pkg

The way of getting a list of open ports in linux based systems is pretty easy
to understand:

1. Get a list of all connections and their inodes, these are stored at:

   - `/proc/net/tcp`
   - `/proc/net/tcp6`
   - `/proc/net/udp`
   - `/proc/net/udp6`

   All of the above follow the same format:

   ```text
   ~ :: head -n1 < /proc/net/tcp
   sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
    0: 3600007F:0035 00000000:0000 0A 00000000:00000000 00:00000000 00000000   991        0 15761 1 0000000000000000 100 0 0 10 5
   ```

   There are no process ids (`PID`) here, we have to map all found `inode`'s to
   their respective `pids` on the system

   {{<callout type="Tip">}}
   inode refers to a datastructure describing a file-system object, see [wikipedia](https://en.wikipedia.org/wiki/Inode)
   {{</callout>}}

2. Read each `/proc/<pid>/fd` directory to access their socket inodes (files in the format `socket:[<inode>]`)
3. Return a list of ports with their inodes and process id's

## Diving in

`linux-open-ports` exports a function `GetOpenPorts` and the corresponding type `OpenPort`:

```go
type OpenPort struct {
	Protocol string
	Port     int
	PID      int
}

func GetOpenPorts() ([]OpenPort, error) {
    // ...
}
```

The implemention roughly follows the outlined logic introduced before.

`GetOpenPorts` calls `findPIDByInode` for each inode in each file:

```go
func GetOpenPorts() ([]OpenPort, error) {
	var openPorts []OpenPort
	uniquePorts := make(map[string]bool)

	protocolFiles := map[string][]string{
		"tcp": {"/proc/net/tcp", "/proc/net/tcp6"},
		"udp": {"/proc/net/udp", "/proc/net/udp6"},
	}

	for protocol, files := range protocolFiles {
		for _, filePath := range files {
            // .. scanner setup and error handling
			for scanner.Scan() {
				fields := strings.Fields(scanner.Text())
                // .. field checks and assignments
				inode := fields[9]
				pid := findPIDByInode(inode)
                // ..
			}
		}
	}

	return openPorts, nil
}
```

The `findPIDByInode` function reads the whole `/proc` dir on each invocation to
find the process the inode belongs to.

```go
func findPIDByInode(inode string) int {
	procDirs, _ := os.ReadDir("/proc")
	for _, procDir := range procDirs {
		if !procDir.IsDir() || !isNumeric(procDir.Name()) {
			continue
		}

		pid := procDir.Name()
		fdDir := filepath.Join("/proc", pid, "fd")
		fdFiles, err := os.ReadDir(fdDir)
		if err != nil {
			continue
		}

		for _, fdFile := range fdFiles {
			fdPath := filepath.Join(fdDir, fdFile.Name())
			link, err := os.Readlink(fdPath)
			if err == nil && strings.Contains(link, fmt.Sprintf("socket:[%s]", inode)) {
				pidInt, _ := strconv.Atoi(pid)
				return pidInt
			}
		}
	}
	return -1
}

func isNumeric(s string) bool {
	_, err := strconv.Atoi(s)
	return err == nil
}
```

## Parsing integers is slow

The first low-hanging fruit catching my eye is the `isNumeric` function call,
which attempts to parse the directory name and checks if it is a number to make
sure the directory is the directory of a process. Using `unicode.IsDigit` on
the first byte of the directory name should be sufficient and faster:

```go{hl_lines=[4,5]}
func findPIDByInode(inode string) int {
	procDirs, _ := os.ReadDir("/proc")
	for _, procDir := range procDirs {
		pid := procDir.Name()
		if !procDir.IsDir() || !unicode.IsDigit(rune(pid[0])) {
			continue
		}

		fdDir := filepath.Join("/proc", pid, "fd")
		fdFiles, err := os.ReadDir(fdDir)
		if err != nil {
			continue
		}

		for _, fdFile := range fdFiles {
			fdPath := filepath.Join(fdDir, fdFile.Name())
			link, err := os.Readlink(fdPath)
			if err == nil && strings.Contains(link, fmt.Sprintf("socket:[%s]", inode)) {
				pidInt, _ := strconv.Atoi(pid)
				return pidInt
			}
		}
	}
	return -1
}
```

Running the benchmark tells us we got down from `1570580328 ns/op` to
`1108555474 ns/op` (1.57s to 1.11s, 0.46s or 1.41x faster).

```text
goos: linux
goarch: amd64
pkg: github.com/intevel/linux-open-ports
cpu: AMD Ryzen 7 PRO 7840U w/ Radeon 780M Graphics
BenchmarkGetOpenPorts
BenchmarkGetOpenPorts-16               1        1108555474 ns/op
PASS
ok      github.com/intevel/linux-open-ports     1.123s
```

## Lets cache the mapping and gain a 38147125738.8x speedup

The informed reader will notice iterating the `/proc/` dir every time we hit a
new inode is not that smart. Instead we should do it once and look up found
inodes in the inode to pid mapping:

```go {hl_lines=[2,"22-27"]}
func inodePIDMap() map[string]string {
	m := map[string]string{}
	procDirs, _ := os.ReadDir("/proc")
	for _, procDir := range procDirs {
		pid := procDir.Name()
		if !procDir.IsDir() && !unicode.IsDigit(rune(pid[0])) {
			continue
		}

		fdDir := filepath.Join("/proc", pid, "fd")
		fdFiles, err := os.ReadDir(fdDir)
		if err != nil {
			continue
		}

		for _, fdFile := range fdFiles {
			path := filepath.Join(fdDir, fdFile.Name())
			linkName, err := os.Readlink(path)
			if err != nil {
				continue
			}
			if strings.Contains(linkName, "socket") {
				// index 8:till end -1 because socket:[ is 8 bytes long and ]
				// is at the end
				inode := linkName[8 : len(linkName)-1]
				m[inode] = pid
			}
		}
	}
	return m
}
```

The `GetOpenPorts` function has to be updated to match this change:

```go {hl_lines=[10,"19-22"]}
func GetOpenPorts() ([]OpenPort, error) {
	var openPorts []OpenPort
	uniquePorts := make(map[string]bool)

	protocolFiles := map[string][]string{
		"tcp": {"/proc/net/tcp", "/proc/net/tcp6"},
		"udp": {"/proc/net/udp", "/proc/net/udp6"},
	}

	cachedInodePIDMap := inodePIDMap()

	for protocol, files := range protocolFiles {
		for _, filePath := range files {
            // .. scanner setup and error handling
			for scanner.Scan() {
				fields := strings.Fields(scanner.Text())
                // .. field checks and assignments
				inode := fields[9]
				pid, ok := cachedInodePIDMap[inode]
				if !ok {
					continue
				}
                // ..
			}
		}
	}

	return openPorts, nil
}
```

The speedup is enormous, from `1108555474 ns/op` to `0.02906 ns/op`,
corresponding to `38147125739.848587x` speedup.

{{<callout type="Old benchmark">}}

```text
goos: linux
goarch: amd64
pkg: github.com/intevel/linux-open-ports
cpu: AMD Ryzen 7 PRO 7840U w/ Radeon 780M Graphics
BenchmarkGetOpenPorts
BenchmarkGetOpenPorts-16               1        1108555474 ns/op
PASS
ok      github.com/intevel/linux-open-ports     1.123s
```

{{</callout>}}

```text
goos: linux
goarch: amd64
pkg: github.com/intevel/linux-open-ports
cpu: AMD Ryzen 7 PRO 7840U w/ Radeon 780M Graphics
BenchmarkGetOpenPorts-16        1000000000               0.02906 ns/op
PASS
ok      github.com/intevel/linux-open-ports     0.235s
```

I would go further on this, but the above change already results in such a
large performance increase, I'm going to call it a day. However if it wouldn't
be much faster, my next steps would be to remove the `fmt.Sprintf` in the
for-loop body. Beforehand I would spin up a profiler and investigate hot
functions.

I already upstreamed these changes, see [`refactor: cache inode->pid lookup via map on function startup #1`](https://github.com/Intevel/linux-open-ports/pull/1) for the diff.
