convert $1 -modulate 100,50 $2
./peelingpaint.sh -m cracks -s 100 -g 75 $2 scripts/images/peelingtexture.jpg $2
./picframe.sh $2 $2
