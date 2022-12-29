---
title: "Getting started with Neovim - PDE p.I"
date: 2022-12-27
summary: "Installation, configuration and usage guide"
tags:
- nvim
- PDE
---

> This is the first part of the personalized development environment series
> - Next part: [Part II](/posts/2022/configure-coc-nvim/)

## Prerequisites
The reader of this guide needs to know the basics of:
- Vim motions and keys
- opening and saving files in Vim

Learn [here](https://www.youtube.com/watch?v=X6AR2RMB5tE&list=PLm323Lc7iSW_wuxqmKx_xxNtJC_hJbQ7R), [here](https://www.youtube.com/watch?v=5JGVtttuDQA&list=PLm323Lc7iSW_wuxqmKx_xxNtJC_hJbQ7R&index=3) and [here](https://www.youtube.com/watch?v=KfENDDEpCsI&list=PLm323Lc7iSW_wuxqmKx_xxNtJC_hJbQ7R&index=4)

## Abstract
The pde series is intended to provide a simple guide for a new neovim user to learn about configuring the editor.

The series will cover:
- neovim config with lua
- config setup and dir structure
- must have plugins and their configurations i use
    - language servers
    - fuzzy finders
- theming with lualine, bufferline

This part covers:
- neovim config with lua
    - options
    - first plugins
    - plugin options
    - custom keybindings
- config setup 
- config dir structure


More info:
- Neovim documentation is located [here](https://neovim.io/doc/)
- My configuration can be found [here](https://github.com/xNaCly/dotfiles/tree/master/nvim)

## Installing
To install read the neovim [wiki](https://github.com/neovim/neovim/wiki/Installing-Neovim).

**Hint**:
If you are on a linux system use your package manager to install neovim:
```bash
sudo pacman -S neovim
sudo apt install neovim
```

**Hint** 2:
For windows I'd recommend installing scoop in the powershell and using it to install neovim
```powershell
# allow executing remote scripts
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# install scoop
irm get.scoop.sh | iex
# install neovim using scoop
scoop install neovim
```

## Config
Neovim can be configured using Vimscript[^vimscript] or Lua[^lua] - 
I'd recommend the second option over the first, simply because Lua is a real programming language which also is:
- minimal and powerful
- widely used[^luausers] 
- well documented[^luadocs]
- fast [^luavsvs] 

This guide will use Lua,
due to the fact that I noticed significant performance improvements using lua instead of vimscript.



### Config guide
#### Config path
Config paths differ on windows compared to those on a unix system.
I use Windows sometimes, therefore I included the following windows guide additionally to the unix guide.


Configuration paths for Neovim, more info [here](https://wiki.archlinux.org/title/Neovim#Configuration):
- Windows:
- `C:\Users\<username>\AppData\Local\nvim`

- Unix:
- `$XDG_CONFIG_HOME/nvim`
- `~/<username>/.config/nvim`

#### Config layout
```text
nvim/
|   coc-settings.json
|   init.lua
|
\---lua/
    keybindings.lua
    options.lua
    plugin-options.lua
    plugins.lua
```

1. Create the `nvim` folder
2. Create the `lua` folder in the nvim folder
3. create the `init.lua` file in the nvim folder
4. create the following files in the `nvim/lua` folder:
    - `keybindings.lua`: we will create new keybindings here
    - `options.lua`: general options
    - `plugin-options.lua`: options for plugins
    - `plugins.lua`: specify plugins we need


#### Configuring

*If any of the following options are not commented well enough, start neovim and run:*

`:help <option>`


> After each step save and reload the config using `:source %`

1. Open `nvim/init.lua` and enter the following configuration:
```lua
-- lua automatically adds all .lua 
-- files in the nvim/lua directory to the namespace

-- order of import is relevant,
-- plugins have to be installed before configuring them

-- import the options
require("options")
-- import the plugins
require("plugins")
-- import the plugin options
require("plugin-options")
-- import the keybinds
require("keybindings")
```

2. Open `nvim/lua/options.lua` and enter the following configuration:
```lua
-- bind variables
local g = vim.g
local o = vim.opt

-- set the leader key to space
g.mapleader = " "

-- disable default file tree
g.loaded_netrw = 1
g.loaded_netrwPlugin = 1
g.netrw_banner = 0
g.netrw_winsize = 0

-- enable line numbers
o.number = true

-- dont save buffers on closing them
o.hidden = true

-- enable syntax highlighting
o.syntax = "on"

-- disable wrapping chars which are out of the current view
o.wrap = false

-- set encodings
o.encoding = "utf-8"
o.fileencoding = "utf-8"

-- more space for commands at the bottom
o.cmdheight = 2

-- enable better splitting
o.splitbelow = true
o.splitright = true

o.conceallevel = 0

-- indentation, 4 spaces for a tab
o.tabstop = 4
o.shiftwidth = 4

-- automatically insert tabs
o.smarttab = true

-- replace tab with spaces
o.expandtab = true

-- indent blocks automatically
o.smartindent = true
o.autoindent = true

-- enable tabline if a tab is there
o.showtabline = 1

-- dont show mode in the bottom bar
o.showmode = false

-- set updatetime to 50ms (updates every 50ms)
o.updatetime = 50
o.timeoutlen = 500

-- enable better colors
o.termguicolors = true

-- better searching
o.incsearch = true
o.smartcase = true
o.hlsearch = false

-- disable backups
o.backup = false
o.background = "dark"

-- display the current line different from the rest of the file
o.cursorline = true

-- disable swap files
o.swapfile = false
```

3. Open `nvim/lua/plugins.lua` and enter the following configuration:
```lua
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

4. Open `nvim/lua/plugin-options.lua` and enter the following configuration:
```lua
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
```

4. Open `nvim/lua/keybindings.lua` and enter the following configuration:
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

-- toggle the nvim tree sidebar with ctrl+b
map("n", "<C-b>", ":NvimTreeToggle<CR>", {silent = true})

-- move visual selection down with shift+J
map("v", "J", ":m '>+1<CR>gv=gv")
-- move visual selection up with shift+K
map("v", "K", ":m '<-2<CR>gv=gv")
```

## Before and after

![before after](/vim/before_after.webp)
*Left the now configured neovim, right the stock neovim*

## Foreshadowing 
After setting the foundation by installing plugins, setting options and configuring keybinds we will move on to configuring language servers and fuzzy finders.
This and more in Part `II` and Part `III`.



[^vimscript]: https://vimdoc.sourceforge.net/htmldoc/usr_41.html
[^lua]: https://www.lua.org/
[^luadocs]: https://www.lua.org/manual/5.4/
[^luavsvs]: https://sr.ht/~henriquehbr/lua-vs-vimscript/
[^luausers]: https://en.wikipedia.org/wiki/Category:Lua_(programming_language)-scriptable_software
