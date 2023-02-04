"""
フラスクブループリント タスク

web周り対応
MVCのコントローラ？
ユースケース？
"""

import re
from flask import Blueprint, render_template, request, redirect, flash, url_for, abort, \
    g  # , current_app
from are.db import get_db, keyvalue
from are.task import _repository
from are.auth import login_required
from are import task

bp = Blueprint('task', __name__, template_folder='templates', url_prefix='/x/task')


@bp.route('')
def index():
    args = get_args()

    if len(request.args) == 0:
        return today()

    colors = keyvalue.get_task_colors()

    change = request.args.get('change', '')
    if change:
        args[change] = request.args.get('to', '')
        return redirect(url_for('task.index', **args))

    addtag = request.args.get('addtag', '')
    if addtag:
        tagall = args['tag'].split()
        if addtag not in tagall:
            tagall.append(addtag)
            args['tag'] = ' '.join(tagall)
        return redirect(url_for('task.index', **args))

    deltag = request.args.get('deltag', '')
    if deltag:
        tagall = args['tag'].split()
        tagall.remove(deltag)
        args['tag'] = ' '.join(tagall)
        return redirect(url_for('task.index', **args))

    hidetag = request.args.get('hidetag', '')
    if hidetag:
        tagall = args['tag'].split()
        tagall = ['-' + hidetag if tag == hidetag else tag for tag in tagall]
        args['tag'] = ' '.join(tagall)
        return redirect(url_for('task.index', **args))

    showtag = request.args.get('showtag', '')
    if showtag:
        tagall = args['tag'].split()
        tagall = [showtag if tag == '-' + showtag else tag for tag in tagall]
        args['tag'] = ' '.join(tagall)
        return redirect(url_for('task.index', **args))

    if 'notag' in request.args:
        args['notag'] = ''

    if 'nosite' in request.args:
        args['nosite'] = ''

    if "".join(args.values()) == "":
        return today()

    sites = _repository.get_sites()
    rows = _repository.get_list(args)

    joutai = ''
    tags = {}
    tasks = {}
    for item in rows:
        tags[item['番号']] = item['タグ'].split()
        if item["状態"] == joutai:
            tasks[item['状態']].append(item)
        else:
            joutai = item['状態']
            tasks[item['状態']] = []
            tasks[item['状態']].append(item)

    return render_template('index.html', sites=sites, tasks=tasks, tags=tags, search=args, colors=colors, taglink=_タグリンク())

@bp.route('/all')
def all():
    args = get_args()
    args["all"] = "yes"

    colors = keyvalue.get_task_colors()
    sites = _repository.get_sites()
    rows = _repository.get_list(args)

    joutai = ''
    tags = {}
    tasks = {}
    for item in rows:
        tags[item['番号']] = item['タグ'].split()
        if item["状態"] == joutai:
            tasks[item['状態']].append(item)
        else:
            joutai = item['状態']
            tasks[item['状態']] = []
            tasks[item['状態']].append(item)

    return render_template('index.html', sites=sites, tasks=tasks, tags=tags, search=args, colors=colors, taglink=_タグリンク())


@bp.route('/today')
def today():
    args = get_args()

    colors = keyvalue.get_task_colors()
    sites = _repository.get_sites()
    rows = _repository.本日分取得(args)

    joutai = ''
    tags = {}
    tasks = {}
    for item in rows:
        tags[item['番号']] = item['タグ'].split()
        if item["状態"] == joutai:
            tasks[item['状態']].append(item)
        else:
            joutai = item['状態']
            tasks[item['状態']] = []
            tasks[item['状態']].append(item)

    return render_template('index.html', sites=sites, tasks=tasks, tags=tags, search=args, colors=colors, taglink=_タグリンク())


