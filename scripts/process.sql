

drop table if exists process;

create table process (
 	start_time   timestamptz,
 	end_time   timestamptz,
	pid        integer,
	ppid       integer,
	retval     integer,
	signal     integer,
	comm       varchar(512),
	primary key (start_time,pid)
);

create index process_pid_start on process (pid,start_time);
