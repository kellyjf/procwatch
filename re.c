
#include <stdio.h>
#include <regex.h>


int main (int argc, char **argv) {

	regex_t         retrace;
	int             rc;
	FILE            *fp;
	regmatch_t      rematch[32];


	rc=regcomp(&retrace, "^\\s*([^-]+)-(\\d+)\\s*\[\\d+\\]\\s*(.{4})", REG_EXTENDED);
	rc=regcomp(&retrace, "^[ ]*(\\w+)-([0-9]+)\\s+.{4}\+([0-9]+.[0-9]+):\\s+(\\w+):.*$", REG_EXTENDED);
	printf("%d\n",rc);


	//if ((fp=fopen("/sys/kernel/debug/tracing/trace_pipe","r"))==NULL) {
	if ((fp=fopen("trace","r"))==NULL) {
		perror("/sys/kernel/debug/tracing/trace_pipe");
		return(1);
	} else {
		static unsigned char buf[1024];
		while(fgets(buf,sizeof(buf),fp)) {
			rc=regexec(&retrace, buf, 32, rematch,0);
			if(rc==0) {
				printf("rc=%d %s", rc, buf);
			}
		}
		
	}

	fclose(fp);
}


	
