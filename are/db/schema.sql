DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS keyvalue;
DROP TABLE IF EXISTS queue;

-- DROP TABLE IF EXISTS "basedata";
-- DROP INDEX IF EXISTS "datetimeindex";

CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER,
	"username"	TEXT NOT NULL UNIQUE,
	"password"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

--ブログ
CREATE TABLE IF NOT EXISTS "post" (
	"id"	INTEGER,
	"author_id"	INTEGER NOT NULL,
	"created"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"title"	TEXT NOT NULL,
	"body"	TEXT NOT NULL,
	FOREIGN KEY("author_id") REFERENCES "user"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

--タスク
CREATE TABLE IF NOT EXISTS "task" (
	"連番"	INTEGER,
	"状態"	TEXT NOT NULL DEFAULT '未',
	"所有者"	TEXT NOT NULL,
	"タスク名"	TEXT NOT NULL,
	"重要度"	INTEGER NOT NULL DEFAULT 0,
	"予定日"	TEXT NOT NULL DEFAULT '9999-12-31',
	"タグ"	TEXT NOT NULL,
	"備考"	TEXT NOT NULL,
	"親タスク"	INTEGER NOT NULL DEFAULT 0,
	"追加日時"	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"変更日時"	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"完了日時"	TEXT NOT NULL DEFAULT '',
	"コスト"	INTEGER NOT NULL DEFAULT 0,
	"実コスト"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("連番" AUTOINCREMENT)
);

--ベースデータ
CREATE TABLE IF NOT EXISTS "basedata" (
	"site"	TEXT,
	"identifier"	TEXT,
	"datetime"	TEXT NOT NULL,
	"title"	TEXT NOT NULL,
	"tags"	TEXT NOT NULL,
	"body"	TEXT NOT NULL,
	"jst"	TEXT NOT NULL,
	PRIMARY KEY("site","identifier")
);
CREATE INDEX IF NOT EXISTS "datetimeindex" ON "basedata" (
	"site",
	"datetime"	DESC
);

--キーバリューストア PENDINGリレーショナルDBから取り除く？
CREATE TABLE IF NOT EXISTS "keyvalue" (
	"key"	TEXT NOT NULL,
	"value"	TEXT NOT NULL,
	PRIMARY KEY("key")
);

--キュー
CREATE TABLE IF NOT EXISTS "queue" (
	"serial_number"	INTEGER NOT NULL,
	"reservation_time"	TEXT NOT NULL,
	"queue_type"	TEXT NOT NULL,
	"content"	TEXT NOT NULL,
	"add_time"	TEXT NOT NULL,
	PRIMARY KEY("serial_number" AUTOINCREMENT)
);
INSERT INTO queue (reservation_time, queue_type, content, add_time)
VALUES (strftime('%Y-%m-%d %H:59:59', CURRENT_TIMESTAMP), "backup", "", CURRENT_TIMESTAMP)
