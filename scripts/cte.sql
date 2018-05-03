create function ptree(integer) returns setof pinfo as $$
with recursive tree as (
	select * from pinfo where pid=$1
	union all
	select p.* from pinfo p, tree t where p.pid=t.ppid
) 
select * from tree;
$$ language sql;


