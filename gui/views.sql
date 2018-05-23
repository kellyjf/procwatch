
drop view if exists commands;
drop view if exists parents;

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
	on a.pid=e.cpid
	and a.mtime= (select mtime from args where pid=e.cpid and (e.mtime-mtime)<10 order by mtime limit 1) 
	order by 1;

