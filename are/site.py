import os
import re
from datetime import datetime, timezone
# from pprint import pformat

from flask import Blueprint, abort, render_template, request, redirect, url_for, current_app, jsonify, \
    send_from_directory, session

# from are.auth import login_required
from are.db import get_db, basedata, queue, keyvalue

bp = Blueprint('site', __name__, static_url_path='', static_folder='static_site')


# 投稿
@bp.route('/<site>/', methods=('POST',))
def post(site):
    body = request.form['body'].strip().replace('\r', '')
    if not body:
        return redirect(url_for('site.top', site=site))

    # jp = datetime.now()
    dt = datetime.now(timezone.utc)
    jp = dt.astimezone()  # PENDING 消す？
    identifier = dt.strftime('%Y%m%d%H%M%S%f')
    dtstr = dt.strftime('%Y-%m-%d %H:%M:%S')
    jpstr = jp.strftime('%Y-%m-%d %H:%M:%S')

    n = body.find("\n")
    nn = body.find("\n\n")
    if n > 0 and n == nn:  # 最初の改行が2連続ならタイトル
        title = body[:n].strip()
        body = body[nn:].strip()
    else:
        title = identifier

    tags = request.form['tags'].strip()
    if tags:
        taglist = re.sub(r'\s+', " ", tags).split(" ")
        tags = " #" + " #".join(taglist) + " "

    db = get_db()
    basedata.create(db, site, identifier, dtstr, title, tags, body, jpstr)
    queue.create(db, "multipost", site + ':' + identifier)
    db.commit()

    return redirect(url_for('site.top', site=site))


# サイトトップ
@bp.route('/<site>', methods=('GET',))
def top(site):
    _add_header('X-rute', f'top /<site>')
    # locale = request.args.get('locale', 'utcP9')
    locale = session['locale_'+site] if 'locale_'+site in session else 'utcP9'
    current_app.logger.debug(locale)
    datas = basedata.get_timeline(site, locale)
    if not datas:
        abort(404, "Not Found : " + site)

    sitesetting = keyvalue.get_sitesetting(site)

    return render_template('site/timeline.html', title='タイムライン',
                           datalist=datas, site=site, locale=locale,
                           sitesetting=sitesetting,
                           titlelink=_タイトルリンク(site))


# サイト機能
@bp.route('/<site>/', methods=('GET',))
def sub(site):
    _add_header('X-rute', f'sub /<site>')

    if 'search' in request.args:
        return _検索(site, request.args.get('search', ''))

    if 'tag' in request.args:
        return _タグ検索(site, request.args.get('tag', ''))

    if 'titles' in request.args:
        return _タイトル一覧(site)

    abort(404)


@bp.route('/<site>/<path>', methods=('GET',))
def item(site, path):
    _add_header('X-rute', f'item /<site>/<path>')

    # PENDING Apacheやnginxなどコンテンツサーバをフロントに持ってきたらいらないのでは？
    file = _静的ファイル(site + '/' + path)
    if file:
        return file

    locale = session['locale_'+site] if 'locale_'+site in session else 'utcP9'
    data = basedata.get_one(site, path, locale)
    if not data:
        return _パス解析(site, path)

    datalist = [data]  # fixme タイムラインテンプレート流用のため配列化 単ページテンプレート作ったら消す

    return render_template('site/timeline.html',
                           title=path, datalist=datalist, site=site, path=path, search=path, locale=locale,
                           titlelink=_タイトルリンク(site))


@bp.route('/<site>/<path>.json', methods=('GET',))
def item2json(site, path):
    _add_header('X-rute', 'item2json /<site>/<path>.json')

    data = basedata.get_one(site, path)
    if not data:
        abort(404)

    return jsonify(dict(data))


@bp.route('/<site>/<path>.txt', methods=('GET',))
def item2text(site, path):
    _add_header('X-rute', 'item2text /<site>/<path>.txt')

    data = basedata.get_one(site, path)
    if not data:
        return _パス解析txt(site, path)

    if data['identifier'] == data['title']:
        text = data['body']
    else:
        text = data['title'] + '\n\n' + data['body']

    return text, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@bp.route('/<site>/<path:path>.json', methods=('GET',))
def subitem2json(site, path):
    _add_header('X-rute', 'subitem2json /<site>/<path:path>.json')
    # TODO カテゴリどうにかする
    abort(404)


