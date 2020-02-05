import logging as lg
import sys
import traceback

import backoff
import requests
from pmc.restapi_client import ppformat as ppf
from num2words import num2words as n2w

RETRY_MAX_TIME = 120
RETRY_MAX_TRIES = 0
RETRY_MAX_TIME_BETWEEN_TRIES = 15
RETRY_CODES = tuple((408, 429, *range(500, 600)))
RETRY_EXCEPTIONS = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.RetryError,
)
RETRY_PREDICATE = lambda response: response.status_code in RETRY_CODES  # noqa
RETRY_WAIT_GEN = backoff.fibo
RETRY_WAIT_GEN_KWARGS = {"max_value": RETRY_MAX_TIME_BETWEEN_TRIES}


def _backoff_log(details):
    details["tries_ordinal"] = n2w(details["tries"], ordinal=True)
    exc_typ, exc, _ = sys.exc_info()

    if isinstance(details.get("value", None), requests.Response):
        details["value"] = ppf.http_response(details["value"], inline=True)
    elif exc is not None:
        exc_fmt = traceback.format_exception_only(exc_typ, exc)[-1]
        details["value"] = exc_fmt.rstrip("\n")

    lg.debug(
        "Re-trying <<{value}>> waiting for {wait:0.1f}s before trying `{tries_ordinal}` "
        "time.".format(**details)
    )


class FtsClassFactory:  # Fts stands for Fault Tolerant Session
    def __new__(
        self,
        predicate=RETRY_PREDICATE,
        max_time=RETRY_MAX_TIME,
        max_tries=RETRY_MAX_TRIES,
        wait_gen=RETRY_WAIT_GEN,
        on_backoff=_backoff_log,
        exception=RETRY_EXCEPTIONS,
        logger=None,
        **wait_gen_kwargs,
    ):
        if len(wait_gen_kwargs) == 0:
            wait_gen_kwargs = RETRY_WAIT_GEN_KWARGS

        class FtSession(requests.Session):
            @backoff.on_predicate(
                predicate=predicate,
                wait_gen=wait_gen,
                max_time=max_time,
                max_tries=max_tries,
                on_backoff=on_backoff,
                logger=logger,
                **wait_gen_kwargs,
            )
            @backoff.on_exception(
                exception=exception,
                wait_gen=wait_gen,
                max_time=max_time,
                max_tries=max_tries,
                on_backoff=on_backoff,
                logger=logger,
                **wait_gen_kwargs,
            )
            def request(self, method, url, *args, **kwargs) -> requests.Response:
                return super().request(method, url, *args, **kwargs)

        return FtSession


# if __name__ == "__main__":
#     SessionClass = FtsClassFactory(max_tries=3, max_time=2)
#     sess = SessionClass()
#     resp = sess.get(url="https://httpstat.us/503")
#     print(resp.headers.get("Content-Type").find("application/json"))
#     print(u.format_http_response(resp, inline=True))
