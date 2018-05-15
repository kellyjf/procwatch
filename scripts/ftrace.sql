
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


	
