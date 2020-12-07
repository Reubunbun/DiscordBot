if [ -z "$3" ] 
then
	convert $1 -negate $2
else
	convert $1 -channel $3 -negate $2
fi
