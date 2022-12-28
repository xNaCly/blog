---
title: "Install & Configure coc.nvim - PDE p.II"
date: 2022-12-28
summary: "Guide and example on how to configure the coc.nvim extension and lsp provider (config and keybinds)"
draft: true
tags:
- nvim
- PDE
---

> This is the second part of the personalized development environment series, every part depends heavily on the previous one 
> - Prev part: [Part I](/posts/2022/neovim-ped-1/)
> - ~~Next part: [Part III](/posts/2022/configure-fzf-nvim/)~~

Coc allows us to install vscode extensions and use language servers originially written for vscode

## Installing coc

Add the highlighted lines 16 and 17 to `nvim/lua/plugins.lua`

```lua {hl_lines=[16,17]}
-- i use vimplug to manage my plugins
-- this checks if vimplug is installed, if not install it
vim.cmd([[
if empty(glob('~/.config/nvim/autoload/plug.vim'))
  silent !curl -fLo ~/.config/nvim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
endif
]])

-- assign variable
local Plug = vim.fn['plug#']


-- in between this we call Plug to specify plugins
vim.call('plug#begin', '~/.config/nvim/plugged')
    -- vscode extension provider
    Plug 'neoclide/coc.nvim'

    -- display buffers and tabs nicely
    Plug 'akinsho/bufferline.nvim'


    -- color theme / sheme
    Plug('folke/tokyonight.nvim', { branch = 'main' })


    -- comment helper
    Plug 'tpope/vim-commentary'


    -- status line
    Plug 'nvim-lualine/lualine.nvim'


    -- file explorer
    Plug 'nvim-tree/nvim-tree.lua'


    -- icons for everything, file explorer, tabs, statusline
    Plug 'nvim-tree/nvim-web-devicons'


    -- automatically add "([ pairs if first one is typed
    Plug 'jiangmiao/auto-pairs'


    -- startup interface
    Plug 'mhinz/vim-startify'

vim.call('plug#end')
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
```

3. reload the config by running `:source %`

## Coc keybindings
```lua
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
