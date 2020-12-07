command="convert -delay 5 $1"
for i in `seq 104 4 200`; do
	command="$command \\( -clone 0 -modulate 100,100,$i \\)"
done
for i in `seq 4 4 96`; do
	command="$command \\( -clone 0 -modulate 100,100,$i \\)"
done
command="$command -loop 0 $2"
eval $command
chmod 644 $2
