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
    ('/x/task?cycle=none', '単発'),
    ('/x/task?cycle=routine', '定期'),
    ('/x/task?cycle=randomly', '不定'),
    ('/x/task?sort=', '重要度順'),
    ('/x/task?sort=time', '登録時順'),
    ('/x/task?sort=update', '更新時順'),
    ('/x/task?sort=cost', 'コスト順'),
    ('/x/task?sort=title', 'タスク名順'),
]))
def test_タスク絞り込みタイトル(client, path, pagetitle):
    response = client.get(path).data.decode('utf-8')
    m = re.search(r'<h1>.*</h1>', response, re.DOTALL)
    # print(m)
    # print(response)
    assert pagetitle in m.group()
