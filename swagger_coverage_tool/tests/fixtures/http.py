from types import SimpleNamespace

import httpx
import pytest
import requests


@pytest.fixture
def httpx_response() -> httpx.Response:
    request = httpx.Request("GET", "https://example.com/api/users?id=5")
    response = httpx.Response(200, request=request, content=b"data")
    return response


@pytest.fixture
def requests_response() -> requests.Response:
    req = SimpleNamespace()
    req.method = "POST"
    req.url = "https://example.com/api/create_user?verbose=true"
    req.body = b"payload"

    response = requests.Response()
    response.status_code = 201
    response._content = b"created"
    response.request = req
    return response
