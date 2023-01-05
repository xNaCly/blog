---
title: "Top 10 neovim plugins"
date: 2023-01-05
summary: "Top 10 neovim plugins everyone needs"
tags:
  - nvim
---

My nvim config including plugins and keybindings can be found [here](https://github.com/xNaCly/dotfiles/blob/master/nvim/lua/plugins.lua)

{{<callout type="Vim plug">}}
You'll need the following in your `nvim/lua/plugins.lua`.

See my guide on [Getting started with Neovim](/posts/2022/neovim-ped-1/) for an in depth understanding of configuring Neovim.

```lua
-- check if vimplug is installed, if not install it
vim.cmd([[
if empty(glob('~/.config/nvim/autoload/plug.vim'))
  silent !curl -fLo ~/.config/nvim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
endif
]])

local Plug = vim.fn['plug#']
vim.call('plug#begin', '~/.config/nvim/plugged')
    -- add plugins you want to install here
vim.call('plug#end')
```

{{</callout>}}

## 1. auto-pairs

Insert or delete brackets, parens, quotes in pair

Add to neovim:

```lua
    -- automatically add "([ pairs if first one is typed
    Plug 'jiangmiao/auto-pairs'
```

- [Github](https://github.com/jiangmiao/auto-pairs)

## 2. vim-commentary

Work with comments, vim commentary allows you to toggle the comment of the current visual selection using `gc`.
Knows what file type wants which comment prefix / style.

```lua
    -- comment helper
    Plug 'tpope/vim-commentary'
```

- [Github](https://github.com/tpope/vim-commentary)

## 3. nvim-tree and nvim-web-devicons

File explorer written in lua. Its fast, watches for changes and allows basic file management.

```lua
    -- file explorer
    Plug 'nvim-tree/nvim-tree.lua'
    -- icons for everything, file explorer, tabs, statusline
    Plug 'nvim-tree/nvim-web-devicons'
```

- [Github nvim-tree](https://github.com/nvim-tree/nvim-tree.lua)
- [Github nvim-web-devicons](https://github.com/nvim-tree/nvim-web-devicons)

## 4. toogle-term

A neovim lua plugin to help easily manage multiple terminal windows

```lua
    -- toggle floating term
    Plug 'akinsho/toggleterm.nvim'
```

- [Github](https://github.com/akinsho/toggleterm.nvim)

{{<callout type="Hint">}}

#### Keybind for toggling the terminal window

```lua
-- toggleterm tree setup
require("toggleterm").setup{
    open_mapping = [[<c-J>]],
    direction = 'float',
}
```

{{</callout>}}

## 5. coc.nvim

Nodejs extension host for vim & neovim, load extensions like VSCode and host language servers.

Specifically usefull for language server integration (linting, formatting)

{{<callout type="Hint">}}
Take a look at my guide for coc.nvim: [Install & Configure coc.nvim](/posts/2022/configure-coc-nvim/).

I cover the following topics:

- installation
- installation of extension
- keybindings
- configuration
  {{</callout>}}

```lua
    -- vscode extension provider
    Plug 'neoclide/coc.nvim'
```

- [Github](https://github.com/neoclide/coc.nvim)

## 6. fzf.vim

Fuzzy finder for files via names and text content.

{{<callout type="Hint">}}
For in depth installation, configuration and keybindings take a look at my guide for fzf.nvim here: [Install & Configure FzF in Neovim](/posts/2023/configure-fzf-nvim/).
{{</callout>}}

```lua
    -- fuzzy finder
    Plug('junegunn/fzf', { ['do'] = vim.fn['fzf#install()'] })
    plug('junegunn/fzf.vim')
```

- [Github](https://github.com/junegunn/fzf.vim)

## 7. lualine.nvim

Fast and easy to configure neovim statusline plugin.

```lua
    -- status line
    Plug 'nvim-lualine/lualine.nvim'
```

- [Github](https://github.com/nvim-lualine/lualine.nvim)

{{<callout type="Hint">}}

#### Set a theme:

```lua
-- lualine
require('lualine').setup {
  options = {
    theme = bubbles_theme,
    }
}
```

{{</callout>}}

## 8. bufferline.nvim

Plugin to better display buffers and tabs.

```lua
    -- display buffers and tabs nicely
    Plug 'akinsho/bufferline.nvim'
```

- [Github](https://github.com/akinsho/bufferline.nvim)

{{<callout type="Hint">}}

#### Only display tabs not buffers:

```lua
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
```

{{</callout>}}

## 9. vim-startify

Clean starting dashboard

```lua
    -- startup interface
    Plug 'mhinz/vim-startify'
```

- [Github](https://github.com/yggdroot/indentLine)

## 10. indentLine

Plugin to highlight indentations, such as tab stops.

```lua
    -- highlights indent
    Plug 'yggdroot/indentLine'
```

- [Github](https://github.com/yggdroot/indentLine)

## Honorable mentions

### Color theme

My current fav vim theme is: [Tokyonight](https://github.com/folke/tokyonight.nvim)

**Installing**:

```lua
    -- color theme / sheme
    Plug('folke/tokyonight.nvim', { branch = 'main' })
```

**Setting the theme**

```lua
-- set colorsheme
vim.cmd([[colorscheme tokyonight-night]])
```

### Syntax highlighter and ast generator

```lua
    -- syntax highlighting and parser
    Plug(
        'nvim-treesitter/nvim-treesitter',
        {['do'] = vim.fn['TSUpdate']}
    )
```

### Time tracking with wakatime

```lua
    -- time tracking
    Plug 'wakatime/vim-wakatime'
```
