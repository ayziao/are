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


def get_likeid(site, search, locale=None):
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
        ' ORDER BY datetime LIMIT 1000;',
        (site, search + "%",)
    ).fetchall()

    return ret


def search(site, search, order=None, locale=None):
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
        (site, "%" + search + "%", "%" + search + "%",)
    ).fetchall()

    return ret


def tagsearch(site, search, order=None, locale=None):
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
        (site, "%#" + search + "%",)
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
        'SELECT title, count(title) as count '
        ' FROM basedata '
        ' WHERE site = ? '
        ' AND (identifier <> title) '
        ' GROUP BY title '
        ' ORDER BY count(title) DESC , title ',
        (site,)
    ).fetchall()
    return ret
