---
title: "How to fix corrupted git objects"
summary: "How to fix the 'object ... is corrupt' issue which renders git unusable"
date: 2023-01-26
tags:
  - git
  - guide
---

If you ever encountered the following issue, keep reading to fix it:

```text
$ git status
error: object file .git/objects/42/123456789abcde123456789abcde is empty
error: object file .git/objects/42/123456789abcde123456789abcde is empty
fatal: loose object 123456789abcde123456789abcde (stored in .git/objects/42/123456789abcde123456789abcde) is corrupt
$ git pull
error: object file .git/objects/42/123456789abcde123456789abcde is empty
fatal: loose object 123456789abcde123456789abcde (stored in .git/objects/42/123456789abcde123456789abcde) is corrupt
```

1. Navigate to the root of your git repo directory (the root should contain a `.git` folder, check `ls -la` and look for the `.git` folder at the top):
   ![ls-la](/corrupted-git/ls-la.png)
2. Run the following command:

   ```bash
   find .git/objects -size 0 -delete
   ```

   `find` looks for all files in the directory `.git/objects` with size `0` and deletes them

3. Run `git pull` and check if the output is correct. If it is, you removed all corrupted objects and therefore fixed the issue.

{{<callout type="Tip">}}
If this error keeps happening, consider making a backup of the files in your repo without the `.git` directory and clone a clean repo from the remote.
After that replace the contents with your backup and commit + push the changes to the remote.
{{</callout>}}
