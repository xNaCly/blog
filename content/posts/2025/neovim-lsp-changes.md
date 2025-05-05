---
title: "Switching from lspconfig to vim.lsp.config and vim.lsp.enable"
date: 2025-05-05
summary: nvim@v0.11 finally stabilizes lsp configuration "shortcuts" from nightly
tags:
  - nvim
---

## Previous Configuration via `lsp-config`

Previously I used
[`neovim/nvim-lspconfig`](https://github.com/neovim/nvim-lspconfig) to
get a default configuration for the language servers I use:

```lua
vim.lsp.config.sqleibniz = {
    cmd = { '/usr/bin/sqleibniz', '--lsp' },
    filetypes = { "sql" },
    root_markers = { "leibniz.lua" }
}
vim.lsp.enable('sqleibniz')

local lspconfig = require "lspconfig"
local lsps = {
    "rust_analyzer",
    "gopls",
    "ts_ls",
    "cssls",
    "lua_ls",
    "hls",
}
for _, lsp in pairs(lsps) do
    lspconfig[lsp].setup {}
end

lspconfig.clangd.setup {
    init_options = {
        fallbackFlags = { '--std=c23' }
    },
}
```

So around three places/ways for configuring language servers:

1. `vim.lsp.config` & `vim.lsp.enable`, which previously were only
   available in `nightly` and weren't integrated with `lspconfig`
   (required building neovim from source)
2. `lspconfig[<lsp name>].setup` with all `lsps` elements
3. manual configuration options for eg `clangd`

## Updated Configuration since `v0.11`

The updated configuration using `config` (to register) and `enable` (to
start), merging all three previous methods for configuring my language
servers into a singular array:

```lua
local lsps = {
    { "rust_analyzer" },
    { "gopls" },
    { "ts_ls" },
    { "cssls" },
    { "lua_ls" },
    { "hls" },
    {
        "clangd",
        {
            init_options = {
                -- im using this standard since i want the compiler to
                -- know about true, false, etc - see
                -- https://xnacly.me/posts/2025/clangd-lsp/
                fallbackFlags = { '--std=c23' }
            },
        }
    },
    -- my custom sql language server
    {
        "sqleibniz",
        {
            cmd = { '/usr/bin/sqleibniz', '--lsp' },
            filetypes = { "sql" },
            root_markers = { "leibniz.lua" }
        }
    },
}

for _, lsp in pairs(lsps) do
    local name, config = lsp[1], lsp[2]
    vim.lsp.enable(name)
    if config then
        vim.lsp.config(name, config)
    end
end
```
