#!/bin/bash
#
# Developed by Fred Weinhaus 11/11/2014 .......... revised 7/17/2020
#
# ------------------------------------------------------------------------------
# 
# Licensing:
# 
# Copyright © Fred Weinhaus
# 
# My scripts are available free of charge for non-commercial use, ONLY.
# 
# For use of my scripts in commercial (for-profit) environments or 
# non-free applications, please contact me (Fred Weinhaus) for 
# licensing arrangements. My email address is fmw at alink dot net.
# 
# If you: 1) redistribute, 2) incorporate any of these scripts into other 
# free applications or 3) reprogram them in another scripting language, 
# then you must contact me for permission, especially if the result might 
# be used in a commercial or for-profit environment.
# 
# My scripts are also subject, in a subordinate manner, to the ImageMagick 
# license, which can be found at: http://www.imagemagick.org/script/license.php
# 
# ------------------------------------------------------------------------------
# 
####
#
# USAGE: tshirt [-r region] [-c coords] [-f fit] [-g gravity] [-v vshift] 
# [-o offset] [-R rotate] [-l lighting] [-s sharpen] [-b blur] [-d displace] 
# [-a antialias] [-A attenuate] [-B brightness] [-S saturation] [-C compose] 
# [-o opacity] [-E] [-D directory] infile bgfile [maskfile] outfile
#
# USAGE: tshirt [-help|-h]
#
# OPTIONS:
#
# -r     region        region is a simple rectangle defined as the WxH+X+Y 
#                      of the region in the tshirt (bgfile) where the overlay 
#                      image (bgfile) will be placed. The components of W, H 
#                      X and Y are integers and specify the width, height 
#                      xoffset and yoffset of the rectangle. Only one or the 
#                      other of region or coordinates should be specified. 
#                      But coordinates take precedent.
# -c     coords        coords are the 4 x,y corners of the region in the  
#                      tshirt (bgfile) where the overlay image (infile) will  
#                      be placed; coordinates must be listed clockwise from 
#                      top left corner; coordinates are integers>=0. Only  
#                      one or the other of region or coordinates should be 
#                      specified. But coordinates take precedent. Coordinates 
#                      are not restricted to a rectangle and the region 
#                      defined by the coordinates can have rotation.
# -f     fit           fit can be: crop (c), distort (d) scale (s), top (t) 
#                      or none (n); If crop, then the overlay image (infile) 
#                      will be resized to the width of the region (or coordinate 
#                      area) and cropped if needed. This will not distort the 
#                      image. The image will not be cropped, if its height is 
#                      smaller than that of the region and it will then be 
#                      aligned at the top of the region. If distort, then the 
#                      overlay image (infile) will be resized to fit exactly    
#                      to the region (or coordinate area). This will cause 
#                      distortion, if the aspect ratio of the overlay image 
#                      (infile) does not match the aspect ratio of the region 
#                      (or coordinate area). If scale, then the overlay image 
#                      (infile) will be resized so that the larger dimension 
#                      fits the region (or coordinate area) and the other 
#                      dimension is smaller. The resized overlay image (infile) 
#                      will be centered in the region. If top, then the overlay 
#                      image (infile) will be resized so that both width and 
#                      height fit into the region without distorting and placed 
#                      at the top center of the region. The default=none, which 
#                      means that the image will be resized to fit the width of  
#                      the region (or coordinate area) and aligned at the top of 
#                      the region. If the height of the resized image is larger 
#                      than the height of the region, it will extend past the 
#                      bottom of the region.
# -g     gravity       gravity for selecting the crop location; choices are:
#                      north (n), south (s) or center (c). The default=center
# -v     vshift        vertical shift of the crop region with respect to the 
#                      gravity setting; integer; negative is upward and positive 
#                      is downward; default=0 (no shift)
# -o     offset        additional x,y offset of the region or coordinates 
#                      in order to make positional adjustments easier; 
#                      comma separated x,y pair; positive or negative integer; 
#                      default is no offset.
# -R     rotate        additional clockwise positive rotation in order to make 
#                      orientational adjustments easier; -360<=float<=360; 
#                      default=0
# -l     lighting      lighting is the contrast increase/decrease for highlights to 
#                      apply to the overlay image (infile); -100<=integer=<100; 
#                      positive values increase contrast; negative values decrease 
#                      contrast; default=20                     
# -s     sharpen       sharpening to apply to the overlay (infile) image;
#                      float>=0; default=1
# -b     blur          blurring to apply to the displacement map to avoid 
#                      jagged displacement; float>=0; default=1
# -d     displace      amount of displacement for the distortion of the 
#                      overlay (infile) image; integer>=0; default=10
# -a     antialias     antialias amount to apply to alpha channel of tshirt 
#                      (bgfile) image; float>=0; default=2
# -A     attenuate     attenuation of the effect of coarse texture on the background 
#                      (bgfile) image from showing on the overlay (input) image; 
#                      float>=0; larger values blur the tshirt texture more which 
#                      attenuates the effects; default=0
# -B     brightness    brightness percent change to the input overlay image; 
#                      positive or negative integer; default=0
# -S     saturation    saturation percent change to the input overlay image; 
#                      positive or negative integer; default=0
# -C     compose       compose method to merge the input overlay (infile) image with  
#                      the background (bgfile); choices are: hardlight, multiply, 
#                      screen or over; default=hardlight
# -O     opacity       opacity to apply to the image; 0<=integer<=100; default=100 
#                      (fully opaque)
# -E     export        export the lighting image, displacement map and other 
#                      needed parameters to be able to use a condensed script 
#                      to repeat the processing on the same size and style tshirt 
#                      image for faster processing.
# -D     directory     directory to write all the exported data, including a text file 
#                      called tshirtdata.txt containing the same textual parameter data 
#                      sent to terminal. The directory can be specified in the tshirtwarp 
#                      script to import all the needed images and textual data.
#
# infile is the overlay image to apply to the tshirt.
# 
# bgfile is the tshirt image.
# 
# maskfile is a mask of part or all of the tshirt to limit the region onto which the 
# overlay image is to be applied.
#
###
#
# NAME: TSHIRT 
# 
# PURPOSE: Transforms an image to place it in a region of a tshirt image.
# 
# DESCRIPTION: TSHIRT transforms an image to place it in a region of a tshirt 
# image. The transformed image will display hightlights from the tshirt image 
# and be distorted to match the wrinkles in the tshirt image.
# 
# 
# OPTIONS: 
# 
# -r region ... REGION is a simple (unrotated) rectangle defined as the 
# WxH+X+Y of the region in the tshirt (bgfile) where the overlay image (bgfile) 
# will be placed. The components of W, H, X, Y are integers and specify the 
# width, height, upperleft xoffset and yoffset of the rectangle. Only one or 
# the other of region or coordinates should be specified. But coordinates take 
# precedent.
# 
# -c coords ... COORDS are the 4 x,y corners of the region in the tshirt 
# (bgfile) where the overlay image (bgfile) will be placed. The coordinates 
# must be listed clockwise from top left corner; coordinates are integers>=0. 
# Only one or the other of region or coordinates should be specified. But 
# coordinates take precedent. Coordinates are not restricted to a rectangle 
# and the region defined by the coordinates can have rotation.
# 
# -f fit ... fit can be: crop (c), distort (d) scale (s), top (t) or none (n); 
# If crop, then the overlay image (infile) will be resized to the width of the 
# region (or coordinate area) and cropped if needed. This will not distort the 
# image. The image will not be cropped, if its height is smaller than that of 
# the region and it will then be aligned at the top of the region. If distort, 
# then the overlay image (infile) will be resized to fit exactly to the region 
# (or coordinate area). This will cause distortion, if the aspect ratio of the 
# overlay image (infile) does not match the aspect ratio of the region (or 
# coordinate area). If scale, then the overlay image (infile) will be resized 
# so that the larger dimension fits the region (or coordinate area) and the 
# other dimension is smaller. The resized overlay image (infile) will be 
# centered in the region. If top, then the overlay image (infile) will be 
# resized so that both width and height fit into the region without distorting 
# and placed at the top center of the region. The default=none, which means 
# that the image will be resized to fit the width of the region (or coordinate 
# area) and aligned at the top of the region. If the height of the resized 
# image is larger than the height of the region, it will extend past the bottom 
# of the region.
# 
# -g gravity ... GRAVITY for selecting the crop location. The choices are:
# north (n), south (s) or center (c). The default=center. 
# 
# -v vshift ... VSHIFT is the vertical shift of the crop region with respect 
# to the gravity setting. Values are integer.  Negative is upward and positive 
# is downward. The default=0 (no shift).
# 
# -o offset ... OFFSET is an additional x,y offset of the region or coordinates 
# in order to make positional adjustments easier. This is a comma separated 
# x,y pair. Values are ositive or negative integers for x and y. The default 
# is no offset.
# 
# -R rotate ... ROTATE is an additional clockwise positive rotation in order 
# to make orientational adjustments easier. Values are -360<=float<=360. 
# The default=0.
#
# -l lighting ... LIGHTING is the contrast increase/decrease for highlights to  
# apply to the overlay image (infile). Values are -100<=integer<=100. Positive values 
# increase contrast and negative values decrease contrast. The default=20.
#                    
# -s sharpen ... SHARPEN is the sharpening to apply to the overlay (infile) 
# image. Values are floats>=0. The default=1.
# 
# -b blur ... BLUR is the blurring to apply to the displacement map to avoid 
# jagged displacement. Values are floats>=0. The default=1.
# 
# -d displace ... DISPLACE is the amount of displacement for the distortion 
# of the overlay (infile) image. Values are integers>=0. The default=10.
# 
# -a antialias ... ANTIALIAS amount to apply to alpha channel of tshirt 
# (bgfile) image. Values are floats>=0. The default=2.
# 
# -A attenuate ... ATTENUATE is the attenuation of the effect of coarse texture from 
# the background (bgfile) image from showing on the overlay (input) image. Values are  
# floats>=0. Larger values blur the tshirt texture more which attenuates the effects. 
# The default=0.
# 
# -B brightness ... BRIGHTNESS percent change to the input overlay image. Value are  
# positive or negative integers. The default=0.
# 
# -S saturation ... SATURATION percent change to the input overlay image. Values are  
# positive or negative integers. The default=0.
# 
# -C compose ... COMPOSE method to merge the overlay (infile) image with the 
# background (bgfile). Choices are: hardlight (h), multiply (m), screen (s) or over (o). 
# The default=hardlight. The choice of hardlight allows the overlay image 
# to be brighten and darken according to the folds in the tshirt. The other compose 
# methods will not do that. The choice of over simply places the overlay image 
# unchanged upon the tshirt image. The choice of multiply does a multiply operation, 
# which may change colors and would need adjustment by -B and -S arguments.
# 
# -O opacity ... OPACITY to apply to the image. Values are 0<=integers<=100. 
# The default=100 (fully opaque).
# 
# -E ... EXPORT the lighting image, displacement map and other needed 
# parameters for use with a condensed script to repeat the processing on the 
# same tshirt image apart from coloring for faster processing. The lighting 
# image will be named lighting.png and the displacement map will named 
# displace.png. The other arguments will be displayed to the terminal and 
# can be copied and pasted into my script, tshirtwarp.
# 
# -D directory ... DIRECORTY to write all the exported data when using the -E export 
# option, including a text file called tshirtdata.txt that contains the same textual 
# parameter data sent to terminal. The directory can be specified in the tshirtwarp 
# script to import all the needed images and textual data. This permits one tshirtwarp 
# script to be used with all style tshirts, rather than save a customized script for 
# each style tshirt. If the directory does not exist, it will be created.
# 
# IMPORTANT: The nominal transformed image will not fit the exact height of the  
# region or coordinates area, if the aspect ratio of the image differs from   
# that of the region or coordinate area. The process maintains the correct  
# aspect ratio of the input image. Depending upon the aspect ratio, the 
# transformed image may be shorter or taller than the height of the region. 
# To crop the image so that it fits the region or coordinate area, use the 
# -f option. 
# 
# REQUIREMENTS: IM 6.5.3.4 due to the use of -compose displace.
# 
# CAVEAT: No guarantee that this script will work on all platforms, 
# nor that trapping of inconsistent parameters is complete and 
# foolproof. Use At Your Own Risk. 
# 
######
#

