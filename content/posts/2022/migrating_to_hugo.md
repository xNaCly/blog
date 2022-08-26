---
title: Why and how i migrated my blog from nuxt/content to hugo
summary: reasons for migrating your blog to hugo
date: 2022-08-16
slug: migrate-to-hugo
tags:
- js 
- blog 
- md
- web
---

> **DISCLAIMER**
> 
> I used nuxt content with vue 2, some of these points do not apply to nuxt content v2 with vue 3

## Why i used nuxt content (nc)
Nc is a nuxt module which parses several file types and displays their contents in html.[^1]
I used nc to display my blog articles in my portfolio by letting it parse my markdown into html.

Don't get me wrong, nc is amazing. 

Its easy to implement a blog using nc with so many features such as automatically generating a table of contents or providing a full text search. nc also has a lot of possible integrations for things like rss.

However: 
## Why i don't use it anymore
My portfolio was written back when vue version 2 was the latest iteration, therefore i wanted to migrate to vue3 and nuxt 2. While doing so i had a lot of issues and at the end decided to not give a damn and just use a different solution.

### Dependency and Vulnerability hell
Installing nc, even the newest release, installs 1500 packages, several of them deprecated and around 20 vulnerabilities:

![installing_nuxt_content](/migrating_to_hugo/installing_nuxt.webp)

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

## [UPDATE: 2022-08-23]
I now have deprecated my portfolio and moved everything to hugo. As one can see my skill set and a short biography are displayed at [~/about](/about). I also created my own [theme](https://github.com/xnacly/hugo-theme-mini) by forking the [hugo-mini-theme](https://github.com/nodejh/hugo-theme-mini) and changing it to my liking. I implemented dark and light theme support depending on the system preference, as well as better responsiveness. I am currently thinking about merging my changes into upstream, but thats a whole other story.

[^1]: https://content.nuxtjs.org/
[^2]: https://content.nuxtjs.org/v1/getting-started/introduction
[^3]: https://content.nuxtjs.org/v1/community/integrations
