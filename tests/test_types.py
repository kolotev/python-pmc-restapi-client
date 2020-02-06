from pmc.restapi_client import types as t


def test_rootless_url():
    url = "http://localhost"
    u = t.HttpUrl(url)
    assert u.url == url + "/"


def test_root_url():
    url = "http://localhost/"
    u = t.HttpUrl(url)
    assert u.url == url


def test_normalize():
    url = "http://localhost///////xyz///m/../n"
    url_model = "http://localhost/xyz/n"
    u = t.HttpUrl(url)
    assert u.url == url_model
