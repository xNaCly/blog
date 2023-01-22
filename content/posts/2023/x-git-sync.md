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

## Possible use cases

I wrote this tool to fit my need for uploading a new version of my uni documents vault every 5 minutes with my new changes while taking notes on a class.

Previously obsidian together with the [obsidian-git]() plugin satisfied this need by doing exactly what i wanted.
I am however using a think pad provided by my work which has some issues when using multiple electron based applications and i don't really like the vim implementation in obsidian.

So i thought to myself: _what a nice way to get something done for myself and learn go while I'm at it_.
So here it is, my small, minimal and configurable tool to sync your changes every `x` seconds with your git remote.

## Setup

### Installation

The installation is simple and straightforward, either build from source or install from the latest release.

#### Installing from Release

To get the latest executable without a lot of hassle follow the following three steps

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
mv xgs /usr/bin/xgs # might require super user privileges
```

You should now see a `xgs` executable in the directory

### Configuration

{{<callout type="Tip">}}
This section will probably change in the future so consult the documentation or the changelog to see if there are any breaking changes.

- [Documentation](https://github.com/xNaCly/x-git-sync/blob/master/README.md#x-git-sync)
  {{</callout>}}

`xgs` allows the user to change a whole lot using the config file located at:

- On Unix systems, `$XDG_CONFIG_HOME/xgs.json` or `$HOME/.config/xgs.json`
- On Darwin, `$HOME/Library/Application Support/xgs.json`
- On Windows, `%AppData%/xgs.json`
- On Plan 9, `$home/lib/xgs.json`

### Defaults

To view the default configuration shipped with `xgs`, take a look at the documentation [here](https://github.com/xNaCly/x-git-sync/blob/master/README.md#config-options-and-defaults)

Here is the default config, which (who would've guessed is my preferred way of using `xgs`):

```json
{
  "auto_commit_prefix": "backup: ",
  "commit_title_date_format": "2006-01-02 15:04:05",
  "add_affected_files": true,
  "backup_interval": 300,
  "commit_cmd": "git commit -m",
  "debug": false,
  "pull_on_start": true
}
```

## Usage

{{<callout type="Info"}}
`xgs` requires and calls to `git` for almost everything it does, make sure its installed and in the systems path
{{</callout>}}

To use `xgs` you simply navigate to a directory which has a git remote configured. After that run:

```bash
xgd
```

You'll see some logs and thats it, you are now syncing your repo every 300 seconds by default.

## Tips and tricks

### Configure commit title and body

### Configure interval between backups / commits

### Configure command used to make commit

### Configure pulling on starting
