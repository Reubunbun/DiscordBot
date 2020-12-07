height=$( echo "$4*0.3" | bc )
command="convert -delay 3 $1 \( -alpha set -background none -fill red -stroke blue -font 'Helvetica-Bold' -gravity Center -size $3x$height caption:'$5' \) -gravity North -composite"
for i in `seq 104 4 200`; do
	command="$command \\( -clone 0 \\( -alpha set -background none -fill red -stroke blue -font 'Helvetica-Bold' -gravity Center -size $3x$height caption:'$5' -modulate 100,100,$i \\) -gravity North -composite \\)"
done
for i in `seq 4 4 96`; do
	command="$command \\( -clone 0 \\( -alpha set -background none -fill red -stroke blue -font 'Helvetica-Bold' -gravity Center -size $3x$height caption:'$5' -modulate 100,100,$i \\) -gravity North -composite \\)"
done
command="$command -loop 0 $2"
eval $command
chmod 644 $2
