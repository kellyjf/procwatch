select a.ppid, f.comm, a.ftime, a.etime::time, a.pid, a.netns, a.args from args a left join  forks f  on a.ftime=f.mtime and a.ppid=f.pid order by a.mtime;
