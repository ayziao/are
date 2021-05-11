import os
import pathlib
import subprocess
import zipfile
from datetime import datetime
import json

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app
from werkzeug.exceptions import abort

from are.auth import login_required
from are.db import get_db, keyvalue
from are.ext import multipost

bp = Blueprint('queue', __name__, url_prefix='/x/queue')


@bp.route('')
def queue():
    db = get_db()
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
        return "ok" + " " + que['queue_type'] + " " + que['content']

    if que['queue_type'] == 'multipost':
        return _マルチポスト(db, que)

    if que['queue_type'] == 'backup':
        return _バックアップ(db, que)

    return "ok" + " " + que['queue_type'] + " " + que['content']


@bp.route('/list')
def list():
    db = get_db()
    #         ' WHERE reservation_time < CURRENT_TIMESTAMP'
    que = db.execute(
        'SELECT *'
        ' FROM queue '
        ' ORDER BY reservation_time , serial_number ASC LIMIT 1000'
    ).fetchall()

    return dict(que)


def _バックアップ(db, que):
    _backup_path = os.path.join(current_app.instance_path, 'backup')
    dbpath = pathlib.Path(current_app.config['DATABASE'])
    bk = pathlib.Path(_backup_path + '/' + dbpath.name)

    if bk.exists():
        dt = datetime.fromtimestamp(bk.stat().st_mtime)
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

    db.execute('UPDATE queue '
               ' SET reservation_time = datetime(reservation_time, "+1 hours") '
               ' WHERE serial_number = ?', (que['serial_number'],))
    db.commit()
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
    return "ok " + que['queue_type'] + " " + que['content'] + msg


def _get_data(site, identifier):
    db = get_db()
    _data = db.execute(
        'SELECT * FROM basedata '
        ' WHERE site = ? AND identifier = ? '
        , (site, identifier)
    ).fetchone()
    return _data
