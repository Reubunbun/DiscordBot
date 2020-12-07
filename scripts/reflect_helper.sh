./reflect.sh -c $[$[$3*$5]/100] $1
if [ "$6" == "left" ]; then
	mv *_left.jpg $2
	rm *_blend.jpg *_right.jpg
elif [ "$6" == "right" ]; then
	mv *_right.jpg $2
	rm *_blend.jpg *_left.jpg
elif [ "$6" == "blend" ]; then
	mv *_blend.jpg $2
	rm *_right.jpg *_left.jpg
fi
