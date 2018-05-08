#include <stdio.h>
#include <string.h>
#include <db.h>

DB  *db;

typedef struct {
	unsigned int   end_sec, end_usec;
	unsigned short pid;
} process_key_t;

typedef struct {
	process_key_t  key;
	unsigned int   start_sec, start_usec;
	unsigned short ppid;
	unsigned char  retval, signal;
	unsigned int   netns;
	char           args[128];
} process_t;

int db_open(char *path) {
	db_create(&db, NULL, 0);
	return db->open(db, NULL, "file.db", "process", DB_BTREE, DB_CREATE, 0644);
}

int db_fork(unsigned int boot_sec, unsigned int boot_usec, unsigned int pid, unsigned int ppid ) {
	process_t *proc =  calloc(sizeof(process_t),1);
	DBT        key, value;

	proc->key.pid = pid;
	proc->ppid = ppid;
	proc->start_sec =  boot_sec;
	proc->start_usec =  boot_usec;

	key.data=&(proc->key);
	key.size=sizeof(process_key_t);

	value.data = proc;
	value.size=sizeof(process_t);

	return db->put(db, NULL, &key, &value, 0);

}

int db_exec(unsigned int boot_sec, unsigned int boot_usec, unsigned int pid, unsigned int ppid ) {
}



int db_close() {
	return db->close(db,0 );
}



int main(int argc, char **argv) {


	DBT   key, value;




	db->get(db, NULL, &key, &value, 0);


	printf("%s, %s!\n", key.data, value.data);


	return 0;
}

