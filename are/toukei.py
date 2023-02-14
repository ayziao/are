from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, url_for

from are.db import get_db

bp = Blueprint('toukei', __name__, url_prefix='/x/toukei')


@bp.route('')
def index():
    return 'toukei index'


@bp.route('/daycount')
def daycount():
    db = get_db()

    tag_where = ''
    body_where = ''
    site = request.args.get('site', 'test')
    tag = request.args.get('tag', '')
    search_body = request.args.get('search_body', '')

    param = [site]
    if tag:
        tag_where = "AND (tags like ? or tags like ?)"
        param.extend([f"% {tag} %", f"% {tag}:%"])
    if search_body:
        body_where = "AND body LIKE ?"
        param.append(f"%{search_body}%")

    sql = f"""
    SELECT
        DATE("datetime") as "date" ,
        COUNT(*) as "count"
    FROM basedata
    WHERE site = ?
        {tag_where}
        {body_where}
    GROUP BY DATE("datetime")
    ORDER BY DATE("datetime") DESC
    LIMIT ?
    """
    limit = 1000  # PENDING ページングする？
    param.append(limit)
    counts = db.execute(sql, param).fetchall()
    tags = tagcount()

    return render_template('toukei/count.html', counts=counts, tags=tags, path='daycount', site=site)


@bp.route('/monthcount')
def monthcount():
    db = get_db()

    tag_where = ''
    body_where = ''
    site = request.args.get('site', 'test')
    tag = request.args.get('tag', '')
    search_body = request.args.get('search_body', '')

    param = [site]
    if tag:
        tag_where = "AND (tags like ? or tags like ?)"
        param.extend([f"% {tag} %", f"% {tag}:%"])
    if search_body:
        body_where = "AND body LIKE ?"
        param.append(f"%{search_body}%")

    date = 'strftime(\'%Y-%m\',"datetime")'

    sql = f"""
        SELECT 
            {date} as "date",
            COUNT(*) as "count"
        FROM basedata
        WHERE site = ?
            {tag_where}
            {body_where}
        GROUP BY {date}
        ORDER BY {date}
        LIMIT ?
        """
    limit = 1000  # PENDING ページングする？
    param.append(limit)
    counts = db.execute(sql, param).fetchall()

    tags = tagcount()

    return render_template('toukei/count.html', counts=counts, tags=tags, path='monthcount', site=site)


@bp.route('/weekcount')
def weekcount():
    db = get_db()

    tag_where = ''
    body_where = ''
    past_where = ''
    site = request.args.get('site', 'test')
    tag = request.args.get('tag', '')
    search_body = request.args.get('search_body', '')
    dt = datetime.now()
    past_days = 0

    param = [site]
    if tag:
        tag_where = "AND (tags like ? or tags like ?)"
        param.extend([f"% {tag} %", f"% {tag}:%"])
    if search_body:
        body_where = "AND body LIKE ?"
        param.append(f"%{search_body}%")
    if isinstance(past_days, int) and past_days > 0:
        dt -= timedelta(days=past_days)
        past_where = 'AND "datetime" > ' + "'" + dt.strftime("%Y-%m-%d %H:%M:%S") + "'"

    date = 'strftime(\'%w\',"datetime")'
    week_fix = 0

    sql = f"""
        SELECT 
            {date} as "date",
            COUNT(*) as "count"
        FROM basedata
        WHERE site = ?
            {tag_where}
            {body_where}
            {past_where}
        GROUP BY {date}
        ORDER BY {date}
        LIMIT ?
        """
    limit = 1000  # PENDING ページングする？
    param.append(limit)
    ret = db.execute(sql, param).fetchall()

    ret_week = []

    for i in range(7):
        if len(ret) > 0 and (int(ret[0]["date"]) - week_fix) == i:
            pop = ret.pop(0)
            ret_week.append({'date': str(i), 'count': pop["count"]})
        else:
            ret_week.append({'date': str(i), 'count': 0})
    tags = tagcount()

    return render_template('toukei/count.html', counts=ret_week, tags=tags, path='weekcount', site=site)


@bp.route('/hourcount')
def hourcount():
    db = get_db()

    site = request.args.get('site', 'test')
    tag = request.args.get('tag', '')
    search_body = request.args.get('search_body', '')
    past_days = int(request.args.get('past_days', '0'))

    tag_where = ''
    body_where = ''
    past_where = ''
    dt = datetime.now()
    param = [site]  # type: List[Union[str, int]]

    if tag != '':
        tag_where = "AND (tags like ? or tags like ?)"
        param.extend([f"% {tag} %", f"% {tag}:%"])
    if search_body != '':
        body_where = "AND body LIKE ?"
        param.append(f"%{search_body}%")
    if isinstance(past_days, int) and past_days > 0:
        dt -= timedelta(days=past_days)
        past_where = 'AND "datetime" > ' + "'" + dt.strftime("%Y-%m-%d %H:%M:%S") + "'"
    date = 'strftime(\'%H\',"datetime")'

    sql = f"""
    SELECT 
        {date} as "date",
        COUNT(*) as "count"
    FROM basedata
    WHERE site = ?
        {tag_where}
        {body_where}
        {past_where}
    GROUP BY {date}
    ORDER BY {date}
    """
    ret = db.execute(sql, param).fetchall()
    tags = tagcount()

    return render_template('toukei/count.html', counts=ret, tags=tags, path='hourcount', site=site)


def tagcount():
    db = get_db()
    site = request.args.get('site', 'test')

    param = [site, site]

    tags = "replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(" \
           "replace(tags,'0',''),'1',''),'2',''),'3',''),'4',''),'5',''),'6',''),'7',''),'8',''),'9',''),':','')"
    sql = f"""
        SELECT
            ' ' as "tags",
            COUNT(*) as "count"
        FROM basedata
        WHERE
            site = ?
        UNION ALL
        SELECT
            {tags} as "tags",
            COUNT(*) as "count"
        FROM basedata
        WHERE
            site = ?
        GROUP BY {tags}
        ORDER BY COUNT(*) DESC
        """
    ret = db.execute(sql, param).fetchall()

    count_sum = {}
    for row in ret:
        tags = row["tags"].strip().replace('\t', ' ').split(' ')
        for tag_ in tags:
            if tag_ not in count_sum.keys():
                count_sum[tag_] = row["count"]
            else:
                count_sum[tag_] += row["count"]

    result = []
    for k, v in sorted(count_sum.items(), key=lambda x: -x[1]):
        result.append({'tag': k, 'count': v})

    return result
