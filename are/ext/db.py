import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_ext_db():
    if 'ext_db' not in g:
        g.ext_db = sqlite3.connect(
            current_app.config['EXT_DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.ext_db.row_factory = sqlite3.Row

    return g.ext_db


def close_ext_db(e=None):
    ext_db = g.pop('ext_db', None)

    if ext_db is not None:
        ext_db.close()


def init_ext_db():
    ext_db = get_ext_db()

    with current_app.open_resource('ext/schema.sql') as f:
        ext_db.executescript(f.read().decode('utf8'))


@click.command('init-ext_db')
@with_appcontext
def init_ext_db_command():
    """Clear the existing data and create new tables."""
    init_ext_db()
    click.echo('Initialized the ext database.')


def init_app(app):
    app.teardown_appcontext(close_ext_db)
    app.cli.add_command(init_ext_db_command)