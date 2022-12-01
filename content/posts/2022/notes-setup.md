---
title: "How to write notes in University"
date: 2022-09-23
slug: notes
summary: An overview of my note setup
tags:
    - uni
    - markdown
---

## Note taking

I write all my university notes in obsidian, and have a generic, but well thought through system.

The root directory consists of 4 elements:

```bash
ls
# _templates  Privates  Uni  Vault.md
```

-   `_templates` includes templates, i currently only use one for class notes
-   `Privates` contains work and private life content
-   `Uni` contains all my university notes, scripts etc
-   `Vault.md` is the Vault (_a obsidian specific term, eq: Project, Workspace_) entry point

### Folder and Note System

```bash
pwd
# /home/-/documents/Uni
ls -la
# total 28
# drwxrwx---+ 1 - -    0 14. Sep 14:57 .
# drwxrwx---+ 1 - -    0 23. Sep 16:15 ..
# drwxrwx---+ 1 - -    0 13. Sep 15:18 00_Scripte
# drwxrwx---+ 1 - -    0 13. Sep 15:18 01_Semester
# drwxrwx---+ 1 - -    0 31. Aug 12:07 02_Semester
# drwxrwx---+ 1 - -    0 23. Sep 10:14 03_Semester
# drwxrwx---+ 1 - -    0 14. Sep 14:57 07_Arbeiten
# -rwxrwx---+ 1 - - 1863 14. Sep 14:59 Uni.md
cd 03_Semester
ls -la
# total 36
# drwxrwx---+ 1 - -   0 23. Sep 10:14  .
# drwxrwx---+ 1 - -   0 14. Sep 14:57  ..
# drwxrwx---+ 1 - -   0  6. Sep 10:30  00_Webengineering_II
# drwxrwx---+ 1 - -   0 13. Sep 13:44  01_Netztechnik
# drwxrwx---+ 1 - -   0 21. Sep 09:05 '03_Formale Sprachen'
# -rwxrwx---+ 1 - - 586 23. Sep 11:44  03_Semester.md
# drwxrwx---+ 1 - -   0 14. Sep 15:04 '04_Systemnahe Programmierung'
# drwxrwx---+ 1 - -   0 16. Sep 08:15 '05_Software Engineering'
# drwxrwx---+ 1 - -   0 23. Sep 11:44  06_Datenbanken
```

Every folder starts with two integers, depending on the order of the appearance of the class in the current semester and
the class name separated by `_`.

Every folder also includes a markdown file with the folders name. This file contains links to the notes contained in the
current folder.

![folder-markdown](/notes/folder_markdown.webp)

This is required because otherwise obsidian won't display the link connection in the graph view.

As seen in the screenshot above, my files follow a convention too.

University notes for a single class are prefixed by a abbreviation of the class name and the current date separated by
`_`.:

```text
xx_YYYY_mm_DD.md

e.g.: se_2022_09_10.md
-> Software Engineering on the 10th September 2022
```

### Application of choice

My go to application for taking notes is obsidian, i chose obsidian because it stores all contents in
[markdown](https://help.obsidian.md/How+to/Format+your+notes).

Obsidian supports a wide array of markdown add-ons, plugins other useful stuff for university, such as:

-   graph view ![graph-view](/notes/graph.webp)
-   callouts (better blockquotes) ![callout](/notes/callouts.webp)
-   diagrams with mermaidjs ![diagram](/notes/mermaidjs.webp)
-   LaTeX ![latex](/notes/latex.webp)

(_obsidian has a vim plugin_) 😁

## Note syncing

I use the obsidian-git[^obsidian-plugin] configured to backup my changes to a git repo hosted on GitHub every 5 minutes.

This plugin requires git to be installed, git credentials being set up and the vault needs to be in a git repository.

[^obsidian-plugin]: https://github.com/denolehov/obsidian-git
