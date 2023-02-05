---
title: Git cheat sheet & Guide
summary: Small but sufficient cheat sheet and guide that contain all absolutely necessary git commands and flows for everyday use (intended for beginners)
date: 2023-02-04
tags:
  - git
  - guide
---

## Overview

{{<callout type="Tip">}}
As always, text in between `<>` is meant to be replaced with your configuration / content.
For example (in python)

```python
print("coding is <emotion>")
```

You can replace this however you want.

```python
print("coding is fun")
```

{{</callout>}}

After we got this out of the way.

I'll now explain the connection between Github and git: We first need to understand what exactly git is.

[Git](https://git-scm.com/) is a versioning tool, i.e. you upload changes you made to a project to have a kind of
backup. You can use git to go back to a previous backup.

- `commit`: a backup, a part of the project, a version, a revision
- `repository`: a project or a collection of backups
- `remote`: the origin / url of the repository

Git is the tool that allows you to create commits, jump back to older commits and upload them. Github is the website
that allows you to create and host repositories, manage them and much more, see [here](https://github.com/features).

Many people, including myself, use Github to collaborate and share code with the world.

{{<callout type="Danger">}}

This guide requires git to be installed on your system, download the installer from [here](https://git-scm.com/download/win).

All the following commands will need to be ran in the powershell or the cmd on windows or in the terminal on linux and hit enter.

- to access the command line on windows you can hit `WINDOWS+R` to open the run prompt, now type `cmd` and hit enter.
- on linux just search for the terminal, you'll find it

{{</callout>}}

## How to authenticate

To safely interact with out repository (which is hosted on github) from our local machine, we need to authenticate.

{{<callout type="Warning">}}
A requirement for the following is a github account, if you dont have one yet go ahead and sign up on [github](https://github.com/)!
{{</callout>}}

Lets go through a few settings and generate a token, which we will use to tell github its us whos trying to update the repositories:

1. Sign up for github or log into github
2. Click on the profile picture on the top right:
   ![](/gitcheat/go-to-settings.png)
3. After getting into the settings we now scroll all the way down and click on developer settings:
   ![](/gitcheat/dev-settings.png)
4. Now we click on the personal access tokens toggle and select the `Token (classic)->Generate new token (classic)` option
   ![](/gitcheat/token-flow.png)
5. In the next menu we input the name of the token (here: `local machine`), afterwards we set the expiration to none (_github recommonds not setting this option, even though its very convient_)
   ![](/gitcheat/token-flow1.png)
6. The next step is to select the permissions the token will hold (for this example we just allow read and write to repositories, note the small red box):
   ![](/gitcheat/token-flow2.png)
7. To finally create the token, scroll all the way down and hit the big generate now button:
   ![](/gitcheat/token-flow3.png)
8. Copy the created token by clicking on the button right next to the token

9. The 9th step contains a lot of stuff:

   Open a terminal and type the following commands:

```bash {hl_lines=[2, 6, 12]}
# tell git to store your credentials indefinitly
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

## Creating a new repository on github

<!-- TODO: screenshots with numbers and which boxes to check -->
<!-- reponame: example -->

1. Navigate to your GitHub homepage ([here](https://github.com))
2. Click on the profile picture in the top right corner and select `Your repositories` in the newly opened drop-down menu:
   ![](/gitcheat/repo-flow.png)
3. Once navigated to the repository overview we simply click on the green `New` button in the top right corner:
   ![](/gitcheat/repo-flow1.png)
4. Now we input a repository name (Sub step 1), a description (Sub step 2), select whether or not to make the repo public (Sub step 3) and tell github if it should create a README file in our repository (Sub step 4). After that we hit `Create repository` (Sub step 5).
   ![](/gitcheat/repo-flow2.png)
5. For the following chapter we need the url to the project, either copy it from the url bar or follow the quick 2 step guide:
   ![](/gitcheat/repo-flow3.png)
   - click on the `Code` button
   - click on the copy icon button next to the url to copy it

## Downloading (cloning) a project

{{<callout type="Info">}}
When cloning a repository, git downloads most of the data stored at the url, which includes past commits and files
{{</callout>}}

To clone a repository, one has to know the url of the repository and pass it to the `git clone` subcommand:

```bash
# clone your newly created project:
git clone https://github.com/<username>/<project>
# copy the following and paste the url from the previous chapter at the end (keep a space between clone and your url)
git clone
```

After cloning there will be a new folder in your current directory and there will be output on your terminal similar to this:

![](/gitcheat/git-clone.png)

- Newly created directory:
  - on linux: `~/<reponame>`
  - on windows: `C:/Users/<user>/<reponame>`

## Making changes

{{<callout type="Warning">}}
To modify your newly created repository, you first need to clone your repo (see the previous chapter for help on that).
{{</callout>}}

We will now modify the `Readme.md` created by hitting the check while creating the Github repository.

Open the README.md file in the directory on your system in any editor you want, for me its vim:

![](/gitcheat/modify-flow.png)

Make a change, save the file:

![](/gitcheat/modify-flow1.png)

{{<callout type="Tip">}}
To view the changes you made run `git diff` in the directory which is the newly cloned repo.

Output of running `git diff` after i modified the `README.md` file:

```diff
diff --git a/README.md b/README.md
index 9716b1d..fe185f3 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,5 @@
 # Test-repo
+
 test repos description
+
+this is a change / modification
```

The diff highlights the changes made. Two empty lines and a new paragraph were added. (Additions are annotated with `+`, modifications with `~` and deletions with `-`)

{{</callout>}}

## Creating a commit

As i outlined in the introductory chapter a commit is a revision or a backup which we want to add to the repository's history.
This commit has a title and a list of changes which we made. A commits title should describe the changes made in it.

We modified the README and added a new paragraph, so we write exactly that in the commit title:

```bash
# tell git what file to include in the commit we want to create
# the -A flag tells git to include all modified files in the repo
git add -A
# git commit creates the commit with the changes we told it to include using git add
# the -m flag tells git to set the following in "" as the commit message
git commit -m "added new paragraph to readme"
```

The output of `git commit` highlights the changes we made as well as the commit title we specified.:

```text
[master a8fee7b] added new paragaph to readme
 1 file changed, 3 insertions(+)
```

## Uploading changes

To upload the commit we created we tell git to push:

```bash
git push
```

Result:
![](/gitcheat/git-push.png)

## Viewing the changes

After we made the changes, created a new commit and pushed it to the remote we can now go back to the web browser and reload the repository page:

![](/gitcheat/changes-in-repo.png)

- take a look at (`1`) which displays the last commit which was pushed to the remote, thats the commit we made
- now look at (`2`) which displays the change we made to the README.

## Wrapping up:

{{<callout type="Info">}}
All of the above can be done using [GitHub desktop](https://desktop.github.com/) which includes git and authenticates without having to use the terminal or remember any git commands.
{{</callout>}}

You are now able to

- understand the basics of git and github
- authenticate to github using git
- create a new repository
- create a new commit
- upload / push this commit to the newly created repository
- view these changes and the commit on github
