import pytest
from pmc.restapi_client import RestApi, FtsClassFactory
from pmc.restapi_client.exceptions import HttpServerError


def test_create_api_instance():
    """
    Test `creation of new instance` functionality.
    """
    api_ep = "http://localhost///api/"
    api_url = "http://localhost/api/"
    api = RestApi(ep=api_ep)
    assert api is not None  # check that we have got an instance
    assert str(api) == api_url  # check that the url was normalized.


def test_resource_list():
    """
    Test `access to the resource list` functionality.
    """
    ep = "http://localhost/api/"
    resource_url = "http://localhost/api/items"
    api = RestApi(ep=ep)
    resource = api.items
    assert type(resource) is RestApi  # check creation of the resource of correct type
    assert str(resource) == resource_url  # check that the url was normalized.


def test_resource_item():
    """
    Test `access to the resource item` functionality.
    """
    ep = "http://localhost/api/"
    item_x_url = "http://localhost/api/items/x"
    item_5_url = "http://localhost/api/items/5"
    api = RestApi(ep=ep)
    itemres_x = api.items("x")
    assert str(itemres_x) == item_x_url  # check that the url was normalized.
    itemres_5 = api.items(5)
    assert str(itemres_5) == item_5_url  # check that the url was normalized.


def test_get_list(requests_mock):
    ep = "http://localhost/api/"

    # prepare response with Mocker
    payload = {"result": ["a", "b", "c"]}
    requests_mock.get(
        ep + "items", json=payload, headers={"Content-Type": "application/json"}
    )

    # use RestApi
    api = RestApi(ep=ep)
    data, resp = api.items.get()
    assert data == payload


def test_get_item(requests_mock):
    ep = "http://localhost/api/"
    item_id = 5
    item_id_url = ep + f"items/{item_id}"

    # prepare response with Mocker
    payload = {"result": ["a", "b", "c"]}
    requests_mock.get(
        item_id_url, json=payload, headers={"Content-Type": "application/json"}
    )

    # use RestApi
    api = RestApi(ep=ep)
    data, resp = api.items(item_id).get()
    assert data == payload


def test_post_item(requests_mock):
    ep = "http://localhost/api/"
    items_url = ep + f"items"

    # prepare response with Mocker
    payload = {"a": 1, "b": 2, "c": 3}
    result = {"result": ["a", "b", "c"]}
    requests_mock.post(
        items_url, json=result, headers={"Content-Type": "application/json"}
    )

    # use RestApi
    api = RestApi(ep=ep)
    data, resp = api.items.post(data=payload)
    assert data == result


def test_500(requests_mock):
    ep = "http://localhost/api/500"

    # prepare response with Mocker
    requests_mock.get(ep, status_code=500)

    # use RestApi
    SessionClass = FtsClassFactory(max_tries=3, max_time=2)
    api = RestApi(ep=ep, session=SessionClass())
    assert str(api._) == ep

    with pytest.raises(HttpServerError):  # match=r".* 123 .*"
        data, resp = api._.get()
