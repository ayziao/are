from are.ext import keyvalue


def test_get_sitesetting(app):
    with app.app_context():
        assert keyvalue.getSitesetting('test') == {"ext_key": "ext_value"}
