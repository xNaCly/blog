---
title: "Neovim Motions and small helpers"
date: 2022-12-22
summary: "Helpfull neovim motions and tips for fzf, rg with preview and coc.vim with inline diagnostics, etc."
tags:
  - vim
---

## Prerequisite:

To follow this tutorial you will need to have your neovim configured with lua.
If you need help with that,
take a look at [Transitioning from Vim](https://neovim.io/doc/user/nvim.html#nvim-from-vim) or my dotfiles [xnacly/dotfiles](https://github.com/xNaCly/dotfiles/tree/master/nvim).

I manage my packages with [vimplug](https://github.com/junegunn/vim-plug/). Add the following to your vim config to install vimplug:

```lua
vim.cmd([[
if empty(glob('~/.config/nvim/autoload/plug.vim'))
  silent !curl -fLo ~/.config/nvim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
endif
]])
```

I use these packages in this guide:

```lua
local Plug = vim.fn['plug#']
vim.call('plug#begin', '~/.config/nvim/plugged')
    -- Nodejs extension host for vim & neovim, load extensions like VSCode and host language servers.
    -- primarly used for prettier and language servers
    Plug 'neoclide/coc.nvim'

    -- fuzzy finder, supports previews
    Plug('junegunn/fzf', { ['do'] = vim.fn['fzf#install()'] })
    Plug('junegunn/fzf.vim')

    -- Tree-sitter is a parser generator tool and an incremental parsing library, enables better syntax highlighting
    Plug('nvim-treesitter/nvim-treesitter', {['do'] = vim.fn['TSUpdate']})

    -- icons for the file manager
    Plug 'nvim-tree/nvim-web-devicons'

    -- file manager in the sidebar
    Plug 'nvim-tree/nvim-tree.lua'
vim.call('plug#end')
```

## Moving lines in visual selection

### Keymap definitions

To define new keybindings i use the [Functional wrapper for mapping custom keybindings](https://gist.github.com/Jarmos-san/d46605cd3a795513526448f36e0db18e#file-example-keymap-lua) function:

```lua
function map(mode, lhs, rhs, opts)
    local options = { noremap = true }
    if opts then
        options = vim.tbl_extend("force", options, opts)
    end
    vim.api.nvim_set_keymap(mode, lhs, rhs, options)
end
```

| Param   | Description                          | Values                                 |
| ------- | ------------------------------------ | -------------------------------------- |
| mode    | which mode to map the keybind to     | `v` : visual, `n`: normal, `i`: insert |
| lhs     | left hand side (keybind)             | string                                 |
| rhs     | right hand side (command to execute) | string                                 |
| options | options, such as `noremap`           | object                                 |

### Moving the visual selection

```lua
-- move selection down
map("v", "J", ":m '>+1<CR>gv=gv")
-- move selection up
map("v", "K", ":m '<-2<CR>gv=gv")
```

Source the file using `source %`

Now you can select multiple lines using `Shift+v` and moving it with `Shift+k` or `Shift+j`

## coc.nvim

Coc allows us to install vscode extensions, get suggestions (intellj) and error reporting

### use Prettier

1. Install [Prettier](https://github.com/neoclide/coc-prettier):

   open neovim and run the following command: `:CocInstall coc-prettier`

2. register a new `:Prettier` command:

```lua
vim.cmd[[
    command! -nargs=0 Prettier :CocCommand prettier.forceFormatDocument
]]
```

3. reload the config by running `:source %`

### Coc keybindings:
```lua
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

-- show docs for something by pressing Shift+k
map("n", "K", "<CMD>lua _G.show_docs()<CR>", {silent = true})
local opts = {silent = true, noremap = true, expr = true, replace_keycodes = false}
-- enables autocomplete on space
map("i", "<TAB>", 'coc#pum#visible() ? coc#pum#confirm() : v:lua.check_back_space() ? "<TAB>" : coc#refresh()', opts)
```

### Inline lsp diagnostics, fancy styles and diagnostic signs

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

## fuzzy file finder

![fuzzy](/vim/fzf.png)

### Keybindings:
```lua
-- call fzf with leader f 
map("n", "<Leader>f", ":FZF<CR>", {silent = true})
-- call fzf with leader p
map("n", "<Leader>p", ":Rg<CR>", {silent = true})
```

### Config:
I use [bat](https://github.com/sharkdp/bat) for preview. Install it to use fzf preview
```lua
vim.cmd([[let g:fzf_layout = {'window': {'width': 0.9, 'height': 0.9}}]])
vim.cmd([[let $FZF_DEFAULT_OPTS="--preview 'bat --color=always {}'"]])
```

## Filemanager
```lua
-- open file manager sidebar using ctrl+b
map("n", "<C-b>", ":NvimTreeToggle<CR>", {silent = true})
```

