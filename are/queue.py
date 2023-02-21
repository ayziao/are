import os
import pathlib
import subprocess
import zipfile
import datetime
import locale
import json

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app
from werkzeug.exceptions import abort

from are.auth import login_required
from are.db import get_exclusive_db, get_db, keyvalue
from are.ext import multipost
from are import task

bp = Blueprint('queue', __name__, url_prefix='/x/queue')


@bp.route('')
def queue():
    db = get_exclusive_db()

    db.execute('BEGIN DEFERRED')
    que = db.execute(
        'SELECT *'
        ' FROM queue '
        ' WHERE reservation_time < CURRENT_TIMESTAMP'
        ' ORDER BY reservation_time , serial_number ASC LIMIT 1'
    ).fetchone()

    if not que:
        return 'no queue'

    if que['queue_type'] == 'test':
        db.execute('DELETE FROM queue WHERE serial_number = ?', (que['serial_number'],))
        db.commit()
        db.close()
        return "ok" + " " + que['queue_type'] + " " + que['content']

    if que['queue_type'] == 'multipost':
        return _マルチポスト(db, que)

    if que['queue_type'] == 'backup':
        return _バックアップ(db, que)

    if que['queue_type'] == 'タスク日次集計':
        return _タスク日次集計(db, que)

    return "ok" + " " + que['queue_type'] + " " + que['content']


@bp.route('/list')
def list():
    db = get_db()
    #         ' WHERE reservation_time < CURRENT_TIMESTAMP'
    rows = db.execute(
        'SELECT *'
        ' FROM queue '
        ' ORDER BY reservation_time , serial_number ASC LIMIT 1000'
    ).fetchall()

    ques = []
    for item in rows:
        ques.append(dict(item))

    return ques


def _バックアップ(db, que):
    _backup_path = os.path.join(current_app.instance_path, 'backup')
    dbpath = pathlib.Path(current_app.config['DATABASE'])
    bk = pathlib.Path(_backup_path + '/' + dbpath.name)

    if bk.exists():
        dt = datetime.datetime.fromtimestamp(bk.stat().st_mtime)
        bkz = pathlib.Path(_backup_path + '/hourly' + dt.strftime('%H') + '.zip')
        with zipfile.ZipFile(str(bkz), "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(str(bk), dbpath.name)

        if dt.strftime('%H') == '00':
            print('毎日')
            bkd = pathlib.Path(_backup_path + '/daily' + dt.strftime('%d') + '.zip')
            ret = subprocess.run(('cp', str(bkz), str(bkd)))
            # print(ret)
            if dt.strftime('%d') == '01':
                print('毎月')
                bkm = pathlib.Path(_backup_path + '/monthly' + dt.strftime('%m') + '.zip')
                ret = subprocess.run(('cp', str(bkz), str(bkm)))
                # print(ret)

    ret = subprocess.run(('cp', current_app.config['DATABASE'], _backup_path))

    # datetime(reservation_time, "+1 hours")
    db.execute('UPDATE queue '
               ' SET reservation_time = strftime("%Y-%m-%d %H:59:59", CURRENT_TIMESTAMP) '
               ' WHERE serial_number = ?', (que['serial_number'],))
    db.commit()
    db.close()
    return 'バックアップ ' + bk.name


def _マルチポスト(db, que):
    arr = que['content'].split(':')
    ret = _get_data(arr[0], arr[1])
    body = ret['body']
    if ret['title'] != ret['identifier']:
        body = ret['title'] + "\n\n" + body
    msg = ""

    siteseting = keyvalue.get_sitesetting(arr[0])
    if siteseting:
        if "twitter_main" in siteseting:
            tw = multipost.tweet(siteseting["twitter_main"], body)
            if 'id_str' in tw:
                msg += ' tw:' + tw['id_str']

        if "mstdnkey" in siteseting:
            to = multipost.toot(siteseting["mstdnkey"], body)
            if 'id' in to:
                msg += ' to:' + str(to['id'])

    db.execute('DELETE FROM queue WHERE serial_number = ?', (que['serial_number'],))
    db.commit()
    db.close()
    return "ok " + que['queue_type'] + " " + que['content'] + msg


def _タスク日次集計(db, que):
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
    date = datetime.date.today()

    task.日次集計(db)
    task.アーカイブ(db)  # TODO 自動じゃないときのこと考える
    task.restore4tag(db, '日', '完', '次')  # 完了日タスクを次に戻す
    task.restore4tag(db, '常備', '完', '後')  # 完了常備タスクを後に戻す
    task.restore4tag(db, '繰り返し', '完', '未')  # 完了繰り返しタスクを未に戻す
    task.restore4tag(db, date.strftime('%A'), '完', '次')  # 完了曜日タスクを次に戻す
    if date.strftime('%A') == '月曜日':
        task.restore4tag(db, '週', '完', '次')  # 完了週タスクを次に戻す
    if date.strftime('%d') == '01':
        task.restore4tag(db, '月', '完', '次')  # 完了月タスクを次に戻す
        task.restore4tag(db, str(int(date.strftime('%d')))+'月', '完', '次')  # 完了当月タスクを次に戻す
    if date.strftime('%m%d') == '0701':
        task.restore4tag(db, '年', '完', '次')  # 完了年タスクを次に戻す

    db.execute('UPDATE queue '
               ' SET reservation_time = strftime("%Y-%m-%d 23:59:59", CURRENT_TIMESTAMP) '
               ' WHERE serial_number = ?', (que['serial_number'],))
    db.commit()
    db.close()
    return 'タスク日次集計'


def _get_data(site, identifier):
    db = get_db()
    _data = db.execute(
        'SELECT * FROM basedata '
        ' WHERE site = ? AND identifier = ? '
        , (site, identifier)
    ).fetchone()
    return _data
