---
title: "Image editor in C: Part II"
summary: Writing a basic image editor as a comp science project, Part II
author: xnacly
date: 2022-03-09
tags:
    - c
---

Today I will lay out the structure and functions of the `util` and `pgm` libraries. Generally speaking, you should take
all the following code and explanations with a grain of salt due to me not being very proficient in and with C.

## The PGM handler

Located in `src/libs/pgm/` the file contains all the functions showcased in the header file
[here](https://xnacly.vercel.app/blog/image_editor_part_1#Files).

We will get started with the easiest methods, working our way up to the harder functions.

The very first thing however will be me explaining the mandatory data structure we had to use.

### Image data structure

```c
typedef struct {
  int width;
  int height;
  int **data;
} Image;
```

Even though this is pretty self-explanatory, we should talk about the third value of the structure. The `int **data`
defines a double pointer containing each and every pixel from an image.

For instance, one can access the value of a pixel at the coordinates `x=0` and `y=0` by using the following snippet:

```c
Image *img = createImage(25,25,255);

int x = 0;
int y = 0;

int pixel_value_at_coords = img->data[x][y];
printf("pixel at (%d,%d): %d", x,y,pixel_value_at_coords);

// Result: pixel at (0,0): 255
```

As one can see, there is a function used in line 1 which wasn't introduced yet: `createImage()`

### The `createImage` method

This method is crucial for several other methods, such as `copyImage()` and `loadImage()`.

Create Image contains the following code, which we will walk through step by step:

```c
Image *createImage(int width, int height, int default_brightness) {
  Image *img;
  img = malloc(sizeof *img);

  img->width = width;
  img->height = height;

  img->data = (int **)malloc(height * sizeof(int *));

  for (int i = 0; i < height; i++) {
    img->data[i] = (int *)malloc(width * sizeof(int));

    for (int ii = 0; ii < width; ii++) {
      img->data[i][ii] = default_brightness;
    }
  }

  return img;
}
```

Foremost in Line one, we define the return type to be of type `Image`. Remember, we defined this structure at the
beginning. We define three parameters in the method head, which all share the type `int`.

Line two declares the variable `*img` of type `Image`-pointer, which we will return later. Line three allocates memory
for this variable, allowing us to store data in this variable.

The Lines four and five are assigning the values of our function parameters to the variables in the structure using the
arrow operator (`->`).

Right in the next line, we have a rather complicated line of code which allocates the double pointer to, again, allow us
to store data in it. Let's take a closer look at this line of code by splitting it in three parts:

-   `img->data =`: assigns everything right of `=` to the `data` variable in the `img` pointer
-   `(int **)`: `malloc` returns `void*`, therefore we need to cast this pointer into a double `int` pointer
-   `malloc(height * sizeof(int *))`

The last one is a bit tricky:

We know we use `malloc` to allocate memory, but what does `height * sizeof(int *)` do, and why do we need to use it
here? The answer is simpler than you think.:

Basically, the data field is an array of pointers, each of them is filled with exactly as many pixels as the height is
big. Let's visualize this concept:

| Image     | Width: 0 | Width: 1 | Width: 2 |
| --------- | -------- | -------- | -------- |
| Height: 0 | 0,0      | 0,1      | 0,2      |
| Height: 1 | 1,0      | 1,1      | 1,2      |
| Height: 2 | 2,0      | 2,1      | 2,2      |

You should notice our point of origin being in the top right, learn why
[here](https://gamedev.stackexchange.com/questions/83570/why-is-the-origin-in-computer-graphics-coordinates-at-the-top-left).
This means you can mentally visualize this concept by simply flipping the known coordinate system upside down, meaning
0,0 is in the top left corner instead of the bottom left corner. As you can see, in this example the array contains
three arrays with height, therefore we allocate the field with the size of `height*sizeof(int)`. To explain in simple
terms, we tell the compiler to expect three fields of height, which we will later each fill with values.

After explaining this line in depth, we will now take a closer look at the for loops of this function. The first one
loops over the columns of the field we just allocated and allocates each one of these rows with:

```c
img->data[i] = (int *)malloc(width * sizeof(int));
// cast *void into *int, allocate as many items as there are pixels for each height, e.g.: 0-1080, 1-1080, 2-1080
```

The second loop assigns the default value specified in the function parameter `default_brightness` to every pixel in the
data field.

### The `freeImage` method

This method enables memory management for the main menu.

```c
void freeImage(Image **img_pointer) {
  if(*img_pointer == NULL) return;
  free(*img_pointer);
  *img_pointer = NULL;
}
```

> Pointers in C are passed by value not by reference, this means editing a pointer inside a function is only possible by
> passing the address of the pointer to the function.

Not much to explain here, the first line makes the function do nothing if the pointer is already `NULL`. The second line
frees the given pointer, and the third line assigns `NULL` to the just freed pointer. This is necessary due to the fact
that pointers can still point to random memory after being assigned.

More Info [here](https://moviecultists.com/does-freeing-a-pointer-set-it-to-null) and
[here](https://en.wikipedia.org/wiki/C_dynamic_memory_allocation).

### The `copyImage` method

This method performs a deep copy of the given Image pointer and returns it.

```c
Image *copyImage(Image *img_pointer) {
  int width = img_pointer->width;
  int height = img_pointer->height;
  Image *cpImage = createImage(width, height, 1);

  for (int i = 0; i < height; i++) {
    for (int ii = 0; ii < width; ii++) {
      cpImage->data[i][ii] = img_pointer->data[i][ii];
    }
  }

  return cpImage;
}
```

Line one and two assign the height and width of the passed image to temporary variables. Line 3 creates a new image. The
two `for`-loops loop over every item in every column and every row, allowing for a deep copy to be made.

### The `loadImage` method

This method was by far the hardest of any code to implement in the whole project. Wrapping my head around reading files
and parsing their contents was such a struggle and cost me a lot of time.

The method’s head is defined as follows:

```c
Image *loadImage(char file_name[]) {
```

The method can be called by passing a file name with path to the `file_name` parameter.

In line 1 we open the file, by passing the given file name and the `“r”` parameter to indicate the mode we intend to
use: _See `fopen` man pages [here](https://man7.org/linux/man-pages/man3/fopen.3.html)._

```c
FILE *file = fopen(file_name, "r");
```

Next we check if opening the file failed, if this is the case we return `NULL` to indicate failure.:

```c
if (file == NULL)
    return NULL;
```

Now we check if the file confirms to the `PGM/P2` standard, which I explained
[here](https://xnacly.vercel.app/blog/image_editor_part_1#pgm-standard).

To do this, we first need to get the first character of the file, which should be a `P`:

```c
char pgm_prefix = getc(file);
```

Directly after, we declare some variables for later usage:

```c
int pgm_version = 0;
int width = 0;
int height = 0;
int brightness = 0;
```

Now we get the first integer of the file, which should, if the file is PGM conform, be a 2 or a 5. But in our case only
needing to support P2, we can simply test for that:

```c
// get first int of the file
fscanf(file, "%d\n", &pgm_version);
// check if first line of the file conforms to the pgm standard
if (pgm_prefix != 'P' || pgm_version != 2) {
   return NULL;
}
```

Remembering the explanation from [here](https://xnacly.vercel.app/blog/image_editor_part_1#pgm-standard), we know the
second and third integers are the width and height and the fourth integer is the max brightness. To get these values, we
use `fscanf` again. We will need to check if the scanned variables are 0 or smaller than 0.:

```c
fscanf(file, "%d", &width);
fscanf(file, "%d", &height);
fscanf(file, "%d", &brightness);

if (width <= 0 || height <= 0 || brightness <= 0) {
    return NULL;
}
```

After establishing this solid foundation, we can now get started with creating the image and assigning all the values at
their respecting coordinates:

```c
Image *img = createImage(width, height, 255);
for (int i = 0; i < height; i++) {
	for (int ii = 0; ii < width; ii++) {
	  fscanf(file, "%d", &img->data[i][ii]);
	}
}
```

Finally, we close the file and return the created Image.

```c
fclose(file);
return img;
```

### The `saveImage` method

This function saves the image to a file.

Opening file with mode `“w”` (write) and return 0 if opening failed.:

```c
FILE *file = fopen(file_name, "w");
if (file == NULL) {
	return 0;
}
```

Now we print the first three lines, like the standard dictates.:

```
P2
width height
brightness
```

```c
fprintf(file, "P2\n%d %d\n%d\n", img_pointer->width, img_pointer->height, MAX_BRIGHT);
```

`*MAX_BRIGHT` is a macro in `_util.h` which I defined to be `255`.

To write all the pixel data into the file, we just loop over every pixel again and write the data to the file.:

```c
// loops over every pixel and appends the value to the file
for (int i = 0; i < img_pointer->height; i++) {
	for (int ii = 0; ii < img_pointer->width; ii++) {
	  fprintf(file, "%d\n", img_pointer->data[i][ii]);
  }
}
```

The function ends with closing the file and returning one as the indicator for success.

```c
fclose(file);
return 1;
```

## The Utility methods

This source file contains functions not fitting into the other modules. We have for example the compare function, which
is needed for a `qsort` call in the `median` function in `_image.c`.:

```c
int compare(const void *a, const void *b) {
  int int_a = *((int *)a);
  int int_b = *((int *)b);

  if (int_a == int_b)
    return 0;
  else if (int_a < int_b)
    return -1;
  else
    return 1;
}
```

There is also the `toInt` method, which converts a string to an integer. I wrote this function after Clang told me
multiple times to refrain from using `scanf` and I should use `strtol` instead, so I did.:

`strtol` documentation [here](https://man7.org/linux/man-pages/man3/strtol.3.html).

```c
int toInt(const char *text) {
  char *ptr;
  long l;

  l = strtol(text, &ptr, 10);

  return (int)l;
}
```

We also have two feedback methods to communicate errors and warnings to the user:

```c
void throw_error(char text[]) {
  printf("%s%s%s\n", ANSI_COLOR_RED, text, ANSI_RESET);
  exit(1);
}

void throw_warning(char text[]) {
  printf("%s%s%s\n", ANSI_COLOR_YELLOW, text, ANSI_RESET);
}
```

The last utility function is a check if the made selection in the main menu is a valid input:

Basically, if the selection is not in the defined range in the enum or there is currently no image in memory, disallow
the user to make edits to an image.

```c
int check_is_option_valid(int selection, int image_in_memory) {
  if (selection > SELECTION_EXIT) {
    return SELECTION_INVALID;
  }
  // disallow editing and saving if there is no file in mem
  if (selection != 0 && selection != SELECTION_EXIT && !image_in_memory) {
    throw_warning("No Image loaded into the program.");
    return SELECTION_INVALID;
  }
  return selection;
}
```

## Conclusion so far

For me personally, my lack of a sophisticated knowledge of c made the beginning and some parts of this project so far
very hard. I have some experience as a somewhat full-stack web-dev, but having to learn and use c in such a small amount
of time was very challenging. I had a hard time understanding pointers at first and made easily avoidable mistakes.
Whenever I searched online, I was feeling like there weren't that many resources. Linux man pages really helped me out,
but they don't introduce you to methods you could use for specific tasks, except of the `see also` section.

A big mistake I made from the beginning was to not read the PGM specification correctly, I just assumed I could access
all pixels by looping from 0 to width and in that loop, loop from 0 to height. This did in fact not work and gave me
headaches.

I also made the mistake of not knowing that pointers were passed by value not by reference, meaning the `freeImage`
method did in fact not free the memory taken up by the structures.

To conclude, I'd say it was smart to start working on the project this early, as I it is about to be finished.
