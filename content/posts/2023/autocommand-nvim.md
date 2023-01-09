---
title: "Using autocommands with the new neovim api"
summary: Short guide to adding autocommands to neovim using lua with the vim.api.nvim_create_autocmd interface
date: 2023-01-07
tags:
  - nvim
---

## Define autocommands

{{<callout type="Hint">}}
As always, for help and more infos, see:

```vim
:help nvim_create_autocmd()
```

or neovims online docs:

- [nvim_create_autocmd]()
- [Events](https://neovim.io/doc/user/autocmd.html#autocmd-events)
- [Patterns](https://neovim.io/doc/user/autocmd.html#autocmd-pattern)

{{</callout>}}

## Run a command before saving a file

```lua
-- run the following just before saving
vim.api.nvim_create_autocmd("BufWritePre", {
  pattern = "*.*",
  callback = function () print("hello world") end,
  -- you wont see any output due to neovim
  -- overwriting the output with the written file output
})
```

## Run Prettier before saving a file

If you followed the [configure-coc-nvim](/posts/2022/configure-coc-nvim/#installing-and-using-coc-extensions) guide,
you already have the `Prettier` command defined. We want to run `:Prettier` on every save for every file type we open.
This can be archived by using the `nvim_create_autocmd` function together with the `vim.cmd` interface:

```lua
vim.api.nvim_create_autocmd("BufWritePre", {
  pattern = "*.*",
  callback = function () vim.cmd(":Prettier") end,
})
```
