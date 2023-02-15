"""
タスクモジュール

関数定義はフラスクと直接関係ないもの
フラスクブループリントは見えるところに変数化
MVCのコントローラ？
ユースケース？
"""

import datetime
from dateutil.relativedelta import relativedelta

from are.task import _flaskbp
from are.task import _repository

bp = _flaskbp.bp


def restore4tag(db, tag, status, to):
    tag = '% ' + tag + ' %'

    db.execute(
        'UPDATE task SET "状態" = ?, "完了日時" = "", "実績値" = 0 '
        ' WHERE "状態" = ? AND "タグ" LIKE ? ', (to, status, tag))


def アーカイブ(db):
    db.execute(
        'insert into task_archive '
        ' (番号,サイト, 状態, 重要度, タスク名, タグ, 備考, 予測値, 実績値, 親番号,'
        ' 予定日, 完了日, 日時,'
        ' 作成者, 所有者, 対応者) '
        ' select '
        ' 番号, サイト, 状態, 重要度, タスク名, タグ, 備考, 予測値, 実績値, 親番号,'
        ' 予定日, substr(完了日時, 1, 10), 完了日時,'
        ' 作成者, 所有者, 対応者'
        ' from task '
        ' WHERE 完了日時 <> "" '
    )
    db.execute(
        'DELETE FROM task WHERE 完了日時 <> "" '
        ' AND "タグ" NOT LIKE "% 年 %" AND "タグ" NOT LIKE "% 半期 %" AND "タグ" NOT LIKE "%月 %" '
        ' AND "タグ" NOT LIKE "% 週 %" AND "タグ" NOT LIKE "%日 %" AND "タグ" NOT LIKE "% 季 %" '
        ' AND "タグ" NOT LIKE "% 春 %" AND "タグ" NOT LIKE "% 夏 %" AND "タグ" NOT LIKE "% 秋 %" '
        ' AND "タグ" NOT LIKE "% 冬 %" AND "タグ" NOT LIKE "% 常備 %" AND "タグ" NOT LIKE "% 繰り返し %" '
    )
    db.execute(
        ' UPDATE task SET "変更日時" = "完了日時" '
        ' WHERE 完了日時 <> "" '
        ' AND ("タグ" LIKE "% 繰り返し %" OR "タグ" LIKE "% 常備 %") '
    )
    _repository.完了日時消去(db, '')
    return True


def 日次集計(db):
    sql = '''
        SELECT 
            "サイト",
            "状態",
            count(*) as 件数,
            SUM("予測値") as 予想 ,
            SUM("実績値") as 実績 ,
            strftime("%Y-%m-%d", 完了日時) as 完了日
        FROM task
        GROUP BY 
            サイト,
            状態,
            strftime("%Y-%m-%d", 完了日時)
        ORDER by
            状態 DESC,
            strftime("%Y-%m-%d", 完了日時) DESC
        '''
    rows = db.execute(sql).fetchall()

    yesterday = datetime.date.today() + relativedelta(days=-1)

    for r in rows:
        if r['状態'] == '完' and r['完了日'] != yesterday.strftime('%Y-%m-%d'):
            continue

        point = r['予想']
        if r['完了日'] == yesterday.strftime('%Y-%m-%d'):
            point = r['実績']

        db.execute(
            'INSERT INTO "タスク日次集計" ("サイト", "日付", "集計区分" ,"状態", "件数", "ポイント")'
            ' VALUES (?, ?, ?, ?, ?, ?)',
            (r['サイト'], yesterday, '自動', r['状態'], r['件数'], point)
        )

    return rows
