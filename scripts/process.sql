

drop table if exists process;

create table process (
 	mtimenl   interval,
 	mtimeft   interval,
 	start_time   timestamptz,
 	end_time   timestamptz,
	pid        integer,
	ppid       integer,
	retval     integer,
	signal     integer,
	netns      varchar(20),
	comm       varchar(512),
	primary key (start_time,pid)
);

create index process_pid_start on process (pid,start_time);
