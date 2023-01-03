---
title: "Install & Configure FzF in Neovim - PDE p.III"
date: 2023-01-03
summary: "Guide to using fzf in neovim with preview and keybinds"
tags:
    - nvim
    - PDE
---

{{<callout type="Info">}}
This is the third part of the personalized development environment series, every part depends heavily on the previous
one

-   Prev part: [Part II](/posts/2022/configure-coc-nvim/)
{{</callout>}}


Fzf is a fuzzy file finder. It supports searching for files and searching for text in these files with a preview.

## Installing
{{<callout type="Warning">}}
#### Requirements
- I use [bat](https://github.com/sharkdp/bat) for previewing file contents while searching. Install instructions [here](https://github.com/sharkdp/bat#installation)
- For full text search install [ripgrep](https://github.com/BurntSushi/ripgrep). Install instructions [here](https://github.com/BurntSushi/ripgrep#installation)
{{</callout>}}

To install fzf, add the following highlighted lines to your `nvim/lua/plugins.lua`:
```lua {hl_lines=["15-17"]}
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
    -- fuzzy finder
    Plug('junegunn/fzf', { ['do'] = vim.fn['fzf#install()'] })
    Plug('junegunn/fzf.vim')

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

As always save the file with `:w` and source it using `:source %`. Now install the plugins using `:PlugInstall`.
## Configuring
### Keybinds
The default keybindings i use for fzf and ripgrep are `Leader+f` and `Leader+p`.

To configure these keybinds add the following to your `nvim/lua/keybinds.lua`:

```lua {hl_lines=["41-44"]}
-- helper for mapping custom keybindings
-- source: https://gist.github.com/Jarmos-san/d46605cd3a795513526448f36e0db18e#file-example-keymap-lua
function map(mode, lhs, rhs, opts)
    local options = { noremap = true }
    if opts then
        options = vim.tbl_extend("force", options, opts)
    end
    vim.api.nvim_set_keymap(mode, lhs, rhs, options)
end

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

-- toggle the nvim tree sidebar
map("n", "<C-b>", ":NvimTreeToggle<CR>", {silent = true})

-- on space f open fzf for files
map("n", "<Leader>f", ":FZF<CR>", {silent = true})
-- on space p open ripgrep for strings in files
map("n", "<Leader>p", ":Rg<CR>", {silent = true})

-- move visual selection down
map("v", "J", ":m '>+1<CR>gv=gv")
-- move visual selection up
map("v", "K", ":m '<-2<CR>gv=gv")

-- use Tab to trigger completion for the currently selected completion
local opts = {silent = true, noremap = true, expr = true, replace_keycodes = false}
map("i", "<TAB>", 'coc#pum#visible() ? coc#pum#confirm() : v:lua.check_back_space() ? "<TAB>" : coc#refresh()', opts)
```

### Cosmetic

We will now configure fzf and ripgrep to show a preview and use a bigger window.
To apply this config add the following highlighted lines to your `nvim/lua/plugin-options.lua`:

```lua {hl_lines=["4-6"]}
-- set colorsheme
vim.cmd([[colorscheme tokyonight-night]])

-- define fzf config, window size, preview using bat, etc
vim.cmd([[let g:fzf_layout = {'window': {'width': 0.9, 'height': 0.9}}]])
vim.cmd([[let $FZF_DEFAULT_OPTS="--preview 'bat --color=always {}'"]])

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

## Screenshots:
fzf:
![fzf showcase](/vim/fzf-showcase.png)
ripgrep:
![ripgrep showcase](/vim/ripgrep-showcase.png)