@bp.route('/create', methods=('GET', 'POST'))
def create():
    default = {
        'tag': request.args.get('tag', ''),
        'cost': request.args.get('cost', 0),
        'rate': int(request.args.get('rate', '0').strip('over').strip('under')),
        'site': request.args.get('site', ''),
        'owner': request.args.get('owner', '未')
    }
    if not default["owner"]:
        default["owner"] = '未'

    if request.method == 'POST':
        title = request.form['title']
        rate = int(request.form['rate'].strip('over').strip('under')) if request.form['rate'] else default['rate']
        cost = request.form['cost'] if request.form['cost'] else default['cost']
        tag = ' ' + request.form['tag'].strip() + ' '
        body = request.form['body']

        site = request.form['site'] if request.form['site'] else default['site']
        owner = request.form['owner'] if request.form['owner'] else default['owner']

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            _repository.create(db, g.user['id'], owner, site, rate, cost, title, tag, body)
            db.commit()
            return redirect(url_for('task.index', tag=tag.strip()))

    return render_template('create.html', default=default)


def get_task(number):
    item = _repository.get_one(number)
    if item is None:
        abort(404, "task id {0} doesn't exist.".format(number))

    return item


def get_args():
    args = {
        'status': request.args.get('status', ''),
        'owner': request.args.get('owner', ''),
        'rate': request.args.get('rate', ''),
        'cost': request.args.get('cost', ''),
        'tag1st': request.args.get('tag1st', ''),
        'tag': request.args.get('tag', ''),
        'sort': request.args.get('sort', ''),
        'cycle': request.args.get('cycle', ''),
        'site': request.args.get('site', ''),
        'title': request.args.get('title', ''),
        'all': request.args.get('all', '')}
    return args


@bp.route('/<int:number>/update', methods=('GET', 'POST'))
# @login_required
def update(number):
    task = get_task(number)
    fi = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

    if request.method == 'POST':
        status = request.form['status']
        title = request.form['title']
        tag = ' ' + request.form['tag'].strip() + ' '
        body = request.form['body']
        rate = request.form['rate']
        cost = request.form['cost']
        actual = request.form['actual']

        # site = ' ' + request.form['site'].strip() + ' '
        site = request.form['site']
        owner = request.form['owner']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE task SET '
                ' "状態" = ?, "所有者" = ?, "サイト" = ?, "タスク名" = ?, "タグ" = ?, "備考" = ?, "予測値" = ?, "実績値" = ?, "重要度" = ?, '
                ' "変更日時" = datetime("now")'
                ' WHERE "番号" = ?',
                (status, owner, site, title, tag, body, cost, actual, rate, number)
            )
            db.commit()
            return redirect(url_for('task.index', tag=tag.strip()))

    return render_template('update.html', task=task, fi=fi)


@bp.route('/<int:number>/delete', methods=('POST',))
@login_required
def delete(number):
    get_task(number)
    db = get_db()
    db.execute('DELETE FROM task WHERE "番号" = ?', (number,))
    db.commit()
    return redirect(url_for('task.index'))


@bp.route('/<int:number>/costup', methods=('GET',))
def costup(number):
    args = get_args()

    fi = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

    task = get_task(number)
    if task['状態'] == '完':
        _対象 = '実績値'
    else:
        _対象 = '予測値'
    if task[_対象] < 89:
        aa = fi.index(task[_対象])
        db = get_db()
        db.execute(
            f'UPDATE task SET "{_対象}" = ? , "変更日時" = datetime("now")'
            ' WHERE "番号" = ?', (fi[aa + 1], number))
        db.commit()

    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/rateup', methods=('GET',))
def rateup(number):
    args = get_args()
    item = get_task(number)
    if item['重要度'] < 5:
        db = get_db()
        db.execute(
            'UPDATE task SET "重要度" = "重要度" + 1 ,"変更日時" = datetime("now") '
            ' WHERE "番号" = ?', (number,))
        db.commit()

        if args['rate'].isnumeric():
            args['rate'] = int(args['rate']) + 1

    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/ratedown', methods=('GET',))
def ratedown(number):
    args = get_args()
    item = get_task(number)
    if item['重要度'] > 0:
        db = get_db()
        db.execute(
            'UPDATE task SET "重要度" = "重要度" - 1 , "変更日時" = datetime("now") '
            ' WHERE "番号" = ?', (number,))
        db.commit()

        if args['rate'].isnumeric():
            args['rate'] = int(args['rate']) - 1

    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/rateto', methods=('GET',))
