"""
フラスクアプリケーション アレ

アレをナニする

使い方
export FLASK_APP=are
python3 -m flask run

"""

import datetime
import os

from flask import Flask, Markup


def _URL経路設定(app):
    @app.route('/')
    def hello():
        # return _hello()
        return 'Hello, World!'

    app.add_url_rule('/', endpoint='index')

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)

    from . import task
    app.register_blueprint(task.bp)

    from . import queue
    app.register_blueprint(queue.bp)

    from . import toukei
    app.register_blueprint(toukei.bp)

    # メインなアレ
    from . import site
    app.register_blueprint(site.bp)

    # 開発お勉強用
    from . import xdev
    app.register_blueprint(xdev.bp)


def _テンプレートフィルタ登録(app):
    @app.template_filter('linebreaksbr')
    def linebreaksbr(arg):
        return Markup(arg.replace('\n', '<br>'))

    @app.template_filter()
    def jptime(dt, format_='%Y-%m-%d %H:%M:%S'):
        if not dt:
            return

        u"""utcの時間を日本時間で指定されたフォーマットで文字列化する."""
        local = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=9)

        return local.strftime(format_)


def create_app(test_config=None):
    """
    フラスコアプリケーションの生成と設定
    :param test_config:
    :return:
    """
    app = Flask(__name__, static_url_path='/', instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, __name__ + '.sqlite'),
        EXT_DATABASE=os.path.join(app.instance_path, __name__ + '_ext.sqlite'),
    )

    if test_config is None:
        # テストしていないときに、インスタンス構成が存在する場合はそれをロードします
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 渡された場合は、テスト構成をロードします
        app.config.from_mapping(test_config)

    # インスタンスフォルダが存在することを確実に
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    try:
        _backup_path = os.path.join(app.instance_path, 'backup')
        os.makedirs(_backup_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from .ext import db as ext_db
    ext_db.init_app(app)


    _URL経路設定(app)

    _テンプレートフィルタ登録(app)

    return app

# デバッグとか調査用
# print(__name__)
