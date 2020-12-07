convert $1 -resize 520x601! -alpha set -background none -shear 0x30 -rotate -60 -gravity center -crop 1108x601-300+0 top_shear.png
convert $1 -resize 520x601! -alpha set -background none -shear 0x30 left_shear.png
convert $1 -resize 520x601! -alpha set -background none -shear 0x-30 right_shear.png
convert left_shear.png right_shear.png +append \( top_shear.png -repage +0-300 \) -background none -layers merge +repage -resize 30% $2
rm -f top_shear.png left_shear.png right_shear.png
