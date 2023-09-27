---
title: "Disable Firefox Translation"
summary: "Disabling popup prompt and translation in firefox@^118"
date: 2023-09-27
tags:
  - Firefox
---

{{<callout type="Info">}}

Firefox is now gradually rolling out the new _fullpage
translation_ feature, which performs the translations on
the users device, read more about it
[here](https://support.mozilla.org/en-US/kb/website-translation).
Even though I don't need this feature I admire the
privacy first approach from Mozilla, still I find the
automatically appearing popup annoying.

![popup-translation](/firefox/popup.png)

{{</callout>}}

## Disabling the popup

1. Navigate to `about:config`, disregard the warning
2. Search for `browser.translations.automaticallyPopup`
3. Change its value from `true` to `false`

## Disabling translations

1. Seach for `browser.translations.enable`
2. Change its value from `true` to `false`
