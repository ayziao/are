import json

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from are.auth import login_required
from are.db import get_db
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
        arr = que['content'].split(':')
        ret = getdata(arr[0], arr[1])
        body = ret['body']
        if ret['title'] != ret['identifier']:
            body = ret['title'] + "\n\n" + body
        msg = ""

        siteseting = getsiteseting(arr[0])
        if siteseting :
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

def getdata(site, identifier):
    db = get_db()
    _data = db.execute(
        'SELECT * FROM basedata '
        ' WHERE site = ? AND identifier = ? '
        , (site, identifier)
    ).fetchone()
    return _data



def getsiteseting(site):
    db = get_db()
    ret = None
    _data = db.execute(
        'SELECT * FROM keyvalue	'
        ' WHERE key = ? '
        , ('sitesetting_' + site,)
    ).fetchone()
    if _data:
        ret = json.loads(_data['value'])
    return ret
