---
title: Getting started with Arch on a Macbook pro 2012 (9,2)
summary: A guide to wifi, touchpad support and more on your macbook pro 2012 using arch
author: xnacly
date: 2021-12-27
tags: 
- linux
- wifi
- xorg
---

## Enable tap to click and natural scrolling

-   install [`libinput`](https://wiki.archlinux.org/title/Libinput)
-   paste the following in your shell:

```bash
mkdir /etc/X11/xorg.conf.d;
echo 'Section "InputClass"
        Identifier "libinput touchpad catchall"
        MatchIsTouchpad "on"
        MatchDevicePath "/dev/input/event*"
        Driver "libinput"
        Option "Tapping" "on"
        Option "NaturalScrolling" "on"
EndSection' > /etc/X11/xorg.conf.d/40-libinput.conf;
systemctl restart lightdm
```

Link to Source [^1]

## Get wireless running (the GUI method)

-   install [`yay`](https://github.com/Jguer/yay#installation)
-   install [`broadcom-wl`](https://wiki.archlinux.org/title/Broadcom_wireless#broadcom-wl)
-   reboot
-   `ip addr` should now display `wlan0`
-   install [`NetworkManager`](https://wiki.archlinux.org/title/NetworkManager) and use
    `systemctl enable NetworkManager.service` + `systemctl start NetworkManager.service`
-   install and run [`nm-connection-editor`](https://archlinux.org/packages/extra/x86_64/nm-connection-editor/)
-   add a new connection in the bottom left and choose `WIFI`
-   enter your wifi ssid and password, disable ipv6 (_optional_)

Link to Source[^2]

## Change screen and keyboard backlight brightness

-   install [`brightnessctl`](https://archlinux.org/packages/community/x86_64/brightnessctl/) and
    [`xev`](https://archlinux.org/packages/extra/x86_64/xorg-xev/)
-   check what keys your macbook uses to manage the screen and keyboard backlight brightness:

    ```bash
    xev | awk -F'[ )]+' '/^KeyPress/ { a[NR+2] } NR in a { printf "%-3s %s\n", $5, $8 }'
    ```

    -   press the keys for screen brightness and keyboard brightness
    -   copy the key names
    -   Paste them in your `i3 config`:

    _Keyboard backlight:_

    ```
    bindsym XF86KbdBrightnessUp exec brightnessctl --device='smc::kbd_backlight' set +10
    bindsym XF86KbdBrightnessDown exec brightnessctl --device='smc::kbd_backlight' set 10-
    ```

    _Screenbrightness:_

    ```
    bindsym XF86MonBrightnessUp exec brightnessctl set +300
    bindsym XF86MonBrightnessDown exec brightnessctl set 300-
    ```

[^1]: https://unix.stackexchange.com/questions/337008/activate-tap-to-click-on-touchpad
[^2]: https://wiki.archlinux.org/title/Network_configuration/Wireless
