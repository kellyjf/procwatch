

reset:
	psql process < process.sql


#DATA := $(wildcard nlproc-* esnoop-* sardata-* sysinfo-*)
DATA := $(wildcard fdr-*  sardata-* sysinfo-*)

fetch:
	scp -rp atg4g-2-p1:{fdr,sys}*-* .

archive:
	mv -f $(DATA) archives

clean:
	rm -rf $(DATA)