def rateto(number):
    args = get_args()
    change = int(request.args.get('change', -1))
    item = get_task(number)
    if 0 <= change != item['重要度']:
        db = get_db()
        db.execute(
            'UPDATE task SET "重要度" = ? , "変更日時" = datetime("now")'
            ' WHERE "番号" = ?', (change, number))
        db.commit()

    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/done', methods=('GET',))
def done(number):
    args = get_args()

    db = get_db()
    db.execute(
        'UPDATE task SET "状態" = "完" , "完了日時" = datetime("now") ,"実績値" = "予測値"'
        ' WHERE "番号" = ?', (number,))
    db.commit()
    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/doing', methods=('GET',))
def doing(number):
    args = get_args()

    item = _repository.get_one(number)

    if item['状態'] == '！':
        _状態 = '！！'
    else:
        _状態 = '！'

    db = get_db()
    db.execute(
        'UPDATE task SET "状態" = ? , "完了日時" = "" , "変更日時" = datetime("now") ,"実績値" = 0 '
        ' WHERE "番号" = ?',
        (_状態, number)
    )
    db.commit()
    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/next', methods=('GET',))
def next(number):
    args = get_args()

    db = get_db()
    db.execute(
        'UPDATE task SET "状態" = "次" , "完了日時"  = "" , "変更日時" = datetime("now") ,"実績値" = 0 '
        ' WHERE "番号" = ?', (number,))
    db.commit()
    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/later', methods=('GET',))
def later(number):
    args = get_args()

    db = get_db()
    db.execute(
        'UPDATE task SET "状態" = "後" , "完了日時"  = "" , "変更日時" = datetime("now") ,"実績値" = 0 '
        ' WHERE "番号" = ?', (number,))
    db.commit()
    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/restore', methods=('GET',))
def restore(number):
    args = get_args()

    db = get_db()
    db.execute(
        'UPDATE task SET "状態" = "未" , "完了日時" = "" , "変更日時" = datetime("now") ,"実績値" = 0 '
        ' WHERE "番号" = ?', (number,))
    db.commit()
    return redirect(url_for('task.index', **args))


@bp.route('/restore', methods=('GET',))
def restore4tag():
    tag = request.args.get('tag', '')
    if tag == '':
        return redirect(url_for('task.集計'))

    status = request.args.get('status', '完')
    to = request.args.get('to', '未')

    db = get_db()
    task.restore4tag(db, tag, status, to)
    db.commit()

    return redirect(url_for('task.集計'))


@bp.route('/linklist', methods=('GET',))
def linklist():
    return render_template('link.html')


