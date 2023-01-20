---
title: "How to periodically backup a git repository to its remote"
summary: "A guide to updating a repository periodically using x-git-sync"
date: 2023-01-20
draft: true
tags:
  - backup
  - go
  - sync
---

{{<callout type="Info">}}
x-git-sync is a minimal and highly configurable tool to automatically backup a git repository at configured intervals.
{{</callout>}}

## Setup

### Installation

The installation is simple and straightforward, either build from source or install from the latest release.

#### Installing from Release

To get the latest executable without a lot of hussle follow the following three steps

- navigate to [x-git-sync/Releases](https://github.com/xNaCly/x-git-sync/releases/tag/v0.1.0),
  download the `xgs_v0-1-0_linux-x86_64` executable
- move the executable to the `$PATH`: `mv ./xgs_v0-1-0_linux-x86_64 /usr/bin/xgs`
- you should now be able to run xgs

#### Building from source

To get the latest and newest changes build the project from source:

> Requires `git` and `go`

```bash
git clone https://github.com/xnacly/x-git-sync xgs
cd xgs
go build
```

You should now see a `xgs` executable in the directory

### Configuration

## Usage

## Tips and tricks
