import json
import requests
from typing import Union


def duration(seconds):
    """Pretty print time duration"""
    sign_string = "negative" if seconds < 0 else ""
    _seconds = abs(seconds)
    days, _seconds = divmod(_seconds, 86400)
    hours, _seconds = divmod(_seconds, 3600)
    minutes, _seconds = divmod(_seconds, 60)
    result = ""

    if sign_string:
        result += f"{sign_string} "
    if days > 0:
        result += f"{days:.0f} day{'s' if days > 1 else ''} "
    if hours > 0:
        result += f"{hours:.0f} hour{'s' if hours > 1 else ''} "
    if minutes > 0:
        result += f"{minutes:.0f} minute{'s' if minutes > 1 else ''} "
    result += f"{_seconds:.3f} second{'s' if _seconds > 1 else ''}"

    return result


def _request(
    request: requests.models.PreparedRequest, skip_headers=False, json_indent=4
):
    return _request_response(
        "REQUEST", request, skip_headers=skip_headers, json_indent=json_indent
    )


def _response(response: requests.models.Response, skip_headers=False, json_indent=4):
    return _request_response(
        "RESPONSE", response, skip_headers=skip_headers, json_indent=json_indent
    )


def _request_response(
    title: str,
    request_response: Union[requests.models.Response, requests.models.PreparedRequest],
    skip_headers=False,
    json_indent=4,
):
    """
    Pretty formatting of response info from response instance.
    :param title: str => Title of the banner
    :param request_response: Union(requests.models.Response, requests.models.PreparedRequest)

    :return:
    """
    # if not isinstance(
    #     request_response, (requests.models.Response, requests.models.PreparedRequest)
    # ):
    #     raise ValueError(
    #         "`request_response` must be one of the following sub-types: "
    #         "requests.models.Response, requests.models.PreparedRequest."
    #         f"{type(request_response)} provided instead."
    #     )

    # is_request = isinstance(request_response, requests.models.PreparedRequest)
    is_request = not hasattr(request_response, "request")

    banner_str = f"=== {title} ==="

    method_str = (
        request_response.method if is_request else request_response.request.method
    )
    url_str = request_response.url
    headers_str = "\n".join(
        "{}: {}".format(k.title(), v) for k, v in request_response.headers.items()
    )
    body = (
        request_response.body
        if hasattr(request_response, "body")
        else request_response.text
    )

    body_is_json = False
    try:
        body_str = (
            json.dumps(json.loads(body), indent=json_indent, sort_keys=True)
            if request_response.headers["Content-Type"].find("application/json") >= 0
            else str(body)
        )
        body_is_json = True
    except Exception:
        body_str = str(body) if body is not None else ""

    if not body_is_json:
        body_str = body_str[:100] + (" ... [skipped]" if len(body_str) > 100 else "")

    req_resp_str = (
        f"{method_str} {url_str}"
        if is_request
        else (
            f"HTTP/{float(request_response.raw.version / 10)} "
            f"{request_response.status_code} "
            f"{request_response.reason}"
        )
    )

    return (
        f"{banner_str}\n"
        f"{req_resp_str}\n\n"
        f"{headers_str if not skip_headers else ''}\n\n"
        f"{'({})'.format(body_str) if body_str else ''}"
    )


def http_response(response: requests.models.Response, inline=True, verbose=1):
    if verbose:
        if not inline:
            return f"\n{_request(response.request)}\n\n{_response(response)}"

        else:
            request = response.request

            request_content = _request(request, skip_headers=True, json_indent=0)
            request_content = request_content.replace("\n", " ")
            response_content = _response(response, skip_headers=True, json_indent=0)
            response_content = response_content.replace("\n", " ")

            return f"{request_content} {response_content}"
    else:
        return ""
