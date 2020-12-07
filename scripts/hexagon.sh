if [ $3 -gt 1000 ]; then
	t="2"
else
	t="1"
fi
./stainedglass.sh -k hexagon -b 150 -t $t -s $( printf "%.0f" $( echo "$3*0.036" | bc ) ) $1 $2
