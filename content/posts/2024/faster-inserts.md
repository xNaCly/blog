---
title: "Inserting 100k rows 66 times faster"
summary: "Doing less enables doing more INSERTs"
date: 2024-03-20
tags:
  - js
  - SQL
  - sqlite3
---

In the process of implementing the initial data syncing logic for a mostly
offline application I noticed my database abstraction taking a solid 2 minutes
for inserting short of 750k rows into a single database table.

I set out to fix this bottleneck.

## Problems and Issues

A new issue arose before i could even tackle the aforementioned performance
problems: At first I used the spread syntax for a variadic amount of function
parameters.

```js
class Database {
  async create(...items) {}
}
new Database().create(...new Array(750_000));
```

This polluted the call stack and promptly caused a stack overflow:

```text
/home/teo/programming_wsl/blog_test/main.js:7
new Database().create(...new Array(750_000));
               ^

RangeError: Maximum call stack size exceeded
    at Object.<anonymous> (/home/teo/programming_wsl/blog_test/main.js:7:16)
    at Module._compile (node:internal/modules/cjs/loader:1275:14)
    at Module._extensions..js (node:internal/modules/cjs/loader:1329:10)
    at Module.load (node:internal/modules/cjs/loader:1133:32)
    at Module._load (node:internal/modules/cjs/loader:972:12)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:83:12)
    at node:internal/main/run_main_module:23:47

Node.js v19.9.0
```

Believe me this seems obvious in retrospect, but it took me a solid day of
combing trough typescript source maps to find the cause.

{{<callout type="Takeaway">}}
I will never use the spread operator again - looking at you react.js
{{</callout>}}

## First Estimates and Benchmarking

Fixing this issue allowed me to call my `create` function and pass the rows to
insert in. The first tests were nothing short of disappointing: 57 seconds for
inserting 500k rows, 1min 10 seconds for inserting 750k rows - this was too
slow.

```js
  async create(items) {
    return new Promise((res, rej) => {
      this.connection.serialize(() => {
        this.connection.run("BEGIN TRANSACTION");
        for (let i = 0; i < items.length; i++) {
          try {
            this.connection.run(
              "INSERT INTO user (name, age) VALUES (?, ?)",
              items[i]?.name,
              items[i]?.age
            );
          } catch (e) {
            this.connection.run("ROLLBACK TRANSACTION");
            return rej(e);
          }
        }
        this.connection.run("COMMIT");
        return res();
      });
    });
  }
```

My next idea was to get specific and reproducible numbers, thus i created a
benchmark, for the simplified `create` implementation above, with differing
loads, starting with 10 rows and stopping at a million rows:

```js
const Database = require("./main.js");

const DB = new Database();

const amount = [10, 100, 1000, 10_000, 100_000, 1_000_000];
const data = { name: "xnacly", age: 99 };

describe("create", () => {
  for (const a of amount) {
    let d = new Array(a).fill(data);
    test(`create-${a}`, async () => {
      await DB.create(d);
    });
  }
});
```

Measured times:

|                | `create` |
| -------------- | -------- |
| 10 rows        | 2ms      |
| 100 rows       | 1ms      |
| 1,000 rows     | 13ms     |
| 10,000 rows    | 100ms    |
| 100,000 rows   | 1089ms   |
| 1,000,000 rows | 11795ms  |

## Approaches

My first idea was to omit calls in the hot paths that obviously are contained
in the create methods loop for inserting every row passed into it. After
taking a look, i notice there are no heavy or even many operations here. How
could I improve the database interaction itself? This was the moment I
stumbled upon bulk inserts.

```sql
INSERT INTO user (name, age) VALUES ("xnacly", 99);
```

The naive example implementation makes a database call for every row it wants
to insert. Bulk inserting reduces this to a single call to the database layer
by appending more value tuples to the above statement:

```sql
INSERT INTO user (name, age) VALUES
    ("xnacly", 99),
    ("xnacly", 99),
    ("xnacly", 99);
```

Using the above to implement a faster `create` method as follows:

```js
  async createFast(items) {
    if (!items.length) return Promise.resolve();
    let insert = "INSERT INTO user (name, age) VALUES ";
    insert += new Array(items.length).fill("(?,?)").join(",");
    let params = new Array(items.length * 2);
    let i = 0;
    for (const item of items) {
      params[i] = item.name;
      params[i + 1] = item.age;
      i += 2;
    }
    return new Promise((res, rej) => {
      this.connection.serialize(() => {
        this.connection.run("BEGIN TRANSACTION");
        try {
          this.connection.run(insert, params);
        } catch (e) {
          this.connection.run("ROLLBACK TRANSACTION");
          return rej(e);
        }
        this.connection.run("COMMIT");
      });
      return res();
    });
  }
```

Extending our tests for `createFast`:

```js
describe("createFast", () => {
  for (const a of amount) {
    let d = new Array(a).fill(data);
    test(`createFast-${a}`, async () => {
      await DB.createFast(d);
    });
  }
});
```

|                | `create` | `createFast` | Improvement |
| -------------- | -------- | ------------ | ----------- |
| 10 rows        | 2ms      | 1ms          | 2x          |
| 100 rows       | 1ms      | 1ms          | /           |
| 1,000 rows     | 13ms     | 3ms          | 4.3x        |
| 10,000 rows    | 100ms    | 22ms         | 4.5x        |
| 100,000 rows   | 1089ms   | 215ms        | 5.1x        |
| 1,000,000 rows | 11795ms  | 1997ms       | 5.9x        |

{{<callout type="Info">}}
The before benchmarks were done on the following system:

- CPU: Intel(R) Core(TM) i5-6200U CPU @ 2.30GHz 4 cores
- RAM: 8,0 GB DDR3 1600 MHz

The system was under heavy load while benchmarking, thus the recorded times
are still pretty slow.

{{</callout>}}

## Escaping from micro benchmarks into the real world

Applying the results from the micro benchmarks to my real world projects
database layer resulted in significant runtime improvements, up to 66x faster.

|             | `create` | `createFast` | Improvement |
| ----------- | -------- | ------------ | ----------- |
| 10 rows     | 7ms      | 2ms          | 3.5x        |
| 100 rows    | 48ms     | 1ms          | 48x         |
| 1000 rows   | 335ms    | 9ms          | 37.2x       |
| 10000 rows  | 2681ms   | 80ms         | 33.5x       |
| 100000 rows | 25347ms  | 390ms        | 66x         |
