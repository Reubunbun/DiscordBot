command="convert -delay 40 $1"
for i in `seq 1 2 40`; do
	command="$command \\( -clone 0 -implode -$i -set delay 10 \\)"
done
command="$command -loop 0 $2"
eval $command
chmod 644 $2
