#include <stdio.h>
#include <string.h>
#include <db.h>


int main(int argc, char **argv) {

	DB  *db;

	DBT   key, value;


	db_create(&db, NULL, 0);
	db->open(db, NULL, "file.db", "process", DB_BTREE, DB_CREATE, 0644);

	memset(&key, 0, sizeof(key));	
	memset(&value, 0, sizeof(value));	

	key.data = "Hello";
	key.size=6;
	value.data="World";
	value.size=6;

	db->put(db, NULL, &key, &value, 0);
	memset(&value, 0, sizeof(value));	
	db->get(db, NULL, &key, &value, 0);


	printf("%s, %s!\n", key.data, value.data);

	db->close(db,0 );

	return 0;
}

