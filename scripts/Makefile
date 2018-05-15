

reset:
	psql process < process.sql


#DATA := $(wildcard nlproc-* esnoop-* sardata-* sysinfo-*)
DATA := $(wildcard fdr-* nlproc-*  sardata-* sysinfo-*)

fetch:
	scp -rp atg4g-2-p1:{fdr,nlproc,sysinfo}*-* .

archive:
	mv -f $(DATA) archives

clean:
	rm -rf $(DATA)
