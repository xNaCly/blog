---
title: "How to periodically sync a git repository with its remote"
summary: "A guide to updating a repository periodically using x-git-sync"
date: 2023-01-23
tags:
  - backup
  - go
  - sync
---

{{<callout type="Info">}}
x-git-sync is a minimal and highly configurable tool to automatically backup a git repository at configured intervals.
{{</callout>}}

{{<rawhtml>}}
<video style="margin-top: 2rem; border-radius: var(--spacing)" width=100% controls autoplay>

<source src="/xgs/demo.mp4" type="video/mp4">
Your browser does not support the video tag.  
 </video>
{{</rawhtml>}}

## Possible use cases

I wrote this tool to fit my need for uploading a new version of my uni documents vault every 5 minutes with my new changes while taking notes on a class.

Previously obsidian together with the [obsidian-git](https://github.com/denolehov/obsidian-git) plugin satisfied this need by doing exactly what i wanted.
I am however using a think pad provided by my work which has some issues when using multiple electron based applications and i don't really like the vim implementation in obsidian.

So i thought to myself: _what a nice way to get something done for myself and learn go while I'm at it_.
So here it is, my small, minimal and configurable tool to sync your local changes with your git remote changes every `x` seconds.

## Setup

### Installation

The installation is simple and straightforward, either build from source or install from the latest release.

#### Installing from Release

To get the latest executable without a lot of hassle follow the following three steps

- navigate to [x-git-sync/Releases](https://github.com/xNaCly/x-git-sync/releases/),
  download the `xgs_...` executable, rename it to `xgs`
- move the executable to the `$PATH`: `mv ./xgs /usr/bin/xgs`
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

{{<callout type="Info">}}
`xgs` requires and calls to `git` for almost everything it does, make sure its installed and in the systems path
{{</callout>}}

To use `xgs` you simply navigate to a directory which has a git remote configured. After that run:

```bash
xgd
```

You'll see some logs and that's it, you are now syncing your repo every 300 seconds by default.

## Tips and tricks

This section contains some configuration tips and tricks.

### Configure commit title and body

The commit title `xgs` generates is concatenated using the following format:

```text
{auto_commit_prefix} {commit_title_date_format}\n\n
{add_affected_files}
```

Use the following `xgs.json` key value pairs to customize the format:

- `auto_commit_prefix` to specify the commit title prefix, by default it's set to `"backup: "`.
- `commit_title_date_format` to specify the commit date and time format, the default is: `"2006-01-02 15:04:05"`
  - the formatting of dates in go is a little unconventional: (taken from the `xgs` documentation)
  ```json
  // specifies the date format which the date will be formatted as
  //
  //  - 2006 for the year, 06 would only be the last two integer
  //  - 01 for the month
  //  - 02 for the day
  //  - 15 for the hour (24-hour format), 05 for 12-hour format
  //  - 04 for the minute
  //  - 05 for the second
  //
  // time formatting in go is weird, see docs:
  //
  // https://www.digitalocean.com/community/tutorials/how-to-use-dates-and-times-in-go
  "commit_title_date_format": "2006-01-02 15:04:05",
  ```
- `add_affected_files` to specify whether or not `xgs` should display the changed files in its commits:

  - `add_affected_files: false`:

    ```text
      backup: 2023-01-23 09:22:45
    ```

  - `add_affected_files: true`:

    ```text
      backup: 2023-01-23 09:22:45

      Affected files:
      out.gif (added)
      xgs.tape (modified)
    ```

### Configure interval between backups / commits

Simply set the `backup_interval` to any amount you desire (its in seconds)

### Configure command used to make commit

By default `xgs` uses the `git commit -m` command to create a git commit, if you need different arguments i got your back, just set `commit_cmd` to something different.

### Configure pulling on starting

If you want `xgs` to not pull all changes from the remote on startup set the `pull_on_start` setting to `false`.

### View verbose logs

If you're interested in the inner workings of `xgs` and want to see debug logs, either set the `debug` flag to `true` or invoke `xgs` like so:

```bash
xgs --debug
```
