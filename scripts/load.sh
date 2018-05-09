#!/bin/bash

sqlite3 proc.sqlite < ftrace.sql

while read key table ; do 
	echo $key $table
	awk -v kind="$key" '$1==kind' re-180509-0639 | cut  -f 2- | sqlite3 proc.sqlite --separator '	' ".import /dev/stdin $table"
done <<!
FORK forks
EXEC execs
ARGS args
EXIT exits
EGRP egrps
KILL kills
!
exit

