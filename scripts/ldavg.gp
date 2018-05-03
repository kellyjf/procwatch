set term png
set output "ldavg-1.png"

plot 'ldavg-1.txt' u 1:2 w lines
pause -1


