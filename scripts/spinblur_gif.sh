command="convert -delay 1 $1 -radial-blur 6"
for i in `seq 8 2 24`; do
	command="$command \\( -clone 0 -radial-blur $i \\)"
done
for i in `seq 24 -2 6`; do
	command="$command \\( -clone 0 -radial-blur $i \\)"
done
command="$command -loop 0 $2"
eval $command
chmod 644 $2
