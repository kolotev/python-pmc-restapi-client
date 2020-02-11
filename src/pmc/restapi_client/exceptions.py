class RestBaseException(Exception):
    """
    All Rest exceptions inherit from this exception.
    """


class RestHttpBaseException(RestBaseException):
    """
    All Rest HTTP Exceptions inherit from this exception.
    """

    def __init__(self, *args, **kwargs):
        """
        Helper to get and a proper dict iterator with Py2k and Py3k
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        super(RestHttpBaseException, self).__init__(*args)


class HttpClientError(RestHttpBaseException):
    """
    Called when the server tells us there was a client error (4xx).
    """


class HttpNotFoundError(HttpClientError):
    """
    Called when the server sends a 404 error.
    """


class HttpServerError(RestHttpBaseException):
    """
    Called when the server tells us there was a server error (5xx).
    """


class ImproperlyConfigured(RestBaseException):
    """
    Rest is somehow improperly configured.
    """
