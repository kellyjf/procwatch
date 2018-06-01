

reset:
	psql process < process.sql


ifeq ($(LRU),)
LRU := 172.27.9.56
endif

DATA := $(wildcard fdr-* nlproc-*  sardata-* sysinfo-*)

fetch:
	scp -i ~/.ssh/jaguar.key  -rp root@$(LRU):{fdr,nlproc,sysinfo}*-* .

archive:
	mv -f $(DATA) archives

clean:
	rm -rf $(DATA)
