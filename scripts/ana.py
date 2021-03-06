#!/usr/bin/python

import argparse
from datetime import datetime as dt
import pytz

import psycopg2 as pg


def main():
	parser=argparse.ArgumentParser()
	args=parser.parse_args()


	conn=pg.connect(dbname="ftrace")
	conn.set_session(autocommit=False)
	cura=conn.cursor()
	curp=conn.cursor()
	curf=conn.cursor()
	curu=conn.cursor()
	zone=pytz.timezone("America/Denver")

#	curp.execute("create index args_mtime on args(mtime,pid)")
#	curp.execute("create index exits_mtime on exits(mtime,pid)")

	cura.execute("select * from args order by mtime ")
	for ndx, rec in enumerate(cura):
		arg=dict(zip([x.name for x in cura.description], list(rec)))

		curf.execute("select * from forks where cpid=%s and mtime<%s order by mtime desc limit 1",[arg.get('pid'),float(arg.get('mtime')+10.0)])
		fork=curf.fetchone()
		if fork:
			efork=dict(zip([x.name for x in curf.description], list(fork)))
			curu.execute("update args set ftime=%s , ppid=%s where mtime=%s and pid=%s",
				[efork.get('mtime'),efork.get('pid'), arg.get('mtime'),arg.get('pid')])
		else:
			efork={}	

		curf.execute("select * from exits where pid=%s and mtime>%s order by mtime desc limit 1",[arg.get('pid'),float(arg.get('mtime')-10.0)])
		xrec=curf.fetchone()
		if xrec:
			xrec=dict(zip([x.name for x in curf.description], list(xrec)))
			curu.execute("update args set xtime=%s, retval=%s, signal=%s where mtime=%s and pid=%s",
				[xrec.get('mtime'),xrec.get('retval'), xrec.get('signal'),  arg.get('mtime'),arg.get('pid')])
		if False:
			print "{:5} | {:18.18s} | {:12.6f} | {:5} | {:15.15} | {:8} | {} ".format(
			efork.get('pid',''), efork.get('comm',''), 
			arg.get('mtime'),arg.get('pid'),
			arg.get('etime').strftime("%H:%M:%S.%f"),arg.get('netns'), arg.get('args'))
		else:
			if ndx%1000==0:
				print ndx, arg.get('mtime')
	conn.commit()

if __name__ == "__main__":
	main()