@bp.route('/tag1stlist', methods=('GET',))
def tag1stlist():
    db = get_db()

    cycle = '年,月,週,日,半期,季'.split(',')
    result = []

    wh = ' WHERE '
    for i in cycle:
        wh += f'タグ LIKE " {i} %" OR '
    wh = wh[:-3]
    ret = db.execute(
        'SELECT タグ, '
        ' sum(CASE WHEN 状態 = "！" OR 状態 = "！！" THEN 1 ELSE 0 END) as 処理中件数 ,'
        ' sum(CASE WHEN 状態 = "未" THEN 1 ELSE 0 END) as 未完了件数 ,'
        ' sum(CASE WHEN 状態 = "完" THEN 1 ELSE 0 END) as 完了件数 ,'
        ' sum(CASE WHEN 状態 = "保留" THEN 1 ELSE 0 END) as 保留件数 ,'
        ' count(タグ) as 件数'
        ' FROM task '
        f'{wh}'
        ' GROUP BY タグ '
    ).fetchall()

    count_sum = {}
    for row in ret:
        tag_ = row['タグ'].strip().split(' ')[0]
        if tag_ not in count_sum.keys():
            count_sum[tag_] = row['件数']
        else:
            count_sum[tag_] += row['件数']
    for k, v in sorted(count_sum.items(), key=lambda x: -x[1]):
        result.append({'タグ': k, '件数': v})

    wh = ' WHERE '
    for i in cycle:
        wh += f'タグ NOT LIKE " {i} %" AND '
    wh = wh[:-4]
    ret = db.execute(
        'SELECT タグ, '
        ' sum(CASE WHEN 状態 = "！" OR 状態 = "！！" THEN 1 ELSE 0 END) as 処理中件数 ,'
        ' sum(CASE WHEN 状態 = "未" THEN 1 ELSE 0 END) as 未完了件数 ,'
        ' sum(CASE WHEN 状態 = "完" THEN 1 ELSE 0 END) as 完了件数 ,'
        ' sum(CASE WHEN 状態 = "保留" THEN 1 ELSE 0 END) as 保留件数 ,'
        ' count(タグ) as 件数'
        ' FROM task '
        f'{wh}'
        ' GROUP BY タグ '
    ).fetchall()

    count_sum = {}
    for row in ret:
        tag_ = row['タグ'].strip().split(' ')[0]
        if tag_ not in count_sum.keys():
            count_sum[tag_] = row['件数']
        else:
            count_sum[tag_] += row['件数']

    for k, v in sorted(count_sum.items(), key=lambda x: -x[1]):
        result.append({'タグ': k, '件数': v})

    return render_template('list.html', list=result, type='第一タグ')


@bp.route('/taglist', methods=('GET',))
def taglist():
    db = get_db()

    wh = 'WHERE 状態 != "特殊な状態" '
    sql = f'''
    SELECT タグ, count(タグ) as 件数
    FROM task
    {wh}
    GROUP BY タグ
    '''
    # print(sql)
    ret = db.execute(sql).fetchall()

    count_sum = {}
    for row in ret:
        tags = row['タグ'].strip().split(' ')
        for tag_ in tags:
            if tag_ not in count_sum.keys():
                count_sum[tag_] = row['件数']
            else:
                count_sum[tag_] += row['件数']

    # cycle = '年,月,週,日,半期,季,繰り返し'.split(',')
    result = []
    for k, v in sorted(count_sum.items(), key=lambda x: -x[1]):
        result.append({'タグ': k, '件数': v})

    return render_template('list.html', list=result, type='タグ')


@bp.route('/ownerlist', methods=('GET',))
def ownerlist():
    db = get_db()
    ret = db.execute(
        'SELECT 所有者, count(所有者) as 件数, "定期" as cycle '
        ' FROM task '
        ' WHERE "所有者" = "年" OR "所有者" = "月" OR "所有者" = "週" OR "所有者" = "日" OR "所有者" = "半期" OR "所有者" = "季" OR "所有者" = "寝" '
        ' GROUP BY 所有者 '
        'UNION '
        'SELECT 所有者, count(所有者) as 件数 , "単発" as cycle '
        ' FROM task '
        ' WHERE "所有者" <> "年" AND "所有者" <> "月" AND "所有者" <> "週" AND "所有者" <> "日" AND "所有者" <> "半期" AND "所有者" <> "季" AND "所有者" <> "寝" '
        ' GROUP BY 所有者 '
        'ORDER BY cycle  DESC, 件数 DESC '
    ).fetchall()
    return render_template('list.html', list=ret, type='所有者')


@bp.route('/ratelist', methods=('GET',))
def ratelist():
    db = get_db()
    sql = '''
        SELECT 重要度 as 重要度,
        CASE WHEN  重要度 = 5 THEN "★★★★★"
             WHEN  重要度 = 4 THEN "★★★★☆"
             WHEN  重要度 = 3 THEN "★★★☆☆"
             WHEN  重要度 = 2 THEN "★★☆☆☆"
             WHEN  重要度 = 1 THEN "★☆☆☆☆"
             ELSE "☆☆☆☆☆" END as 星,
        sum(CASE WHEN 状態 = "！" OR 状態 = "！！" THEN 1 ELSE 0 END) as 処理中件数 ,
        sum(CASE WHEN 状態 = "未" THEN 1 ELSE 0 END) as 未完了件数 ,
        sum(CASE WHEN 状態 = '完' THEN 1 ELSE 0 END) as 完了件数,
        sum(CASE WHEN 状態 = '保留' THEN 1 ELSE 0 END) as 保留件数,
        count(重要度) as 件数,
        sum(実績値) as 実績値, sum(予測値) as 予測値
        FROM task
        GROUP BY 重要度
        ORDER BY 重要度 DESC
    '''
    # print(sql)
    ret = db.execute(sql).fetchall()
    return render_template('list.html', list=ret, type='重要度')


