---
title: Git cheat sheet & Guide
summary: Small but sufficient cheat sheet and guide that contain all absolutely necessary git commands and flows for everyday use
date: 2022-12-01
draft: true
tags:
    - git
    - guide
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

To safely interact with out repository (which is hosted on github) from our local machine, we need to authenticate.

> A requirement for the following is a github account, if you dont have one yet go ahead and sign up on [github](https://github.com/)!

Lets go through a few settings and generate a token, which we will use to tell github its us whos trying to update the repositories:

1. Sign up for github or log into github
2. Click on the profile picture on the top right:
    ![](/gitcheat/go-to-settings.png)
3. After getting into the settings we now scroll all the way down and click on developer settings:
    ![](/gitcheat/dev-settings.png)
4. Now we click on the personal access tokens toggle and select the `Token (classic)->Generate new token (classic)` option
    ![](/gitcheat/token-flow.png)
5. In the next menu we input the name of the token (here: `local machine`), afterwards we set the expiration to none (*github recommonds not setting this option, even though its very convient*)
    ![](/gitcheat/token-flow1.png)
6. The next step is to select the permissions the token will hold (for this example we just allow read and write to repositories, note the small red box):
    ![](/gitcheat/token-flow2.png)
7. To finally create the token, scroll all the way down and hit the big generate now button:
    ![](/gitcheat/token-flow3.png)
8. Copy the created token by clicking on the button right next to the token

9. The 9th step contains a lot of stuff:

    Open a terminal and type the following commands:
```bash {hl_lines=[2, 6, 12]}
#tell git to store your credentials indefinitly
git config --global credential.helper store

# set your username exactly as the username you selected on github 
# (replace <username> with your username)
git config --global user.name "<username>"

# set your email exactly as the email you selected on github (replace with your username)
git config --global user.email "<example@example.com>"

# view if everything is stored:
git config --global --list
# should output:
# user.name=<username>
# user.email=<example@example.com>
```

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
```bash {hl_lines=[2]}
# remember to replace <username> with your username
git clone https://github.com/<username>/example 
```
Next up we will modify the `Readme.md` created by hitting the check while creating the Github repository


## Uploading changes
