import datetime
from dateutil.relativedelta import relativedelta

from are.task import _flaskbp

bp = _flaskbp.bp


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
