

reset:
	psql process < process.sql


DATA := $(wildcard nlproc-* esnoop-* sardata-* sysinfo-*)

fetch:
	scp -rp atg4g-2-p1:*-* .

archive:
	mv -f $(DATA) archives

clean:
	rm -rf $(DATA)
