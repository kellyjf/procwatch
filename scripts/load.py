#!/usr/bin/python

import argparse
from datetime import datetime as dt
import pytz



if __name__ == "__main__":

	parser=argparse.ArgumentParser()
	parser.add_argument("files", nargs="+", help="Files to process")

	args=parser.parse_args()

	zone=pytz.timezone("America/Denver")

	for dat in args.files:
		with open(dat, "r") as f:
			for line in f:
				flds=line[:-1].split("\t")	
				if 'FORK' in flds[1]:
					if len(flds)>3:
						(epoch,sys,pid,ppid)=flds[0:4]
					if len(flds)>4:
						pcmd=flds[4]
					else:
						pcmd=""
					start=dt.fromtimestamp(int(epoch),zone)
					pid=int(pid)
					ppid=int(ppid)

					# Insert a process

				if 'EXEC' in flds[1]:
					if len(flds)>3:
						(epoch,sys,pid,net)=flds[0:4]
					if len(flds)>4:
						pcmd=flds[4]
					else:
						pcmd=""
					etime=dt.fromtimestamp(int(epoch),zone)
					pid=int(pid)

				if 'EXIT' in flds[1]:
					if len(flds)>4:
						(epoch,sys,pid,ret,sig)=flds[0:5]
					end_time=dt.fromtimestamp(int(epoch),zone)
					pid=int(pid)
					ret=int(ret)
					sig=int(sig)


