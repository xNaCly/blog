---
title: "Quick and dirty RSS/XML to JSON parser"
summary: Parsing RSS feeds into JSON objects using javascript
author: xnacly
date: 2022-07-18
slug: rss-parser
tags: 
- js
- xml
- json
- rss
---

## Perquisites:

> Keep in mind that i wrote this parser in under an hour and therefore it will be either buggy or plain wrong in some or
> most cases.

The parser is in no way intending to be a perfect XML parser matching all edge cases. It is however created as a tool to
get data from an rss feed in a simple and quick way, ignoring anything else.

At this point one could say why not just use a package. And they would be right, there are a great lot of packages
available for parsing XML and you could even just pass it to the DOM[^1] and let nodejs[^2] handle the conversion, but
this isn't possible for my use case.

I specifically use react-native[^3] in this project, therefore nodejs and their implementation of the DOM are out of the
option.

Using a package on the other hand would only enlarge the already existing dependency hell in a rn project.

### What the parser should do:

The parser should be able to dynamically add key and value pairs to an object depending on the keys in the XML string.
This is necessary due to optional keys and keys some publishers use and others don't. [^4]

Take for example the following XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:nyt="http://www.nytimes.com/namespaces/rss/2.0" version="2.0">
  <channel>
    <title>NYT &gt; Top Stories</title>
    <link>https://www.nytimes.com</link>
    <atom:link href="https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml" rel="self" type="application/rss+xml" />
    <description />
    <language>en-us</language>
    <copyright>Copyright 2022 The New York Times Company</copyright>
    <lastBuildDate>Mon, 18 Jul 2022 10:33:55 +0000</lastBuildDate>
    <pubDate>Mon, 18 Jul 2022 10:06:46 +0000</pubDate>
    <image>
      <title>NYT &gt; Top Stories</title>
      <url>https://static01.nyt.com/images/misc/NYT_logo_rss_250x40.webp</url>
      <link>https://www.nytimes.com</link>
    </image>
    <item>
      <title>Heat Wave In Texas and Central Plains Could Be the Hottest Yet</title>
      <link>https://www.nytimes.com/2022/06/25/us/heat-wave-texas-oklahoma-plains.html</link>
      <guid isPermaLink="true">https://www.nytimes.com/2022/06/25/us/heat-wave-texas-oklahoma-plains.html</guid>
      <atom:link href="https://www.nytimes.com/2022/06/25/us/heat-wave-texas-oklahoma-plains.html" rel="standout" />
      <description></description>
      <dc:creator>Isabella Grullón Paz</dc:creator>
      <pubDate>Mon, 18 Jul 2022 04:10:13 +0000</pubDate>
      <media:content height="151" medium="image" url="https://static01.nyt.com/images/2022/07/16/multimedia/-weather-us-heat-2/-weather-us-heat-2-moth.jpg" width="151" />
      <media:credit>Shelby Tauber/Reuters</media:credit>
      <media:description>A dried-up riverbed of the Trinity River in Dallas on Tuesday. In the coming week, parts of Texas could see their hottest temperatures of the summer yet.</media:description>
    </item>
  </channel>
</rss>
```

Calling the parser and pretty printing the result...

```js
parse_rss("https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml").then((_) =>
	console.log(JSON.stringify(_, null, 2))
);
```

should present the data in JSON as follows:

```json
{
	"items": [
		{
			"title": "Heat Wave In Texas and Central Plains Could Be the Hottest Yet",
			"link": "https://www.nytimes.com/2022/06/25/us/heat-wave-texas-oklahoma-plains.html",
			"guid": "https://www.nytimes.com/2022/06/25/us/heat-wave-texas-oklahoma-plains.html",
			"description": " ",
			"dc:creator": "Isabella Grullón Paz",
			"pubDate": "Mon, 18 Jul 2022 04:10:13 +0000",
			"media:credit": "Shelby Tauber/Reuters",
			"media:description": "A dried-up riverbed of the Trinity River in Dallas on Tuesday. In the coming week, parts of Texas could see their hottest temperatures of the summer yet."
		}
	],
	"title": "NYT &gt; Top Stories",
	"link": "https://www.nytimes.com",
	"language": "en-us",
	"copyright": "Copyright 2022 The New York Times Company",
	"lastBuildDate": "Mon, 18 Jul 2022 10:33:55 +0000",
	"pubDate": "Mon, 18 Jul 2022 10:06:46 +0000",
	"image": {
		"title": "NYT &gt; Top Stories",
		"url": "https://static01.nyt.com/images/misc/NYT_logo_rss_250x40.webp",
		"link": "https://www.nytimes.com"
	}
}
```

## Implementation:

To get the functionality we seek, we first will need to send an `HTTP`-`GET`[^5] request and get our XML data, after
that we split the result by lines and parse each line, this should be more efficient than parsing the whole data in one
go.

### Imports and regular expressions

At the top of the file we import `fetch` from the node-fetch[^6] project and declare our RegEx[^7] query which we will
use to split the lines later.

```js
import fetch from "node-fetch"; // 85.4k (gzipped: 23.5k)

