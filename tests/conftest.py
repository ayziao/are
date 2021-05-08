import os
import tempfile

import pytest
from are import create_app
from are.db import get_db, init_db
from are.ext.db import get_ext_db, init_ext_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

with open(os.path.join(os.path.dirname(__file__), 'data_ext.sql'), 'rb') as f:
    _data_ext_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    ext_db_fd, ext_db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'EXT_DATABASE': ext_db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
        init_ext_db()
        get_ext_db().executescript(_data_ext_sql)

    yield app

    os.close(ext_db_fd)
    os.unlink(ext_db_path)

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/x/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/x/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)


