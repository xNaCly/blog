#!/bin/bash
files=`ls -la | awk '{ print $9 }'`
for file in $files
do
    `python3 $HOME/Programming/blog/static/convert.py $file`
done
rm -fr **.png
