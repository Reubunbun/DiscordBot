if [ -z "$8" ]
then
	fill="-fill white"
else
	fill="-fill $8"
fi
if [ -z "$9" ]
then
	stroke="-stroke black"
else
	stroke="-stroke $9"
fi
if [ -z "${10}" ]
then
	font="Helvetica-Bold"
else
	font="${10}"
fi
echo "fill = $fill, stroke = $stroke, font=$font"
convert -alpha set -background none $fill $stroke -font "$font" -gravity Center -size $3x$(echo "$4*0.3" | bc) caption:"$7" $5text.png
convert $1 $5text.png -gravity $6 -composite $2
rm $5text.png
