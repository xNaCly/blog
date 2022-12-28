---
title: "Getting started with Neovim - PDE p.I"
date: 2022-12-28
summary: "Install, configuration and usage guide"
draft: true
tags:
- nvim
- PDE
---

> This is the first part of the personalized development environment series, [Part II]()

## Prerequisites
The reader of this guide needs to know the basics of:
- Vim motions and keys
- opening and saving files in Vim

Learn [here](https://www.youtube.com/watch?v=X6AR2RMB5tE&list=PLm323Lc7iSW_wuxqmKx_xxNtJC_hJbQ7R), [here](https://www.youtube.com/watch?v=5JGVtttuDQA&list=PLm323Lc7iSW_wuxqmKx_xxNtJC_hJbQ7R&index=3) and [here](https://www.youtube.com/watch?v=KfENDDEpCsI&list=PLm323Lc7iSW_wuxqmKx_xxNtJC_hJbQ7R&index=4)

## Abstract
The pde series is intended to provide a simple guide for a new neovim user to learn about configuring the editor.
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

Find the config folder here: ([Config path](#config-path)).

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

```

3. Open `nvim/lua/plugins.lua` and enter the following configuration:
```lua

```

4. Open `nvim/lua/plugin-options.lua` and enter the following configuration:
```lua

```

4. Open `nvim/lua/keybindings.lua` and enter the following configuration:
```lua

```

[^vimscript]: https://vimdoc.sourceforge.net/htmldoc/usr_41.html
[^lua]: https://www.lua.org/
[^luadocs]: https://www.lua.org/manual/5.4/
[^luavsvs]: https://sr.ht/~henriquehbr/lua-vs-vimscript/
[^luausers]: https://en.wikipedia.org/wiki/Category:Lua_(programming_language)-scriptable_software
