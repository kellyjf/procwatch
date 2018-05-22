
with merge as (
(select mtime, 'FORK' as "kind" from forks)
union all
(select mtime, 'EXEC' as "kind" from execs)
union all
(select mtime, 'EXIT' as "kind" from exits)
)
select round(mtime/10),
	sum(case when kind='FORK' then 1 else 0 end) as "fork",
	sum(case when kind='EXEC' then 1 else 0 end) as "exec",
	sum(case when kind='EXIT' then 1 else 0 end) as "exit",
	count(*) as "all"
	from merge
	group by  1 order by 1
;
