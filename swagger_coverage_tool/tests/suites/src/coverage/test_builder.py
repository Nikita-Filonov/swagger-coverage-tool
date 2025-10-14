from pathlib import Path

import pytest

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.coverage.builder import SwaggerServiceCoverageBuilder
from swagger_coverage_tool.src.coverage.models import (
    ServiceEndpointStatusCodeCoverage,
)
from swagger_coverage_tool.src.coverage.status import ServiceEndpointCoverageStatus
from swagger_coverage_tool.src.history.builder import SwaggerServiceCoverageHistoryBuilder
from swagger_coverage_tool.src.history.models import ServiceCoverageHistory
from swagger_coverage_tool.src.swagger.models import (
    SwaggerNormalizedEndpoint,
    SwaggerNormalizedStatusCode, SwaggerNormalized,
)
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import (
    StatusCode,
    QueryParameter,
    EndpointName,
    ServiceKey,
)
from swagger_coverage_tool.src.tracker.models import EndpointCoverageList, EndpointCoverage


# -------------------------------
# TEST: build_status_code_coverage
# -------------------------------

def test_build_status_code_coverage_basic():
    status_code = SwaggerNormalizedStatusCode(
        value=StatusCode(200),
        description="OK",
        has_response=True
    )
    coverage_list = EndpointCoverageList(
        root=[
            EndpointCoverage(
                name=EndpointName("get_users"),
                method=HTTPMethod.GET,
                service=ServiceKey("svc"),
                status_code=StatusCode(200),
                query_parameters=[],
                is_request_covered=True,
                is_response_covered=True,
            )
        ]
    )

    result = SwaggerServiceCoverageBuilder.build_status_code_coverage(
        status_code=status_code,
        coverage_list=coverage_list,
    )

    assert isinstance(result, ServiceEndpointStatusCodeCoverage)
    assert result.value == 200
    assert result.description == "OK"
    assert result.response_coverage == ServiceEndpointCoverageStatus.COVERED
    assert result.status_code_coverage == ServiceEndpointCoverageStatus.COVERED
    assert result.total_cases == 1


def test_build_status_code_coverage_uncovered():
    status_code = SwaggerNormalizedStatusCode(
        value=StatusCode(404),
        description="Not Found",
        has_response=False
    )
    coverage_list = EndpointCoverageList(root=[])

    result = SwaggerServiceCoverageBuilder.build_status_code_coverage(
        status_code=status_code,
        coverage_list=coverage_list,
    )

    assert result.status_code_coverage == ServiceEndpointCoverageStatus.UNCOVERED
    assert result.response_coverage == ServiceEndpointCoverageStatus.MISSING


# -------------------------------
# TEST: build_status_codes
# -------------------------------

def test_build_status_codes_multiple(monkeypatch: pytest.MonkeyPatch):
    """Билдит список из нескольких статус-кодов."""
    endpoint = SwaggerNormalizedEndpoint(
        name=EndpointName("get_users"),
        method=HTTPMethod.GET,
        summary="Test",
        status_codes=[
            SwaggerNormalizedStatusCode(value=StatusCode(200), has_response=True),
            SwaggerNormalizedStatusCode(value=StatusCode(400), has_response=False),
        ],
        query_parameters=[],
    )

    coverage_list = EndpointCoverageList(root=[])

    results = SwaggerServiceCoverageBuilder.build_status_codes(endpoint, coverage_list)
    assert isinstance(results, list)
    assert all(isinstance(result, ServiceEndpointStatusCodeCoverage) for result in results)
    assert {result.value for result in results} == {200, 400}


# -------------------------------
# TEST: build_query_parameters
# -------------------------------

def test_build_query_parameters_marks_covered(monkeypatch: pytest.MonkeyPatch):
    endpoint = SwaggerNormalizedEndpoint(
        name=EndpointName("get_users"),
        method=HTTPMethod.GET,
        summary=None,
        has_request=False,
        status_codes=[],
        query_parameters=[QueryParameter("limit"), QueryParameter("offset")],
    )

    coverage_list = EndpointCoverageList(
        root=[
            EndpointCoverage(
                name=EndpointName("get_users"),
                method=HTTPMethod.GET,
                service=ServiceKey("svc"),
                status_code=StatusCode(200),
                query_parameters=[QueryParameter("limit")],
                is_request_covered=False,
                is_response_covered=False,
            )
        ]
    )

    results = SwaggerServiceCoverageBuilder.build_query_parameters(endpoint, coverage_list)
    assert isinstance(results, list)
    assert len(results) == 2

    covered = next(query for query in results if query.name == "limit")
    uncovered = next(query for query in results if query.name == "offset")

    assert covered.coverage == ServiceEndpointCoverageStatus.COVERED
    assert uncovered.coverage == ServiceEndpointCoverageStatus.UNCOVERED


# -------------------------------
# TEST: build
# -------------------------------

def test_build_creates_service_coverage(tmp_path: Path):
    endpoint = SwaggerNormalizedEndpoint(
        name=EndpointName("get_users"),
        method=HTTPMethod.GET,
        summary="Get users",
        has_request=True,
        status_codes=[
            SwaggerNormalizedStatusCode(value=StatusCode(200), has_response=True)
        ],
        query_parameters=[QueryParameter("limit")],
    )

    swagger = SwaggerNormalized(endpoints=[endpoint])

    coverage_list = EndpointCoverageList(
        root=[
            EndpointCoverage(
                name=EndpointName("get_users"),
                method=HTTPMethod.GET,
                service=ServiceKey("svc"),
                status_code=StatusCode(200),
                query_parameters=[QueryParameter("limit")],
                is_request_covered=True,
                is_response_covered=True,
            )
        ]
    )

    settings = Settings(services=[])
    settings.history_file = tmp_path / "history.json"
    history_builder = SwaggerServiceCoverageHistoryBuilder(ServiceCoverageHistory(), settings)

    builder = SwaggerServiceCoverageBuilder(
        swagger=swagger,
        history_builder=history_builder,
        endpoint_coverage_list=coverage_list,
    )

    result = builder.build()

    assert result is not None
    assert len(result.endpoints) == 1

    endpoint_result = result.endpoints[0]
    assert endpoint_result.name == "get_users"
    assert endpoint_result.coverage == ServiceEndpointCoverageStatus.COVERED
    assert endpoint_result.request_coverage == ServiceEndpointCoverageStatus.COVERED

    assert len(endpoint_result.status_codes) == 1
    assert endpoint_result.status_codes[0].status_code_coverage == ServiceEndpointCoverageStatus.COVERED
    assert len(endpoint_result.total_coverage_history) >= 1
    assert len(result.total_coverage_history) >= 1
