from are.db import get_db
from json import loads


# サイト別設定取得
def get_sitesetting(site):
    db = get_db()
    ret = None
    _data = db.execute(
        'SELECT * FROM keyvalue '
        f' WHERE key = "sitesetting_{site}" '
    ).fetchone()
    if _data:
        ret = loads(_data['value'])

    return ret


def get_task_colors():
    sql = '''
        SELECT * FROM keyvalue
        WHERE key Like "sitesetting%"
    '''
    rows = get_db().execute(sql).fetchall()
    ret = {}
    for item in rows:
        value = loads(item['value'])
        if 'task_border_color' in value:
            ret[item['key'].replace("sitesetting_", "")] = value['task_border_color']

    return ret
