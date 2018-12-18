#!/bin/bash

# Location of downloaded images
TOP_IMG_DIR=../images/*/

for dir in $TOP_IMG_DIR; do
  echo "\n\n-----------------------------"
  echo "Optimizing directory $dir..."
  (cd $dir && jpegoptim *.jpg)
  echo "Done optimizing $dir."
done
