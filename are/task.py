from flask import Blueprint, render_template, request, redirect, flash, url_for, abort  # , g, current_app
from are.db import get_db
from are.auth import login_required

bp = Blueprint('task', __name__, url_prefix='/x/task')


@bp.route('')
def index():
    args = get_args()
    change = request.args.get('change', '')
    if change:
        args[change] = request.args.get('to', '')

    where = ' WHERE "状態" <> "特殊な状態"'
    if args['owner']:
        if args['owner'][0] == '-':
            where += ' AND "所有者" <> "' + args['owner'][1:] + '" '
        else:
            where += ' AND "所有者" = "' + args['owner'] + '" '
    if args['rate']:
        if 'only' in args['rate']:
            where += ' AND "重要度" = "' + args['rate'][0] + '" '
        else:
            where += ' AND "重要度" <= "' + args['rate'] + '"  AND "重要度" <> 0'
    if args['cost']:
        where += ' AND "コスト" = "' + args['cost'] + '" '
    if args['tag']:
        where += ' AND "タグ" like "% ' + args['tag'] + ' %" '
    if args['cycle']:
        if args['cycle'] == "routine":
            where += ' AND ("所有者" = "年" OR "所有者" = "月" OR "所有者" = "週" OR "所有者" = "日" ' \
                     ' OR "所有者" = "半期")'
        elif args['cycle'] == "randomly":
            where += ' AND ("タグ" LIKE "%繰り返し%" OR "タグ" LIKE "%常備%") '
        else:
            where += ' AND "所有者" <> "年" AND "所有者" <> "月" AND "所有者" <> "週" AND "所有者" <> "日" ' \
                     ' AND "所有者" <> "半期" AND "タグ" NOT LIKE "%常備%" AND "タグ" NOT LIKE "%繰り返し%" '

    order = ' ORDER BY "状態" DESC, "完了日時" DESC, ' \
            ' CASE "重要度" WHEN 0 THEN 9 ELSE "重要度" END DESC, ' \
            ' "変更日時" DESC '
    if args['sort'] == 'time':
        order = ' ORDER BY "状態" DESC, "完了日時" DESC, "連番" DESC '
    if args['sort'] == 'update':
        order = ' ORDER BY "状態" DESC, "完了日時" DESC, "変更日時" DESC '
    if args['sort'] == 'cost':
        order = ' ORDER BY "状態" DESC, "完了日時" DESC, "コスト" '

    sql = 'SELECT *, ' \
          ' strftime("%Y-%m-%d ", "完了日時") || ' \
          '     substr("0"||(strftime("%H", "完了日時")+9),-2,2) || ' \
          '     strftime(":%M:%S", "完了日時") as utcP9time ' \
          ' FROM task ' + where + order
    rows = get_db().execute(sql).fetchall()

    # current_app.logger.debug(sql)

    joutai = ''
    tags = {}
    tasks = {}
    for item in rows:
        tags[item['連番']] = item['タグ'].split()
        if item["状態"] == joutai:
            tasks[item['状態']].append(item)
        else:
            joutai = item['状態']
            tasks[item['状態']] = []
            tasks[item['状態']].append(item)

    return render_template('task/index.html', tasks=tasks, tags=tags, search=args)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    default = {
        'owner': request.args.get('owner', '未'),
        'tag': request.args.get('tag', ''),
        'cost': request.args.get('cost', 0),
        'rate': request.args.get('rate', 0)
    }
    if not default["owner"]:
        default["owner"] = '未'

    if request.method == 'POST':
        owner = request.form['owner'] if request.form['owner'] else default['owner']
        cost = request.form['cost'] if request.form['cost'] else default['cost']
        rate = request.form['rate'] if request.form['rate'] else default['rate']
        title = request.form['title']
        tag = ' ' + request.form['tag'].strip() + ' '
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO task ("所有者", "重要度", "コスト", "タスク名", "タグ", "備考")'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (owner, rate, cost, title, tag, body)
            )
            db.commit()
            return redirect(url_for('task.index', owner=owner, tag=tag.strip()))

    return render_template('task/create.html', default=default)


def get_task(number):
    db = get_db()

    task = db.execute(
        'SELECT *'
        ' FROM task'
        ' WHERE "連番" = ?',
        (number,)
    ).fetchone()

    if task is None:
        abort(404, "task id {0} doesn't exist.".format(number))

    return task


def get_args():
    args = {
        'owner': request.args.get('owner', ''),
        'rate': request.args.get('rate', ''),
        'cost': request.args.get('cost', ''),
        'tag': request.args.get('tag', ''),
        'sort': request.args.get('sort', ''),
        'cycle': request.args.get('cycle', '')}
    return args


@bp.route('/<int:number>/update', methods=('GET', 'POST'))
# @login_required
def update(number):
    task = get_task(number)
    fi = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

    if request.method == 'POST':
        status = request.form['status']
        owner = request.form['owner']
        title = request.form['title']
        tag = ' ' + request.form['tag'].strip() + ' '
        body = request.form['body']
        cost = request.form['cost']
        actual = request.form['actual']
        rate = request.form['rate']

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE task SET '
                ' "状態" = ?, "所有者" = ?, "タスク名" = ?, "タグ" = ?, "備考" = ?, "コスト" = ?, "実コスト" = ?, "重要度" = ?, '
                ' "変更日時" = datetime("now")'
                ' WHERE "連番" = ?',
                (status, owner, title, tag, body, cost, actual, rate, number)
            )
            db.commit()
            return redirect(url_for('task.index', owner=owner, tag=tag.strip()))

    return render_template('task/update.html', task=task, fi=fi)