# set up defaults
coords=""				# coordinates of corners clockwise from top left
region=""				# WxH+X+Y area on background to place overlay image
fit="none"        		# crop or distort the image to fit vertical aspect ratio of region
gravity="center"		# gravity for cropping
vshift=0				# vertical shift of crop region
offset=""       		# additional x,y offsets of region or coordinates
rotate=0				# additional rotation for use only with region
lighting=20				# contrast increase for highlights; integer
blur=1					# blurring/smoothing of displacement image to reduce texture; float
displace=10				# amount of displacement for distortions; integer
sharpen=1				# sharpening of warped overlay image; float
antialias=2				# antialias amount to apply to alpha channel of tshirt image; float
attenuate=0				# attenuation of bgfile texture onto the infile; float 
brightness=0			# brightness change to the infile; integer 
saturation=0			# saturation change to the infile; integer 
compose="hardlight"		# compose method; hardlight or multiply
opacity=100             # opacity to apply to the image.
export="no"				# export lighting image, displacement map and other arguments
directory=""			# directory to write the lighting image, displacement map and text file


# set directory for temporary files
tmpdir="/tmp"

# set up functions to report Usage and Usage with Description
PROGNAME=`type $0 | awk '{print $3}'`  # search for executable on path
PROGDIR=`dirname $PROGNAME`            # extract directory of program
PROGNAME=`basename $PROGNAME`          # base name of program
usage1() 
	{
	echo >&2 ""
	echo >&2 "$PROGNAME:" "$@"
	sed >&2 -e '1,/^####/d;  /^###/g;  /^#/!q;  s/^#//;  s/^ //;  4,$p' "$PROGDIR/$PROGNAME"
	}
