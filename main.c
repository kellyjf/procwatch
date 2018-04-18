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

// For time
#include <time.h>

// For O_RDONLY
#include <fcntl.h>

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
	time_t         now;

	time(&now);

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
				case PROC_EVENT_FORK:
					printf("%u\tFORK\t%d\t%d", 
						now,
						ev->event_data.fork.parent_pid,
						ev->event_data.fork.child_pid);
					{
						int fd;
						char path[512];
						sprintf(path,"/proc/%d/cmdline",ev->event_data.fork.parent_pid);
						if ((fd=open(path, O_RDONLY))>0) {
							int bytes;
							bytes=read(fd, path, sizeof(path)-1);
							if(bytes>0) {
								int c;
								for(c=0; c<bytes; c++) {
									if (path[c]== 0x00) path[c]=' ';
								}
								if(c<sizeof(path)) path[c]='\0';
								printf("\t%s", path);
							}
							close(fd);
						} else {
							printf("\t?");
							perror(path);
						}
					}
					printf("\n");
					break;
				case PROC_EVENT_EXEC:
					printf("%u\tEXEC\t%d", now, ev->event_data.exec.process_pid);
					{
						int fd;
						int bytes;
						char path[512];

						sprintf(path,"/proc/%d/ns/net",ev->event_data.exec.process_pid);
						if ((bytes=readlink(path, path, sizeof(path)))>0) {
							int c;
							for(c=0; c<bytes; c++) {
								if (path[c]== 0x00) path[c]=' ';
							}
							if(c<sizeof(path)) path[c]='\0';
							printf("\t%s", path);
						} else {
							printf("\t?");
							perror(path);
						}

						sprintf(path,"/proc/%d/cmdline",ev->event_data.exec.process_pid);
						if ((fd=open(path, O_RDONLY))>0) {
							bytes=read(fd, path, sizeof(path)-1);
							if(bytes>0) {
								int c;
								for(c=0; c<bytes; c++) {
									if (path[c]== 0x00) path[c]=' ';
								}
								if(c<sizeof(path)) path[c]='\0';
								printf("\t%s", path);
							}
							close(fd);
						} else {
							printf("\t?");
							perror(path);
						}
					}
					printf("\n");
					break;
				case PROC_EVENT_EXIT:
					{
						unsigned int rc = ev->event_data.exit.exit_code;
						printf("%u\tEXIT\t%d\t%d\t%d\n",  now,
							ev->event_data.exit.process_pid,
							(rc>>8),
							(rc & 0xff));
					}
					break;
				case PROC_EVENT_COMM:
					//printf("COMM: %s\n", ev->event_data.comm.comm);
					break;
				}
			}
		}
		/*
		write(1, buf, len);
		write(1, &len, sizeof(len));
		write(1, "\n\n\n\n", 4);
		*/
	}

	return(len);
}
int main (int argc, char **argv) {

	int          sock;
	nla          addr;	
	int          cnt;

 
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
