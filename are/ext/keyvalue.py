from are.ext.db import get_ext_db
from json import loads


# サイト別設定取得
def getSitesetting(site):
    db = get_ext_db()
    ret = db.execute(
        'SELECT * FROM keyvalue '
        f' WHERE key = "sitesetting_{site}" '
    ).fetchone()

    return loads(ret["value"])