const TAG_REGEX = new RegExp(/<|>/);
```

> Building RegEx queries before loops instead of in loops will greatly improve your runtime performance, especially on
> large XML files

### Getting the feed data

The next step is to first declare the object which we will use to store all key-value pairs found in the data and
secondly we declare the parsing function with an url as a parameter.

The function is asynchronous due to making a web request.:

```js
/**/

async function parse_rss(url) {
	let feed = {
		items: [],
	};

	let res = await fetch(url)
		.then(async (x) => {
			return (await x.text()).trim().split("\n");
		})
		.catch((e) => console.error(e));

	return feed;
}
```

Our method awaits the Promise returned by calling fetch and again awaits the conversion into text. After the content is
available it gets trimmed (removing whitespace in front and behind) and split into lines by splitting at each `\n`. Our
error handling is done by having a catch console erroring every error occurring.

### The problem with child elements p.I

If you think about it, at this point we can parse line by line and easily extract content such as the title,
description, link and other stuff. But what about a child element such as `item` title, link and description. How do we
know if we are currently in a child context. To fix this problem we introduce two new variables:

```js
/**/

let lastImportantKey = "";
let itemObj = {};
```

The variable `lastImportantKey` is used to check if we are currently in a child context. `itemObj` is used to insert
values if we are in a child context and if the end tag such as `</item>` is encountered push the object into the
`feed.items` array.

### Parsing setup

To begin parsing we of course have to loop over our response...

```js
/**/

let lastImportantKey = "";
let itemObj = {};

res.forEach((el) => {});
```

and split each line using our already build regex query:

```js
/**/

let lastImportantKey = "";
let itemObj = {};

res.forEach((el) => {
	el = el.split(TAG_REGEX);
	/* do stuff*/
});

/**/
```

To visualize our line after splitting, we do a quick `console.log`:

```js
res.forEach((el) => {
	el = el.split(TAG_REGEX);
	console.log(el);
});
```

```bash
$: npm start
['', 'title', 'NYT &gt; Top Stories', '/title', '']
['', 'link', 'https://www.nytimes.com', '/link', '']
```

As you can see we conveniently have the tag type/name at the index `1` of the array and the content at the index `2` of
the array.

### Do i like this tag?

Sometimes one can find XML tags like the following with additional attributes. Personally i don't need the attributes,
so i will only use the tag name as the key:

```xml
<guid isPermaLink="true">https://www.nytimes.com/2022/07/17/us/politics/climate-change-manchin-biden.html</guid>
<category domain="http://www.nytimes.com/namespaces/keywords/nyt_org">Robb Elementary School (Uvalde, Tex)</category>
```

```js
/**/
let lastImportantKey = "";
let itemObj = {};

res.forEach((el) => {
	el = el.split(TAG_REGEX);

	if (el[1].includes(" ")) el[1] = el[1].split(" ")[0];

	/* parse here */

	/**/
});
```

Splitting the tag name at the space converts the above into the following json:

```js
{
  /**/
  guid: "",
  category: "",
  /**/
}
```

### The (not so) hard part

We now know if a tag is what we want to have in our JSON result and therefore can now work on getting the value and the
key into the feeds object. The next thing to do is checking if the tag has any content, as discussed before and
afterwards inserting the content as a value with the tag name as a key into the resulting JSON object.:

```js
/**/
let lastImportantKey = "";
let itemObj = {};

res.forEach((el) => {
	/*split line */

	if (el[2]) {
		feed[el[1]] = el[2];
	}

	/**/
});
```

If you run this you will notice some issues...

```json
{
  "items": [],
  "title": "In Rome, a New Museum for Recovered Treasures Before They Return Home",
  "link": "https://www.nytimes.com/2022/07/17/arts/design/rome-museum-recovered-treasures.html",
  "language": "en-us",
  "copyright": "Copyright 2022 The New York Times Company",
  "lastBuildDate": "Mon, 18 Jul 2022 10:28:54 +0000",
  "pubDate": "Sun, 17 Jul 2022 19:45:54 +0000",
  "url": "https://static01.nyt.com/images/misc/NYT_logo_rss_250x40.webp",
  "guid": "https://www.nytimes.com/2022/07/17/arts/design/rome-museum-recovered-treasures.html",
  "description": "The Museum of Rescued Art showcases antiquities that were looted or otherwise lost before they go back to institutions in the regions from which they were taken.",
  "dc:creator": "Elisabetta Povoledo",
  "media:credit": "Gianni Cipriano for The New York Times",
  "media:description": "The Museum of Rescued Art in Rome, which opened last month, is focusing attention on the many art
works that have been salvaged, some from natural disasters and others from thieves.",
  "category": "Museum of Rescued Art"
}
```

First of all the title is all wrong, its now the title of the last item. The same issue persists in link and description
as well. Also we don't even have any items in the Array.

The first issue is easily explainable - an object can only have unique keys, therefore parsing further into the data
will only overwrite the already set values such as title, description and url.

This brings us to the next section:

### The problem with child elements p.II

As explained in p.I we already laid the foundation to fix the problems above by declaring two variables. Now we simply
implement the usage of these two for `item` and `image` parent and their child elements.:

So now lets check if we have a tag with the name item or image and set `lastImportantKey` to the corresponding tag name.

```js
/**/
let lastImportantKey = "";
let itemObj = {};

