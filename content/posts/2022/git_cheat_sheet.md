---
title: Git cheat sheet
summary: Small but sufficient cheat sheet that contains all absolutely necessary git commands for everyday use
date: 2022-12-01
draft: true
tags:
    - git
---

## Overview

> As always, text in between `<>` is meant to be replaced with your configuration / content.
> For example (in python)
> ```python
> print("coding is <emotion>")
> ```
> You can replace this however you want.
> Hint:
> ```python
> print("coding is pain")
> ```

After we got this out of the way.

I'll now explain the connection between Github and git: We first need to understand what exactly git is.

[Git](https://git-scm.com/) is a versioning tool, i.e. you upload changes you made to a project to have a kind of
backup. You can use git to go back to a previous backup.

-   `commit`: a backup, a part of the project, a version, a revision
-   `repository`: a project or a collection of backups

Git is the tool that allows you to create commits, jump back to older commits and upload them. Github is the website
that allows you to create repositories, manage them and much more, see [here](https://github.com/features).

Many people, including myself, use Github to collaborate and share code with the world.

> **INFO**:
> 
> all the following commands will need to be ran in the powershell on windows or in the terminal on linux

## How to authenticate

## Downloading (cloning) a project

*When cloning a repository, git downloads most of the data stored at the url, which includes past commits and files*

To clone a repository, one has to know the url of the repository and pass it to the `git clone` subcommand:

```bash {hl_lines=[3]}
git clone <url>
# for example clone this blog:
git clone https://github.com/xNaCly/blog.git
```

After cloning there will be a new folder in your current directory, by default:
- on windows: `C:/Users/<user>/`
- on linux: `~`

## Creating a new repository on github 

<!-- TODO: screenshots with numbers and which boxes to check -->
<!-- reponame: example -->

## Making changes
To modify your newly created repository, we first need to clone the repository:
```bash
git clone https://github.com/<username>/example # remember to replace <username> with your username
```
Next up we will modify the `Readme.md` created by hitting the check while creating the Github repository



## Uploading changes
