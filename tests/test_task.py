import pytest

import re

from are.db import get_db


def test_ログイン状態(client, auth):
    response = client.get('/x/task')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/x/task')
    assert b'Log Out' in response.data
    assert 'タスク'.encode('utf-8') in response.data


@pytest.mark.parametrize('path, pagetitle', ([
    ('/x/task', '重要度順'),
    ('/x/task?cycle=', '全種'),
    ('/x/task?cycle=none', 'selected>単発'),
    ('/x/task?cycle=routine', 'selected>定期'),
    ('/x/task?cycle=randomly', 'selected>不定'),
    ('/x/task?sort=', '重要度順'),
    ('/x/task?sort=time', 'selected>登録順'),
    ('/x/task?sort=update', 'selected>更新順'),
    ('/x/task?sort=cost', 'selected>ポイント順'),
    ('/x/task?sort=title', 'selected>タスク名順'),
]))
def test_タスク絞り込みタイトル(client, path, pagetitle):
    response = client.get(path).data.decode('utf-8')
    m = re.search(r'<h1>.*</h1>', response, re.DOTALL)
    # print(m)
    # print(response)
    assert pagetitle in m.group()


def test_新規タスク(client, auth, app):
    auth.login()
    assert client.get('/x/task/create').status_code == 200
    client.post('/x/task/create',
                data={'title': 'create', 'body': '', 'owner': '', 'tag': '', 'rate': '', 'site': '', 'cost': '',
                      'sort': ''})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT("番号") FROM task').fetchone()[0]
        assert count == 1


def test_完了日消去(client, auth, app):
    auth.login()
    client.post('/x/task/create',
                data={'title': 'create', 'body': '', 'owner': '', 'tag': '', 'rate': '', 'site': '', 'cost': '',
                      'sort': ''})

    def dict_from_row(row):
        return dict(zip(row.keys(), row))

    assert client.get('/x/task/1/done').status_code == 302

    with app.app_context():
        db = get_db()
        item = db.execute('SELECT * FROM task').fetchone()
        # print(dict_from_row(item))
        assert item['完了日時'] != ''

    assert client.get('/x/task/完了日時消去?option=昨日以前').status_code == 302

    with app.app_context():
        db = get_db()
        item = db.execute('SELECT * FROM task').fetchone()
        # print(dict_from_row(item))
        assert item['完了日時'] != ''


    client.post('/x/task/create',
                data={'title': 'create', 'body': '', 'owner': '', 'tag': '', 'rate': '', 'site': '', 'cost': '',
                      'sort': ''})

    def dict_from_row(row):
        return dict(zip(row.keys(), row))

    assert client.get('/x/task/2/done').status_code == 302

    with app.app_context():
        db = get_db()
        item = db.execute('SELECT * FROM task WHERE 番号 = 2').fetchone()
        # print(dict_from_row(item))
        assert item['完了日時'] != ''

    assert client.get('/x/task/完了日時消去').status_code == 302

    with app.app_context():
        db = get_db()
        item = db.execute('SELECT * FROM task WHERE 番号 = 2').fetchone()
        # print(dict_from_row(item))
        assert item['完了日時'] == ''


