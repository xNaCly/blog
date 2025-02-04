---
title: "Syntax Highlight for SQL in Diagnostics"
summary: "Adding syntax highlighting to SQL snippets in sqleibniz diagnostics"
date: 2025-02-04
draft: true
tags:
    - rust
    - sqleibniz
    - sql
---

This is the third article of my quest for improving the developer experience
around using sql:

1. [Making SQL Keyword Suggestions Work](/posts/2024/making-sql-keyword-suggestions-work/)
2. [Embedding Lua in sqleibniz with Rust](/posts/2024/embed-lua-in-rust/)

{{<callout type="TLDR">}}
I added syntax highlight to sqleibniz diagnostic output:

![sqleibniz diagnostic with syntax highlight](/syntax-highlight/sqleibniz.png)
{{</callout>}}

This time I was annoyed by tools like rustc for not applying syntax highlighting to diagnostics:

![rustc compilation error without syntax highlight](/syntax-highlight/rustc.png)

sqleibniz is also missing this feature:

![sqleibniz diagnostic without syntax highlight](/syntax-highlight/old_sqleibniz.png)

## String builder
## ANSI color escape codes
## Mapping Tokens to Colors 
## Highlighting module
## Attaching to diagnostic display
