---
title: "Install & Configure coc.nvim - PDE p.II"
date: 2022-12-29
summary: "Guide and example on how to configure the coc.nvim extension and lsp provider (config and keybinds)"
tags:
  - nvim
  - PDE
---

> This is the second part of the personalized development environment series, every part depends heavily on the previous one
>
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

2. register a new `:Prettier` command by adding the highlighted lines in your `plugin-options.lua`

```lua {hl_lines=[28,29]}
-- set colorsheme
vim.cmd([[colorscheme tokyonight-night]])

-- bufferline config
require("bufferline").setup{
    options = {
        -- only display tabs, hide buffers
        mode = "tabs",

        -- style for kitty terminal
        separator_style = "slant",

        -- display coc diagnostics
        diagnostics = "coc"
    }
}

-- nvim tree setup
require("nvim-tree").setup()

-- lualine setup
require("lualine").setup{
    options = {
        theme = "palenight"
    }
}

-- registering :Prettier command
vim.cmd([[command! -nargs=0 Prettier :CocCommand prettier.forceFormatDocument]])
```

3. reload the config by running `:source %`

## Coc keybindings

Add the highlighted lines to the `keybindings.lua` file:

```lua {hl_lines=["19-30", "32-36", "38-43"]}
-- helper for mapping custom keybindings
-- source: https://gist.github.com/Jarmos-san/d46605cd3a795513526448f36e0db18e#file-example-keymap-lua
function map(mode, lhs, rhs, opts)
    local options = { noremap = true }
    if opts then
        options = vim.tbl_extend("force", options, opts)
    end
    vim.api.nvim_set_keymap(mode, lhs, rhs, options)
end

-- toggle the nvim tree sidebar with ctrl+b
map("n", "<C-b>", ":NvimTreeToggle<CR>", {silent = true})

-- move visual selection down with shift+J
map("v", "J", ":m '>+1<CR>gv=gv")
-- move visual selection up with shift+K
map("v", "K", ":m '<-2<CR>gv=gv")

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

-- autocomplete
function _G.check_back_space()
    local col = vim.fn.col('.') - 1
    return col == 0 or vim.fn.getline('.'):sub(col, col):match('%s') ~= nil
end

-- view the definition of the currently hovering over element
map("n", "gd", "<Plug>(coc-definition)", {silent = true})
-- view a list of the references of the currently hovering over element
map("n", "gr", "<Plug>(coc-references)", {silent = true})
-- view documentation for the currently hovering over element
map("n", "K", "<CMD>lua _G.show_docs()<CR>", {silent = true})
```

## Coc configuration

> **Info**:
>
> To get intellj sense for the config install the `coc-json`:
>
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
![coc showcase](/vim/coc.webp)
![coc showcase 2](/vim/coc2.webp)
