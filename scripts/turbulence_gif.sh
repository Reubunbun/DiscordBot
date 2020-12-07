command="convert -delay 4 $1 "
for i in `seq 20 2 60`; do
	command="$command \\( -clone 0 \\( -clone 0 -define convolve:scale='50%!' -bias 50% -morphology Convolve Sobel -colorspace gray -blur 0x$i -auto-level \\) -virtual-pixel mirror -background black -define compose:args='$( echo '$[$i*2]' | cut -d, -f1 ),$( echo '$[$i*2]' | cut -d, -f2 )' -compose displace -composite \\)"
done
for i in `seq 58 -2 22`; do
	command="$command \\( -clone 0 \\( -clone 0 -define convolve:scale='50%!' -bias 50% -morphology Convolve Sobel -colorspace gray -blur 0x$i -auto-level \\) -virtual-pixel mirror -background black -define compose:args='$( echo '$[$i*2]' | cut -d, -f1 ),$( echo '$[$i*2]' | cut -d, -f2 )' -compose displace -composite \\)"
done
command="$command -loop 0 $2"
eval $command
convert $2 -delete 0-1 $2