usage2() 
	{
	echo >&2 ""
	echo >&2 "$PROGNAME:" "$@"
	sed >&2 -e '1,/^####/d;  /^######/g;  /^#/!q;  s/^#*//;  s/^ //;  4,$p' "$PROGDIR/$PROGNAME"
	}


# function to report error messages
errMsg()
	{
	echo ""
	echo $1
	echo ""
	usage1
	exit 1
	}


# function to test for minus at start of value of second part of option 1 or 2
checkMinus()
	{
	test=`echo "$1" | grep -c '^-.*$'`   # returns 1 if match; 0 otherwise
    [ $test -eq 1 ] && errMsg "$errorMsg"
	}

# test for correct number of arguments and get values
if [ $# -eq 0 ]
	then
	# help information
   echo ""
   usage2
   exit 0
elif [ $# -gt 39 ]
	then
	errMsg "--- TOO MANY ARGUMENTS WERE PROVIDED ---"
else
	while [ $# -gt 0 ]
		do
			# get parameter values
			case "$1" in
		     -help|-h)    # help information
					   echo ""
					   usage2
					   exit 0
					   ;;
				-r)    # get region
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID REGION SPECIFICATION ---"
					   checkMinus "$1"
					   region=`expr "$1" : '\([0-9]*[x][0-9]*[+][0-9]*[+][0-9]*\)'`
					   [ "$region" = "" ] && errMsg "--- REGION=$region MUST BE NON-NEGATIVE INTEGERS OF THE FORM WxH+X+Y ---"
					   ;;
				-c)    # get coords
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID COORDS SPECIFICATION ---"
					   checkMinus "$1"
					   coords=`expr "$1" : '\([ ,0-9]*\)'`
					   [ "$coords" = "" ] && errMsg "--- COORDS=$coords MUST BE 4 SPACE SEPARATED INTEGER X,Y PAIRS ---"
					   ;;
		 		-f)    # fit
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID FIT SPECIFICATION ---"
					   checkMinus "$1"
					   # test gravity values
					   fit="$1"
					   fit=`echo "$1" | tr '[A-Z]' '[a-z]'`
					   case "$fit" in 
					   		none|n) fit="none" ;;
					   		crop|c) fit="crop" ;;
					   		distort|d) fit="distort" ;;
					   		scale|s) fit="scale" ;;
					   		top|t) fit="top" ;;
					   		*) errMsg "--- FIT=$fit IS AN INVALID VALUE ---" 
					   	esac
					   ;;
		 		-g)    # gravity
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID GRAVITY SPECIFICATION ---"
					   checkMinus "$1"
					   # test gravity values
					   gravity="$1"
					   gravity=`echo "$1" | tr '[A-Z]' '[a-z]'`
					   case "$gravity" in 
					   		center|c) gravity=center ;;
					   		north|n) gravity=north ;;
					   		south|s) gravity=south ;;
					   		*) errMsg "--- GRAVITY=$gravity IS AN INVALID VALUE ---" 
					   	esac
					   ;;
				-v)    # get vshift
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID VSHIFT SPECIFICATION ---"
#					   checkMinus "$1"
					   vshift=`expr "$1" : '\([-]*[0-9]*\)'`
					   [ "$vshift" = "" ] && errMsg "--- VSHIFT=$vshift MUST BE AN INTEGER ---"
					   ;;
				-o)    # get offset
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID OFFSET SPECIFICATION ---"
#					   checkMinus "$1"
					   offset=`expr "$1" : '\([-]*[0-9]*,[-]*[0-9]*\)'`
					   [ "$offset" = "" ] && errMsg "--- OFFSET=$offset MUST BE ONE INTEGER X,Y PAIR ---"
					   ;;
				-R)    # get rotate
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID ROTATE SPECIFICATION ---"
#					   checkMinus "$1"
					   rotate=`expr "$1" : '\([-]*[.0-9]*\)'`
					   [ "$rotate" = "" ] && errMsg "--- ROTATE=$rotate MUST BE A FLOAT ---"
					   test1=`echo "$rotate < -360" | bc`
					   test2=`echo "$rotate > 360" | bc`
					   [ $test1 -eq 1 -o $test2 -eq 1 ] && errMsg "--- ROTATE=$rotate MUST BE A FLOAT BETWEEN -360 AND 360 ---"
					   ;;
				-s)    # get sharpen
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID SHARPEN SPECIFICATION ---"
					   checkMinus "$1"
					   sharpen=`expr "$1" : '\([.0-9]*\)'`
					   [ "$sharpen" = "" ] && errMsg "--- SHARPEN=$sharpen MUST BE A NON-NEGATIVE FLOAT ---"
					   ;;
				-b)    # get blur
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID BLUR SPECIFICATION ---"
					   checkMinus "$1"
					   blur=`expr "$1" : '\([.0-9]*\)'`
					   [ "$blur" = "" ] && errMsg "--- BLUR=$blur MUST BE A NON-NEGATIVE FLOAT ---"
					   ;;
				-a)    # get antialias
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID ANTIALIAS SPECIFICATION ---"
					   checkMinus "$1"
					   antialias=`expr "$1" : '\([.0-9]*\)'`
					   [ "$antialias" = "" ] && errMsg "--- ANTIALIAS=$antialias MUST BE A NON-NEGATIVE FLOAT ---"
					   ;;
				-l)    # get lighting
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID LIGHTING SPECIFICATION ---"
					   #checkMinus "$1"
					   lighting=`expr "$1" : '\([-0-9]*\)'`
					   [ "$lighting" = "" ] && errMsg "--- LIGHTING=$lighting MUST BE AN INTEGER ---"
					   test1=`echo "$lighting < -100" | bc`
					   test2=`echo "$lighting > 100" | bc`
					   [ $test1 -eq 1 -o $test2 -eq 1 ] && errMsg "--- LIGHTING=$lighting MUST BE AN INTEGER BETWEEN -30 AND 30 ---"
					   ;;
				-d)    # get displace
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID DISPLACE SPECIFICATION ---"
					   checkMinus "$1"
					   displace=`expr "$1" : '\([0-9]*\)'`
					   [ "$displace" = "" ] && errMsg "--- DISPLACE=$displace MUST BE A NON-NEGATIVE INTEGER ---"
					   ;;
				-A)    # get attenuate
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID ATTENUATE SPECIFICATION ---"
					   checkMinus "$1"
					   attenuate=`expr "$1" : '\([.0-9]*\)'`
					   [ "$attenuate" = "" ] && errMsg "--- ATTENUATE=$attenuate MUST BE A NON-NEGATIVE FLOAT ---"
					   ;;
				-B)    # get brightness
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID BRIGHTNESS SPECIFICATION ---"
					   #checkMinus "$1"
					   brightness=`expr "$1" : '\([-0-9]*\)'`
					   [ "$brightness" = "" ] && errMsg "--- BRIGHTNESS=$brightness MUST BE AN INTEGER ---"
					   testA=`echo "$brightness < -100" | bc`
					   testB=`echo "$brightness > 100" | bc`
					   [ $testA -eq 1 -o $testB -eq 1 ] && errMsg "--- BRIGHTNESS=$brightness MUST BE AN INTEGER BETWEEN -100 AND 100 ---"
					   ;;
				-S)    # get saturation
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID SATURATION SPECIFICATION ---"
					   #checkMinus "$1"
					   saturation=`expr "$1" : '\([-0-9]*\)'`
					   [ "$saturation" = "" ] && errMsg "--- SATURATION=$saturation MUST BE AN INTEGER ---"
					   testA=`echo "$saturation < -100" | bc`
					   testB=`echo "$saturation > 100" | bc`
					   [ $testA -eq 1 -o $testB -eq 1 ] && errMsg "--- SATURATION=$saturation MUST BE AN INTEGER BETWEEN -100 AND 100 ---"
					   ;;
		 		-C)    # compose
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID COMPOSE SPECIFICATION ---"
					   checkMinus "$1"
					   # test gravity values
					   compose="$1"
					   compose=`echo "$1" | tr '[A-Z]' '[a-z]'`
					   case "$compose" in 
					   		hardlight|h) compose="hardlight" ;;
					   		multiply|m) compose="multiply" ;;
					   		screen|s) compose="screen" ;;
					   		over|o) compose="over" ;;
					   		*) errMsg "--- COMPOSE=$compose IS AN INVALID VALUE ---" 
					   	esac
					   ;;
				-O)    # get opacity
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID OPACITY SPECIFICATION ---"
					   checkMinus "$1"
					   opacity=`expr "$1" : '\([0-9]*\)'`
					   [ "$opacity" = "" ] && errMsg "--- OPACITY=$opacity MUST BE A NON-NEGATIVE INTEGER ---"
					   test=`echo "$opacity > 100" | bc`
					   [ $test -eq 1 ] && errMsg "--- OPACITY=$opacity MUST BE AN INTEGER BETWEEN 0 AND 100 ---"
					   ;;
				-E)    # get  export
					   export="yes"
					   ;;
				-D)    # get directory
					   shift  # to get the next parameter
					   # test if parameter starts with minus sign 
					   errorMsg="--- INVALID DIRECTORY SPECIFICATION ---"
					   checkMinus "$1"
					   directory="$1"
					   ;;
			 	-)    # STDIN and end of arguments
					   break
					   ;;
				-*)    # any other - argument
					   errMsg "--- UNKNOWN OPTION ---"
					   ;;
		     	 *)    # end of arguments
					   break
					   ;;
			esac
			shift   # next option
	done
	#
	# get infile and outfile
	if [ $# -eq 4 ]; then
		infile="$1"
		bgfile="$2"
		maskfile="$3"
		outfile="$4"
	elif [ $# -eq 3 ]; then
		infile="$1"
		bgfile="$2"
		outfile="$3"
	else
		errMsg "--- INCONSISTENT NUMBER OF INPUT AND OUTPUT IMAGES SPECIFIED ---"
	fi

fi

# test that infile provided
[ "$infile" = "" ] && errMsg "NO OVERLAY FILE SPECIFIED"

# test that bgfile provided
[ "$bgfile" = "" ] && errMsg "NO BACKGROUND (TSHIRT) FILE SPECIFIED"

# test that outfile provided
[ "$outfile" = "" ] && errMsg "NO OUTPUT FILE SPECIFIED"


dir="$tmpdir/TSHIRT.$$"
mkdir "$dir" || {
  echo >&2 "UNABLE TO CREATE WORKING DIR \"$dir\" -- ABORTING"
  exit 10
}
trap "rm -rf $dir;" 0
trap "rm -rf $dir; exit 1" 1 2 3 10 15
trap "rm -rf $dir; exit 1" ERR

# set up brighness, saturation, hue and contrast
bri=$((100+$brightness))
sat=$((100+$saturation))
hue=`convert xc: -format "%[fx:(200/360)*$hue+100]" info:`

# set up modulation
if [ "$brightness" = "0" -a "$saturation" = "0" ]; then
	modulating=""
else
	modulating="-modulate $bri,$sat,100"
fi


# read overlay image
if ! convert -quiet "$infile" +repage $modulating $dir/tmpI.mpc; then
	errMsg "--- FILE $infile DOES NOT EXIST OR IS NOT AN ORDINARY FILE, NOT READABLE OR HAS ZERO SIZE ---"
fi	

# read tshirt image and make color (so that result is not grayscale when overlay image is grayscale)
if ! convert -quiet "$bgfile" +repage -colorspace sRGB $dir/tmpT.mpc; then
	errMsg "--- FILE $infile DOES NOT EXIST OR IS NOT AN ORDINARY FILE, NOT READABLE OR HAS ZERO SIZE ---"
fi	

if [ "$maskfile" != "" ]; then
	# read maskfile image
	if ! convert -quiet "$maskfile" +repage $dir/tmpM.mpc; then
		errMsg "--- FILE $maskfile DOES NOT EXIST OR IS NOT AN ORDINARY FILE, NOT READABLE OR HAS ZERO SIZE ---"
	fi	
fi

# extract coordinates of subsection of tshirt and bounding box
if [ "$coords" = "" -a "$region" = "" ]; then
	errMsg "--- EITHER COORDINATES OR REGION IS REQUIRED ---"
elif [ "$coords" != "" ]; then
	clist=`echo $coords | sed 's/[, ][, ]*/ /g';`
	test=`echo $clist | wc -w | tr -d " "`
	if [ $test -eq 8 ]; then
		x1=`echo $clist | cut -d\  -f1`
		y1=`echo $clist | cut -d\  -f2`
		x2=`echo $clist | cut -d\  -f3`
		y2=`echo $clist | cut -d\  -f4`
		x3=`echo $clist | cut -d\  -f5`
		y3=`echo $clist | cut -d\  -f6`
		x4=`echo $clist | cut -d\  -f7`
		y4=`echo $clist | cut -d\  -f8`
		
		if [ "$offset" != "" ]; then
			xx=`echo "$offset" | cut -d, -f1`
			yy=`echo "$offset" | cut -d, -f2`
			x1=$((x1+xx))
			y1=$((y1+yy))
			x2=$((x2+xx))
			y2=$((y2+yy))
			x3=$((x3+xx))
			y3=$((y3+yy))
			x4=$((x4+xx))
			y4=$((y4+yy))
		fi
		#echo "$x1,$y1;  $x2,$y2;  $x3,$y3;  $x4,$y4;"
	
		# get bounding box
		minx=`convert xc: -format "%[fx:min(min(min($x1,$x2),$x3),$x4)]" info:`
		miny=`convert xc: -format "%[fx:min(min(min($y1,$y2),$y3),$y4)]" info:`
		maxx=`convert xc: -format "%[fx:max(max(max($x1,$x2),$x3),$x4)]" info:`
		maxy=`convert xc: -format "%[fx:max(max(max($y1,$y2),$y3),$y4)]" info:`
		wd=`convert xc: -format "%[fx:$maxx-$minx+1]" info:`
		ht=`convert xc: -format "%[fx:$maxy-$miny+1]" info:`
		#echo "minx=$minx; miny=$miny; maxx=$maxx; maxy=$maxy; wd=$wd, ht=$ht;"

		# compute offsets, topwidth and correction rotation angle
		xoffset=$x1
		yoffset=$y1
		topwidth=`convert xc: -format "%[fx:hypot(($x2-$x1),($y2-$y1))+1]" info:`
		leftheight=`convert xc: -format "%[fx:hypot(($x4-$x1),($y4-$y1))+1]" info:`
		angle=`convert xc: -format "%[fx:-atan2(($y2-$y1),($x2-$x1))]" info:`
		#echo "xoffset=$xoffset; yoffset=$yoffset; topwidth=$topwidth; angle=$angle;"
	else
		errMsg "--- INCONSISTENT NUMBER OF COORDINATES ---"
	fi
elif [ "$region" != "" ]; then
		region=`echo "$region" | tr -d " " | tr -cs "0-9\n" " "`
		wd=`echo "$region" | cut -d\  -f1`
		ht=`echo "$region" | cut -d\  -f2`
		minx=`echo "$region" | cut -d\  -f3`
		miny=`echo "$region" | cut -d\  -f4`
		#echo "minx=$minx; miny=$miny; wd=$wd, ht=$ht;"
		if [ "$offset" != "" ]; then
			xx=`echo "$offset" | cut -d, -f1`
			yy=`echo "$offset" | cut -d, -f2`
			minx=$((minx+xx))
			miny=$((miny+yy))
		fi
		xoffset=$minx
		yoffset=$miny
		topwidth=$wd
		leftheight=$ht
		angle=0
		#echo "xoffset=$xoffset; yoffset=$yoffset; topwidth=$topwidth; angle=$angle;"
		x1=$minx
		y1=$miny
		x2=$((minx+$wd-1))
		y2=$miny
		x3=$((minx+$wd-1))
		y3=$((miny+$ht-1))
		x4=$minx
		y4=$((miny+$ht-1))
		#echo "$x1,$y1;  $x2,$y2;  $x3,$y3;  $x4,$y4;"
		#echo "xoffset=$xoffset; yoffset=$yoffset; topwidth=$topwidth; angle=$angle;"
fi


# get width and height of overlay image and compute scale factor to fit region
ww=`convert -ping $dir/tmpI.mpc -format "%w" info:`
hh=`convert -ping $dir/tmpI.mpc -format "%h" info:`
# distort does not need scale to be computed. Perspective distort will do that.
if [ "$fit" = "scale" ]; then
	if [ $hh -ge $ww ]; then
		scale=`convert xc: -format "%[fx:($hh-1)/($leftheight-1)]" info:`
	else
		scale=`convert xc: -format "%[fx:($ww-1)/($topwidth-1)]" info:`
	fi
elif [ "$fit" = "top" ]; then
	xscale=`convert xc: -format "%[fx:($ww-1)/($topwidth-1)]" info:`
	yscale=`convert xc: -format "%[fx:($hh-1)/($leftheight-1)]" info:`
	scale=`convert xc: -format "%[fx:$xscale>$yscale?$xscale:$yscale]" info:`
	scaleflag=`convert xc: -format "%[fx:$xscale>$yscale?1:0]" info:`
	[ $scaleflag -eq 1 ] && scaleflag="x" || scaleflag="y"
elif [ "$fit" = "crop" -o "$fit" = "none" ]; then
	scale=`convert xc: -format "%[fx:($ww-1)/($topwidth-1)]" info:`
fi
#echo "ww=$ww; hh=$hh; wd=$wd; ht=$ht; topwidth=$topwidth; leftheight=$leftheight; xscale=$xscale; yscale=$yscale; scaleflag=$scaleflag; scale=$scale;"


# compute corresponding coordinates in overlay image
if [ "$coords" != "" ]; then
	# subtract offset and unrotate
	xo1=`convert xc: -format "%[fx:round(($x1-$xoffset)*cos($angle)+($y1-$yoffset)*sin($angle))]" info:`
	yo1=`convert xc: -format "%[fx:round(($x1-$xoffset)*sin($angle)+($y1-$yoffset)*cos($angle))]" info:`
	xo2=`convert xc: -format "%[fx:round(($x2-$xoffset)*cos($angle)+($y2-$yoffset)*sin($angle))]" info:`
	yo2=`convert xc: -format "%[fx:round(($x2-$xoffset)*sin($angle)+($y2-$yoffset)*cos($angle))]" info:`
	xo3=`convert xc: -format "%[fx:round(($x3-$xoffset)*cos($angle)+($y3-$yoffset)*sin($angle))]" info:`
	yo3=`convert xc: -format "%[fx:round(($x3-$xoffset)*sin($angle)+($y3-$yoffset)*cos($angle))]" info:`
	xo4=`convert xc: -format "%[fx:round(($x4-$xoffset)*cos($angle)+($y4-$yoffset)*sin($angle))]" info:`
	yo4=`convert xc: -format "%[fx:round(($x4-$xoffset)*sin($angle)+($y4-$yoffset)*cos($angle))]" info:`
	# compute max width and height
	# error fixed below 3/19/2020 wo=`convert xc: -format "%[fx:max($xo4-$xo1,$xo3-$xo2)+1]" info:`
	wo=`convert xc: -format "%[fx:max($xo2-$xo1,$xo4-$xo3)+1]" info:`
	ho=`convert xc: -format "%[fx:max($yo4-$yo1,$yo3-$yo2)+1]" info:`
	#echo "xoffset=$xoffset; yoffset=$yoffset; angle=$angle; wo=$wo; ho=$ho;"
	if [ "$fit" = "distort" ]; then
		xo1=0
		yo1=0
		xo2=$((ww-1))
		yo2=$yo1
		xo3=$xo2
		yo3=$((hh-1))
		xo4=$xo1
		yo4=$yo3
	elif [ "$fit" = "scale" ]; then
		if [ $hh -ge $ww ]; then
			xo1=`convert xc: -format "%[fx:round(0.5*($ww-$scale*$wo))]" info:`
			yo1=0
			xo2=`convert xc: -format "%[fx:(round($xo1+$scale*$wo-1))]" info:`
			yo2=$yo1
			xo3=$xo2
			yo3=`convert xc: -format "%[fx:(round($yo1+$scale*$ho-1))]" info:`
			xo4=$xo1
			yo4=$yo3
		else
			xo1=0
			yo1=`convert xc: -format "%[fx:round(0.5*($hh-$scale*$ho))]" info:`
			xo2=`convert xc: -format "%[fx:(round($xo1+$scale*$wo-1))]" info:`
			yo2=$yo1
			xo3=$xo2
			yo3=`convert xc: -format "%[fx:(round($yo1+$scale*$ho-1))]" info:`
			xo4=$xo1
			yo4=$yo3
		fi
	elif [ "$fit" = "top" ]; then
		if [ "$scaleflag" = "y" ]; then
			xo1=`convert xc: -format "%[fx:round(0.5*($ww-$scale*$wo))]" info:`
			yo1=0
			xo2=`convert xc: -format "%[fx:(round($xo1+$scale*$wo-1))]" info:`
			yo2=$yo1
			xo3=$xo2
			yo3=`convert xc: -format "%[fx:(round($yo1+$scale*$ho-1))]" info:`
			xo4=$xo1
			yo4=$yo3
		else
			xo1=0
			# center
			#yo1=`convert xc: -format "%[fx:round(0.5*($hh-$scale*$ht))]" info:`
			yo1=0
			xo2=`convert xc: -format "%[fx:(round($xo1+$scale*$wo-1))]" info:`
			yo2=$yo1
			xo3=$xo2
			yo3=`convert xc: -format "%[fx:(round($yo1+$scale*$ho-1))]" info:`
			xo4=$xo1
			yo4=$yo3
		fi
	elif [ "$fit" = "crop" -o "$fit" = "none" ]; then
		xo1=0
		yo1=0
		xo2=$((ww-1))
		yo2=$yo1
		xo3=$xo2
		yo3=`convert xc: -format "%[fx:(round($scale*$ho-1))]" info:`
		xo4=$xo1
		yo4=$yo3
	fi

elif [ "$region" != "" ]; then
	# use input width and scaled height of region for overlay coordinates
	if [ "$fit" = "distort" ]; then
		xo1=0
		yo1=0
		xo2=$((ww-1))
		yo2=$yo1
		xo3=$xo2
		yo3=$((hh-1))
		xo4=$xo1
		yo4=$yo3
	elif [ "$fit" = "scale" ]; then
		if [ $hh -ge $ww ]; then
			xo1=`convert xc: -format "%[fx:round(0.5*($ww-$scale*$wd))]" info:`
			yo1=0
			xo2=`convert xc: -format "%[fx:(round($xo1+$scale*$wd-1))]" info:`
			yo2=$yo1
			xo3=$xo2
			yo3=`convert xc: -format "%[fx:(round($yo1+$scale*$ht-1))]" info:`
			xo4=$xo1
			yo4=$yo3
		else
			xo1=0
			yo1=`convert xc: -format "%[fx:round(0.5*($hh-$scale*$ht))]" info:`
			xo2=`convert xc: -format "%[fx:(round($xo1+$scale*$wd-1))]" info:`
			yo2=$yo1
			xo3=$xo2
			yo3=`convert xc: -format "%[fx:(round($yo1+$scale*$ht-1))]" info:`
			xo4=$xo1
			yo4=$yo3
		fi
	elif [ "$fit" = "top" ]; then
		if [ "$scaleflag" = "y" ]; then
			xo1=`convert xc: -format "%[fx:round(0.5*($ww-$scale*$wd))]" info:`
			yo1=0
			xo2=`convert xc: -format "%[fx:(round($xo1+$scale*$wd-1))]" info:`
			yo2=$yo1
			xo3=$xo2
			yo3=`convert xc: -format "%[fx:(round($yo1+$scale*$ht-1))]" info:`
			xo4=$xo1
			yo4=$yo3
		else
			xo1=0
			# center
			#yo1=`convert xc: -format "%[fx:round(0.5*($hh-$scale*$ht))]" info:`
			yo1=0
			xo2=`convert xc: -format "%[fx:(round($xo1+$scale*$wd-1))]" info:`
			yo2=$yo1
			xo3=$xo2
			yo3=`convert xc: -format "%[fx:(round($yo1+$scale*$ht-1))]" info:`
			xo4=$xo1
			yo4=$yo3
		fi
	elif [ "$fit" = "crop" -o "$fit" = "none" ]; then
		xo1=0
		yo1=0
		xo2=$((ww-1))
		yo2=$yo1
		xo3=$xo2
		yo3=`convert xc: -format "%[fx:(round($scale*$ht-1))]" info:`
		xo4=$xo1
		yo4=$yo3
	fi
fi
#echo "$xo1,$yo1;  $xo2,$yo2;  $xo3,$yo3;  $xo4,$yo4;"
	

# apply rotation about center of scaled down image translated to correct upper left corner
if [ "$rotate" != "0" ]; then
	rotate=`convert xc: -format "%[fx:(pi/180)*$rotate]" info:`
	xcent=`convert xc: -format "%[fx:round(0.5*$topwidth)+$x1]" info:`		
	ycent=`convert xc: -format "%[fx:round(0.5*($hh/$scale)+$y1)]" info:`
#	echo "rotate=$rotate; xcent=$xcent; ycent=$ycent"
	x1=`convert xc: -format "%[fx:round($xcent+($x1-$xcent)*cos($rotate)-($y1-$ycent)*sin($rotate))]" info:`
	y1=`convert xc: -format "%[fx:round($ycent+($x1-$xcent)*sin($rotate)+($y1-$ycent)*cos($rotate))]" info:`
	x2=`convert xc: -format "%[fx:round($xcent+($x2-$xcent)*cos($rotate)-($y2-$ycent)*sin($rotate))]" info:`
	y2=`convert xc: -format "%[fx:round($ycent+($x2-$xcent)*sin($rotate)+($y2-$ycent)*cos($rotate))]" info:`
	x3=`convert xc: -format "%[fx:round($xcent+($x3-$xcent)*cos($rotate)-($y3-$ycent)*sin($rotate))]" info:`
	y3=`convert xc: -format "%[fx:round($ycent+($x3-$xcent)*sin($rotate)+($y3-$ycent)*cos($rotate))]" info:`
	x4=`convert xc: -format "%[fx:round($xcent+($x4-$xcent)*cos($rotate)-($y4-$ycent)*sin($rotate))]" info:`
	y4=`convert xc: -format "%[fx:round($ycent+($x4-$xcent)*sin($rotate)+($y4-$ycent)*cos($rotate))]" info:`
#	echo "$x1,$y1;  $x2,$y2;  $x3,$y3;  $x4,$y4;"
fi

im_version=`convert -list configure | \
	sed '/^LIB_VERSION_NUMBER */!d; s//,/;  s/,/,0/g;  s/,0*\([0-9][0-9]\)/\1/g' | head -n 1`

if [ "$im_version" -ge "07000000" ]; then
	identifying="magick identify"
else
	identifying="identify"
fi

# test if tshirt/bgfile has alpha. If so remove and save for later.
is_alpha=`$identifying -verbose $dir/tmpT.mpc | grep "Alpha" | head -n 1`
[ "$is_alpha" != "" ] && convert $dir/tmpT.mpc -alpha extract -blur 0x$antialias -level 50x100% $dir/tmpA.mpc

# convert tshirt/bgfile to grayscale and compute amount to add/subtract to change mean to 50%
# use bounding box before any additional rotation as good approximation of region
diff=`convert $dir/tmpT.mpc -alpha off -colorspace gray -write $dir/tmpTG.mpc \
	-crop ${wd}x${ht}+${minx}+${miny} +repage -format "%[fx:100*mean-50]" info:`
#echo "diff=$diff"	


# set up lighting
# test for sign of lighting
test=`convert xc: -format "%[fx:($lighting>0)?1:0]" info:`
if [ "$lighting" = "0" ]; then
	lproc=""
elif [ $test -eq 1 ]; then
	cont=`convert xc: -format "%[fx:$lighting/3]" info:`
	lproc="-sigmoidal-contrast $cont,50%"
elif [ $test -eq 0 ]; then
	cont=`convert xc: -format "%[fx:abs($lighting)/3]" info:`
	lproc="+sigmoidal-contrast $cont,50%"
fi
#echo "lproc=$lproc"

# set up blurring of the displacement image to soften texture
if [ "$blur" != "0" ]; then
	bproc="-blur 0x$blur"
else
	bproc=""
fi

# set up blurring of the bgimage image to soften texture
if [ "$attenuate" != "0" ]; then
	aproc="-blur 0x$attenuate"
else
	aproc=""
fi
#echo "aproc=$aproc"


# convert grayscale tshirt to 50% mean, then to lighting image and displacement image
convert \( $dir/tmpTG.mpc -evaluate subtract $diff% \) \
	\( -clone 0 $aproc $lproc -write $dir/tmpL.mpc \) +delete \
	$bproc $dir/tmpD.mpc

# check if export directory exists.
if [ "$export" = "yes" -a "$directory" != "" ]; then
	# remove trailing \
	if [ ! -d "$directory" ]; then 
		mkdir "$directory" || {
  		echo >&2 "UNABLE TO CREATE DIRECTORY \"$directory\" -- ABORTING"
  		exit 10
  		}
  	fi
	# remove trailing \
  	directory=`echo "$directory" | sed 's/[/]*$//'`
	convert $dir/tmpL.mpc $directory/lighting.png
	convert $dir/tmpD.mpc -alpha set $directory/displace.png
elif [ "$export" = "yes" -a "$directory" = "" ]; then
	convert $dir/tmpL.mpc lighting.png
	convert $dir/tmpD.mpc -alpha set displace.png
fi


# set up sharpening of overlay image in perspective
if [ "$sharpen" != "0" ]; then
	sproc="-unsharp 0x$sharpen -clamp"
else
	sproc=""
fi
#echo "sproc=$sproc"


# set up cropping
cropping=""
if [ "$fit" = "crop" ]; then
	hc=$((yo3+1))
	test=`convert xc: -format "%[fx:($hh>$hc)?1:0]" info:`
	if [ $test -eq 1 ]; then
		cropping="-gravity $gravity -crop ${ww}x${hc}+0+0 +repage"
	fi
fi
#echo "hh=$hh; hc=$hc; cropping=$cropping"

# set up swapping for -C over
if [ "$compose" = "over" ]; then
	swapping="+swap"
else
	swapping=""
fi

# set up for opacity
if [ "$opacity" != "100" ]; then
	opacity=`convert xc: -format "%[fx:$opacity/100]" info:`
	oproc="-alpha on -channel a -evaluate multiply $opacity +channel"
else
	oproc=""
fi

# line2 1-4:  process overlay image to perspective transform with transparent
#             background the size of the tshirt image and sharpen
# lines 5-7:  apply lighting image and make tshirt background from lighting image 
#			  transparent using alpha of previous steps
# lines 8-10: apply displacement image
# note: need to add -colorspace sRGB to tmpTG to keep tmpI as color after layers merge 7/17/2020 some time after 7.0.8.23
convert -respect-parenthesis \( $dir/tmpTG.mpc -alpha transparent -colorspace sRGB \) \
	\( $dir/tmpI.mpc $cropping -virtual-pixel none +distort perspective \
	"$xo1,$yo1 $x1,$y1   $xo2,$yo2 $x2,$y2   $xo3,$yo3 $x3,$y3   $xo4,$yo4 $x4,$y4" $sproc \) \
	-background none -layers merge +repage \
	\
	\( -clone 0 -alpha extract \) \
	\( -clone 0 $oproc \( $dir/tmpL.mpc \) $swapping -alpha off -compose $compose -composite \) \
	-delete 0 +swap -compose over -alpha off -compose copy_opacity -composite \
	\
	$dir/tmpD.mpc \
	-define compose:args=-$displace,-$displace -compose displace -composite \
	$dir/tmpITD.mpc


if [ "$maskfile" != "" ]; then
	mask="$dir/tmpM.mpc"
else
	mask=""
fi

# composite distorted overlay onto tshirt
if [ "$is_alpha" != "" ]; then
	convert $dir/tmpT.mpc $dir/tmpITD.mpc $mask -compose over -composite \
		$dir/tmpA.mpc -alpha off -compose copy_opacity -composite "$outfile"
else
	convert $dir/tmpT.mpc $dir/tmpITD.mpc $mask -compose over -composite "$outfile"
fi

if [ "$export" = "yes" ]; then
	# show arguments to terminal
	echo "coordinates=\"$xo1,$yo1 $x1,$y1 $xo2,$yo2 $x2,$y2 $xo3,$yo3 $x3,$y3 $xo4,$yo4 $x4,$y4\""
	echo "fit=\"$fit\""
	echo "topwidth=\"$topwidth\""
	echo "leftheight=\"$leftheight\""
	echo "antialias=\"$antialias\""
	echo "sharpen=\"$sharpen\""
	echo "displace=\"$displace\""
	echo "modulating=\"$modulating\""
	echo "compose=\"$compose\""
	echo "opacity=\"$opacity\""
fi

if [ "$export" = "yes" -a "$directory" != "" ]; then
	# save arguments to textfile
	echo "coordinates=\"$xo1,$yo1 $x1,$y1 $xo2,$yo2 $x2,$y2 $xo3,$yo3 $x3,$y3 $xo4,$yo4 $x4,$y4\"" > $directory/tshirtdata.txt
	echo "fit=\"$fit\"" >> $directory/tshirtdata.txt
	echo "topwidth=\"$topwidth\"" >> $directory/tshirtdata.txt
	echo "leftheight=\"$leftheight\"" >> $directory/tshirtdata.txt
	echo "antialias=\"$antialias\"" >> $directory/tshirtdata.txt
	echo "sharpen=\"$sharpen\"" >> $directory/tshirtdata.txt
	echo "displace=\"$displace\"" >> $directory/tshirtdata.txt
	echo "modulating=\"$modulating\"" >> $directory/tshirtdata.txt
	echo "compose=\"$compose\"" >> $directory/tshirtdata.txt
	echo "opacity=\"$opacity\"" >> $directory/tshirtdata.txt
fi

exit 0