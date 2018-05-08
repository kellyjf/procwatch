
#include <stdio.h>
#include <regex.h>


char *re_common="^[ ]*(\\w+)-([0-9]+) \[[0-9]+]\\s+.{4}\\s+([0-9]+.[0-9]+):\\s*(.*)$";
char *re_fork="^sched_process_fork: comm=(\\w+) pid=([0-9]+) child_comm=(\\w+) child_pid=([0-9]+)(.*)$";
char *re_exec="^sched_process_fork: filename=(\\w+) pid=([0-9]+) old_pid=([0-9]+)(.*)$";
char *re_sysexec="^eprobe_sys_execve: (.*) arg1=(\\w+) arg2=(\\w+) (.*)$";
char *re_exit="^sched_process_exit: comm=(\\w+) pid=([0-9]+) prio=([0-9]+)(.*)$";
char *re_kill="^sys_kill\\(pid: (\\w+), sig: (\\w+)(.*)$";

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
	RE_END
} re_type_t;

enum {
	COMM_NAME=1,
	COMM_PID,
	COMM_TIME,
	COMM_SUB,
};
enum {
	FORK_PID=1,
	FORK_COMM,
	FORK_CHILD_PID,
	FORK_CHILD_COMM,
};

enum {
	EXEC_FILE=1,
	EXEC_PID,
	EXEC_OLD_PID,
};

re_t re[RE_END];

#define RMFIELD(re,fnum,buf)  \
	(re)->regmatch[fnum].rm_eo-(re)->regmatch[fnum].rm_so, \
	(re)->regmatch[fnum].rm_eo-(re)->regmatch[fnum].rm_so, \
	buf+(re)->regmatch[fnum].rm_so

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
int  re_handle_exec(re_t *r, char *buf, char *subline) {
	int    f;
	printf("%s", r->name);
	printf("\t%*.*s", RMFIELD(&re[0], COMM_PID, buf));
	printf("\t%*.*s", RMFIELD(&re[0], COMM_TIME, buf));
	printf("\t%*.*s", RMFIELD(r, EXEC_FILE, subline));
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
	{ .re="^[ ]*(\\w+)-([0-9]+) \[[0-9]+]\\s+.{4}\\s+([0-9]+.[0-9]+):\\s*(.*)$",},
	{ .re="^sched_process_fork: comm=(\\w+) pid=([0-9]+) child_comm=(\\w+) child_pid=([0-9]+)(.*)$", re_handle_fork, 4, "FORK"},
	{ .re="^sched_process_exec: filename=(.+) pid=([0-9]+) old_pid=([0-9]+)(.*)$", re_handle, 3 , "EXEC"},
	{ .re="^sched_process_exit: comm=(\\w+) pid=([0-9]+) prio=([0-9]+)(.*)$", re_handle, 3, "EXIT"},
	{ .re="^eprobe_sys_execve: .* arg1=*(.+) arg2=(.+) arg3=(.+) arg4=(.+) arg5=(.+) arg6=(.*)$",re_handle_args, 6, "ARGS"},
	{ .re="^sys_kill\\(pid: (\\w+), sig: (\\w+)(.*)$",re_handle, 2, "KILL"},
};

int main (int argc, char **argv) {

	int             rc;
	FILE            *fp;

	int             ndx;

	for(ndx=0; ndx<sizeof(re)/sizeof(re_t); ndx++) {
		re_t  *elem = re+ndx;
		rc=regcomp(&re[ndx].regex, re[ndx].re, REG_EXTENDED);
	}



	//if ((fp=fopen("/sys/kernel/debug/tracing/trace_pipe","r"))==NULL) {
	if ((fp=fopen("trace","r"))==NULL) {
		perror("/sys/kernel/debug/tracing/trace_pipe");
		return(1);
	} else {
		static unsigned char buf[1024];
		while(fgets(buf,sizeof(buf),fp)) {
			rc=regexec(&re[RE_COMMON].regex, buf, 8, re[0].regmatch,0);
			if(rc==0) {
				char *subline = buf+re[0].regmatch[4].rm_so;
				re_type_t retype;

				for (retype=RE_COMMON+1; retype<RE_END; retype++) {
					int  ret;
					re_t *elem = re+retype;
					ret=regexec(&elem->regex, subline, 8, elem->regmatch,0);
					if (ret==0)  {
						if (elem->handle) elem->handle(elem, buf, subline);
					}	
				}
			}
		}
		
	}

	fclose(fp);
}


	
