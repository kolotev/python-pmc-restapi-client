from dataclasses import dataclass, InitVar, field
from furl import furl


@dataclass
class HttpUrl:
    url: InitVar[str]
    scheme: str = field(init=False)
    user: str = field(init=False, default=None)
    password: str = field(repr=False, init=False, default=None)
    host: str = field(init=False)
    port: int = field(init=False)
    path: str = field(init=False)
    query: str = field(init=False, default=None)
    fragment: str = field(init=False, default=None)
    _: "furl.furl.furl" = field(init=False, default=None, repr=False)

    def __post_init__(self, url):
        f = furl(url)
        f.path.normalize()
        if f.path == "":
            f.path /= "/"
        self._ = f
        # from devtools import debug as d
        # print(d.format(f.asdict()))

        for k, v in {
            "scheme": "scheme",
            "user": "username",
            "password": "password",
            "host": "host",
            "port": "port",
            "path": "path",
            "query": "query",
            "fragment": "fragment",
        }.items():
            try:
                setattr(self, k, getattr(f, v))
            except ValueError as e:
                raise ValueError(f"URL property `{k}` is malformed or invalid: {e}")

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

    def set(self, *args, **kwargs):
        return self._.set(*args, **kwargs)


if __name__ == "__main__":
    # u = HttpUrl("http://x.y.z/path")
    # u.path /= "../../xyxz/..///m"
    # u.path.normalize()
    # print(u)

    z = HttpUrl("https://dev.ncbi.nlm.nih.gov/pmc/grantlink/api/?bla=x")
    # z = u# .copy()
    z.path /= "pubmed10"
    z._.set(path=z.path)
    z.path.normalize()
    print(z.url, z.path)
    print(z.value, z.path, z._)