@bp.route('/pointlist', methods=('GET',))
def pointlist():
    db = get_db()
    ret = db.execute(
        'SELECT 予測値, '
        ' sum(CASE WHEN 状態 = "！" OR 状態 = "！！" THEN 1 ELSE 0 END) as 処理中件数 ,'
        ' sum(CASE WHEN 状態 = "未" THEN 1 ELSE 0 END) as 未完了件数 ,'
        ' sum(CASE WHEN 状態 = "完" THEN 1 ELSE 0 END) as 完了件数 ,'
        ' sum(CASE WHEN 状態 = "保留" THEN 1 ELSE 0 END) as 保留件数 ,'
        ' count(予測値) as 件数 '
        ' FROM task '
        ' GROUP BY 予測値 '
        ' ORDER BY 予測値 DESC '
    ).fetchall()
    return render_template('list.html', list=ret, type='ポイント')


@bp.route('/cyclelist', methods=('GET',))
def cyclelist():
    db = get_db()
    ret = db.execute(
        'SELECT "単発" as name, "none" as cycle, count(*) as 件数,'
        ' sum(CASE WHEN 状態 = "！" OR 状態 = "！！" THEN 1 ELSE 0 END) as 処理中件数 ,'
        ' sum(CASE WHEN 状態 = "未" THEN 1 ELSE 0 END) as 未完了件数 ,'
        ' sum(CASE WHEN 状態 = "完" THEN 1 ELSE 0 END) as 完了件数 ,'
        ' sum(CASE WHEN 状態 = "保留" THEN 1 ELSE 0 END) as 保留件数 ,'
        ' sum(実績値) as 実績値, sum(予測値) as 予測値 '
        ' FROM task '
        ' WHERE "タグ" NOT LIKE "% 年 %" AND "タグ" NOT LIKE "% 月 %" AND "タグ" NOT LIKE "% 週 %" '
        '   AND "タグ" NOT LIKE "% 日 %" AND "タグ" NOT LIKE "% 寝 %" AND "タグ" NOT LIKE "% 食 %" '
        '   AND "タグ" NOT LIKE "% 常備 %" AND "タグ" NOT LIKE "% 繰り返し %" '
        ' UNION '
        ' SELECT "定期" as name, "routine" as cycle, count(*) as 件数,'
        ' sum(CASE WHEN 状態 = "！" OR 状態 = "！！" THEN 1 ELSE 0 END) as 処理中件数 ,'
        ' sum(CASE WHEN 状態 = "未" THEN 1 ELSE 0 END) as 未完了件数 ,'
        ' sum(CASE WHEN 状態 = "完" THEN 1 ELSE 0 END) as 完了件数 ,'
        ' sum(CASE WHEN 状態 = "保留" THEN 1 ELSE 0 END) as 保留件数, '
        ' sum(実績値) as 実績値, sum(予測値) as 予測値 '
        ' FROM task '
        ' WHERE ("タグ" LIKE "% 年 %" OR "タグ" LIKE "% 月 %" OR "タグ" LIKE "% 週 %" OR '
        '        "タグ" LIKE "% 日 %" OR "タグ" LIKE "% 寝 %" OR "タグ" LIKE "% 食 %")'
        ' UNION '
        ' SELECT "不定" as name, "randomly" as cycle, count(*) as 件数, '
        ' sum(CASE WHEN 状態 = "！" OR 状態 = "！！" THEN 1 ELSE 0 END) as 処理中件数 ,'
        ' sum(CASE WHEN 状態 = "未" THEN 1 ELSE 0 END) as 未完了件数 ,'
        ' sum(CASE WHEN 状態 = "完" THEN 1 ELSE 0 END) as 完了件数 ,'
        ' sum(CASE WHEN 状態 = "保留" THEN 1 ELSE 0 END) as 保留件数, '
        ' sum(実績値) as 実績値, sum(予測値) as 予測値 '
        ' FROM task '
        ' WHERE ("タグ" LIKE "% 繰り返し %" OR "タグ" LIKE "% 常備 %")'
    ).fetchall()
    return render_template('list.html', list=ret, type='サイクル')


