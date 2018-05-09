#include <stddef.h>
#include <stdio.h>
#include <time.h>
#include <sys/sysinfo.h>

int lruinfo() {
	FILE *fp;
	unsigned char buf[256];

	memset(buf, 0, sizeof(buf));
	if ((fp=fopen("/proc/sys/kernel/random/boot_id","r"))==NULL) {
		perror("boot_id");
	} else {
		char *start, *end;

		fgets(buf,sizeof(buf),fp);
		for(start=buf,end=buf; *start; start++, end++) {
			while(*end && *end=='-') { end++ ;}
			if(end!=start) {
				*start=*end;
			}
		}
		printf("BOOT\t%s",buf);
	}
	fclose(fp);

	if ((fp=popen("hostname","r"))==NULL) {
		perror("hostname");
	} else {
		while(fgets(buf,sizeof(buf),fp)) {
			printf("HOSTNAME\t%s",buf);
		}
	}
	fclose(fp);

	if ((fp=popen("wtf","r"))==NULL) {
		perror("boot_id");
		return -1;
	} else {
		while(fgets(buf,sizeof(buf),fp)) {
			printf("WTF\t%3.3s\t%s",buf,buf+4);
		}
	}
	fclose(fp);

	return 0;	
}

int syncline(void){
    /* get uptime in seconds */
    struct sysinfo info;
    sysinfo(&info);

    /* calculate boot time in seconds since the Epoch */
    const time_t boottime = time(NULL) - info.uptime;

    /* get monotonic clock time */
    struct timespec monotime;
    clock_gettime(CLOCK_MONOTONIC, &monotime);

    /* calculate current time in seconds since the Epoch */
    time_t curtime = boottime + monotime.tv_sec;

    /* get realtime clock time for comparison */
    struct timespec realtime;
    clock_gettime(CLOCK_REALTIME, &realtime);

    printf("SYNC\t%u.%09u\t%u.%09u\n", 
	monotime.tv_sec, monotime.tv_nsec,
	realtime.tv_sec, realtime.tv_nsec);

    return 0;
}