res.forEach((el) => {
	/*split line */

	if (el[1] === "item" || el[1] === "image") lastImportantKey = el[1];
	else if (el[1] === "/item" || el[1] === "/image") {
		lastImportantKey = "";
		if (el[1] === "/image") feed.image = itemObj;
		else feed.items.push(itemObj);
		itemObj = {};
	}
	if (el[2]) {
		if (lastImportantKey === "item" || lastImportantKey === "image") itemObj[el[1]] = el[2];
		else feed[el[1]] = el[2];
	}

	/**/
});
```

As one can see we reset the `lastImportantKey` variable if the end tag of either `item` or `image` is encountered. We
either push our `itemObj` into the `feed.items` array if the closing tag was an item or add an `image` object to feed if
the closing tag was an image. After being done with the `itemObj` we reset it to be empty again.

To finish up we insert parsed values into the `itemObj` if `lastImportantKey` is item or image, otherwise we insert
normally.

## Wrapping up

The parser now produces the following output for a german newspaper based on their rss feed:

```js
parse_rss("https://www.spiegel.de/schlagzeilen/tops/index.rss").then((_) => {
	console.log(JSON.stringify(_, null, 2));
});
```

```json
{
	"items": [
		{
			"title": "Klimakrise: Die Hitze sucht Europa heim",
			"link": "https://www.spiegel.de/wissenschaft/mensch/klimakrise-die-hitze-sucht-europa-heim-a-89aa1152-ed32-40af-9606-8fd6573423f2#ref=rss",
			"description": "Wieder rollt eine Welle heißer Luft über die iberische Halbinsel und über Westeuropa. In der kommenden Woche erreicht sie Deutschland. Wir werden lernen müssen, mit Hitze, Dürre und Bränden zu leben.",
			"category": "Wissenschaft",
			"guid": "https://www.spiegel.de/wissenschaft/mensch/klimakrise-die-hitze-sucht-europa-heim-a-89aa1152-ed32-40af-9606-8fd6573423f2",
			"pubDate": "Thu, 14 Jul 2022 10:25:33 +0200",
			"content:encoded": "Wieder rollt eine Welle heißer Luft über die iberische Halbinsel und über Westeuropa. In der kommenden Woche erreicht sie Deutschland. Wir werden lernen müssen, mit Hitze, Dürre und Bränden zu leben."
		}
	],
	"title": "DER SPIEGEL - Schlagzeilen - Tops",
	"link": "https://www.spiegel.de/",
	"description": "Deutschlands führende Nachrichtenseite. Alles Wichtige aus Politik, Wirtschaft, Sport, Kultur, Wissenschaft, Technik und mehr.",
	"language": "de",
	"pubDate": "Mon, 18 Jul 2022 12:30:03 +0200",
	"lastBuildDate": "Mon, 18 Jul 2022 12:30:03 +0200",
	"image": {
		"title": "DER SPIEGEL",
		"link": "https://www.spiegel.de/",
		"url": "https://www.spiegel.de/public/spon/images/logos/der-spiegel-h60.webp"
	}
}
```

### Source:

```js
import fetch from "node-fetch";

const TAG_REGEX = new RegExp(/<|>/);

async function parse_rss(url) {
	let feed = {
		items: [],
	};

	let res = await fetch(url)
		.then(async (x) => {
			return (await x.text()).trim().split("\n");
		})
		.catch((e) => console.error(e));

	let lastImportantKey = "";
	let itemObj = {};

	res.forEach((el) => {
		el = el.split(TAG_REGEX);

		if (el[1].includes(" ")) el[1] = el[1].split(" ")[0];

		if (el[1] === "item" || el[1] === "image") lastImportantKey = el[1];
		else if (el[1] === "/item" || el[1] === "/image") {
			lastImportantKey = "";
			if (el[1] === "/image") feed.image = itemObj;
			else feed.items.push(itemObj);
			itemObj = {};
		}

		if (el[2]) {
			if (lastImportantKey === "item" || lastImportantKey === "image") itemObj[el[1]] = el[2];
			else feed[el[1]] = el[2];
		}
	});

	return feed;
}

parse_rss("https://www.spiegel.de/schlagzeilen/tops/index.rss").then((_) => {
	console.log(JSON.stringify(_, null, 2));
});
```

[^1]: https://www.w3schools.com/xml/xml_parser.asp
[^2]: https://nodejs.org/en/
[^3]: https://www.rssboard.org/rss-specification
[^4]: https://reactnative.dev/
[^5]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET
[^6]: https://www.npmjs.com/package/node-fetch
[^7]: https://en.wikipedia.org/wiki/Regular_expression