@bp.route('/statuslist', methods=('GET',))
def statuslist():
    db = get_db()
    ret = db.execute(
        'SELECT 状態, '
        ' count(予測値) as 件数, '
        ' sum(実績値) as 実績値, '
        ' sum(予測値) as 予測値 '
        ' FROM task '
        ' GROUP BY 状態 '
        ' ORDER BY 状態 DESC '
    ).fetchall()
    return render_template('list.html', list=ret, type='状態')


@bp.route('/sitelist', methods=('GET',))
def sitelist():
    db = get_db()
    ret = db.execute(
        'SELECT サイト, '
        ' count(予測値) as 件数, '
        ' sum(実績値) as 実績値, '
        ' sum(予測値) as 予測値 '
        ' FROM task '
        ' GROUP BY サイト '
        ' ORDER BY サイト DESC '
    ).fetchall()
    return render_template('list.html', list=ret, type='サイト')


@bp.route('/archive', methods=('GET',))
def archive():
    db = get_db()
    task.アーカイブ(db)
    db.commit()
    return redirect(url_for('task.集計'))


@bp.route('/archiveupdate', methods=('GET',))
def archiveupdate():
    return 'archiveupdate'


@bp.route('/archivecostup', methods=('GET',))
def archivecostup():
    return 'archivecostup'


