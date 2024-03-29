from are.db import get_db


def create(db, site, identifier, dtstr, title, tags, body, jpstr):
    db.execute(
        'INSERT INTO basedata (site, identifier, datetime, title, tags, body ,jst)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?)',
        (site, identifier, dtstr, title, tags, body, jpstr)
    )


def get_one(site, name, locale=None):
    db = get_db()
    if locale == 'utc' or locale == 'utcP9':
        datatimehenkan = ''
    else:
        datatimehenkan = 'datetime(datetime, "+9 hours") as '

    ret = db.execute(
        f'SELECT identifier, title, body, tags, jst, datetime as utc, {datatimehenkan}datetime ,'
        ' substr("0"||(strftime("%H", datetime)+9),-2,2) || strftime(":%M:%S", datetime) as utcP9time '
        ' FROM basedata '
        ' WHERE site = ? AND (identifier = ? OR title = ?)'
        ' ORDER BY datetime DESC LIMIT 1;',
        (site, name, name,)
    ).fetchone()

    return ret


def get_timeline(site, locale=None):
    db = get_db()
    if locale == 'utc' or locale == 'utcP9':
        datatimehenkan = ''
    else:
        datatimehenkan = 'datetime(datetime, "+9 hours") as '

    sql = 'SELECT identifier, title, body, tags, jst, ' \
          f' {datatimehenkan}datetime ,' \
          ' datetime as utc,' \
          ' substr("0"||(strftime("%H", datetime)+9),-2,2) || strftime(":%M:%S", datetime) as utcP9time ' \
          ' FROM basedata ' \
          ' WHERE site = ? ' \
          ' ORDER BY identifier DESC LIMIT 100;'
    return db.execute(sql, (site,)).fetchall()


def get_likeid(site, search_, locale=None, order='ASC'):
    db = get_db()
    if locale == 'utc' or locale == 'utcP9':
        datatimehenkan = ''
    else:
        datatimehenkan = 'datetime(datetime, "+9 hours") as '

    ret = db.execute(
        f'SELECT identifier, title, body, tags, jst, datetime as utc, {datatimehenkan}datetime ,'
        ' substr("0"||(strftime("%H", datetime)+9),-2,2) || strftime(":%M:%S", datetime) as utcP9time '
        ' FROM basedata '
        ' WHERE site = ? AND identifier LIKE ? '
        f' ORDER BY datetime {order} LIMIT 1000;',
        (site, search_ + "%",)
    ).fetchall()

    return ret


def search(site, search_, order=None, locale=None):
    db = get_db()
    if locale == 'utc' or locale == 'utcP9':
        datatimehenkan = ''
    else:
        datatimehenkan = 'datetime(datetime, "+9 hours") as '

    if order != 'ASC':
        order = 'DESC'

    ret = db.execute(
        f'SELECT identifier, title, body, tags, jst, datetime as utc, {datatimehenkan}datetime ,'
        ' substr("0"||(strftime("%H", datetime)+9),-2,2) || strftime(":%M:%S", datetime) as utcP9time '
        ' FROM basedata '
        ' WHERE site = ? '
        ' AND ( body LIKE ? OR title LIKE ? ) '
        ' AND tags NOT LIKE "% gyazo_posted %" '
        ' ORDER BY datetime ' + order + ' LIMIT 100;',
        (site, "%" + search_ + "%", "%" + search_ + "%",)
    ).fetchall()

    return ret


def tagsearch(site, search_, order=None, locale=None):
    db = get_db()
    if locale == 'utc' or locale == 'utcP9':
        datatimehenkan = ''
    else:
        datatimehenkan = 'datetime(datetime, "+9 hours") as '

    if order != 'ASC':
        order = 'DESC'

    ret = db.execute(
        f'SELECT identifier, title, body, tags, jst, datetime as utc, {datatimehenkan}datetime ,'
        ' substr("0"||(strftime("%H", datetime)+9),-2,2) || strftime(":%M:%S", datetime) as utcP9time '
        ' FROM basedata '
        ' WHERE site = ? AND tags LIKE ? AND tags NOT LIKE "% gyazo_posted %" '
        ' ORDER BY datetime ' + order + ' LIMIT 100;',
        (site, "%#" + search_ + "%",)
    ).fetchall()

    return ret


def get_titlearray(site):
    db = get_db()
    titles = []
    ret = db.execute(
        'SELECT DISTINCT title FROM basedata '
        ' WHERE site = ? '
        ' AND (identifier <> title)'
        ' ORDER BY length(title) DESC;',
        (site,)
    ).fetchall()
    for row in ret:
        titles.append(row['title'])
    return titles


def get_titlecount(site):
    db = get_db()
    ret = db.execute(
        'SELECT title, count(title) as count ,'
        '(SELECT count(*) FROM basedata '
        ' WHERE site = ?'
        ' AND ( body LIKE "%" || b1.title || "%" OR title LIKE "%" || b1.title || "%" ) '
        ') as searchcount'
        ' FROM basedata as b1'
        ' WHERE site = ? '
        ' AND (identifier <> title) '
        ' GROUP BY title '
        ' ORDER BY count(title) DESC , title ',
        (site, site)
    ).fetchall()
    return ret


def next_identifier(site, date):
    db = get_db()
    ret = db.execute(
        ' SELECT identifier '
        ' FROM basedata '
        ' WHERE site = ? '
        ' AND tags NOT LIKE "% gyazo_posted %" '
        ' AND identifier > ? '
        ' ORDER BY "identifier" ASC LIMIT 1 ',
        (site, f"{date}999999999999")
    ).fetchone()

    if ret:
        return ret['identifier']
    else:
        return ''


def prev_identifier(site, date):
    db = get_db()
    ret = db.execute(
        ' SELECT identifier '
        ' FROM basedata '
        ' WHERE site = ? '
        ' AND tags NOT LIKE "% gyazo_posted %" '
        ' AND identifier < ? '
        ' ORDER BY "identifier" DESC LIMIT 1 ',
        (site, f"{date}000000000000")
    ).fetchone()

    if ret:
        return ret['identifier']
    else:
        return ''
