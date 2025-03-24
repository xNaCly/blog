---
title: "Using the latest C standard with clang lsp in nvim"
date: 2025-03-24
summary: "The default config of the clang lsp is old, so you have to specific --std"
tags:
- c
- nvim
---

I found the default clang language server does not adhere to the latest C
standard (c23) and therefore cries about the use of `bool` - which is a new
keyword in c23[^c23-wikipedia]. Since I am using neovim and its `lsp` api
[^nvim-lsp], its a quick fix, at least with my config[^dotfiles].

{{<callout type="Warning">}}
I am using a nightly build of neovim, some apis and/or options may not be
available in the latest stable build:

```text
NVIM v0.11.0-dev-2074+gc982608226
Build type: Release
LuaJIT 2.1.1741730670
Run "nvim -V1 -v" for more info
```
{{</callout>}}


Previously I just kept a list of language servers I need and neovim does the
rest (if the binary is installed and has the executable bit - mind you).

```lua
-- dotfiles/nvim/lua/teo/lsp.lua
local lspconfig = require "lspconfig"
local lsps = {
    "rust_analyzer",
    "gopls",
    "ts_ls",
    "html",
    "cssls",
    "lua_ls",
    "clangd" -- this is removed in the next step
    "hls"
}
for _, lsp in pairs(lsps) do
    lspconfig[lsp].setup {}
end
```

I didn't think about the need of setting specific options for a single one of
these, so I just define `clangd` and its option by hand - I dont need to
overengineer this:

```lua
lspconfig.clangd.setup {
    init_options = {
        fallbackFlags = { '--std=c23' }
    },
}
```


[^c23-wikipedia]: https://en.wikipedia.org/wiki/C23_(C_standard_revision)#Typeshttps://en.wikipedia.org/wiki/C23_(C_standard_revision)#Types
[^nvim-lsp]: https://neovim.io/doc/user/lsp.html
[^dotfiles]: https://github.com/xnacly/dotfiles