@bp.route('/history', methods=('GET',))
def history():
    args = get_args()

    change = request.args.get('change', '')
    if change:
        args[change] = request.args.get('to', '')
        return redirect(url_for('task.history', **args))

    addtag = request.args.get('addtag', '')
    if addtag:
        tagall = args['tag'].split()
        if addtag not in tagall:
            tagall.append(addtag)
            args['tag'] = ' '.join(tagall)
        return redirect(url_for('task.history', **args))

    deltag = request.args.get('deltag', '')
    if deltag:
        tagall = args['tag'].split()
        tagall.remove(deltag)
        args['tag'] = ' '.join(tagall)
        return redirect(url_for('task.history', **args))

    hidetag = request.args.get('hidetag', '')
    if hidetag:
        tagall = args['tag'].split()
        tagall = ['-' + hidetag if tag == hidetag else tag for tag in tagall]
        args['tag'] = ' '.join(tagall)
        return redirect(url_for('task.index', **args))

    showtag = request.args.get('showtag', '')
    if showtag:
        tagall = args['tag'].split()
        tagall = [showtag if tag == '-' + showtag else tag for tag in tagall]
        args['tag'] = ' '.join(tagall)
        return redirect(url_for('task.history', **args))

    if 'notag' in request.args:
        args['notag'] = ''

    where = ' WHERE "状態" <> "特殊な状態"'

    if args['status']:
        if args['status'][0] == '-':
            where += ' AND "状態" <> "' + args['status'][1:] + '" '
        else:
            where += ' AND "状態" = "' + args['status'] + '" '
    if args['owner']:
        if args['owner'][0] == '-':
            where += ' AND "所有者" <> "' + args['owner'][1:] + '" '
        else:
            where += ' AND "所有者" = "' + args['owner'] + '" '
    if args['rate']:
        if 'over' in args['rate']:
            where += ' AND "重要度" >= "' + args['rate'][0] + '" '
        elif 'under' in args['rate']:
            where += ' AND "重要度" <= "' + args['rate'][0] + '"  AND "重要度" <> 0 '
        else:
            where += ' AND "重要度" = "' + args['rate'] + '" '
    if args['cost']:
        where += ' AND "予測値" = "' + args['cost'] + '" '
    if args['tag1st']:
        if args['tag1st'][0] == '-':
            where += ' AND "タグ" NOT LIKE " ' + args['tag1st'][1:] + ' %" '
        else:
            where += ' AND "タグ" LIKE " ' + args['tag1st'] + ' %" '
    if args['tag']:
        tagall = args['tag'].split()
        for tag in tagall:
            if tag[0] == '-':
                where += ' AND "タグ" NOT LIKE "% ' + tag[1:] + ' %" '
            else:
                where += ' AND "タグ" LIKE "% ' + tag + ' %" '
    if 'notag' in args:
        where += ' AND ("タグ" = "" OR "タグ" = "  ") '
    if args['cycle']:
        if args['cycle'] == "routine":
            where += ' AND ("タグ" LIKE "% 年 %" OR "タグ" LIKE "% 半期 %" OR "タグ" LIKE "%月 %" OR ' \
                     ' "タグ" LIKE "% 週 %" OR "タグ" LIKE "%日 %" OR "タグ" LIKE "% 季 %" OR ' \
                     ' "タグ" LIKE "% 春 %" OR "タグ" LIKE "% 夏 %" OR "タグ" LIKE "% 秋 %" OR "タグ" LIKE "% 冬 %")'
        elif args['cycle'] == "randomly":
            where += ' AND ("タグ" LIKE "% 繰り返し %" OR "タグ" LIKE "% 常備 %") '
        else:
            where += ' AND "タグ" NOT LIKE "% 年 %" AND "タグ" NOT LIKE "% 半期 %" AND "タグ" NOT LIKE "%月 %" ' \
                     ' AND "タグ" NOT LIKE "% 週 %" AND "タグ" NOT LIKE "%日 %" AND "タグ" NOT LIKE "% 季 %" ' \
                     ' AND "タグ" NOT LIKE "% 春 %" AND "タグ" NOT LIKE "% 夏 %" AND "タグ" NOT LIKE "% 秋 %" ' \
                     ' AND "タグ" NOT LIKE "% 冬 %" AND "タグ" NOT LIKE "% 常備 %" AND "タグ" NOT LIKE "% 繰り返し %" '
    if args['title']:
        where += ' AND "タスク名" LIKE "%' + args['title'] + '%" '

    order = ' ORDER BY "状態" DESC, "日時" DESC, ' \
            ' CASE "重要度" WHEN 0 THEN 9 ELSE "重要度" END DESC, ' \
            ' "日時" DESC '
    if args['sort'] == 'time':
        order = ' ORDER BY "状態" DESC, "日時" DESC, "番号" DESC '
    if args['sort'] == 'update':
        order = ' ORDER BY "状態" DESC, "日時" DESC '
    if args['sort'] == 'cost':
        order = ' ORDER BY "状態" DESC, "日時" DESC, "予測値" '
    if args['sort'] == 'title':
        order = ' ORDER BY "状態" DESC, "タスク名" '

    sql = 'SELECT *, 日時 as 完了日時, ' \
          ' strftime("%Y-%m-%d ", "日時") || ' \
          '     substr("0"||(strftime("%H", "日時")+9),-2,2) || ' \
          '     strftime(":%M:%S", "日時") as utcP9time ' \
          ' FROM task_archive ' + where + order + ' LIMIT 1000'

    # print(sql)

    rows = get_db().execute(sql).fetchall()

    joutai = ''
    tags = {}
    tasks = {}
    for item in rows:
        tags[item['保存番号']] = item['タグ'].split()
        if item["状態"] == joutai:
            tasks[item['状態']].append(item)
        else:
            joutai = item['状態']
            tasks[item['状態']] = []
            tasks[item['状態']].append(item)

    return render_template('history.html', tasks=tasks, tags=tags, search=args)


