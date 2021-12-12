""" タスクリポジトリユニットテスト
"""
from are.db import get_db
from are.task import repository


def test_create(app):
    with app.app_context():
        db = get_db()
        repository.create(db, 'author', 'owner', 'site', 0, 0, 'title', 'tag', 'body')
        db.commit()

        count = db.execute('SELECT COUNT("連番") FROM task').fetchone()[0]
        assert count == 1

def test_第一タグ一覧取得(app):
    with app.app_context():
        db = get_db()
        ret = repository.第一タグ一覧取得()
        assert ret