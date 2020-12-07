if [ -z "$5" ]
then
	convert $1 -resize $3x$4 $2
else
	convert $1 -resize $3x$4\! $2
fi
