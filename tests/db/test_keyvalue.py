from are.db import keyvalue


def test_get_sitesetting(app):
    with app.app_context():
        assert keyvalue.get_sitesetting('test') == {"key": "value"}
