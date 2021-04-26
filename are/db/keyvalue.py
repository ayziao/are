from are.db import get_db
from json import loads


# サイト別設定取得
def getSitesetting(site):
    db = get_db()
    ret = db.execute(
        'SELECT * FROM keyvalue '
        f' WHERE key = "sitesetting_{site}" '
    ).fetchone()

    return loads(ret["value"])
