DROP TABLE IF EXISTS keyvalue;

--キーバリューストア PENDINGリレーショナルDBから取り除く？
CREATE TABLE IF NOT EXISTS "keyvalue" (
	"key"	TEXT NOT NULL,
	"value"	TEXT NOT NULL,
	PRIMARY KEY("key")
);