@bp.route('/集計', methods=('GET',))
def 集計():
    args = get_args()
    res = ''

    db = get_db()
 
    sql = '''
    SELECT 
        "状態",
        count(*) as 件数,
        SUM("予測値") as 予想 ,
        SUM("実績値") as 実績 ,
        strftime("%Y-%m-%d", 完了日時) as 完了日
    FROM task
    GROUP BY 
        状態,
        strftime("%Y-%m-%d", 完了日時)
    ORDER by
        状態 DESC,
        strftime("%Y-%m-%d", 完了日時) DESC
    '''
    rows = db.execute(sql).fetchall()

    ks = rows[0].keys()
    for r in rows:
        row = ''
        for k in ks:
            if k != '実績' or int(r[k]) > 0:
                if k == '状態':
                    row += f"\t{r[k].ljust(2,'　')}"
                elif k == '件数':
                    row += f":{str(r[k]).rjust(3)}件 "
                elif k == '予想':
                    row += f"\t{str(r[k]).rjust(4)}p "
                elif k == '実績':
                    row += f"\t{str(r[k]).rjust(4)}s "
                elif k == '完了日':
                    if r[k]:
                        row += f"\t{k}:{r[k]}"
                else:
                    row += f"\t{k}:{r[k]}"
        res += '\n' + row.strip()


    res += '\n\n完了 サイト別内訳'
    sql = '''
    SELECT
        "サイト",
        COUNT("番号") as "件数",
        sum("実績値") as "実績",
        sum("予測値")  as "予想", 
        sum("実績値" * "重要度") as "★実績",
        sum("予測値" * "重要度")  as "★予想" 
    FROM "task" 
    WHERE "完了日時" != ""
    GROUP BY "サイト"  
    '''
    rows = db.execute(sql).fetchall()
    ks = rows[0].keys()
    for r in rows:
        row = ''
        for k in ks:
                if k == 'サイト':
                    row += f"\t{r[k]}"
                elif k == '件数':
                    row += f":{str(r[k]).rjust(3)}件 "
                elif k == '予想':
                    row += f"\t{str(r[k]).rjust(4)}p "
                elif k == '実績':
                    row += f"\t{str(r[k]).rjust(4)}s "
                elif k == '★予想':
                    row += f"\t{str(r[k]).rjust(4)}★p "
                elif k == '★実績':
                    row += f"\t{str(r[k]).rjust(4)}★s "
                elif k == '完了日':
                    if r[k]:
                        row += f"\t{k}:{r[k]}"
                else:
                    row += f"\t{k}:{r[k]}"
        res += '\n' + row.strip()


    tags = {}
    tasks = {}
    args['status'] = '完'

    args['cycle'] = 'none'
    tasks["単発"] = []
    rows = _repository.get_list(args)
    for item in rows:
        tags[item['番号']] = item['タグ'].split()
        tasks["単発"].append(item)

    args['cycle'] = 'routine'
    tasks["定期"] = []
    rows = _repository.get_list(args)
    for item in rows:
        tags[item['番号']] = item['タグ'].split()
        tasks["定期"].append(item)

    args['cycle'] = 'randomly'
    tasks["不定"] = []
    rows = _repository.get_list(args)
    for item in rows:
        tags[item['番号']] = item['タグ'].split()
        tasks["不定"].append(item)

    args['cycle'] = ''

    return render_template('summary.html', summary=res.strip(), tasks=tasks, tags=tags, search=args)


@bp.route('/完了日時消去', methods=('GET',))
def 完了日時消去():
    option = request.args.get('option', '')
    db = get_db()
    _repository.完了日時消去(db, option)
    db.commit()

    return redirect(url_for('task.集計'))


def _タグリンク():
    def taglink(text):

        m = re.search('\[.+\]', text)
        if m == None:
            return text

        tag =m.group()[1:-1]
        s = re.split('\[.+\]', text)

        rep = "<a href='" + url_for('task.index', tag=tag) + "'>[" + tag + "]</a>"

        return s[0] + rep + s[1] 

    return taglink
