from flask import Blueprint, session, redirect, url_for, current_app, request, make_response
from are.auth import login_required
from are.db import keyvalue, get_db

bp = Blueprint('xdev', __name__, url_prefix='/x/dev')


@bp.route('/sql')
@login_required
def sql():
    db = get_db()
    #         ' WHERE reservation_time < CURRENT_TIMESTAMP'
    sql = '''
    SELECT 
        "状態",
        count(*) as 件数,
        strftime("%Y-%m-%d", 完了日時) as 完了日 ,
        SUM("コスト") as 予想 ,
        SUM("実コスト") as 実績
    FROM task
    GROUP BY 
        状態,
        strftime("%Y-%m-%d", 完了日時)
    ORDER by
        状態 DESC,
        strftime("%Y-%m-%d", 完了日時) DESC
    '''
    rows = db.execute(sql).fetchall()

    ret = {'sql': sql}
    arr = []
    for i in rows:
        arr.append(dict(i))
    ret['tasks'] = arr
    # return ret

    res = sql + '\n'
    ks = rows[0].keys()
    for r in rows:
        res += '\n'
        for k in ks:
            res += f"\t{k}:{r[k]}"
    response = make_response(res, 200)
    response.mimetype = "text/plain"
    return response


@bp.route('/keyvalue')
@login_required
def keyvalue():
    db = get_db()
    #         ' WHERE reservation_time < CURRENT_TIMESTAMP'
    que = db.execute(
        'SELECT *'
        ' FROM keyvalue '
    ).fetchall()

    return dict(que)


@bp.route('/locale/<tz>')
def locale(tz):
    session['locale'] = tz
    current_app.logger.debug(tz)
    ref = request.args.get('ref', '')
    if ref:
        return redirect(url_for('site.top', site=ref))
    else:
        return redirect(url_for('task.index'))


@bp.route('')
def こんにちわ():  # pragma: no cover
    return "こんにちわこんにちわ"


@bp.route('/k')
def k():  # pragma: no cover
    return keyvalue.get_sitesetting('txt')


@bp.route('/q')
def q():  # pragma: no cover
    db = get_db()

    # db.execute('DELETE FROM queue WHERE serial_number = ?', (56,))
    # db.commit()

    _sql = '''
    SELECT *
    FROM queue
    '''
    rows = db.execute(_sql).fetchall()

    if not rows:
        return 'no queue'

    res = _sql + '\n'
    ks = rows[0].keys()
    for r in rows:
        res += '\n'
        for k in ks:
            res += f"\t{k}:{r[k]}"
    response = make_response(res, 200)
    response.mimetype = "text/plain"
    return response




@bp.route('/dev')
def dev():  # pragma: no cover
    print(__name__)
    print(__file__)
    # print(__spec__)
    # print(__cached__)
    print(__package__)

    text = 'これはタイトル\n\n僕はリンクの冒険が\n\n好きですリンクが冒険してるので リンクの冒険は冒険ですね \nいやまじで'
    # text = 'マリオブラザーズリンクの冒険'
    # text = 'マリオブラザーズ'
    # text = 'aa'

    # hoge = _piyo(text)

    print(_title(text))

    t = ["リンクの冒険", "リンク", "冒険"]

    # ret = _sp(text, t)
    # return ret

    def f(s):
        p = [s]
        b = ""
        for ｋ in t:
            p = s.split(ｋ, 1)
            if len(p) > 1:
                b = ｋ
                for i, v in enumerate(p):
                    p[i] = f(v)
                break
        return f"[{b}]".join(p)

    return f(text)

    # ret = text.split("リンクの冒険", 1)
    # print(ret)
    return ret

    # for kye in ls:
    #     text = text.replace(kye, f"[{kye}]")
    #
    # return text


def _sp(text, ls):  # pragma: no cover
    # print("##############")
    # print(text)

    are = [text]
    kore = ""
    for kye in ls:
        are = text.split(kye, 1)
        # print(are)
        # print(len(are))
        if len(are) > 1:
            kore = kye

            for i, v in enumerate(are):
                are[i] = _sp(v, ls)
            break

    # print(are)
    # print(kore)

    koretagu = "[" + kore + "]"

    return koretagu.join(are)


def _piyo(text):  # pragma: no cover
    # 文字列を２文字づつのリストにする
    # あいうえお あい いう うえ えお
    # wiki名検索用

    # print(text + str(len(text)))
    # print(text[0:2])

    aaa = []

    ttt = text.split()

    for x in ttt:
        # print(x)
        for i in range(len(x) - 1):
            aaa.append(x[i:i + 2])

    # for i, v in enumerate(text):
    # for i in range(len(text)-1):
    #     aaa.append(text[i:i + 2])

    # print(aaa)
    return list(set(aaa))


def _title(text):  # pragma: no cover
    n = text.find("\n")
    nn = text.find("\n\n")

    if n > 0 and n == nn:
        return text[:n]

    return ""
