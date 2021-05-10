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
