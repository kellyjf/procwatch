
drop view if exists commands;
drop view if exists parents;

drop table if exists forks;
drop table if exists execs;
drop table if exists args;
drop table if exists exits;
drop table if exists egrps;
drop table if exists kills;
drop table if exists sgens;


create table forks (
 	mtime      float,
 	etime      timestamptz,
	pid        integer,
	comm       varchar(512),
	cpid       integer,
	primary key (mtime,pid,cpid)
);

create table execs (
 	mtime      float,
 	etime      timestamptz,
	pid        integer,
	comm       varchar(512),
	primary key (mtime,pid)
);

create table args (
 	ftime      float,
 	mtime      float,
 	xtime      float,
 	etime      timestamptz,
	pid        integer,
	ppid       integer,
	retval     integer,
	signal     integer,
	netns      varchar(8), 
	args       varchar(512),
	primary key (mtime,pid)
);

create table exits (
 	mtime      float,
 	etime      timestamptz,
	pid        integer,
	retval     integer,
	signal     integer,
	primary key (mtime,pid)
);

create table egrps (
 	mtime      float,
 	etime      timestamptz,
	pid        integer,
	retval     integer,
	primary key (mtime,pid)
);

create table kills (
 	mtime      float,
 	etime      timestamptz,
	pid        integer,
	target     integer,
	signal     integer
);

create table sgens (
 	mtime      float,
 	etime      timestamptz,
	pid        integer,
	signal     integer,
	target     integer,
	code       varchar(8)
);


	
create view commands as 
	select 
		to_char(e.mtime,'999999.999') as "Boot", 
		to_char(e.etime at time zone 'UTC' ,'HH24:MI:SS.MS') as "Time",
		to_char(e.pid,'99999') as "Pid",
		a.netns as "NetNS",
		case when a.args is null then e.comm else a.args end as "Command",
		e.mtime, e.etime,e.pid
	from execs e left join args a 
	on a.pid=e.pid and abs(e.mtime-a.mtime)<10 
	order by 1;

create view parents as 
	select 
		to_char(e.mtime,'999999.999') as "Boot", 
		to_char(e.etime at time zone 'UTC' ,'HH24:MI:SS.MS') as "Time",
		to_char(e.pid,'99999') as "Pid",
		to_char(e.cpid,'99999') as "Cpid",
		a.args as "Command",
		e.mtime, e.pid, e.cpid
	from forks e left join args a 
	on a.pid=e.pid and (e.mtime-a.mtime)<10 
	order by 1;

