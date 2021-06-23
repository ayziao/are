""" タスクリポジトリユニットテスト
"""
from are.db import task, get_db


def test_create(app):
    with app.app_context():
        db = get_db()
        task.create(db, 'author', 'owner', 'site', 0, 0, 'title', 'tag', 'body')
        db.commit()

        count = db.execute('SELECT COUNT("連番") FROM task').fetchone()[0]
        assert count == 1
