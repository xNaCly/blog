---
title: Git cheat sheet
summary: Small but sufficient cheat sheet that contains all absolutely necessary git commands for everyday use
date: 2022-12-01
draft: true
tags:
    - git
---

## Overview

To explain the connection between Github and git, we first need to understand what exactly git is.
[Git](https://git-scm.com/) is a versioning tool, i.e. you upload changes you made to a project to have a kind of
backup. You can use git to go back to a previous backup.

-   `commit`: a backup, a part of the project, a version, a revision
-   `repository`: a project or a collection of backups

Git is the tool that allows you to create commits, jump back to older commits and upload them. Github is the website
that allows you to create repositories, manage them and much more, see [here](https://github.com/features).

Many people, including myself, use Github to collaborate and share code with the world.

## How to authenticate

## Downloading (cloning) a project

To clone a repository, one has to know the url and pass it to the `git clone` subcommand:

```bash {hl_lines=[3]}
git clone <url>
# for example clone this blog:
git clone https://github.com/xNaCly/blog.git
```

## Making changes

## Uploading changes
