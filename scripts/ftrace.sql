
drop table if exists forks;
drop table if exists execs;
drop table if exists args;
drop table if exists exits;
drop table if exists egrps;
drop table if exists kills;


create table forks (
	pid        integer,
 	start_time   float,
	comm       varchar(512),
	ppid       integer,
	primary key (start_time,pid)
);

create table execs (
	pid        integer,
 	start_time   float,
	comm       varchar(512),
	primary key (start_time,pid)
);

create table args (
	pid        integer,
 	start_time   float,
	args       varchar(512),
	primary key (start_time,pid)
);

create table exits (
	pid        integer,
 	start_time   float,
	primary key (start_time,pid)
);

create table egrps (
	pid        integer,
 	start_time   float,
	retval        integer,
	primary key (start_time,pid)
);

create table kills (
	pid        integer,
 	start_time   float,
	target        integer,
	signal        integer,
	primary key (start_time,pid)
);


	
