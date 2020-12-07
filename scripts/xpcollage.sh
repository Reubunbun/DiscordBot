if [ "$3" -gt "$4" ]; then
	s=$[$3/2]
else
	s=$[$4/2]
fi
./overlapcrop.sh -s $s -o 50% -m sequential -u -M -L -R $1 $2
