---
title: Linux guide for power users
summary: A guide to help you setup your Linux work machine and configure it for a power users workflow
author: xnacly
slug: linux-for-powerusers
date: 2022-08-23
tags:
    - linux
---

## What to expect

This guide is meant as a loose inspiration for a poweruser looking to switch to Linux. It showcases:

-   window manager, terminal, i3status, nvim, git, fish, wallpapers and dunst configuration
-   basic package manager usage
-   some information about everything you need to know to really configure a power users system.

If you already know how to install Linux skip [Installing](#installing-a-distro) and go straight to
[What do we need, how do we get it](#what-do-we-need-how-do-we-get-it)

If you want to see Screenshots of the results click [here](#screenshots-1).

If you want to take a look at my dofiles, they are [here](https://github.com/xnacly/dotfiles)

## Getting started with the Lingo (What is all this stuff)

### Linux `(+-/GNU)`

Linux is the kernel of your distro, written in C and Assembly by Linus Torvalds and thousands of contributors.

The kernel manages most of your installed drivers, allocates your resources and generally acts as an interface between
soft- and hardware.

![kernel_hardware](/linux/linux_kernel.webp)

The `+-/Gnu` in the heading is a reference to the Linux kernel using GNU code and extensions, and therefore some people
think the Linux kernel should be named with the post-fix `/Gnu` or `+Gnu`.[^gnu/linux_controversy]

Most people use Linux as a synopsis for everything included in a distribution, such as kernel, drivers, desktop
environment, window manager, shell, etc. even though Linux is just the name of the kernel. Everyone knows what you're
talking about by just calling everything Linux.

> **View the current kernel version and build by running**
>
> ```bash
> $: uname -a
> # outdated wsl kernel
> Linux THINK-**** 4.4.0-19041-Microsoft #1237-Microsoft Sat Sep 11 14:32:00 PST 2021 x86_64 x86_64 x86_64 GNU/Linux
> ```

### Distribution

As hinted above a distribution is a package of software. Most Linux distribution contain the Kernel, some sort of
desktop environment, a window manager, multiple Apps such as a word processor and a Webbrowser.

Some Distros are known for their gigantic package repositories like [Debian](https://www.debian.org/index.en.html) and
[Arch](https://arch/linux.org/), other are famous for their security like e.g.
[RedHat](https://www.redhat.com/en/technologies//linux-platforms/enterprise-linux) or the discontinued
[CentOS](https://www.centos.org/). There are some distros which shine by being different or minimal, such as
[NixOS](https://nixos.org/) (unconventional package managing), [Artix](https://artix/linux.org/) (different init system)
or [Void Linux](https://voidlinux.org/) (all the before + support for musl libc implementation)

No one really knows how many distros there
[are](https://upload.wikimedia.org/wikipedia/commons/b/b5//linux_Distribution_Timeline_21_10_2021.svg), because everyone
can make one and switching between them is very easy.

#### Package manager

A package manager is a tool which installes, removes and updates software for you. No more going to a random website and
downloading an `*.exe` file only to have your hdd bricked after disabling the antivirus and running the totally
legitimate vbux generator. Package managers are accessed using the terminal, but some desktop environments include
graphical user interfaces for managing packages.

A package manager such as pacman is relatively secure due to package signing and other measures which were put in place
to save users from malicious software.

Almost all distributions contain a package manager, the most famous are: `apt`, `pacman` and `dnf`.

package manager cli examples:

```bash
# install a tool named neovim
sudo apt install neovim
sudo pacman -S neovim

# check for new updates, upgrade the system
sudo apt update && sudo apt upgrade
sudo pacman -Syyu

# remove neovim
sudo apt remove neovim
sudo pacman -R neovim
```

In this tutorial we will use [Manjaro](https://manjaro.org/), therefore you can focus on the package manager included in
the distribution: `pacman`.

#### Desktop environment (DE) vs window manager (WM)

A desktop environment such as [GNOME](https://www.gnome.org/) bundles a file manager, terminal, window manager, settings
and more into the GNOME package. Everything in it is tightly integrated and applications in the bundle often look
similar and depend on the same libraries. A `de` handles almost everything the user interacts with inside the GUI, such
as volume management, connecting to networks, mounting drives, theming and other.

### Which distro to choose?

I love pacman and getting new software updates fast, therefore i personally use Arch Linux, which can sometimes require
knowledge or some time to maintain. The distro we intend to use is based on arch Linux, but has a lot of preconfigured
software, making it interesting for beginners and advanced users.

> **Is Manjaro better than other distros?**
>
> Manjaro is not superior or inferior to any other Linux distribution, they all do the same. Manjaro has its own package
> manager, themes, tools and custom Kernels.

The above was taken from the manjaro download page and i agree wholeheartedly with the first part. Roll a die and pick a
random distro, it won't really matter.

#### Rolling release vs Stable release (Continuous delivery)

To always have the newest and shiniest software at hand, one could decide to pick a distro with a rolling release
circle[^rolling_release], which can at best (or worst) have several updates available a day. Like everything else RR
distros have up- and downsides, you can read further about them [here](https://itsfoss.com/rolling-release/)

Releasing on a specified time frame is defined as a continuous delivery or stable releases. Distros following this
pattern have the convincing argument of stability and tested packages in their repos.

I personally never had stability issues on arch Linux and ppas annoy the shit out of me, therefore i use Arch :).

Relevant:

![arch_meme](/linux/arch.webp)

## Reasons for Manjaro Linux

As said before, in this tutorial we will be using Manjaro due to it:

-   being based on arch
    -   having rolling release updates
    -   having pacman and yay installed
-   containing a fully configured system (yes bloat, idc its a beginners tutorial)
-   (ofc) being Linux

## Installing a Distro

> This section will explain how to install manjaro linux in a virtual machine in depth

Before installing on real hardware i would recommend you to spin up a virtual machine and install Manjaro there. I will
now describe a simplified way to install your operating system:

1. Install [Oracle VirtualBox](https://www.virtualbox.org/wiki/Downloads) (select `Windows hosts`)
2. Head to the manjaro download page [here](https://manjaro.org/download), scroll down till you see the
   `OFFICIAL EDITIONS` badge.

![manjaro_download](/linux/manjaro_download.webp)

3. Download a minimal version of one of the three editions (I picked gnome).
    > **DISCLAIMER**
    >
    > For simplicitie’s sake, we will not check the authenticity of the downloaded image, one should however always
    > check this before installing on bare metal.
4. Start Virtual Box and click on `new`

![virtual box new vm](/linux/vb_1.webp)

5. Name your box with whatever you want, and select `Type: Linux` and `Version: Arch Linux (64-bit)`

![virtual box new vm name and type](/linux/vb_2.webp)

6. Go with the default for `memory size`:

![virtual box new vm memory](/linux/vb_3.webp)

7. You want to create a new hard drive:

![virtual box new vm hard drive](/linux/vb_4.webp)

with the following attributes (you will be asked for these in the next few windows):

-   VDI (VirtualBox Disk Image)
-   dynamically allocated
-   25GB

8. Hit enter and you have your vm
9. Head to `Settings->System->Boot Order` and move the `Hard Disk` option to the top of the list (this allows the vm to
   boot into the operating system after installation and reboot)

10. Go to `Settings->Storage` and add a new iso by following this image:

![virtual box new vm add iso](/linux/vb_5.webp)

11. Click on `open->choose->ok`

12. Now click on `start`

13. Wait till the system boots (you should see some logs), click on `launch installer` and go trough it.

-   Location: go with the default
-   Keyboard: go with your keyboard layout
-   Partions: select `Erase disk`
-   Users: fill the input fields, choose a password you can remember (for vms i always use root) and check the box which
    says `Use the same password for the administrator account`

14. Hit install and install now in the next prompt.
15. Check the `restart now` box and click on `✓Done` (the vm will now reboot into the freshly installed os)
16. Login with your very strong password from 13. and explore the system:

![manjaro result](/linux/manjaro_result.webp)

## What do we need, how do we get it?

Wikipedia defines a power user as:

> a user of computers, software and other electronic devices, who uses advanced features of computer hardware, operating
> systems, programs, or websites which are not used by the average user.
>
> A power user might not have extensive technical knowledge of the systems they use but is rather characterized by
> competence or desire to make the most intensive use of computer programs or systems.

I however would also mention the power users desire to get work done quickly and not have his workflow interrupted.

This can be done by making use of a window manager such as [i3\[-gaps\]](https://i3wm.org/) to:

-   tile windows
-   use workspaces
-   auto start applications
-   automatically move applications on start to a workspace
-   have a fancy bar on one border of the screen
-   manage your windows solely via keyboard shortcuts you configure
-   have a cool [r/unixporn](https://reddit.com/r/unixporn) setup

The downside of most window manager setups is the need to configure every feature you would get by using a desktop
environment yourself, such as volume, wifi and wallpaper management. But don't worry i got you covered on that full
system configuration.

### Application overview

-   Notification daemon: dunst (lightweight and configurable)
-   Window manager: i3-gaps (i3 fork with gaps)
-   File explorer: Nautilus (comes with gnome)
-   Shell: fish (very nice autocompletion and prompts)
-   Terminal Emulator: kitty (i like the name and i need font ligatures for my neovim setup)
-   Editor: Neovim (its the new and improved new and improved vi)
-   Wallpaper setter: nitrogen (its minimal)

## Getting Started

### Installing software

#### Understanding `pacman`

Pacman has a not so beginner friendly interface (it uses flags such as `-S` instead of `install` or `add`), i will
therefore now follow with a simplified guide for pacman.

> Always consult the man pages[^pacman@manpage] or the wiki[^pacman@archwiki] for more info Pacman is very easy to use
> for simple and complex tasks. It's flags are consistent and if you really think about it they make a lot of sense, it
> is also a lot simpler than apt, like I contrasted in [Package manager](#package-manager).

##### `pacman` usage

```bash
# install a package
pacman -S firefox
# remove a package
pacman -R firefox
# search a package
pacman -Ss firefox
# full system upgrade
pacman -Syyu
```

## Configuring your system
> This section will explain how to install and configure certian software

### .files

Dotfiles are files starting with a `.`. These files are hidden by default and can be viewed using the `-a` flag for ls:

```bash {hl_lines=[2, 12, 6]}
$: pwd
/home/teo

# (l)i(s)t directory content 
#   [-l: long listing format]
$: ls -l
total 0
drwxr-xr-x 1 teo teo 4096 Aug 24 09:29 Documents

# (l)i(s)t directory content 
#   [-l: long listing format, -a: list all files (includes hidden)]
$: ls -la 
total 16
drwxr-x--- 1 teo  teo  4096 Aug 24 09:29 .
drwxr-xr-x 1 root root 4096 Aug  5 09:15 ..
-rw------- 1 teo  teo   409 Aug 23 14:31 .bash_history
-rw-r--r-- 1 teo  teo   220 Aug  5 09:15 .bash_logout
-rw-r--r-- 1 teo  teo  3771 Aug  5 09:15 .bashrc
drwxr-xr-x 1 teo  teo  4096 Aug  5 09:15 .landscape
-rw-r--r-- 1 teo  teo     0 Aug 24 09:29 .motd_shown
-rw-r--r-- 1 teo  teo   807 Aug  5 09:15 .profile
-rw-r--r-- 1 teo  teo     0 Aug  5 09:15 .sudo_as_admin_successful
-rw------- 1 teo  teo  2361 Aug  5 11:26 .viminfo
drwxr-xr-x 1 teo  teo  4096 Aug 24 09:29 Documents
```

In the above one can directly see a config file such as `.bashrc`. This file for instance contains all the configuration for bash, as the name suggests.

> **Freedesktop.org: XDG basedir specs** 
> 
>  *`$XDG_CONFIG_HOME` defines the base directory relative to which user-specific configuration files should be stored. 
>  If `$XDG_CONFIG_HOME` is either not set or empty, a default equal to `$HOME/.config` should be used.* [^file_system_standard]

Config files are often stored in files prefixed by a `.`, or in the `.config` directory, therefore they are called dotfiles..

### Neovim (Editor)
To get started we need to get our hands on a powerful editor, such as vim or the new and improved vim: neovim.

Neovim is useful with its defaults, but a minimal config can help to get the most out of it.

Open a new terminal, paste the following:

```sh
# install the neovim package using pacman as the superuser 
sudo pacman -S neovim
# (c)hange (d)irectory to the user config which can be found at ~/.config
cd ~/.config 
# (m)a(k)e a new (dir)ectory named nvim
mkdir nvim
# create a new file named init.vim in the ~/.config/nvim folder
nvim nvim/init.vim
```

now you should see neovim's interface.:
![vim_config](/linux/vim_config.webp)

press `i` to switch to insert mode and paste the following configuration using `ctrl+shift+v`:


```vim
set number								" enable line numbers 
set hidden 								" hide buffers
syntax on                               " Enables syntax highlighing
set nowrap                              " Display long lines as just one line
set encoding=utf-8                      " The encoding displayed
set fileencoding=utf-8                  " The encoding written to file
set ruler								" Show the cursor position all the time
set cmdheight=2                         " More space for displaying messages
set iskeyword+=-                      	" treat dash separated words as a word text object
set splitbelow                          " Horizontal splits will automatically be below
set splitright                          " Vertical splits will automatically be to the right
set t_Co=256                            " Support 256 colors
set conceallevel=0                      " So that I can see `` in markdown files
set tabstop=4                           " Insert 2 spaces for a tab
set shiftwidth=4                        " Change the number of space characters inserted for indentation
set smarttab                            " Makes tabbing smarter will realize you have 2 vs 4
set expandtab                           " Converts tabs to spaces
set smartindent                         " Makes indenting smart
set autoindent                          " Good auto indent
set showtabline=2                       " Always show tabs
set noshowmode                          " We don't need to see things like -- INSERT -- anymore
set updatetime=300                      " Faster completion
set timeoutlen=500                      " By default timeoutlen is 1000 ms
set formatoptions-=cro                  " Stop newline continution of comments
set termguicolors						" allow vim to change term colors
set incsearch 							" enable incremental search
set smartcase							" searches case insensitive until an uppercase character is supplied
set nobackup							" disables backup files
set spell!								" spellchecking
set spelllang=en,de						" set languages for spellchecking
```

Now hit `Esc` and type  `:w` and after that `:source %` to reload the neovim configuration

> **Escaping vim**
>
> there are several ways to exit vim:
| Method | What happens |
| ----------- | ------------ |
| `Esc:q!` or `ZQ`	      | exit and discard |
| `Esc:w` or `ZZ`	      | exit and save    |

#### Plugins (fuzzy file finder, nerd tree)


Add the following to your vim config (`~/.config/nvim/init.vim`) to install vim plug (a package manager for vim).

```vim
" installs vim plug if it isnt already installed
if empty(glob('~/.config/nvim/autoload/plug.vim'))
  silent !curl -fLo ~/.config/nvim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
endif
```

To add plugins to vim we need to do the following:

```vim
call plug#begin('~/.config/nvim/autoload/plugged')
    " define fzf as a plugin 
    Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }

    " plugins for icons in the file tree
    Plug 'kyazdani42/nvim-web-devicons'
    Plug 'ryanoasis/vim-devicons'

    " syntax support for the file tree 
    Plug 'tiagofumo/vim-nerdtree-syntax-highlight'

    " plugin to display a file tree
    Plug 'scrooloose/NERDTree'

    " add the closing pair to ("'{[ 
    Plug 'jiangmiao/auto-pairs'
call plug#end()
```

Now:
1. type in  `:w` and `:source %` to reload the config
2. type in `:PlugInstall` and exit with `ZZ`

Go back into the vim config and add the following lines to interact with the plugins we just installed.:

```vim
" this defines space as out custom button to start key combinations such as space+f to fuzzy search
let mapleader="\<space>" 

" map space+f to the command ':FZF' which starts the fuzzy finder window
nnoremap <silent> <Leader>f :FZF<CR>

" map ctrl+b to the file tree 
nnoremap <silent> <C-b> :NERDTreeToggle<CR>
```

To view available shortcuts for the `NerdTree` press `ctrl+b` to toggle the tree window and press `?` to view help.

##### Screenshots

###### Fzf
![fzf](/linux/fzf.webp)

###### NerdTree
![nerdtree](/linux/nerdtree_and_vim.webp)

### Fish (Shell)

Install fish
```bash
sudo pacman -S fish
```
Set fish as the default shell:
```bash
chsh -s /usr/bin/fish
```

### Git (Version control tool)

Install git:

```bash
sudo pacman -S git
```

Go to [github](https://github.com/)
1. sign in or sign up
2. click on your profile picture 
3. click on settings.
4. now navigate to 

`Settings->Developer Settings->Personal access tokens->Generate new token`

5. name it `manjar-vm`
6. click on the `repo` checkbox 
7. scroll to the bottom and click on generate token.
8. copy the token into a notepad (should be prefixed with `ghp_`)

To push or pull from github, one must first authenticate to their service. This needs to be done using the git config.[^git_credentials_store]

```bash
# tell git to store your credentials indefinitly
git config --global credential.helper store
# set your username exactly as the username you selected on github (replace xnacly with your username)
git config --global user.name "xnacly"
# set your email exactly as the email you selected on github (replace with your username)
git config --global user.email "47723417+xNaCly@users.noreply.github.com"

# to check if everything worked, run:
git config --global --list
# should spit this out:
# user.name=xnacly
# user.email=47723417+xNaCly@users.noreply.github.com
```

Now go to [github/new repo](https://github.com/new) to create a new private repo
1. name it `manjaro vm test`
2. click on `Private`
3. scroll down and create your repo.
4. copy the repo url from the blue box (`https://github.com/<username>/test.git`) 

```bash
# replace <username> with your github username
# You will be prompted for your email and your password, 
# input the email used to sign in to github,
# as the password you will need to use the access token we generated before.
git clone https://github.com/<username>/test.git
# cloning into 'test'...
# Username for 'https://github.com': 
# Password for ... :
# warning: You appear to have cloned an empty repository
```
 
You are now authenticated to github. Test your config by creating a readme and pushing it to master:

```bash
echo "# Test repo" > README.md
git add -A
git commit -m "init commit"
git push
```

Now go to the repo and refresh by pressing `Ctrl+r` and see your changes have been pushed into master.

### i3 (Window manager)
To display anything and manage our windows, we will need the i3gaps group:

```bash
sudo pacman -S i3 dmenu
```
```text
[sudo] password for teo: 
:: There are 5 members in group i3:
:: Repository community
   1) i3-gaps  2) i3-wm  3) i3blocks  4) i3lock  5) i3status

Enter a selection (default=all): 
```

Input your password and hit `Enter`.


Now logout and select i3:
![i3_select](/linux/i3_select.webp)

After boot you will be prompted to generate a config, hit `Enter`.
![i3_first_boot](/linux/i3_firstboot.webp)

Select the default key as the `Super`-Key, it should be the `Win` button. Hit Enter to write the config.
![i3_first_config](/linux/i3_firstboot_config.webp)

i3 has a pretty unique keymap, here are the most basics ones:

| Keycombination  | what it does         |
| :-------------: | :-----------------:  |
| `Super+Enter`   | open a terminal      |
| `Super+Shift+q` | close a window       |
| `Super+d` | start application launcher |
| `Super+Shift+c` | reload i3 config     |
| `Super+Shift+r` | reload i3            |
| `Super+Shift+e` | exit i3 prompt            |
| `Super+[0-9]`   | switch to workspace 1-10 |
| `Super+Shift+[0-9]`   | move focused window to workspace 1-10 |

See the [i3 docs](https://i3wm.org/docs/userguide.html) for keybindings and configuration  help, also see my [i3 config](https://github.com/xNaCly/dotfiles/blob/master/i3/config) for inspiration. 

### i3status (i3 status bar)
i3status is very easily configurable. 

```bash
# (c)hange (d)irectory to the user config which can be found at ~/.config
cd ~/.config 
# (m)a(k)e a new (dir)ectory named i3status
mkdir i3status
# open the config in neovim
nvim i3status/i3status.conf
```

Now in neovim, paste the following:

```text
general {
        interval = 1
}

order += "volume master"
order += "tztime local"

tztime local {
        format = "%d.%m %H:%M "
}

volume master {
        format = "%volume"
        format_muted = "--%"
        device = "pulse"
}
```

This config updates every 1 second and only displays the time, date and volume.
To apply this configuration, we will need to change the configuration file i3status looks at. To do this, we need to change the following in `~/.config/i3/config` by supplying the file path to neovim, like so:

```bash
nvim ~/.config/i3/config
```

![i3status_old](/linux/i3status_old.webp)

```text {linenostart=184,hl_lines=[2]}
bar {
	status_command i3status
}
```

to

![i3status_new](/linux/i3status_new.webp)
```text {linenostart=184,hl_lines=[2]}
bar {
	status_command i3status -c ~/.config/i3status/i3status.conf
}
```



### Kitty (Terminal Emulator)
Kitty is very fast and full of features.

Install kitty:
```bash
sudo pacman -S kitty
```

Configure Kitty by opening `~/.config/kitty/kitty.conf` using neovim and pasting the following in the file:

```text
font_family                 JetBrainsMono Nerd Font         # configure font family
bold_font                   auto                            
italic_font                 auto
bold_italic_font            auto
font_size                   13.0
window_padding_width        5                               # space between window borders and text in terminal
enable_audio_bell           no                              # disable loud alarm when misinput happens
remember_window_size        no
initial_window_width        82c
initial_window_height       24c
confirm_os_window_close     0                               # kitty asks you if you reall want to close it if a process is running, this disables the prompt
```

To replace the default terminal with kitty, open `~/.config/i3/config` with neovim:

1. Search for `i3-sensible` by pressing `/i3-sensible` in normal mode
2. Replace `i3-sensible-terminal` with kitty

```text {hl_lines=[5],linenostart=44}
# Use Mouse+$mod to drag floating windows to their wanted position
floating_modifier $mod

# start a terminal
bindsym $mod+Return exec i3-sensible-terminal

# kill focused window
bindsym $mod+Shift+q kill
```

```text {hl_lines=[5],linenostart=44}
# Use Mouse+$mod to drag floating windows to their wanted position
floating_modifier $mod

# start a terminal
bindsym $mod+Return exec kitty

# kill focused window
bindsym $mod+Shift+q kill
```




### Dunst (Notification daemon)

Gnome ships a cli utility which we will use to test our notification daemon. Running `notify-send "test"` on our current system results in an `GDBus` error.
To fix this we will have to install [dunst](https://wiki.archlinux.org/title/Dunst).:

![dbus_error](/linux/dbus_error.webp)

```bash
sudo pacman -S dunst
```

Sending a new notification will now result in a small window popping up on our screen for a few seconds:

![dunst](/linux/dunst.webp)

### Nitrogen (Wallpaper setter)
Setting a Wallpaper is easier than all the technical incompetent people on [r/PcMasterRace](https://www.reddit.com/r/pcmasterrace/) say. Just install `nitrogen`, add your picture, done.

```bash
sudo pacman -S nitrogen
```
1. Download an image to the `~/Pictures` directory
2. Add the `~/Pictures` directory as a source to nitrogen
![nitrogen_walktrough](/linux/nitrogen_walktrough.webp)
3. Click on the now added image (1), select the prefered alignment option (2) and click `apply` (3)
![nitrogen_after_selection](/linux/nitrogen_after_selection.webp)
4. Done.
![wallpaper_applied](/linux/wallpaper_applied.webp)

> **Warning**
>
> This configuration is not permanent, every restart will require you to set your wallpaper again.

To prevent the walllpaper reset we can read the nitrogen manpage[^nitrogen_manpage], which explains the `--restore` option. To use this option and let nitrogen start on boot, we will edit our i3 config.:
```bash
nvim ~/.config/i3/config
```

1. Press `Shift+g` to jump to the last line of the file. 
2. Now press `o` to switch into insert mode in the line below.
3. We will now insert a `exec --no-startup-id` statement, read more about it here[^i3docs_exec]

```text {linenostart=184,hl_lines=[4]}
bar {
	status_command i3status
}
exec --no-startup-id nitrogen --restore
```

Your wallpaper will now be restored on boot.


## Wrapping up.

After reading through this guide and following each step, you can now:
- understand the difference between a distro and the kernel 
- install linux in a virtual machine
- use a package manager
- use basic vim 
- understand the basics of the unix file system
- use a floating window manager
- use git to version your files
- configure software (i3, vim)

If there is anything wrong or you are having questions just create a new issue [here](https://github.com/xnacly/blog/issues/new)

I will some day follow up on this and make a ricing guide, but until now you should be able to evolve your workflows and get comfy using i3. 

I appended some Screenshots to visualise the result of this guide.

### Screenshots

![screenshot](/linux/screenshot.webp)
![c workflow](/linux/c_workflow_tree.webp)
![c_workflow2](/linux/c_workflow.webp)

[^rolling_release]: https://en.wikipedia.org/wiki/Rolling_release
[^gnu/linux_controversy]: https://en.wikipedia.org/wiki/GNU/Linux_naming_controversy
[^pacman@manpage]: https://archlinux.org/pacman/pacman.8.html
[^pacman@archwiki]: https://wiki.archlinux.org/title/pacman#Usage
[^file_system_standard]: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html#variables
[^git_credentials_store]: https://git-scm.com/docs/git-credential-store
[^i3docs_exec]: https://i3wm.org/docs/userguide.html#_automatically_starting_applications_on_i3_startup
[^nitrogen_manpage]: https://www.mankier.com/1/nitrogen
