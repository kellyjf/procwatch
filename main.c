// For socket
#include <sys/types.h>
#include <sys/socket.h>

// For getpid()
#include <unistd.h>

#include <linux/cn_proc.h>
#include <linux/netlink.h>
#include <linux/connector.h>
//
// For memset
#include <string.h>
#include <stdio.h>

// For gettimeofday
#include <sys/time.h>
#include <time.h>

// For O_RDONLY
#include <fcntl.h>

// For RT
#include <sched.h>



#define PAGE_SIZE 4096


typedef struct sockaddr    sa;
typedef struct sockaddr_nl nla;
typedef struct nlmsghdr    nlm;

int subscribe (int sock) {

	struct iovec iov[3];
	char         nlbuf[NLMSG_LENGTH(0)];
	nlm          *hdr = (nlm*)nlbuf;
	struct cn_msg msg;
	enum proc_cn_mcast_op  op; 
 
	// Prepare a message
	// netlink header first

	memset(hdr, 0, sizeof(nlbuf));
	hdr->nlmsg_len = NLMSG_LENGTH(sizeof(msg)+sizeof(op));	
	hdr->nlmsg_type = NLMSG_DONE;
	hdr->nlmsg_pid = getpid();

	iov[0].iov_base = hdr;
	iov[0].iov_len  = NLMSG_LENGTH(0);
 
	// connector message next
	memset(&msg, 0, sizeof(msg));
	msg.id.idx  = CN_IDX_PROC;
	msg.id.val  = CN_VAL_PROC;
	msg.len     = sizeof(op);

	iov[1].iov_base = &msg;
	iov[1].iov_len  = sizeof(msg);

	// opcode at last
	memset(&op, 0, sizeof(op));
	op = PROC_CN_MCAST_LISTEN;

	iov[2].iov_base = &op;
	iov[2].iov_len  = sizeof(op);
	
	writev(sock, iov, 3);

	return(0);
}

int handle(sock) {
	struct iovec iov[1];
	nla            addr;	
	char           buf[PAGE_SIZE];
	struct msghdr  hdr;
	int            len;
	struct timeval tv;
	struct timespec monotime;
	struct timespec realtime;

//	clock_gettime(CLOCK_REALTIME, &realtime);
	clock_gettime(CLOCK_MONOTONIC, &monotime);

	memset(&hdr, 0 , sizeof(hdr));
	// Remote size addr
	hdr.msg_name    = &addr;	
	hdr.msg_namelen = sizeof(addr);	

	hdr.msg_iov     = iov;
	hdr.msg_iovlen  = 1;
	iov[0].iov_base = buf;
	iov[0].iov_len  = sizeof(buf);

	len = recvmsg(sock, &hdr, 0);


	if (len>0) {

		nlm   *n;

		for (n=(nlm*)buf; NLMSG_OK(n,len); n=NLMSG_NEXT(n,len)) {
			//printf("TYPE: %d\n", n->nlmsg_type);
			struct cn_msg *msg = NLMSG_DATA(n);
			if (msg->id.idx==CN_IDX_PROC  && msg->id.val==CN_VAL_PROC) {

				struct proc_event *ev = (struct proc_event *)msg->data;
//				printf("WHAT: %08x\n",ev->what);
				switch (ev->what) {
#ifdef MAXIMAL
				case PROC_EVENT_FORK:
					printf("%u.%09u\t%u.%09u\tFORK\t%d\t%d", 
						monotime.tv_sec, monotime.tv_nsec,
						realtime.tv_sec, realtime.tv_nsec,
						ev->event_data.fork.parent_pid,
						ev->event_data.fork.child_pid);
					printf("\n");
					break;
				case PROC_EVENT_EXEC:
					printf("%u.%09u\t%u.%09u\tEXEC\t%d",
						monotime.tv_sec, monotime.tv_nsec,
						realtime.tv_sec, realtime.tv_nsec,
						ev->event_data.exec.process_pid);
					{
						int fd;
						int bytes;
						char netns[32];
						char *name = netns;
						unsigned int nsid = 0;

						sprintf(netns,"/proc/%d/ns/net",ev->event_data.exec.process_pid);
						if ((bytes=readlink(netns, netns, sizeof(netns)))>0) {
							int c;
							for(c=0; c<bytes; c++) {
								if (netns[c]== '[') name=netns+c+1;;
								if (netns[c]== ']') netns[c]='\0';
							}
							if(c<sizeof(netns)) netns[c]='\0';
							nsid=strtoul(name,NULL,0);
						} else {
							netns[0]='\0';
							perror(netns);
						}

						printf("\t%08X", nsid);
					}
					printf("\n");
					break;
				case PROC_EVENT_EXIT:
					{
						unsigned int rc = ev->event_data.exit.exit_code;
						printf("%u.%09u\t%u.%09u\tEXIT\t%d\t%d\t%d\n",
							monotime.tv_sec, monotime.tv_nsec,
							realtime.tv_sec, realtime.tv_nsec,
							ev->event_data.exit.process_pid,
							(rc>>8),
							(rc & 0xff));
					}
					break;
				}
#endif
				case PROC_EVENT_FORK:
					printf("FORK\t%d\t%u.%06u\t\t%d", 
						ev->event_data.fork.parent_pid,
						monotime.tv_sec, monotime.tv_nsec,
						ev->event_data.fork.child_pid);
					printf("\n");
					break;
				case PROC_EVENT_EXIT:
					{
						unsigned int rc = ev->event_data.exit.exit_code;
						printf("EXIT\t%d\t%u.%06u\t%d\t%d\n",
							ev->event_data.exit.process_pid,
							monotime.tv_sec, monotime.tv_nsec,
							(rc>>8),
							(rc & 0xff));
					}
					break;
				}
			}
		}
	}

	return(len);
}

int bootdata () {
	
	FILE *fp;
	char  buf[128];

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
	if(0){
		if ((fp=popen("wtf","r"))==NULL) {
			perror("boot_id");
		} else {
			while(fgets(buf,sizeof(buf),fp)) {
				printf("WTF\t%s",buf);
			}
		}
		fclose(fp);
	}


}


extern int syncline();

int main (int argc, char **argv) {

	int          sock;
	nla          addr;	
	int          cnt;
	struct       sched_param sparm;

	memset(&sparm, 0 , sizeof(sparm));
	sparm.sched_priority = 2;
	sched_setscheduler(0, SCHED_RR, &sparm);

	//bootdata();
	syncline();
 
	// Open a netlink socket
	sock = socket(PF_NETLINK, SOCK_DGRAM|SOCK_CLOEXEC, NETLINK_CONNECTOR);
	//sock = socket(PF_NETLINK, SOCK_DGRAM|SOCK_NONBLOCK|SOCK_CLOEXEC, NETLINK_CONNECTOR);

	// Bind it to our pid
	addr.nl_family = AF_NETLINK;
	addr.nl_pid    = getpid();
	addr.nl_groups = CN_IDX_PROC;

	bind(sock, (sa*)&addr, sizeof(addr));

	subscribe(sock);
	
	while(1) {
		handle(sock);
	}

	return(0);
}

