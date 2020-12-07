command="convert -delay 5 $1"
command="$command -bordercolor transparent -border 40x40"

for i in {2..90..2}; do
	s_arg=`echo "$i * 15" | bc`
	i_arg=`echo "scale=2; $i / 54" | bc`
	command="$command \\( -clone 0 -swirl $s_arg -implode $i_arg \\)"
done

command="$command -shave 40x40 +repage -loop 0 $2"

eval $command

chmod 644 $2
