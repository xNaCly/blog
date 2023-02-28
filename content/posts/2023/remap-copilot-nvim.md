---
title: "Remap Copilot suggestions in Nvim with Lua"
summary: Snippet to remap accepting copilot suggestions
date: 2023-02-28
tags:
  - nvim
  - copilot
---

> My [coc.nvim](https://github.com/neoclide/coc.nvim) config allows me to accept suggestions using `TAB`.
> Copilot however also accepts suggestions using `TAB`.
> These two settings conflict for me, therefore i remapped accepting copilots suggestions to `<C-Enter>`.

{{<callout type="Info">}}
If you don't know your paths for configuring neovim i recommend reading the official [documentation]() or my blog series on it:

1. [Part](/posts/2022/neovim-ped-1/)
2. [Part](/posts/2022/configure-coc-nvim/)
3. [Part](/posts/2023/configure-fzf-nvim/)

TLDR:

your neovim config is at `~/.config/nvim/init.lua`, modify it and insert the following lua code snippets into it and restart nvim to apply the changes
{{</callout>}}

## Disable default keybind

The copilot documentation (`:help copilot-maps`) tells us to set `g:copilot_no_tab_map` to `true`. With lua we can do this by modifying this global option using the following snippet:

```lua
vim.g.copilot_no_tab_map = true
```

This disables accepting copilot suggestions on `TAB`.

## Map a key to accepting suggestions

The above referenced documentation also displays a snippet for binding `<C-J>` (Control+J) to accepting copilot suggestions.

```vim
imap <silent><script><expr> <C-J> copilot#Accept("\<CR>")
```

This snippet is written with vim script so we need to translate this to lua using a fancy key mapping helper I introduced in Part II of the personalized development environment series: [post](/posts/2022/neovim-ped-1/#configuring).

```lua
-- helper for mapping custom keybindings
-- source: https://gist.github.com/Jarmos-san/d46605cd3a795513526448f36e0db18e#file-example-keymap-lua
function map(mode, lhs, rhs, opts)
    local options = { noremap = true }
    if opts then
        options = vim.tbl_extend("force", options, opts)
    end
    vim.api.nvim_set_keymap(mode, lhs, rhs, options)
end
```

To translate the mapping while keeping in mind we want to use `<C-Enter>` to accept the suggestion we can write the following:

```lua
-- i: only map the keybind to insert mode
-- <C-Enter>: execute on ctrl+Enter
-- copilot#Accept("<CR>") function to execute,
--      argument is inserted if no suggestion found
-- options:
--  - silent:
--      execute function without logging it in the command bar at the bottom
map("i", "<C-Enter>", "copilot#Accept('<CR>')", { silent = true, expr = true })
```
