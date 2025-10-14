import pytest

from swagger_coverage_tool.src.history.endpoint import build_endpoint_key
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import EndpointName


# -------------------------------
# TEST: build_endpoint_key
# -------------------------------


@pytest.mark.parametrize(
    "method,name,expected",
    [
        (HTTPMethod.POST, EndpointName("create_user"), "HTTPMethod.POST_create_user"),
        (HTTPMethod.PUT, EndpointName("update_user"), "HTTPMethod.PUT_update_user"),
        (HTTPMethod.DELETE, EndpointName("delete_user"), "HTTPMethod.DELETE_delete_user"),
    ],
)
def test_build_endpoint_key_various_methods(method: HTTPMethod, name: EndpointName, expected: str):
    assert build_endpoint_key(name, method) == expected
