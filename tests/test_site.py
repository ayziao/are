import pytest


@pytest.mark.parametrize('path, x_rute', ([
    ('/sitename', 'top /<site>'),
    ('/testsite/YYYYMMDD', 'item /<site>/<path>'),
    ('/testsite/YYYYMMDD?photo', 'item /<site>/<path>'),
    ('/testsite/YYYYMMDDHHmmSSnnuuu', 'item /<site>/<path>'),
    ('/testsite/YYYYMMDD.json', 'item2json /<site>/<path>.json'),
    ('/testsite/YYYYMMDDHHmmSSnnuuu.json', 'item2json /<site>/<path>.json'),
    ('/testsite/YYYYMMDDHHmmSSnnuuu.txt', 'item2text /<site>/<path>.txt'),
    ('/testsite/title', 'item /<site>/<path>'),
    ('/testsite/category/title', 'subitem /<site>/<path:path>'),
    ('/testsite/category/subcategory/title', 'subitem /<site>/<path:path>'),
    ('/testsite/title.json', 'item2json /<site>/<path>.json'),
    ('/testsite/category/title.json', 'subitem2json /<site>/<path:path>.json'),
    ('/testsite/category/subcategory/title.json', 'subitem2json /<site>/<path:path>.json'),
    ('/testsite/css.css', 'item /<site>/<path>'),
    ('/testsite/YYYY/MM/DD.jpg', 'subitem /<site>/<path:path>'),
    ('/testsite/YYYY/MM/DD/HHmmSSnnuuu', 'subitem /<site>/<path:path>'),
    ('/style.css', 'staticfile /<name>.<ext>'),
]))
def test_経路確認(client, path, x_rute):
    response = client.get(path)
    assert response.headers['X-rute'] == x_rute
    # print("\n")
    # print(path)
    # print(x_rute)
    # assert x_rute in response.headers
    # print(response)
    # print(response.headers)
    # print("--------------------------------")
