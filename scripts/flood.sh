convert $1 scripts/images/waves_decreasing.png -filter spline -resize $3x$4\! -unsharp 0x1 -compose Displace -define compose:args=8x8 -composite -flip +level 0,80% -crop $3x$[$4/2]+0+$[$4/2] flood.png
convert $1 flood.png -gravity South -composite $2
rm flood.png
