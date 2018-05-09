
#include <stdio.h>
#include <regex.h>

int _debug;
//int _debug = 1;

typedef struct re_s {
	char       *re;
	int         (*handle)(struct re_s *re, char *buf, char *);
	int         nflds;
	char       *name;
	regex_t     regex;
	regmatch_t  regmatch[8];
} re_t;



typedef enum {
	RE_COMMON = 0,
	RE_FORK,
	RE_EXEC,
	RE_EXIT,
	RE_PROBE,
	RE_KILL,
	RE_SGEN,
	RE_EGRP,
	RE_END
} re_type_t;

enum {
	COMM_NAME=1,
	COMM_PID,
	COMM_TIME,
	COMM_SUB,
};


re_t re[RE_END];

#define RMFIELD(re,fnum,buf)  \
	(re)->regmatch[fnum].rm_eo-(re)->regmatch[fnum].rm_so, \
	(re)->regmatch[fnum].rm_eo-(re)->regmatch[fnum].rm_so, \
	buf+(re)->regmatch[fnum].rm_so

enum {
	FORK_PID=1,
	FORK_COMM,
	FORK_CHILD_PID,
	FORK_CHILD_COMM,
};
int  re_handle_fork(re_t *r, char *buf, char *subline) {
	int    f;
	printf("%s", r->name);
	printf("\t%*.*s", RMFIELD(&re[0], COMM_PID, buf));
	printf("\t%*.*s", RMFIELD(&re[0], COMM_TIME, buf));
	printf("\t%*.*s", RMFIELD(r, FORK_CHILD_PID, subline));
	printf("\t%*.*s", RMFIELD(r, FORK_CHILD_COMM, subline));
	printf("\n");
	return 0;
}
enum {
	EXEC_FILE=1,
	EXEC_PID,
	EXEC_OLD_PID,
};
int  re_handle_exec(re_t *r, char *buf, char *subline) {
	int    f;
	printf("%s", r->name);
	printf("\t%*.*s", RMFIELD(&re[0], COMM_PID, buf));
	printf("\t%*.*s", RMFIELD(&re[0], COMM_TIME, buf));
	printf("\t%*.*s", RMFIELD(r, EXEC_FILE, subline));
	printf("\n");
	return 0;
}
enum {
	SIG_SIG=1,
	SIG_ERRNO,
	SIG_CODE,
	SIG_COMM,
	SIG_PID,
};
int  re_handle_signal(re_t *r, char *buf, char *subline) {
	int    f;
	unsigned char code[16];
	printf("%s", r->name);
	printf("\t%*.*s", RMFIELD(&re[0], COMM_PID, buf));
	printf("\t%*.*s", RMFIELD(&re[0], COMM_TIME, buf));
	printf("\t%*.*s", RMFIELD(r, SIG_SIG, subline));
	printf("\t%*.*s", RMFIELD(r, SIG_PID, subline));
	snprintf(code,sizeof(code),"%*.*s", RMFIELD(r, SIG_PID, subline));
	printf("\t%04X", strtoul(code,NULL,0));
	printf("\n");
	return 0;
}
enum {
	KILL_SIG=1,
	KILL_PID,
};
int  re_handle_kill(re_t *r, char *buf, char *subline) {
	int    f;
	unsigned char code[16];
	printf("%s", r->name);
	printf("\t%*.*s", RMFIELD(&re[0], COMM_PID, buf));
	printf("\t%*.*s", RMFIELD(&re[0], COMM_TIME, buf));
	snprintf(code,sizeof(code),"0x%*.*s", RMFIELD(r, KILL_SIG, subline));
	printf("\t%d", strtoul(code,NULL,0));
	snprintf(code,sizeof(code),"0x%*.*s", RMFIELD(r, KILL_PID, subline));
	printf("\t%d", strtoul(code,NULL,0));
	printf("\n");
	return 0;
}
int  re_handle(re_t *r, char *buf, char *subline) {
	int    f;
	printf("%s", r->name);
	printf("\t%*.*s", RMFIELD(&re[0], COMM_PID, buf));
	printf("\t%*.*s", RMFIELD(&re[0], COMM_TIME, buf));
	for(f=1; f<=r->nflds; f++) {
		printf("\t%*.*s", RMFIELD(r, f, subline));
	}
	printf("\n");
	return 0;
}

