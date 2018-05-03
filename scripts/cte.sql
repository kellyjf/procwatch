create or replace view pinfo  as
	select  
		mtimenl as mtime,
		start_time::time,
		pid,ppid, retval, signal,
		netns, comm
	from process
	order by start_time, pid;

create or replace function pkids(integer) returns setof pinfo as $$
	select * from pinfo where ppid=$1 $$ language sql;

create or replace function psibs(integer) returns setof pinfo as $$
	select * from pinfo where ppid in (
		select ppid from process p where p.pid=$1 
			and abs(date_part('epoch',start_time-p.start_time))<1000) 
	$$ language sql;


create or replace function ptree(integer) returns setof pinfo as $$
with recursive tree as (
	select * from pinfo where pid=$1
	union all
	select p.* from pinfo p, tree t where p.pid=t.ppid
) 
select * from tree;
$$ language sql;

create or replace function ctree(integer) returns setof pinfo as $$
with recursive tree as (
	select * from pinfo where pid=$1
	union all
	select p.* from pinfo p, tree t where p.ppid=t.pid
) 
select * from tree;
$$ language sql;


