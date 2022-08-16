---
title: Why and how i migrated my blog from nuxt/content to hugo
summary: reasons for migrating your blog to hugo
date: 2022-08-16
author: xnacly
tags:
- js blog markdown
draft: true
---

> **DISCLAIMER**
> 
> I used nuxt content with vue 2, some of these points do not apply to nuxt content v2 with vue 3

## Why i used nuxt content (nc)
Nc is a plugin for nuxt which parses several file types and displays their contents in html.[^1]
I used nc to display my blog articles in my portfolio by letting it parse my markdown into html.

Don't get me wrong, nc is amazing. 

Its easy to implement a blog using nc with so many features such as automatically generating a table of contents or providing a full text search. nc also has a lot of possible integrations for things like rss.

However: 
## Why i don't use it anymore
My portfolio was written back when vue version 2 was the latest iteration, therfore i am 

### Dependency and Vulnerability hell
Installing nc, even the newest release, installs 1500 packages, several of them deprecated and around 20 vulnerabilities:

![installing_nuxt_content](/migrating_to_hugo/installing_nuxt.png)

### Missing features
Out of the box nc is lacking a lot of features, such as generating a rss feed for all blog posts, code syntax highlighting and other.[^2]

There are packages providing these functionalities[^3], which will however depend on packages and thus will only add oil to the dumpster fire of dependencies.


### Performance

First content paint using SSR and performance hacks i accumulated around the web was still at around 2 seconds, which is too slow for a simple site such as a portfolio with a blog.

After stripping out the blog, nc and all the styling used for the blog, i was able to cut FCP in halve.

Currently my portfolio only contains a small about page and renders my skills from a json file with icons and for how long ive been using the certain tech.
This is a very small page and I don't think it needs a framework such as nuxt, therefore i will probably add the rest of the portfolio to this hugo blog and create my own hugo theme.

## Why use Hugo
I was about to write my own blogging system by converting the markdown files into html using pandoc and hosting the result on github. 

I scrapped that idea after seeing what Hugo can do.

Hugo is used in my blog for:
- generating a xml rss feed
- extracting yaml frontmatter
- sorting posts by tag or by date
- styling articles
- highlighting the syntax of code blocks

and providing me with a github action, which allows me to edit a markdown file, commit and push to github and my blog gets updated.

Here is the source for this blog: https://github.com/xNaCly/blog

[^1]: https://content.nuxtjs.org/
[^2]: https://content.nuxtjs.org/v1/getting-started/introduction
[^3]: https://content.nuxtjs.org/v1/community/integrations
