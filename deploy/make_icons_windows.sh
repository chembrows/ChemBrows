#!/bin/bash

#http://stackoverflow.com/questions/4354617/how-to-make-get-a-multi-size-ico-file

convert icon-1024_FOR_MAC_WITH_ALPHA.png -bordercolor white -border 0 \
          \( -clone 0 -resize 16x16 \) \
          \( -clone 0 -resize 20x20 \) \
          \( -clone 0 -resize 24x24 \) \
          \( -clone 0 -resize 32x32 \) \
          \( -clone 0 -resize 40x40 \) \
          \( -clone 0 -resize 48x48 \) \
          \( -clone 0 -resize 64x64 \) \
          \( -clone 0 -resize 96x96 \) \
          \( -clone 0 -resize 256x256 \) \
          -delete 0 favicon.ico
