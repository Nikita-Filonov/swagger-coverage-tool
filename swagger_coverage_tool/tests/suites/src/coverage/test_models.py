from swagger_coverage_tool.src.coverage.models import (
    ServiceCoverage,
    ServiceEndpointCoverage,
    ServiceEndpointStatusCodeCoverage,
    ServiceEndpointQueryParametersCoverage,
)
from swagger_coverage_tool.src.coverage.status import ServiceEndpointCoverageStatus
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import (
    StatusCode,
    QueryParameter,
    EndpointName,
    CoveragePercent,
)


# -------------------------------
# TEST: ServiceEndpointCoverage — properties
# -------------------------------

def test_number_of_covered_status_codes(service_endpoint_coverage: ServiceEndpointCoverage):
    assert service_endpoint_coverage.number_of_covered_status_codes == 2


def test_number_of_covered_responses(service_endpoint_coverage: ServiceEndpointCoverage):
    assert service_endpoint_coverage.number_of_covered_responses == 1


def test_number_of_covered_query_parameters(service_endpoint_coverage: ServiceEndpointCoverage):
    assert service_endpoint_coverage.number_of_covered_query_parameters == 1


def test_total_counts(service_endpoint_coverage: ServiceEndpointCoverage):
    assert service_endpoint_coverage.total_status_codes == 3
    assert service_endpoint_coverage.total_responses == 2
    assert service_endpoint_coverage.total_query_parameters == 2


# -------------------------------
# TEST: ServiceEndpointCoverage — total_coverage
# -------------------------------

def test_total_coverage_computation(service_endpoint_coverage: ServiceEndpointCoverage):
    total = service_endpoint_coverage.total_coverage
    assert isinstance(total, float)
    assert 0 < total <= 100


def test_total_coverage_zero_when_no_data():
    endpoint = ServiceEndpointCoverage(
        name=EndpointName("empty"),
        method=HTTPMethod.GET,
        coverage=ServiceEndpointCoverageStatus.UNCOVERED,
        total_cases=0,
        status_codes=[],
        query_parameters=[],
        request_coverage=ServiceEndpointCoverageStatus.MISSING,
    )

    assert endpoint.total_coverage == CoveragePercent(0.0)


def test_total_coverage_full_when_all_covered():
    endpoint = ServiceEndpointCoverage(
        name=EndpointName("full"),
        method=HTTPMethod.GET,
        coverage=ServiceEndpointCoverageStatus.COVERED,
        total_cases=1,
        status_codes=[
            ServiceEndpointStatusCodeCoverage(
                value=StatusCode(200),
                total_cases=1,
                response_coverage=ServiceEndpointCoverageStatus.COVERED,
                status_code_coverage=ServiceEndpointCoverageStatus.COVERED,
            )
        ],
        query_parameters=[
            ServiceEndpointQueryParametersCoverage(
                name=QueryParameter("id"),
                coverage=ServiceEndpointCoverageStatus.COVERED,
            )
        ],
        request_coverage=ServiceEndpointCoverageStatus.COVERED,
    )

    assert endpoint.total_coverage == CoveragePercent(100.0)


# -------------------------------
# TEST: ServiceCoverage
# -------------------------------

def test_service_coverage_total_coverage_mixed(service_endpoint_coverage: ServiceEndpointCoverage):
    service = ServiceCoverage(
        endpoints=[
            service_endpoint_coverage,
            ServiceEndpointCoverage(
                name=EndpointName("other"),
                method=HTTPMethod.GET,
                coverage=ServiceEndpointCoverageStatus.UNCOVERED,
                total_cases=1,
                status_codes=[],
                query_parameters=[],
                request_coverage=ServiceEndpointCoverageStatus.MISSING,
            ),
        ]
    )

    total = service.total_coverage
    assert isinstance(total, float)
    assert 0 < total < 100


def test_service_coverage_total_coverage_empty():
    service = ServiceCoverage()
    assert service.total_coverage == CoveragePercent(0.0)


def test_service_coverage_total_coverage_full():
    service = ServiceCoverage(
        endpoints=[
            ServiceEndpointCoverage(
                name=EndpointName("a"),
                method=HTTPMethod.GET,
                coverage=ServiceEndpointCoverageStatus.COVERED,
                total_cases=1,
                status_codes=[],
                query_parameters=[],
                request_coverage=ServiceEndpointCoverageStatus.COVERED,
            ),
            ServiceEndpointCoverage(
                name=EndpointName("b"),
                method=HTTPMethod.GET,
                coverage=ServiceEndpointCoverageStatus.COVERED,
                total_cases=1,
                status_codes=[],
                query_parameters=[],
                request_coverage=ServiceEndpointCoverageStatus.COVERED,
            ),
        ]
    )

    assert service.total_coverage == CoveragePercent(100.0)
