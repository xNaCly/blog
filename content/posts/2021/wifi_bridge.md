---
title: Bridge WIFI connection via LAN
summary: How to bridge a WIFI connection to LAN
author: xnacly
date: 2021-10-14
tags: 
- linux
- wifi
- lan
---

1. To start off, we start bash and execute `nm-connection-editor`. _(This starts the network manager)_

2. Now click the `+` on the bottom left of the spawned window.

3. Next up select `Ethernet` from the options and click on `Create` in the bottom right.

4. Go to the `IPv4 Settings` and change the method from `Automatic (DHCP)` to `Shared with other computers`.

5. Now click on `Save` on the bottom right and connect a LAN-cable to your other device.

> You should now be able to use the bridged connection.

**_PS:_**

-   If your device can't establish a connection to a WIFI, or the Network shows WIFI as disabled try running the
    following command:

```bash
nmcli radion wifi on
```

Link to Source[^1]

[^1]: https://www.reddit.com/r/ManjaroLinux/comments/9rs30y/sharing_wifi_over_ethernet/_
