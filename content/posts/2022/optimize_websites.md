---
title: "How to optimize websites for fast loading and slow network speeds"
date: 2022-08-26
slug: web-performance
summary: Optimize websites for a better user experience
tags:
    - web
    - performance
---

Your website is probably too heavy and too slow, that's a fact.

Modern websites load tons of scripts, graphics and ads while you are just trying to visit the website. While loading
more and more content gets injected into the DOM[^dom].

This is a `4.` Step guide to make your website more lightweight.

## 1. Making the right choice

Think what your website needs to able to do and choose the tech stack accordingly:

This is a commonly discussed topic in the tech space, but lets think about it:

-   your website most likely wont need a framework such as react or angular
-   you should probably use SSR[^ssr] with the framework you're using (if its supported)
-   if you're writing a blog, switch to a static site generator such as [hugo](https://gohugo.io) or
    [ty11](https://www.11ty.dev)
-   if you really need dynamic content rerendering, optimize[^react_optimize] [^vuejs_optimize]!

## 2. Use analysers to locate bottlenecks

There are a lot of very good website analysers, such as:

-   [web.dev/measure](https://web.dev/measure/)
-   [firefox built in profiler](https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/index.html)

Use these to find bottlenecks and other issues in your website.

> Benchmark of this blogs landingpage, made [here](https://web.dev/measure/?url=https%3A%2F%2Fxnacly.me) _(total
> 14kb)_ > ![xnacly-benchmark](/optimize/blog-benchmark.webp) Benchmark of the heaviest blog post, made
> [here](https://web.dev/measure/?url=https%3A%2F%2Fxnacly.me%2Fposts%2F2022%2Flinux_guide_for_powerusers%2F) _(total
> 912kb)_ > ![xnacly-benchmark-post](/optimize/blog-post-benchmark.webp)

## 3. Unblock rerendering

The browser considers some resources as blocking and therefore waits for them to load and be parsed which increases time
to first content (css files for instance).

To unblock the rendering process of your website you can use several methods:

1.  css optimizations[^css-optimiziations]
2.  `preload` fonts[^font-preload]

## 4. Decrease total website size

> There are a lot of methods to keep the total size of a website down, but the best way will always be to develop
> minimalistic.

Methods to decrease page load:

-   lazy-load images[^lazy-loading] to only load images the user looks at
-   use well compressed file formats: `webp` instead of `png`[^webp-vs-png]
-   use [postcss](https://purgecss.com/getting-started.html) to minify css and strip out rules which arent used
-   minify javascript and use the least possible
-   use small fonts and host them on the same server as the website

[^dom]: https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction
[^ssr]: https://www.smashingmagazine.com/2020/07/differences-static-generated-sites-server-side-rendered-apps/
[^react_optimize]: https://reactjs.org/docs/optimizing-performance.html
[^vuejs_optimize]: https://vuejs.org/guide/best-practices/performance.html
[^lazy-loading]: https://developer.mozilla.org/en-US/docs/Web/Performance/Lazy_loading
[^css-optimiziations]: https://developer.mozilla.org/en-US/docs/Learn/Performance/CSS
[^font-preload]: https://developer.mozilla.org/en-US/docs/Web/Performance/Lazy_loading#fonts
[^webp-vs-png]: https://www.ionos.com/digitalguide/websites/web-design/webp-format/
