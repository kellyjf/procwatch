#!/usr/bin/python

import argparse

import psycopg2 as pg



if __name__ == "__main__":

	parser=argparse.ArgumentParser()
	parser.add_argument("files", nargs="+", help="Files to process")
	args=parser.parse_args()


	conn=pg.connect(dbname="process")
	cur=conn.cursor()


	for dat in args.files:
		with open(dat, "r") as f:
			
			for num,line in enumerate(f):
				if num<3:
					continue
				try:
					flds=line[:-1].split()	
					if len(flds)<3:
						continue
					(mtime,pid,ppid)=flds[0:3]
					pid=int(pid)
					ppid=int(ppid)
					comm=" ".join(flds[3:])[:512]

					cur.execute("update process set mtimeft=%s, comm=%s where pid=%s and ppid=%s", [mtime,comm, pid, ppid])

				except Exception as e:
					print "ERROR ON LINE ",num,":", line
					raise(e)
	conn.commit()
