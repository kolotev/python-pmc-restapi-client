# This work is based on existing work of David Karchmer aka dkarchmer.
# see https://github.com/dkarchmer/django-rest-framework-client
#
# It was modified due to the following issues:
# - the problems with url construction for restful resources
#   (extra slashes)
#
from . import ppformat as ppf
from .exceptions import HttpServerError, HttpClientError, HttpNotFoundError
from .session import FtsClassFactory
from .types import HttpUrl
import requests
from typing import Tuple, Any

##############################################################################
DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

##############################################################################


class RestApi:
    """
    This class provides RESTFul API queries and responses handling.

    Arguments:
        :param ep: end point of API
        :param session: requests' Session instance
        :param logger: logging compatible logger
        :param debug: integer value representing debug level
        :
        :return: instance this class.

    Raises:
        AttributeError: in case if resource starts with underscore.

    Returns:
        RestApi instance."""

    def __init__(
        self,
        ep: str,  # API end point
        session: requests.Session = None,
        logger=None,
        debug: int = 0,
        group_slash=True,
        discrete_slash=False,
    ):
        self._ep = HttpUrl(ep)
        self._session = session or FtsClassFactory(logger=logger)()
        self._logger = logger
        self._debug = debug
        self._group_slash = group_slash
        self._discrete_slash = discrete_slash

    def __getattr__(self, resource, group=True):
        """
        Returns a RestApi instance for resource segment of API's url.
        To allow api.resource.get() syntax to get list of items of `resource`.

        Arguments:
            resource -- API url segment.

        Returns:
            RestApi instance"""
        if not isinstance(resource, str):
            resource = str(resource)

        if resource.startswith("_"):
            raise RuntimeError(
                "Resources starting with `_` (underscore) are not supported."
            )

        kwargs = self._copy_kwargs(resource, group=group)
        return self._get_resource(**kwargs)

    def __call__(self, item_id):
        """
        Returns a RestApi instance for resource instance/item of API.
        To allow api.resource(item_id).get() syntax to get
        a specific resource by it's id.
        """

        return self.__getattr__(item_id, group=False)

    def _copy_kwargs(self, resource, group):
        kwargs = {}
        kwargs.update({k.lstrip("_"): v for k, v in self.__dict__.items()})
        ep = self._ep.copy()

        if resource is not None:
            ep.path /= resource

            if group:
                if self._group_slash:
                    ep.path /= "/"
            else:
                if self._discrete_slash:
                    ep.path /= "/"

        kwargs["ep"] = ep.url

        return kwargs

    def _get_resource(self, **kwargs):
        return self.__class__(**kwargs)

    def _check_for_errors(self, resp, data):

        message = "HTTP Client"
        exception_class = None

        if resp.status_code == 404:
            exception_class = HttpNotFoundError
        elif 400 <= resp.status_code <= 499:
            exception_class = HttpClientError
        elif 500 <= resp.status_code <= 599:
            exception_class = HttpServerError
            message = "HTTP Server"

        message += (
            f" Error[{resp.status_code}] {resp.url}"
            f" {ppf.http_response(resp, inline=not (bool(self._debug)))}"
        )

        if exception_class:
            raise exception_class(
                message, response=resp, content=resp.content, data=data
            )

    def _try_to_serialize_response(self, resp):

        if "application/json" in resp.headers.get("Content-Type", ""):
            return resp.json()
        return

        # if resp.content:
        #     if type(resp.content) == bytes:
        #         encoding = requests.utils.guess_json_utf(resp.content)
        #         return json.loads(resp.content.decode(encoding))
        #     return json.loads(resp.content)
        #
        # else:
        #     return resp.json()

    def _process_response(self, resp):
        data = self._try_to_serialize_response(resp)
        self._check_for_errors(resp, data)
        return data

    def _get_headers(self):
        headers = DEFAULT_HEADERS
        return headers

    def _request_try(self, method, url, **kwargs):
        # compatible with session.request(method, url, **kwargs)
        session = self._session
        kwargs["headers"] = kwargs.get("headers", {})
        kwargs["headers"].update(self._get_headers())
        resp = session.request(method, url, **kwargs)
        return resp

    def _request(self, method, **kwargs) -> Tuple[Any, requests.Response]:
        resp = self._request_try(method, self._ep.url, **kwargs)
        resp.data = self._process_response(resp)
        return resp

    def get(self, **kwargs):
        return self._request("get", **kwargs)

    def post(self, **kwargs):
        return self._request("post", **kwargs)

    def put(self, **kwargs):
        return self._request("put", **kwargs)

    def patch(self, **kwargs):
        return self._request("patch", **kwargs)

    def delete(self, **kwargs):
        return self._request("delete", **kwargs)

    def head(self, **kwargs):
        return self._request("head", **kwargs)

    @property
    def _(self) -> "RestApi":
        """
        Creates an instance of RestApi, which
        correspond to the "root" aka "/" of the RESTFul API
        end-point.

        Returns:
            RestApi instance"""
        return self.__getattr__("")

    def __str__(self):
        return self._ep.url
