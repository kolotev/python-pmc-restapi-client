from dataclasses import dataclass, InitVar, field
from furl import furl, Path, Query, Fragment


@dataclass(repr=False)
class HttpUrl:
    url: InitVar[str]
    scheme: str = field(init=False)
    user: str = field(init=False)
    password: str = field(init=False, repr=False)
    host: str = field(init=False)
    port: int = field(init=False)
    _path: Path = field(init=False, repr=False)
    query: Query = field(init=False)
    fragment: Fragment = field(init=False)
    _: "furl.furl.furl" = field(init=False, repr=False)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(str(self._))})"

    def __post_init__(self, url):
        f = self._ = furl(url)

        for k, v in {
            "scheme": "scheme",
            "user": "username",
            "password": "password",
            "host": "host",
            "port": "port",
            "_path": "path",
            "query": "query",
            "fragment": "fragment",
        }.items():
            try:
                setattr(self, k, getattr(f, v))
            except ValueError as e:
                raise ValueError(f"URL property `{k}` is malformed or invalid: {e}")

        self.path /= ""
        self._validate()

    def _validate(self):
        if not (
            all([self.scheme, self.host, self.path])
            and self.scheme in ["http", "https"]
        ):
            errors = (
                (
                    [
                        "URL `scheme` is missing or invalid (`http` or `https` is expected)"
                    ]
                    if self.scheme not in ["http", "https"]
                    else []
                )
                + (
                    ["URL `host` is missing or invalid"]
                    if self.host in ["", None]
                    else []
                )
                + (
                    ["URL `path` is missing or invalid"]
                    if self.path in ["", None]
                    else []
                )
            )
            raise ValueError(f"Invalid URL `{self.url}`: {'; '.join(errors)}")

    @property
    def url(self):
        return self._.url

    def copy(self) -> "HttpUrl":
        return HttpUrl(self.url)

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, path: str) -> None:
        self.path.set(path or "/")
        self.path.normalize()