@bp.route('/<site>/<path:path>')
def subitem(site, path):
    _add_header('X-rute', 'subitem /<site>/<path:path>')
    # TODO カテゴリどうにかする
    return 'site = {}'.format(site) + ' path = {}'.format(path)


@bp.route('/<name>.<ext>', methods=('GET',))
def staticfile(name, ext):
    _add_header('X-rute', 'staticfile /<name>.<ext>')

    r = _静的ファイル(f"{name}.{ext}")
    if not r:
        abort(404)

    return r


def _検索(site, search):
    order = request.args.get('order', 'DESC')
    locale = session['locale_'+site] if 'locale_'+site in session else 'utcP9'
    posts = basedata.search(site, search, order, locale)

    return render_template('site/timeline.html', title=search, datalist=posts, site=site, order=order, locale=locale,
                           subcommand="search", search=search, titlelink=_タイトルリンク(site))


def _タグ検索(site, tag):
    order = request.args.get('order', 'DESC')
    locale = session['locale_'+site] if 'locale_'+site in session else 'utcP9'
    posts = basedata.tagsearch(site, tag, order, locale)

    return render_template('site/timeline.html', title=tag, datalist=posts, site=site, order=order, locale=locale,
                           search='tag', subcommand="tag", titlelink=_タイトルリンク(site))


def _パス解析(site, path):
    _add_header('X-rute2', 'pathcheck /<site>/<path>')

    order = request.args.get('order', 'ASC')

    # PENDING YYYYMMDD型かどうかチェックするか

    locale = session['locale_'+site] if 'locale_'+site in session else 'utcP9'
    datas = basedata.get_likeid(site, path, locale, order)
    if not datas:
        abort(404, f"Not Found : {site} {path}")

    prev = basedata.prev_identifier(site, path)[0:8]
    next_ = basedata.next_identifier(site, path)[0:8]

    itinenmae = str(int(path[0:4]) - 1) + path[4:8]  # fixme 雑コーディング
    nananenmae = str(int(path[0:4]) - 7) + path[4:8]  # fixme 雑コーディング

    return render_template('site/timeline.html', title=path, datalist=datas, site=site, path=path,
                           locale=locale, order=order, prev=prev, next=next_, itinenmae=itinenmae,
                           nananenmae=nananenmae, titlelink=_タイトルリンク(site))


def _パス解析txt(site, path):
    _add_header('X-rute2', 'pathcheck /<site>/<path>.txt')

    order = request.args.get('order', 'ASC')

    locale = session['locale_'+site] if 'locale_'+site in session else 'utcP9'
    datas = basedata.get_likeid(site, path, locale, order)
    if not datas:
        abort(404, f"Not Found : {site} {path}")

    day = {'current': ''}

    current = ''

    text = ''

    for data in datas:
        if current != data["datetime"][:10]:
            current = data["datetime"][:10]
            text += '\n' + current + '\n'

        if locale != "utcP9":
            text += data["datetime"][11:] + ' '
        else:
            text += data["utcP9time"] + ' '

        if data["identifier"] != data["title"]:
            text += data["title"] + '\n'
        text +=  data["body"] + '\n'

    return str.lstrip(text), 200, {'Content-Type': 'text/plain; charset=utf-8'}


def _静的ファイル(path):
    if os.path.isfile(bp.static_folder + "/" + path):
        return send_from_directory(bp.static_folder, path)
    if os.path.isfile(current_app.static_folder + "/" + path):
        return send_from_directory(current_app.static_folder, path)
    return None


def _タイトル一覧(site):
    titles = basedata.get_titlecount(site)
    return render_template('site/titles.html', site=site, titles=titles, titlelink=_タイトルリンク(site))


def _タイトルリンク(site):
    titles = basedata.get_titlearray(site)

    # print(titles)

    def titlelink(text):
        sp = [text]
        bk = ""
        for ｋ in titles:
            sp = text.split(ｋ, 1)
            if len(sp) > 1:
                bk = ｋ
                for i, v in enumerate(sp):
                    sp[i] = titlelink(v)
                break
        if bk == "":
            return text
        rep = "<a href='" + url_for('site.top', site=site) + '/' + bk + "'>" + bk + "</a>"
        return rep.join(sp)

    # def nolink(text):
    #     return text
    # return nolink
    return titlelink


@bp.after_request
def add_header(response):
    global _add_header_dic
    response.headers.update(_add_header_dic)
    _add_header_dic = {}
    return response


_add_header_dic = {}


def _add_header(key, var):
    global _add_header_dic
    _add_header_dic[key] = var
