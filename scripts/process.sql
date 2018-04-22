

drop table if exists process;

create table process (
 	start_time   timestamp,
 	end_time   timestamp,
	pid        integer,
	ppid       integer,
	comm       varchar(512),
	retval     integer,
	signal     integer,
	primary key (start_time,pid)
);

create index process_pid_start on process (pid,start_time);
