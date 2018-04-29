#!/usr/bin/python

import argparse
from datetime import datetime as dt
import pytz

import psycopg2 as pg



if __name__ == "__main__":

	parser=argparse.ArgumentParser()
	parser.add_argument("files", nargs="+", help="Files to process")
	args=parser.parse_args()


	conn=pg.connect(dbname="process")
	cur=conn.cursor()

	zone=pytz.timezone("America/Denver")

	for dat in args.files:
		with open(dat, "r") as f:
			
			for num,line in enumerate(f):
				try:
					flds=line[:-1].split("\t")	
					if len(flds)<3:
						continue
					if 'FORK' in flds[2]:
						if len(flds)<5:
							continue
						(mtime,epoch,sys,ppid,pid)=flds[0:5]
						start=dt.fromtimestamp(float(epoch),zone)
						pid=int(pid)
						ppid=int(ppid)

						# Insert a process
						cur.execute("insert into process (start_time, pid, ppid) values (%s, %s, %s)", [start,pid,ppid])

					if 'EXEC' in flds[2]:
						if len(flds)<5:
							continue
						(mtime,epoch,sys,pid,netns)=flds[0:5]
						etime=dt.fromtimestamp(float(epoch),zone)
						pid=int(pid)
						cur.execute("update process set mtimenl=%s, netns=%s where pid=%s and end_time IS NULL", [mtime,netns, pid])

					if 'EXIT' in flds[2]:
						if len(flds)<6:
							continue
						(mtime,epoch,sys,pid,ret,sig)=flds[0:6]
						end_time=dt.fromtimestamp(float(epoch),zone)
						pid=int(pid)
						ret=int(ret)
						sig=int(sig)
						cur.execute("update process set end_time=%s, retval=%s, signal=%s where pid=%s and end_time IS NULL", [end_time,ret,sig,pid])

				except Exception as e:
					print "ERROR ON LINE ",num,":", line
					raise(e)
	conn.commit()
