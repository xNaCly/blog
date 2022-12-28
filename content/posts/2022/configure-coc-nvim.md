---
title: "Install & Configure coc.nvim - PDE p.II"
date: 2022-12-28
summary: "Guide and example on how to configure the coc.nvim extension and lsp provider (config and keybinds)"
draft: true
tags:
- nvim
- PDE
---

> This is the second part of the personalized development environment series, [Part I]()

Coc allows us to install vscode extensions and use language servers originially written for vscode

## Installing coc

```lua
-- in nvim/lua/plugins.lua:

```

## Installing and using coc Extensions

To install extensions, coc exposes the `CocInstall` command:
```vim
:CocInstall <extension>
```

### Prettier

> Prettier is an opinionated code formatter. 
> It enforces a consistent style by parsing your code and re-printing 
> it with its own rules that take the maximum line length into account, wrapping code when necessary.

1. Install [Prettier](https://github.com/neoclide/coc-prettier):

   open neovim and run the following command: `:CocInstall coc-prettier`

2. register a new `:Prettier` command by putting the following in your `init.lua`

```lua
vim.cmd[[
    command! -nargs=0 Prettier :CocCommand prettier.forceFormatDocument
]]
```

3. reload the config by running `:source %`

## Coc keybindings:
```lua
-- helper for mapping new keybinds
function map(mode, lhs, rhs, opts)
    local options = { noremap = true }
    if opts then
        options = vim.tbl_extend("force", options, opts)
    end
    vim.api.nvim_set_keymap(mode, lhs, rhs, options)
end

-- **************************************
-- taken from the coc.nvim example config:
-- https://github.com/neoclide/coc.nvim
function _G.show_docs()
    local cw = vim.fn.expand('<cword>')
    if vim.fn.index({'vim', 'help'}, vim.bo.filetype) >= 0 then
        vim.api.nvim_command('h ' .. cw)
    elseif vim.api.nvim_eval('coc#rpc#ready()') then
        vim.fn.CocActionAsync('doHover')
    else
        vim.api.nvim_command('!' .. vim.o.keywordprg .. ' ' .. cw)
    end
end

function _G.check_back_space()
    local col = vim.fn.col('.') - 1
    return col == 0 or vim.fn.getline('.'):sub(col, col):match('%s') ~= nil
end
-- **************************************

-- show docs for the keyword under the cursor by pressing Shift+k
map("n", "K", "<CMD>lua _G.show_docs()<CR>", {silent = true})

-- go to the definition for the element under the cursor by pressing gd
map("n", "gd", "<Plug>(coc-definition)", {silent = true})
-- go to the references for the element under the cursor by pressing gr
map("n", "gr", "<Plug>(coc-references)", {silent = true})

local opts = {silent = true, noremap = true, expr = true, replace_keycodes = false}
-- enables autocomplete on space
map("i", "<TAB>", 'coc#pum#visible() ? coc#pum#confirm() : v:lua.check_back_space() ? "<TAB>" : coc#refresh()', opts)
```

## Coc configuration

> **Info**:
> 
> To get intellj sense for the config install the `coc-json`:
> ```text
> :CocInstall coc-json
> ```
> 
> - Read more about the configuration options [here](https://github.com/neoclide/coc.nvim/wiki/Using-the-configuration-file).

Coc can be configured via a json file at `~/.config/nvim/coc-settings.json`:

```json
{
  // enable inline diagnostics for all lines in the file
  "diagnostic.checkCurrentLine": true,
  "diagnostic.virtualTextCurrentLineOnly": false,
  "diagnostic.virtualText": true,

  // customise hint signs, i dislike the icons
  "diagnostic.hintSign": "H",
  "diagnostic.infoSign": "I",
  "diagnostic.errorSign": "E",
  "diagnostic.warningSign": "W",

  // make documentation window rounded and bordered
  "hover.floatConfig": {
    "border": true,
    "rounded": true
  },

  // make suggestions window rounded and bordered
  "suggest.virtualText": true,
  "suggest.enableFloat": true,
  "suggest.floatConfig": {
    "border": true,
    "rounded": true
  }
}
```

This config looks like this:
![coc showcase](/vim/coc.png)
![coc showcase 2](/vim/coc2.png)
