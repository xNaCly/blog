---
title: "Using Vue.js with Electron"
summary: "Guide for setting up and packaging a vue.js project with electron and vite"
date: 2023-01-02
---

{{<callout type="Abstract">}}
This is a simple and minimal guide for getting vue.js up and runnning with electron.

Documentation:

- [Vue.js](https://vuejs.org/guide/introduction.html)
- [Electron](https://www.electronjs.org/)
- [electron-forge](https://www.electronforge.io/)
  {{</callout>}}

## Vue.js

```bash
# install and run vue scaffholding tool
npm run vue@latest
# replace <project-name> with the name you specified
cd <project-name>
# install dependecies
yarn
# start dev server
yarn dev
```

This should output:
![console output](/vue-electron/vite.png)

_more info on setting up a vue.js project_[^1]

Navigating to `localhost:<port>` (take a look at the port in the console output) should display the following:

![vue hello world](/vue-electron/vue-hello-world.png)

## Electron

### Adding electron to the project

```bash
# install electron as a dev dependecy
yarn add -D electron@latest
```

Create and open `main.js` at the root of your project. Paste the following into it:

```javascript
const { app, BrowserWindow } = require("electron");
const path = require("path");

// function to create the window from our vue.js project
function createWindow() {
  // get a new instance of window with specified dimensions
  const window = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
    },
  });

  // vue.js outputs to ./dist, therefore we load our index.html from there
  window.loadURL(path.join(__dirname, `/dist/index.html`));
  window.on("closed", function () {
    window = null;
  });
}

// create the window once electron finished starting
app.on("ready", createWindow);

// if all instances of our window are closed close the parent instance
app.on("window-all-closed", function () {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", function () {
  if (mainWindow === null) createWindow();
});
```

After this, add the following highlighted lines to your `package.json`: 
```json {hl_lines=[5, 10]}
{
  "name": "electron-vue",
  "version": "0.0.0",
  "private": true,
  "main": "main.js",
  "scripts": {
    "dev": "vite",
    "start-electron": "vite build && electron .",
    "build": "run-p type-check build-only",
    "preview": "vite preview",
    "test:unit": "vitest --environment jsdom --root src/",
    "build-only": "vite build",
    "type-check": "vue-tsc --noEmit -p tsconfig.vitest.json --composite false"
  }
}
```

{{<callout type="Tip">}}

- To develop the application in the browser, run: `yarn dev`
- To develop the application in a electron instance, run: `yarn start-electron`
  {{</callout>}}

{{<callout type="Warning">}}
While running the `yarn start-electron` command one will notice the lack of content in the newly spawned electron window.

To fix this, add the following to your `vite.config.js`:

```javascript {hl_lines=[17]}
import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueJsx from "@vitejs/plugin-vue-jsx";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), vueJsx()],
  resolve: {
    alias: {
      "@": fileURLToPath(
            new URL("./src", import.meta.url)
        ),
    },
  },
  base: "./",
});
```
{{</callout>}}

### Packaging the Application

To package our application we will use `electron-forge`. 

1. Installing electron forge
    ```bash
    yarn add -D @electron-forge/cli
    ```
2. Importing the project into electron forge
    ```bash
    npx electron-forge import
    ```
3. Packaging the application
    ```bash
    yarn package
    ```

Navigate to `<project>/out/<project>-<os>-<arch>`, here you can find the generated files for the project.

### Creating a installer
The installer allows users to click on a executable and have it install on their system.
{{<callout type="Tip">}}
The installer requires an author and a description, otherwise it won't run. To fulfil these requirements we need to add the following to our `package.json`: (replace `<author>` with your name)


```javascript {hl_lines=[6,7]}
{
  "name": "electron-vue",
  "version": "0.0.0",
  "private": true,
  "main": "main.js",
  "author": "<author>",
  "description": "test app",
  "scripts": {
    "dev": "vite",
    "dev-electron": "vite build && electron .",
    "start": "electron-forge start",
    "build": "run-p type-check build-only",
    "preview": "vite preview",
    "test:unit": "vitest --environment jsdom --root src/",
    "build-only": "vite build",
    "type-check": "vue-tsc --noEmit -p tsconfig.vitest.json --composite false",
    "package": "electron-forge package",
    "electron": "electron-forge make",
    "make": "electron-forge make"
  }
}
```
{{</callout>}}

```bash
yarn make
```

Wait for the completion and navigate to `out/make/<maker>/<arch>/` and take a look at the binary it created in the format: `<name>-<version> Setup.*`.

[^1]: https://vuejs.org/guide/quick-start.html#creating-a-vue-application
