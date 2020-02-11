import pytest
from pmc.restapi_client import RestApi, FtsClassFactory
from pmc.restapi_client.exceptions import HttpServerError


def test_create_api_instance():
    """
    Test `creation of new instance` functionality.
    """
    api_ep = "http://localhost/api/"
    api = RestApi(ep=api_ep)
    assert api is not None  # check that we have got an instance
    assert str(api) == api_ep  # check that the url was normalized.


def test_resource_list():
    """
    Test `access to the resource list` functionality.
    """
    ep = "http://localhost/api/"
    resource_url = "http://localhost/api/items/"
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
        ep + "items/", json=payload, headers={"Content-Type": "application/json"}
    )

    # use RestApi
    api = RestApi(ep=ep)
    resp = api.items.get()
    data = resp.data
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
    resp = api.items(item_id).get()
    data = resp.data
    assert data == payload


def test_post_item(requests_mock):
    ep = "http://localhost/api/"
    items_url = ep + "items/"

    # prepare response with Mocker
    payload = {"a": 1, "b": 2, "c": 3}
    result = {"result": ["a", "b", "c"]}
    requests_mock.post(
        items_url, json=result, headers={"Content-Type": "application/json"}
    )

    # use RestApi
    api = RestApi(ep=ep)
    resp = api.items.post(data=payload)
    data = resp.data
    assert data == result


def test_500(requests_mock):
    ep = "http://localhost/api"
    mock_url = ep + "/"
    # prepare response with Mocker
    requests_mock.get(mock_url, status_code=500)

    # use RestApi
    SessionClass = FtsClassFactory(max_tries=3, max_time=2)
    api = RestApi(ep=ep, session=SessionClass())
    assert str(api._) == mock_url

    with pytest.raises(HttpServerError):
        resp = api._.get()
        data = resp.data
        assert data is None


ep = "https://h/api"


@pytest.mark.parametrize(
    "api_url, items_uri, item_uri, item_id, group_slash, discrete_slash",
    [
        (f"{ep}", f"/items", f"/items/5", 5, False, False,),
        (f"{ep}", f"/items", f"/items/5/", 5, False, True,),
        (f"{ep}/", f"items/", f"items/5", 5, True, False,),
        (f"{ep}/", f"items/", f"items/5/", 5, True, True,),
    ],
)
def test_group_resource_trailing_slash(
    api_url, items_uri, item_uri, item_id, group_slash, discrete_slash
):
    api = RestApi(ep=ep, group_slash=group_slash, discrete_slash=discrete_slash)
    assert str(api._) == api_url
    assert str(api.items) == api_url + items_uri
    assert str(api.items(item_id)) == api_url + item_uri
