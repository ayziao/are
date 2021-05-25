# are
アレをナニ  
https://github.com/ayziao/are

---
## 目的
記録を取る  
記録を見やすくする  
記録の取り具合を確認する
記録を取るための参考情報を得る

---
## 機能
記録を取る
* PCでもモバイルでも取りやすく
* 低速回線でも取りやすく
* しつこいバックアップ

記録を見やすくする
* キーワードリンク
* 時系列絞り込み
* タグ絞り込み

記録の取り具合を確認する
* 投稿数集計 年月日曜時タグ別
* 検索 タイトル,任意文字列,タグ

記録を取るための参考情報を得る
* SNS連携
* ブックマーク
* スクラップブック

---
## インストール
git clone https://github.com/ayziao/are.git  
モジュールのインストール  # fixme  
export FLASK_APP=are  
flask init-db  
flask init-ext_db  
flask ran  

---
## 開発
export FLASK_APP=are  
export FLASK_ENV=development  
flask ran  

### コミットログの書き方
1行目 😀 やったこと：目的  
2行目 空行  
3行目 詳細 補足  

✨ 新機能  
👍 機能改善  
🐜 バグ修正  
♻️ リファクタリング  
🧹 コード整形  
🎨 ユーザーインターフェイス  
💪 パフォーマンス向上  
✅ テスト関連  
📜 ドキュメント  
🚧 動作確認用 開発途中  
🤖 ビルド 補助ツール ライブラリ関連  


###タスクテーブル修正

CREATE TABLE IF NOT EXISTS "task2" (
	"連番"	INTEGER,
	"サイト"	TEXT NOT NULL DEFAULT '',
	"状態"	TEXT NOT NULL DEFAULT '未',
	"重要度"	INTEGER NOT NULL DEFAULT 0,
	"タスク名"	TEXT NOT NULL,
	"タグ"	TEXT NOT NULL DEFAULT '',
	"備考"	TEXT NOT NULL DEFAULT '',
	"コスト"   INTEGER NOT NULL DEFAULT 0,
	"実コスト"	INTEGER NOT NULL DEFAULT 0,
	"親タスク"	INTEGER NOT NULL DEFAULT 0,
	"追加日時"	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"変更日時"	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"予定日"	TEXT NOT NULL DEFAULT '9999-12-31',
	"完了日時"	TEXT NOT NULL DEFAULT '',
	"作成者"	TEXT NOT NULL,
	"所有者"	TEXT NOT NULL,
	PRIMARY KEY("連番" AUTOINCREMENT)
);

insert into task2(状態, 重要度, タスク名, タグ, 備考, コスト, 実コスト, 親タスク, 追加日時, 変更日時, 予定日, 完了日時, 作成者, 所有者) 
select 状態, 重要度, タスク名, タグ, 備考, コスト, 実コスト, 親タスク, 追加日時, 変更日時, 予定日, 完了日時, '', 所有者  from task;

DROP TABLE task;
ALTER TABLE task2 RENAME TO task;


