#!/usr/bin/python

import argparse
from datetime import datetime as dt
import pytz

import psycopg2 as pg



if __name__ == "__main__":

	parser=argparse.ArgumentParser()
	parser.add_argument("files", nargs="+", help="Files to process")
	args=parser.parse_args()


	conn=pg.connect(dbname="ftrace")
	conn.set_session(autocommit=False)
	cur=conn.cursor()

	zone=pytz.timezone("America/Denver")

	for dat in args.files:
		with open(dat, "r") as f:
			eboot = 0
			
			for num,line in enumerate(f):
				try:
					flds=line[:-1].split("\t")	
					if len(flds)<3:
						continue
					if 'SYNC' in flds[0]:
						[mboot,eboot]=flds[1:3]
						eboot=float(eboot)-float(mboot)
					if 'FORK' in flds[0]:
						[pid,mtime,comm,cpid]=flds[1:5]
						mtime=float(mtime)
						pid=int(pid)
						cpid=int(cpid)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into forks (pid, mtime, etime, comm, cpid) values (%s, %s, %s, %s, %s)", [pid,mtime,etime,comm,cpid])

					if 'EXEC' in flds[0]:
						[pid,mtime,comm]=flds[1:4]
						mtime=float(mtime)
						pid=int(pid)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into execs (pid, mtime, etime, comm) values (%s, %s, %s, %s)", [pid,mtime,etime,comm])

					if 'ARGS' in flds[0]:
						[pid,mtime,comm]=flds[1:4]
						mtime=float(mtime)
						pid=int(pid)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into args (pid, mtime, etime, args) values (%s, %s, %s, %s)", [pid,mtime,etime,comm])

					if 'EXIT' in flds[0]:
						[pid,mtime]=flds[1:3]
						mtime=float(mtime)
						pid=int(pid)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into exits (pid, mtime, etime) values (%s, %s, %s)", [pid,mtime,etime])

					if 'EGRP' in flds[0]:
						[pid,mtime,retval]=flds[1:4]
						mtime=float(mtime)
						pid=int(pid)
						retval=int(retval)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into egrps (pid, mtime, etime, retval) values (%s, %s, %s, %s)", [pid,mtime,etime,retval])


					if 'KILL' in flds[0]:
						[pid,mtime,target,signal]=flds[1:5]
						mtime=float(mtime)
						pid=int(pid)
						target=int(target)
						signal=int(signal)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into kills (pid, mtime, etime, target, signal) values (%s, %s, %s, %s, %s)", [pid,mtime,etime,target,signal])


				except Exception as e:
					print "ERROR ON LINE ",num,":", line
					raise(e)
	conn.commit()
