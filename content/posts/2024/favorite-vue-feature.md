---
title: "My Favorite Vue.js Feature"
summary: "Sharing state up and down the DOM, My favorite Vue.js feature and its React.js counter part"
date: 2024-02-06
tags:
  - vue.js
  - react.js
---

## Sharing state down the DOM

Sharing state in a component based framework is a common task. Every
application I have ever build requested a list of data from a JSON-API and
rendered each item by sharing its data with a child component.

### The React way

Passing data down the DOM from the parent to a child component, is encouraged
to be done using component properties. (see [Sharing State Between
Components](https://react.dev/learn/sharing-state-between-components))

```jsx
// TitleList.jsx
import { useState } from "react";

function Title({ title }) {
  return <span>{title}</span>;
}

export default function TitleList() {
  const [titles, updateTitles] = useState(["title1", "title2", "title3"]);
  return (
    <div>
      {titles.map((t) => (
        <Title key={t} title={t} />
      ))}
    </div>
  );
}
```

Using react one can simply define a component named `Title` accepting a
singular argument called `title`. This component is then used to render the
list of titles by mapping over all values and passing the current title to the
children via the title property.

Modifying the list of titles can be done by invoking the `updateTitles` and
spreading the previous values as well as the new value into a new array:

```jsx
// TitleList.jsx
import { useState } from "react";

function Title({ title }) {
  return <span>{title}</span>;
}

export default function TitleList() {
  const [titles, setTitles] = useState(["title1", "title2", "title3"]);
  const [newTitle, setNewTitle] = useState("");
  return (
    <>
      <div>
        {titles.map((t) => (
          <Title key={t} title={t} />
        ))}
      </div>
      <input
        type="text"
        placeholder="new title"
        onChange={(event) => setNewTitle(event.target.value)}
      />
      <button onClick={() => setTitles([...titles, newTitle])}>Add</button>
    </>
  );
}
```

### How Vue.js does it

Using Vue.js the example can be written slightly more concise and intuitive:

```jsx
// Title.vue
<script setup lang="ts">
const props = defineProps<{ title: string }>();
</script>
<template>
  <span>{{ title }}</span>
</template>

// TitleList.vue
<script setup lang="ts">
import { ref } = from "vue";
import Title from "./Title.vue";

const titles = ref<Array<string>>([]);
const newTitle = ref<string>("");
</script>
<template>
  <div>
    <Title v-for="t in titles" :title="t" />
  </div>
  <input type="text" placeholder="new title" v-model="newTitle" />
  <button @click="titles.push(newTitle)">Add</button>
</template>
```

This is logically the same, vue does however allow for direct state
modification- thus omitting the need for allocating a new array each time we
add a new title via the spread syntax (`[...prevElements, newElement]`).

## Sharing state up the DOM

Here up the DOM refers to children modifying and sharing these updates with
their parents. Doing so directly is often not possible or discouraged by
frameworks such as React.js (However react doesn't even allow direct
modification of state inside the current component).

### React.js - Passing functions

When using React the parent often passes a function in which the parents state
is modified to the children via a prop:

```jsx
import { useState } from "react";

function Title({ title, deleteFunction }) {
  return (
    <div>
      <span>{title}</span>
      <button onClick={() => deleteFunction(title)}>Delete</button>
    </div>
  );
}

export default function TitleList() {
  const [titles, updateTitles] = useState(["title1", "title2", "title3"]);
  const [newTitle, setNewTitle] = useState("");
  function deleteByTitle(title) {
    updateTitles(titles.filter((t) => t !== title));
  }
  return (
    <>
      <div>
        {titles.map((t) => (
          <Title key={t} title={t} deleteFunction={deleteByTitle} />
        ))}
      </div>
      <input
        type="text"
        placeholder="new title"
        onChange={(event) => setNewTitle(event.target.value)}
      />
      <button onClick={() => updateTitles([...titles, newTitle])}>Add</button>
    </>
  );
}
```

The above example can be played with and ran here:
{{<rawhtml>}}

<iframe src="https://codesandbox.io/embed/xy2vtq?view=Editor+%2B+Preview&module=%2Fsrc%2FApp.js"
 style="width:100%; height: 500px; border:0; border-radius: 4px; overflow:hidden;"
 title="react.dev"
 allow="accelerometer; ambient-light-sensor; camera; encrypted-media; geolocation; gyroscope; hid; microphone; midi; payment; usb; vr; xr-spatial-tracking"
 sandbox="allow-forms allow-modals allow-popups allow-presentation allow-same-origin allow-scripts"
></iframe>
{{</rawhtml>}}

### Vue.js - emitting events

In the vue world we define a set of events we want to emit in the child
component, the parent component is then able to listen to these events and act
on them. (See [Event
Handling](https://vuejs.org/guide/essentials/event-handling.html))

```jsx
// Title.vue
<script setup lang="ts">
const props = defineProps<{ title: string }>();
const emit = defineEmits(["delete"])
</script>
<template>
  <span>{{ title }}</span>
  <button @click="emit('delete')">Delete</button>
</template>

// TitleList.vue
<script setup lang="ts">
import { ref } from "vue";
import Title from "./Title.vue";
const titles = ref<Array<string>>([]);
const newTitle = ref<string>("");
</script>
<template>
  <div>
    <Title
        v-for="t in titles"
        :title="t"
        @delete="titles = titles.filter((title) => t !== title)" />
  </div>
  <input type="text" placeholder="new title" v-model="newTitle" />
  <button @click="titles.push(newTitle)">Add</button>
</template>
```

{{<callout type="Tip">}}
The above example can be played with and ran
[here](https://play.vuejs.org/#eNqFU01T2zAQ/SuqLjgzYB+4pY6HtM2hPbRMyw1xcO11IpAljSSHMBn/9+5KsekBwm0/nt++XT0f+drafD8AX/LSN07awDyEwTJV6+1K8OAFr4SWvTUusCNz0LGRdc70THD8TvDPc/dOBgVTLy9iStwR0xjtAwtU82xFPOXaufql9MFJva2q7P5hMeM0PCe2hDxhMsEFJ1BZJK2orAzQW1UHwJixspX7GGCYCPZXnXG0CJP6NF5wtowRlTG5aUFBiNkkLwV5J1UAl2UxXbBVxQL7tDq1F4IXaWgxTS2ltgNu+WIjGxyIHtU1sDOqBdKBm6XPsbO/6g3OTtUoF4snzr9DCEazm0bJ5mmWltvB77IJjQqqdduWRQLTNYr5HPwSHw+v2clt/uiNxhc+ErPgjemtVOB+2SDx2oIvWexQr1bKPP+IteAGuJzqzQ6apzfqj/5ANcFvHXhwe9xg7oXabQEvQO3Nn5/xGnMTNx9o3zPN3+CNGkhjgn0ZdIuy/8NFtd+j+9Afd35zCKD9tBQJJeQY8dGuX8+s/ir3Or+O3wk94hVnH3/wjyTnWmcsOaiFTmq4paw8phdfsuRjNlbZq9Whl2HGbzDx2b3gyZKCPyzOud3bWlfHEz0bR0RS5U0D0ZzsIvFekHO+xfAd84z/AGr3Yz4=);

![vue-example](/vue-feature/vue.png)
{{</callout>}}

Event listeners and emitting events is a powerful tool for simplified state
management and I use both a lot when developing with Vue.js.

## Real world example

One can build components such as modals and confirmation prompts with custom
events and the ability to react to actions taken by the user. Lets now take a
look at one such example of a customisable modal:

```jsx
// Modal.vue
<script setup lang="ts">
const props = defineProps<{
    title: string;
    description: string;
    events: Array<{ title: string; name: string }>;
}>();
const emit = defineEmits();
</script>
<template>
    <div>
        <h3>{{ title }}</h3>
        <p>{{ description }}</p>
    </div>
    <div>
        <button
            v-for="event in events"
            @click="emit(event.name)"
        >
        {{ event.title }}
        </button>
    </div>
</template>

// App.vue
<script setup>
import {ref} from "vue";
import Modal from "./Modal.vue";
const eventOutput = ref("");
</script>

<template>
  <Modal
    title="Confirmation"
    description="Confirm you want to do that"
    :events="[
        {title: 'Yes', name: 'yes'},
        {title: 'No', name: 'no'}
        ]"
    @yes="eventOutput = 'yes'"
    @no="eventOutput = 'no'"
    />
    <span>{{ eventOutput }}</span>
</template>
```

Clicking one of the generated buttons changes the
`eventOutput` value to either _yes_ or _no_:

![vue-modal](/vue-feature/modal.png)

{{<callout type="Tip">}}
Read more about events, event handling and custom events [here]().
{{</callout>}}
