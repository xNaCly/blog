---
title: "Image editor in C: Part I"
summary: Writing a basic image editor as a comp science project, Part I
author: xnacly
date: 2022-03-08
tags:
    - c
---

## Project Overview

I am currently majoring in applied computer science at [DHBW](https://www.dhbw.de/startseite). In the first Semester, we
have to submit the first programming project, which is an image editor in C conforming to the PGM standard. It is split
in three subtasks and is to be finished till late March.

|       Task I        |        Task II        | Task III |
| :-----------------: | :-------------------: | :------: |
| methods in `_pgm.h` | methods in `_image.h` |   TUI    |

### Grading

| x                         | Points        |
| ------------------------- | ------------- |
| Task I                    | 15            |
| Task II                   | 15            |
| Task III                  | 10            |
| Robustness & compilablity | 5             |
| Comments & structure      | 5             |
| **Total**                 | **50 Points** |

### Project description

The `PGM` editor should implement the `Portable GrayMap` standard, which I will explain in the next chapter. It should
also include methods to manipulate Images in the `PGM`-format. The following functions are required by the lecturer. :

### README

```text
pgmE - portable graymap Editor
==========
pgmE is an extremely fast, small and efficient editor which implements the pgm standard.

Requirements
------------
In order to build you need:
    - make
    - gcc

Running pgmE
------------
Start it by running:

    make run

This will compile pgmE.

Features
------------
- load pgm images
- save pgm images
- edit pgm images:
    - median filter
    - gauss operator
    - laplace operator
    - resize
    - rotate
    - threshold operato
```

#### Regarding Images

1. create an image structure
2. free the memory of an image structure
3. deep copy an image
4. load image from file system into the program
5. save image to file system

#### Filters and Operators

1. `median` filter
2. `gauss` filter
3. `laplace` operator
4. `threshold` operator
5. `scale`
6. `rotate`

### `.pgm` Standard

#### Differentiating between the three `P*` -image formats

| Type             | ASCII (plain) | Binary (raw) | Extension | Colors                      |
| ---------------- | ------------- | ------------ | --------- | --------------------------- |
| Portable BitMap  | P1            | P4           | .pbm      | 0-1 (white & black)         |
| Portable GrayMap | P2            | P5           | .pgm      | 0-255, 0-65535 (gray scale) |
| Portable PixMap  | P3            | P6           | .ppm      | etc.                        |

[`PGM`](https://en.wikipedia.org/wiki/Netpbm#File_formats) or in my case
[`P2`](http://netpbm.sourceforge.net/doc/pgm.html) is a image format coming from the
[Netpbm Project](https://en.wikipedia.org/wiki/Netpbm). It consists of the two characters `P` and `2` in the first line
of the file to indicate the image format. The second line contains the Dimensions of the image, e.g.: `1920 1080` . The
third line contains the max. brightness possible in the image. Line 3 till the End of the file specifies the pixel grey
values. The specification allows for comments between the first line (format indicator) and the second line (dimension
definition), prefixed with `#` .

#### Example:

```text
P2
# Shows the word "FEEP" (example from Netpbm man page on PGM)
24 7
15
0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
0  3  3  3  3  0  0  7  7  7  7  0  0 11 11 11 11  0  0 15 15 15 15  0
0  3  0  0  0  0  0  7  0  0  0  0  0 11  0  0  0  0  0 15  0  0 15  0
0  3  3  3  0  0  0  7  7  7  0  0  0 11 11 11  0  0  0 15 15 15 15  0
0  3  0  0  0  0  0  7  0  0  0  0  0 11  0  0  0  0  0 15  0  0  0  0
0  3  0  0  0  0  0  7  7  7  7  0  0 11 11 11 11  0  0 15  0  0  0  0
0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
```

## Directory structure

After reading two dozen blogs and a lot of trial and error, i settled on the following dir structure:

```text
.
├── build
│  └── main.out
├── makefile
├── README
└── src
   ├── libs
   │  ├── image
   │  │  ├── _image.c
   │  │  └── _image.h
   │  ├── pgm
   │  │  ├── _pgm.c
   │  │  └── _pgm.h
   │  └── util
   │     ├── _util.c
   │     └── _util.h
   └── main.c
```

### Files:

In the following I will try to explain the file contents and what they do. _The how to the what will follow in the next
parts of this series._

#### `_image.(c|h)`

includes several image manipulation methods

```c
/**
 * @file _image.h
 * @author xnacly
 * @brief includes several image manipulation methods
 * @date 2022-02-21
 */

#ifndef _IMAGE_H_INCLUDED
#define _IMAGE_H_INCLUDED
#include "../pgm/_pgm.h"
// used for: copyImage, createImage
#include "../util/_util.h"
// used for: compare

#define PI 3.141592

/**
 * @brief Applies the median filter to the given image
 * @param img
 */
Image *median(Image *img);

/**
 * @brief Applies the gauss filter to the given image
 * @param img
 */
Image *gauss(Image *img);

/**
 * @brief Modifies the image using the laplace-operator
 * @param img
 */
Image *laplace(Image *img);

/**
 * @brief Modifies the Image using the thresholding method
 * @param img
 * @param threshold
 */
Image *threshold(Image *img, int threshold);

/**
 * @brief Scales the given Image to the width and height specified
 * @param img
 * @param width
 * @param height
 */
Image *scale(Image *img, int width, int height);

/**
 * @brief Rotates the Image to the given angle
 * @param img
 * @param angle
 * @param brigthness
 */
Image *rotate(Image *img, double angle, int brigthness);
#endif
```

#### `_pgm.(c|h)`

handles everything regarding images in the .pgm standard

```c
/**
 * @file _pgm.h
 * @brief handles everything regarding images in the .pgm standard
 * http://netpbm.sourceforge.net/doc/pgm.html (Plain PGM)
 * @author xnacly
 * @date 2022-02-21
 */
#ifndef _PGM_H_INCLUDED
#define _PGM_H_INCLUDED

#define MAX_BRIGHT 255

/**
 * @brief struct to store PGM-image data in
 */
typedef struct {
  int width;
  int height;
  int **data; // 2d pointer: Brightness values
} Image;

/**
 * @brief creates an Image with given width and height, set every pixel to the
 * default_brightness
 * @param width
 * @param height
 * @param default_brightness
 * @return *Image
 */
Image *createImage(int width, int height, int default_brightness);

/**
 * @brief frees the memory taken up by the given Image pointer
 * @param img_pointer Image pointer created with createImage()
 */
void freeImage(Image *img_pointer);

/**
 * @brief  copys the image from the given pointer to a new pointer
 * @param img_pointer Image pointer created with createImage()
 * @return *Image
 */
Image *copyImage(Image *img_pointer);

/**
 * @brief loads image from filesystem with given file name (without extension)
 * @param file_name
 * @return *Image
 */
Image *loadImage(char file_name[]);

/**
 * @brief saves the given pointer in a .pgm file with the given name
 * @param file_name
 * @param img_pointer Image pointer created with createImage()
 * @return 0 or 1
 */
int saveImage(char file_name[], Image *img_pointer);

#endif
```

#### `_util.(c|h)`

provides utility methods and defines ANSI macros for colored output, as well as an enum for the main menu selection
handling

```c
/*
 * _util.h provides utility methods
 */
#ifndef _UTIL_H_INCLUDED
#define _UTIL_H_INCLUDED

#include "../pgm/_pgm.h"

#define ANSI_COLOR_RED "\x1b[91m"
#define ANSI_COLOR_GREEN "\x1b[92m"
#define ANSI_COLOR_YELLOW "\x1b[93m"
#define ANSI_STYLE_BOLD "\x1b[1m"
#define ANSI_RESET "\x1b[0m"

enum {
  SELECTION_LOAD = 0,
  SELECTION_MEDIAN_FILTER,
  SELECTION_GAUSS_FILTER,
  SELECTION_LAPLACE_OPERATOR,
  SELECTION_THRESHOLD,
  SELECTION_SCALE,
  SELECTION_ROTATE,
  SELECTION_SAVE,
  SELECTION_EXIT, // ALWAYS LATEST AVAILABLE OPTION ;)
  SELECTION_INVALID =
      9999 // MAKE SURE THAT THIS WILL RUN INTO THE INVALID SECTION ;)
};

/**
 * used for qsort
 * @param a
 * @param b
 * @return
 */
int compare(const void *a, const void *b);

/**
 * @brief converts string to integer
 * @param text
 * @return integer
 */
int toInt(const char *text);

/**
 * @brief exits the program and prints the given text highlighted red
 * @param text
 */
void throw_error(char text[]);

/**
 * @brief prints the given text highlighted yellow, differs from throw_error by
 * not exiting the program.
 * @param text
 */
void throw_warning(char text[]);

/**
 * @brief checks if the selection meets certian criteria
 * @param selection
 * @param arr_size size of the array containing possible inputs
 * @param edited_unsaved_image_in_memory
 * @param image_in_memory
 */
int check_is_option_valid(int selection, int image_in_memory);
#endif

```

#### `main.c`

takes care of printing the main menu and handling user input, runs the functions implemented in the 'libs'

## Compiler setup

### Compiler choice

The lecturer gave us very specific instructions on how and where to compile our project. The project has to be compiled
with [gcc](https://gcc.gnu.org/) on a Unix system. I’m using Unix for around 2 years now, this makes the requirement
easily fulfillable.

### Compiler flags

Some [warning compiler flags](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html) are mandatory:

-   `-fdiagnostics-color=always` (Use color in diagnostic)
-   `-Wall` (enables all warnings about constructions that are easy to avoid)
-   `-Wpedantic` (Issue all the warnings demanded by strict ISO C)

Some were added by me:

-   `-lm` (link the math library)
-   `-g` (tell gcc to generate debugging and symbol information, _necessary for debugging using
    [gdb](https://en.wikipedia.org/wiki/GNU_Debugger)_)

_After me asking, the lecturer told us to use the [C99](https://en.wikipedia.org/wiki/C99) standard (`-std=c99`)._

### Makefile

After learning about makefiles _(before I knew about them I wrote a shell script to compile my project)_ and gdb I
promptly used both in this project:

```makefile
cc := -fdiagnostics-color=always \
			-Wall -Wpedantic -std=c99 \
			src/main.c src/libs/util/_util.c \
			src/libs/pgm/_pgm.c \
			src/libs/image/_image.c \
			-lm -o build/main.out
main:
	gcc ${cc}
	build/main.out
debug:
	gcc -g ${cc}
	gdb build/main.out
clean:
	rm -r build/; rm test.pgm
pre:
	mkdir build/
```

-   `make main`

    compiles and runs the executable

-   `make debug`

    compiles with the `-g` flag and starts gdb on the executable

-   `make clean`

    removes generated images and the build folder recursive

-   `make pre`

    creates the build dir, due to me being lazy

### Updated, more complicated Makefile

I won't explain too much here, due to the extensive comments and the explaining I've done before. If you are interested
in learning more about `Makefiles`, take a look [here](https://www.gnu.org/software/make/manual/make.html).

New features:

-   more compiler flags
-   better structure
-   comments
-   dynamic (can compile even if i add new source files)
-   made build steps dependent on the pre target

```makefile
# compiler flags
MANDATORY_FLAGS := -fdiagnostics-color=always  \
									-Wall \
									-Wpedantic \
									-std=c99

									# use color in diagnostics
									# enables all construction warnings
									# enable all warnings demanded by ISO C
									# follow ANSI C99

MY_FLAGS := -Wextra \
						-Werror \
						-Wshadow \
						-Wundef \
						-fno-common \

						# set of warnings and errors not covered by -Wall
						# all warnings cause errors
						# warnings for shadowing variables
						# warnings for undefined macros
						# warnings for global variables

BUILD_DIR := ./build
SRC_DIR := ./src

# finds all source files in /src/*
FILES := $(shell find $(SRC_DIR) -name "*.c")

COMPILE := $(MANDATORY_FLAGS) $(MY_FLAGS) $(FILES) -lm -o $(BUILD_DIR)/main.out

# run the previously built executable
run: main
	$(BUILD_DIR)/main.out

# compile the executable
main: pre
	gcc -O2 $(COMPILE)

# compiles executable with debugging info and runs it with the GNU-debugger (gdb)
debug: pre
	gcc -g3 $(COMPILE)
	gdb $(BUILD_DIR)/main.out

# creates build dir, only if its not created yet
pre:
	mkdir -p $(BUILD_DIR)

# removes build and test files/dirs
.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
	rm -f test.pgm
```

> ##### PS:
>
> The next part will focus on the methods found in `_pgm.(c|h)` and some general issues I found myself having while
> working on this project.
