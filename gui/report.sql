select a.ppid, f.comm, a.ftime, a.etime::time, a.pid, a.netns, a.retval, a.signal, a.args 
from args a left join  forks f 
	on a.ftime=f.mtime and a.ppid=f.pid 
where (a.signal != 0 or a.retval != 0 )
order by a.mtime;
