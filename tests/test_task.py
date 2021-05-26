import pytest
from are.db import get_db


def test_index(client, auth):
    response = client.get('/x/task')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/x/task')
    assert b'Log Out' in response.data
    assert 'タスク'.encode('utf-8') in response.data
    assert '重要度順'.encode('utf-8') in response.data

    response = client.get('/x/task?cycle=none')
    assert '単発'.encode('utf-8') in response.data

