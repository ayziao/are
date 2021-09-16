# are
アレをナニ  
https://github.com/ayziao/are

---
## 目的
記憶の外部化
* 現在:記録を取る
* 過去:記録を見やすくする
* 過去:記録の取り具合を確認する
* 未来:記録を取るための参考情報を得る
* 未来:未来の記憶の外部化としてタスク管理
* 他:記録を失わないようにする

---
## 機能
### 現在:記録を取る
* PCでもモバイルでも取りやすく
* 低速回線でも取りやすく
* テキストの記録
* 画像の記録
* 動画？
* 実行タスクの記録
* 却下タスクの記録


### 過去:記録を見やすくする
* キーワードリンク
* 時系列絞り込み
* タグ絞り込み
* 画像一覧
* 検索
* タスク実行履歴


### 過去:記録の取り具合を確認する
* 投稿数集計 年月日曜時タグ別
* 検索集計 タイトル,任意文字列,タグ
* 実行タスク統計
* 未実行タスク統計


### 未来:記録を取るための参考情報を得る
* SNS連携(外部機能)
* ブックマーク(外部機能)
* スクラップブック(外部機能)


### 未来:未来の記憶の外部化としてタスク管理
いつでもどこでもタスクを入力確認できるように
* タスク一覧


### 他:記録を失わないようにする
* しつこいバックアップ
* 外部サービスへのミラー(外部機能)
* 同システム同士の共有



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
### 開発環境実行
export FLASK_APP=are  
export FLASK_ENV=development  
flask ran  

### テスト
coverage run -m pytest && coverage html  
coverage run -m pytest tests/test_task.py && coverage html  
coverage run -m pytest tests/db && coverage html  

### ドメイン
メインサービスドメイン

	サイト  
		公開
		統計
		検索
	タスク
		表示 検索
		一覧
		アーカイブ
			アーカイブ処理
			履歴
			検索
			統計
	ダッシュボード
		下書き
		サイト管理
		タスク管理

外部ドメイン

	複製散布


共通サブドメイン

	システム
		ストレージ
			リレーショナルデータベース
				sqlite
				PostgreSQL
			キーバリューストア
				RDBに無理やり
				NoSQL？
			ファイル
			オンラインストレージ？

		webアプリケーション
			flask
				URLルーティング

		CLIアプリケーション
			コマンド解析

	サブサービス
		ユーザーアカウント
		ユーザー認証状態管理
		アクセス解析
		キュー処理
		メインサービスドメイン用設定保存領域

	外部サービス
		オーオース
			ツイッター
			マストドン
			ギャゾ

### 構造
構造考

サービス系ドメイン

	ユースケース？コントローラ？
		リポジトリからエンティティを取り出してどうにか

	エンティティ
        辞書で済むものはつくらない？

	リポジトリ
		DBとかファイルとかあれこれしてエンティティ組み立てる

	ブループリント？コントローラ？
		フラスクとのあれこれしてユースケース叩く
		結果をテンプレートへ

	テンプレート
		HTML
		特殊なJSON？


### 書き方
コードには How やり方  
テストコードには What 何を   
コミットログには Why 何故 (ユースケースのメソッドコメントにも書くべき？)  
コードコメントには Why not 何故しないか  


### コミットログの書き方
1行目 😀［サブシステム］やったこと：［種別］何故そうするのかの目的  
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
⚙ 設定  
🚧 動作確認用 開発途中  
🤖 ビルド 補助ツール ライブラリ関連  


例  
✨[タスク管理]タスクアーカイブ:アーカイブするため  
🐜[タスク管理]レート変更で絞り込み変更になってしまっていた  
🎨[タスク管理]よく使う「すぐ」に状態「後」の除外を追加:[使い勝手向上]
🚧[タスク管理/アーカイブ履歴]とりあえず1000件に絞る
📜開発方針考
