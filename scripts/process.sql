

drop function pkids(integer);
drop function psibs(integer);
drop function ptree(integer);

drop index  process_pid_start;
drop view  pinfo;
drop table  process;

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


create view pinfo  as
	select  
		mtimenl as mtime,
		start_time::time,
		pid,ppid, retval, signal,
		netns, comm
	from process
	order by start_time, pid;

create function pkids(integer) returns setof pinfo as $$
	select * from pinfo where ppid=$1 $$ language sql;

create function psibs(integer) returns setof pinfo as $$
	select * from pinfo where ppid in (
		select ppid from process p where p.pid=$1 
			and abs(date_part('epoch',start_time-p.start_time))<1000) 
	$$ language sql;


create function ptree(integer) returns setof pinfo as $$
with recursive tree as (
	select * from pinfo where pid=$1
	union all
	select p.* from pinfo p, tree t where p.pid=t.ppid
) 
select * from tree;
$$ language sql;


	
