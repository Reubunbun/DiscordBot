command="convert -delay 5 $1"
for i in `seq 0 0.05 3`; do
	command="$command \\( -clone 0 -implode $i \\)"
done
command="$command -loop 0 $2"
eval $command
chmod 644 $2
