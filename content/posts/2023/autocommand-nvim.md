---
title: "Autocommand Nvim"
summary: Short guide to adding autocommands to neovim using lua (allows formatting before saving)
date: 2023-01-07
draft: true
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

```lua
-- prettier command
vim.cmd([[command! -nargs=0 Prettier :CocCommand prettier.forceFormatDocument]])

-- run prettier before saving
vim.api.nvim_create_autocmd("BufWritePre", {
  pattern = "*.*",
  callback = function () vim.cmd([[:Prettier]]) end,
})
```

## Example: run prettier before saving a file:
