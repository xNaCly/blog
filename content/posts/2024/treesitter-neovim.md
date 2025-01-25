---
title: "Highlighting Parts of Lua as Bash"
date: 2025-01-24
summary: "Using Treesitter in neovim to conditionally highlight code snippets"
tags:
    - nvim
    - treesitter
---

Since i am currently working on a little tool for synching my old macbook pro,
my workstation at home and my work thinkpad - I want to highlight a part of the
lua configuration for said tool as bash, not as a lua string.

I use this tool (`mehr2`) to keep my installed packages on all systems in sync.
I plan to use the following configuration file:

```lua
MEHR2 = {
    packages = {
        default = {
            "git",
            "picom",
            "fish",
            "imagemagick",
            "firefox",
            "flameshot",
            "pipewire",
            "dunst",
            "rofi",
            "i3",
            "acpi",
            "zathura",
            "curl",
        },
        apt = { "build-essentials" },
        pacman = { "base-devel", "pamixer", "hugo", "go", "ghostty" },
        scratch = {
            {
                identifier = "rustup",
                needs = { "curl" },
                update = "rustup update", 
                script = [[
                    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
                    rustup component add rust-docs
                    rustup component add cargo
                    rustup component add clippy
                    rustup component add rustfmt
                ]]
                }
            },
            {
                -- see: https://github.com/neovim/neovim/blob/master/BUILD.md
                identifier = "nvim",
                git = "github.com/neovim/neovim",
                needs = { "make", "cmake", "gcc" },
                branch = "nightly",
                script = [[
                    make CMAKE_BUILD_TYPE=Release
                    make install
                ]]
                }
            },
            {
                -- see: https://github.com/ziglang/zig/wiki/Install-Zig-from-a-Package-Manager
                identifier = "zig",
                execute_for = { "apt" },
                update = "snap refresh zig",
                needs = { "snap" },
                script = "snap install zig --classic --beta"
            },
            {
                -- see: https://ghostty.org/docs/install/build
                identifier = "ghostty",
                execute_for = { "apt" },
                git = "github.com/ghostty-org/ghostty",
                needs = { "zig", "gtk4" },
                script = "zig build -p /usr -Doptimize=ReleaseFast"
            },
            {
                identifier = "go",
                execute_for = { "apt" },
                script = [[
                    VERSION=$(curl -s "https://go.dev/VERSION?m=text" | head -n1)
                    wget https://go.dev/dl/$VERSION.linux-amd64.tar.gz
                    rm -rf /usr/local/go
                    tar -C /usr/local -xzf $VERSION.linux-amd64.tar.gz
                ]]
            },
            {
                -- see: https://gohugo.io/installation/linux/#build-from-source
                identifier = "hugo",
                execute_for = { "apt" },
                needs = { "go" },
                script = "go install github.com/gohugoio/hugo@latest"
            },
        },
        cargo = { "exa", "bat", "ripgrep", "yazi" }
    }
}
```

The `default` array defines packages the current package manager would install.
The packages in the `apt`, `pacman` and `cargo` arrays are only installed if
the corresponding package manager is executable on the target machine (some
differ in names, depending on the package manager, so I install them
specifically). However each entry in the `scratch` array is executed if any of
the entries in the `execute_for` field are found on the system. The execution
is done by passing the value of the `script` field to bash. If the
`execute_for` field is missing, the array entry is executed every time.

Since the `script` field contains a bash script, i want it to be highlighted as
such. Neovim and treesitter enable this exact usecase.

## Neovim setup

I use packer to install treesitter:

```lua
-- .config/nvim/lua/teo/packer.lua

-- packer installation
local fn = vim.fn
local install_path = fn.stdpath('data') .. '/site/pack/packer/start/packer.nvim'
if fn.empty(fn.glob(install_path)) > 0 then
    packer_bootstrap = fn.system({ 'git', 'clone', '--depth', '1', 'https://github.com/wbthomason/packer.nvim',
        install_path })
    download_result = fn.system({ 'ls', '-l', install_path })
    print("download_result: " .. download_result)
end

vim.cmd [[packadd packer.nvim]]

return require('packer').startup(function(use)
    -- syntax highlighting and parser
    use { 'nvim-treesitter/nvim-treesitter', run = ':TSUpdate' }
end)
```

`:PackerSync` will synchronise your neovim instance to your configuration
and install treesitter.

## Treesitter setup

I configure treesitter in a minimalistic way: 

```lua
-- .config/nvim/after/plugin/treesitter.lua

require'nvim-treesitter.configs'.setup {
  ensure_installed = { "c", "lua", "rust", "javascript", "css", "html", "markdown", "javascript"},
  sync_install = false,
  auto_install = true,
  highlight = {
    enable = true,
    additional_vim_regex_highlighting = false,
  },
}
```

## Injections

> Queries are S-expressions and documented
> [here](https://tree-sitter.github.io/tree-sitter/using-parsers/queries/1-syntax.html)

Treesitter injections are placed at
`.config/nvim/queries/<filetype>/injections.scm`[^injection-path] and contain
configurations treesitter injects into files with the corresponding filetype. 

For my specific usecase I search for the `script` table property/field:

```lisp
; Inject into script = [[...]] as bash
((field
    name: (identifier) @_name
    value: (string 
             content: (string_content) @injection.content
             (#eq? @_name "script")
             (#set! injection.language "bash")
 )))
```

The injection works by quering the treesitter tree (inspectable via
`:InspectTree`) for a `field` where its value is a string and its name is equal
to `"script"`. If so the string content is set to be highlighted as bash:

![bat_vs_nvim_with_injection](/treesitter/bat_vs_nvim.png)



[^injection-path]: https://github.com/nvim-treesitter/nvim-treesitter/blob/master/CONTRIBUTING.md#parser-configurations
