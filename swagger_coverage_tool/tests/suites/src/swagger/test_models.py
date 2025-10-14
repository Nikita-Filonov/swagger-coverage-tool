import pytest

from swagger_coverage_tool.src.swagger.models import (
    SwaggerNormalizedStatusCode,
    SwaggerNormalizedEndpoint,
    SwaggerNormalized,
    SwaggerRawResponse,
    SwaggerRawParameter,
    SwaggerRawEndpoint,
    SwaggerRaw,
)
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import StatusCode, EndpointName, QueryParameter


# -------------------------------
# TEST: SwaggerNormalizedStatusCode
# -------------------------------

def test_swagger_normalized_status_code_fields():
    status = SwaggerNormalizedStatusCode(value=StatusCode(200), description="OK", has_response=True)
    assert status.value == 200
    assert status.description == "OK"
    assert status.has_response is True


# -------------------------------
# TEST: SwaggerNormalizedEndpoint
# -------------------------------

def test_swagger_normalized_endpoint_fields():
    status_codes = [SwaggerNormalizedStatusCode(value=StatusCode(200), description="OK", has_response=True)]
    endpoint = SwaggerNormalizedEndpoint(
        name=EndpointName("/users"),
        method=HTTPMethod.GET,
        summary="Get users",
        has_request=False,
        status_codes=status_codes,
        query_parameters=[QueryParameter("limit"), QueryParameter("offset")],
    )

    assert endpoint.name == "/users"
    assert endpoint.method == HTTPMethod.GET
    assert endpoint.summary == "Get users"
    assert endpoint.has_request is False
    assert endpoint.status_codes == status_codes
    assert "limit" in endpoint.query_parameters
    assert "offset" in endpoint.query_parameters


# -------------------------------
# TEST: SwaggerRawEndpoint.get_status_codes
# -------------------------------

def test_get_status_codes_returns_valid_list():
    responses = {
        "200": SwaggerRawResponse(description="OK", content={"application/json": {}}),
        "404": SwaggerRawResponse(description="Not Found", content=None),
    }
    endpoint = SwaggerRawEndpoint(responses=responses)

    result = endpoint.get_status_codes()
    assert len(result) == 2
    assert isinstance(result[0], SwaggerNormalizedStatusCode)
    assert result[0].value == 200
    assert result[0].has_response is True
    assert result[1].has_response is False


def test_get_status_codes_handles_invalid_status_codes():
    responses = {"invalid": SwaggerRawResponse(description="Bad code", content={})}
    endpoint = SwaggerRawEndpoint(responses=responses)

    result = endpoint.get_status_codes()
    assert result == []


# -------------------------------
# TEST: SwaggerRawEndpoint.get_query_parameters
# -------------------------------

def test_get_query_parameters_filters_only_query_params():
    parameters = [
        SwaggerRawParameter(name="limit", inside="query"),
        SwaggerRawParameter(name="token", inside="header"),
        SwaggerRawParameter(name="offset", inside="query"),
    ]
    endpoint = SwaggerRawEndpoint(responses={}, parameters=parameters)

    result = endpoint.get_query_parameters()
    assert set(result) == {"limit", "offset"}


def test_get_query_parameters_with_no_params():
    endpoint = SwaggerRawEndpoint(responses={}, parameters=None)
    result = endpoint.get_query_parameters()
    assert result == []


# -------------------------------
# TEST: SwaggerRaw.normalize
# -------------------------------

def test_normalize_builds_correct_structure():
    raw = SwaggerRaw(
        endpoints={
            "/users": {
                "get": SwaggerRawEndpoint(
                    summary="Get users",
                    request=None,
                    responses={
                        "200": SwaggerRawResponse(description="OK", content={"application/json": {}})
                    },
                    parameters=[SwaggerRawParameter(name="limit", inside="query")],
                )
            }
        }
    )

    normalized = raw.normalize()

    assert isinstance(normalized, SwaggerNormalized)
    assert len(normalized.endpoints) == 1

    endpoint = normalized.endpoints[0]
    assert endpoint.name == "/users"
    assert endpoint.method == HTTPMethod.GET
    assert endpoint.summary == "Get users"
    assert endpoint.has_request is False
    assert endpoint.status_codes[0].value == 200
    assert endpoint.status_codes[0].has_response is True
    assert "limit" in endpoint.query_parameters


def test_normalize_raises_value_error_when_no_endpoints():
    raw = SwaggerRaw(endpoints={})
    with pytest.raises(ValueError, match="No endpoints found"):
        raw.normalize()
