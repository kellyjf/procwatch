#!/usr/bin/python

import argparse
from datetime import datetime as dt
import pytz
import traceback

import psycopg2 as pg



def loadfiles(dbname, files):

	conn=pg.connect(dbname=dbname)
	conn.set_session(autocommit=False)
	cur=conn.cursor()

	zone=pytz.timezone("America/Denver")
	eboot = 0

	for dat in files:
		with open(dat, "r") as f:
			
			for num,line in enumerate(f):
				if num%1000==0:
					print num,line[:-1]
				try:
					if line[-1:]!='\n':
						continue
					flds=line[:-1].split("\t")	
					if len(flds)<3:
						continue
					if 'SYNC' in flds[0] and not eboot:
						[mboot,_eboot]=flds[1:3]
						eboot=float(_eboot)-float(mboot)
					if 'FORK' in flds[0]:
						[pid,mtime,comm,cpid]=flds[1:5]
						mtime=float(mtime)
						pid=int(pid)
						cpid=int(cpid)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into forks (pid, mtime, etime, comm, cpid) values (%s, %s, %s, %s, %s)", [pid,mtime,etime,comm,cpid])

					if 'EXEC' in flds[0]:
						if len(flds)<4:
							continue
						[pid,mtime,comm]=flds[1:4]
						mtime=float(mtime)
						pid=int(pid)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into execs (pid, mtime, etime, comm) values (%s, %s, %s, %s)", [pid,mtime,etime,comm])

					if 'ARGS' in flds[0]:
						if len(flds)<5:
							continue
						[pid,mtime,netns,comm]=flds[1:5]
						mtime=float(mtime)
						pid=int(pid)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into args (pid, mtime, etime, netns, args) values (%s, %s, %s,%s, %s)", [pid,mtime,etime,netns,comm])

					if 'EXIT' in flds[0]:
						if len(flds)<5:
							continue
						[pid,mtime,retval,signal]=flds[1:5]
						mtime=float(mtime)
						pid=int(pid)
						retval=int(retval)
						signal=int(signal)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into exits (pid, mtime, etime,retval,signal) values (%s, %s, %s, %s, %s)", [pid,mtime,etime,retval,signal])

					if 'EGRP' in flds[0]:
						if len(flds)<4:
							continue
						[pid,mtime,retval]=flds[1:4]
						mtime=float(mtime)
						pid=int(pid)
						retval=int(retval)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into egrps (pid, mtime, etime, retval) values (%s, %s, %s, %s)", [pid,mtime,etime,retval])


					if 'KILL' in flds[0]:
						if len(flds)<5:
							continue
						[pid,mtime,target,signal]=flds[1:5]
						mtime=float(mtime)
						pid=int(pid)
						target=int(target)
						signal=int(signal)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into kills (pid, mtime, etime, target, signal) values (%s, %s, %s, %s, %s)", [pid,mtime,etime,target,signal])


					if 'SGEN' in flds[0]:
						if len(flds)<6:
							continue
						[pid,mtime,signal,target,code]=flds[1:6]
						mtime=float(mtime)
						pid=int(pid)
						target=int(target)
						signal=int(signal)
						etime=dt.fromtimestamp(mtime+eboot,zone)

						# Insert a process
						cur.execute("insert into sgens (pid, mtime, etime, target, signal, code) values (%s, %s, %s, %s, %s, %s)", [pid,mtime,etime,target,signal,code])


				except Exception as e:
					print "ERROR ON LINE ",num,":", line
					traceback.print_exc()
	conn.commit()
	conn.close()


def initdb(dbname):

	conn=pg.connect(dbname=dbname)
	conn.set_session(autocommit=False)
	cur=conn.cursor()

	sqlfile=open("ftrace.sql","r")
	cmds=sqlfile.read().rstrip().split(";")
	sqlfile.close()

	for cmd in cmds:
		print "["+cmd+"]"
		if cmd:
			cur.execute(cmd)

	cur.close()
	conn.commit()


if __name__ == "__main__":

	parser=argparse.ArgumentParser()
	parser.add_argument("files", nargs="+", help="Files to process")
	args=parser.parse_args()
	loadfiles('ftrace', args.files)