@bp.route('/<int:number>/delete', methods=('POST',))
@login_required
def delete(number):
    get_task(number)
    db = get_db()
    db.execute('DELETE FROM task WHERE "連番" = ?', (number,))
    db.commit()
    return redirect(url_for('task.index'))


@bp.route('/<int:number>/costup', methods=('GET',))
def costup(number):
    args = get_args()

    fi = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

    task = get_task(number)
    if task['状態'] == '完':
        _対象 = '実コスト'
    else:
        _対象 = 'コスト'
    if task[_対象] < 89:
        aa = fi.index(task[_対象])
        db = get_db()
        db.execute(
            f'UPDATE task SET "{_対象}" = ? , "変更日時" = datetime("now")'
            ' WHERE "連番" = ?', (fi[aa + 1], number))
        db.commit()

    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/rateup', methods=('GET',))
def rateup(number):
    args = get_args()

    task = get_task(number)
    if task['重要度'] < 5:
        db = get_db()
        db.execute(
            'UPDATE task SET "重要度" = "重要度" + 1 ,"変更日時" = datetime("now") '
            ' WHERE "連番" = ?', (number,))
        db.commit()

        if args['rate'].isnumeric():
            args['rate'] = int(args['rate']) + 1

    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/ratedown', methods=('GET',))
def ratedown(number):
    args = get_args()

    task = get_task(number)
    if task['重要度'] > 0:
        db = get_db()
        db.execute(
            'UPDATE task SET "重要度" = "重要度" - 1 , "変更日時" = datetime("now") '
            ' WHERE "連番" = ?', (number,))
        db.commit()

        if args['rate'].isnumeric():
            args['rate'] = int(args['rate']) - 1

    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/rateto', methods=('GET',))
def rateto(number):
    args = get_args()
    change = int(request.args.get('change', -1))
    task = get_task(number)

    # current_app.logger.debug(task['重要度'])

    if 0 <= change != task['重要度']:
        db = get_db()
        db.execute(
            'UPDATE task SET "重要度" = ? , "変更日時" = datetime("now")'
            ' WHERE "連番" = ?', (change, number))
        db.commit()

        if args['rate'].isnumeric():
            args['rate'] = change

    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/done', methods=('GET',))
def done(number):
    args = get_args()

    db = get_db()
    db.execute(
        'UPDATE task SET "状態" = "完" , "完了日時" = datetime("now") ,"実コスト" = "コスト"'
        ' WHERE "連番" = ?', (number,))
    db.commit()
    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/doing', methods=('GET',))
def doing(number):
    args = get_args()

    db = get_db()
    db.execute(
        'UPDATE task SET "状態" = "！" , "変更日時" = datetime("now") '
        ' WHERE "連番" = ?',
        (number,)
    )
    db.commit()
    return redirect(url_for('task.index', **args))


@bp.route('/<int:number>/restore', methods=('GET',))
def restore(number):
    args = get_args()

    db = get_db()
    db.execute(
        'UPDATE task SET "状態" = "未" , "完了日時" = "" , "変更日時" = datetime("now") '
        ' WHERE "連番" = ?', (number,))
    db.commit()
    return redirect(url_for('task.index', **args))


@bp.route('/ownerlist', methods=('GET',))
def ownerlist():
    db = get_db()
    ret = db.execute(
        'SELECT 所有者, count(所有者) as 件数, "定期" as cycle '
        ' FROM task '
        ' WHERE "所有者" = "年" OR "所有者" = "月" OR "所有者" = "週" OR "所有者" = "日"  OR "所有者" = "半期" '
        ' GROUP BY 所有者 '
        'UNION '
        'SELECT 所有者, count(所有者) as 件数 , "単発" as cycle '
        ' FROM task '
        ' WHERE "所有者" <> "年" AND "所有者" <> "月" AND "所有者" <> "週" AND "所有者" <> "日"  AND "所有者" <> "半期" '
        ' GROUP BY 所有者 '
        'ORDER BY cycle  DESC, 件数 DESC '
    ).fetchall()
    return render_template('task/list.html', list=ret, type='所有者')


@bp.route('/ratelist', methods=('GET',))
def ratelist():
    db = get_db()
    ret = db.execute(
        'SELECT 重要度 || "only" as 重要度,'
        ' CASE WHEN  重要度 = 5 THEN "★★★★★"'
        '      WHEN  重要度 = 4 THEN "★★★★☆"'
        '      WHEN  重要度 = 3 THEN "★★★☆☆"'
        '      WHEN  重要度 = 2 THEN "★★☆☆☆"'
        '      WHEN  重要度 = 1 THEN "★☆☆☆☆"'
        '      ELSE "☆☆☆☆☆" END as 星,'
        ' count(重要度) as 件数'
        ' FROM task'
        ' GROUP BY 重要度'
        ' ORDER BY 重要度 DESC'
    ).fetchall()
    return render_template('task/list.html', list=ret, type='重要度')


@bp.route('/costlist', methods=('GET',))
def costlist():
    db = get_db()
    ret = db.execute(
        'SELECT コスト, count(コスト) as 件数 '
        ' FROM task '
        ' GROUP BY コスト '
        ' ORDER BY コスト DESC '
    ).fetchall()
    return render_template('task/list.html', list=ret, type='コスト')
