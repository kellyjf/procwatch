drop view if exists commands;
create view commands as 
	select 
		to_char(e.mtime,'999999.999') as "Boot", 
		to_char(e.etime,'HH24:MI:SS.MS') as "Time",
		to_char(e.pid,'99999') as "Pid",
		a.netns as "NetNS",
		case when a.args is null then e.comm else a.args end as "Command",
		e.mtime, e.pid
	from execs e left join args a 
	on a.pid=e.pid and abs(e.mtime-a.mtime)<10 
	order by 1;

drop view if exists parents;
create view parents as 
	select 
		to_char(e.mtime,'999999.999') as "Boot", 
		to_char(e.etime,'HH24:MI:SS.MS') as "Time",
		to_char(e.pid,'99999') as "Pid",
		to_char(e.cpid,'99999') as "Cpid",
		a.args as "Command",
		e.mtime, e.pid, e.cpid
	from forks e left join args a 
	on a.pid=e.pid and (e.mtime-a.mtime)<10 
	order by 1;


--create view comms as select e.*,a.args  from execs e left join args a on a.pid=e.pid and abs(e.mtime-a.mtime)<10 ;
