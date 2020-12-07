convert $1 -modulate $[80+$[$[$3*8]/10]],$[100+$[$[$3*3]/10]] -level $[$3/2]% -unsharp 0x2+$3 -attenuate $[2+$[$3*7/100]] +noise Gaussian -quality $[31-$[$[$3*3]/10]] $2