int  re_handle_args(re_t *r, char *buf, char *subline) {
	int    f;
	printf("%s", r->name);
	printf("\t%*.*s", RMFIELD(&re[0], COMM_PID, buf));
	printf("\t%*.*s", RMFIELD(&re[0], COMM_TIME, buf));
	for(f=1; f<=r->nflds; f++) {
		char *fs=subline+r->regmatch[f].rm_so;
		int   sz=r->regmatch[f].rm_eo-r->regmatch[f].rm_so-2;
		char *p;
		for(p=fs; p<fs+sz; p++) { if (*p=='\t') *p=' '; }
		if( *fs == '"') {
			(f==1) ? printf("\t") : printf(" ",*fs);
			printf("%*.*s", sz,sz,fs+1);
		} else {
			break;
		}
	}
	printf("\n");
	return 0;
}
re_t re[] = {
	{ .re="^\\s*(.+)-([0-9]+)\\s+\[[0-9]+]\\s+.{4}\\s+([0-9]+.[0-9]+):\\s*(.*)\n$",},
	{ .re="^sched_process_fork: comm=(.+) pid=([0-9]+) child_comm=(\\w+) child_pid=([0-9]+).*\n$", re_handle_fork, 4, "FORK"},
	{ .re="^sched_process_exec: filename=(.+) pid=([0-9]+) old_pid=([0-9]+).*\n$", re_handle_exec, 3 , "EXEC"},
	{ .re="^sched_process_exit: comm=(.+) pid=([0-9]+) prio=([0-9]+).*\n$", re_handle, 0, "EXIT"},
	{ .re="^eprobe_sys_execve: .* arg1=*(.+) arg2=(.+) arg3=(.+) arg4=(.+) arg5=(.+) arg6=(.*)\n$",re_handle_args, 6, "ARGS"},
	{ .re="^sys_kill\\(pid:\\s*(.+),\\s*sig:\\s*(.+)\\).*\n$",re_handle_kill, 2, "KILL"},
	{ .re="^signal_generate:.*sig=([0-9]+) errno=([0-9]+) code=([0-9]+) comm=(\\w+) pid=([0-9]+) (.*)\n$",re_handle_signal, 5, "SGEN"},
	{ .re="^sys_exit_group\\(error_code:\\s*(.*)\\).*$",re_handle, 1, "EGRP"},
};
//	{ .re="^sys_exit_group(error_code:\\s*([0-9a-f]+))\\s*$",re_handle, 1, "EGRP"},


extern int lruinfo();
extern int syncline();

int main (int argc, char **argv) {

	int             rc;
	FILE            *fp;
	int             ndx;
	char            *filename="/sys/kernel/debug/tracing/trace_pipe";

	for(ndx=0; ndx<sizeof(re)/sizeof(re_t); ndx++) {
		re_t  *elem = re+ndx;
		rc=regcomp(&re[ndx].regex, re[ndx].re, REG_EXTENDED);
		if (_debug) printf ("rc=%d %s\n", rc, elem->re);
	}


	syncline();
	lruinfo();

	//if ((fp=fopen("/sys/kernel/debug/tracing/trace_pipe","r"))==NULL) {
	if (argc>1) filename=argv[1];	
	if ((fp=fopen(filename,"r"))==NULL) {
		perror(filename);
		return(1);
	} else {
		static unsigned char buf[1024];
		while(fgets(buf,sizeof(buf),fp)) {
			rc=regexec(&re[RE_COMMON].regex, buf, 8, re[0].regmatch,0&REG_EXTENDED);
			if (_debug) printf("rc=%d %s\n    %s\n",rc, re[RE_COMMON].re, buf);
			if(rc==0) {
				char *subline = buf+re[0].regmatch[4].rm_so;
				re_type_t retype;

				for (retype=RE_COMMON+1; retype<RE_END; retype++) {
					int  ret;
					re_t *elem = re+retype;
					ret=regexec(&elem->regex, subline, 8, elem->regmatch,0&REG_EXTENDED);
					if (_debug) printf("rc=%d %s | [%s] \n", ret, elem->re, subline);
					if (ret==0)  {
						if (elem->handle) elem->handle(elem, buf, subline);
					}	
				}
			}
		}
		
	}

	fclose(fp);
}


	
