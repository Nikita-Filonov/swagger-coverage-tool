from http import HTTPMethod

from swagger_coverage_tool.src.tools.types import ServiceKey, StatusCode, EndpointName
from swagger_coverage_tool.src.tracker.models import EndpointCoverageList, EndpointCoverage


# -------------------------------
# TEST: filter
# -------------------------------

def test_filter_by_name(endpoint_coverage_list: EndpointCoverageList):
    result = endpoint_coverage_list.filter(name=EndpointName("create_user"))
    assert len(result.root) == 1
    assert result.root[0].name == "create_user"


def test_filter_by_service(endpoint_coverage_list: EndpointCoverageList):
    result = endpoint_coverage_list.filter(service=ServiceKey("user-service"))
    assert all(c.service == "user-service" for c in result.root)
    assert len(result.root) == 2


def test_filter_by_method(endpoint_coverage_list: EndpointCoverageList):
    result = endpoint_coverage_list.filter(method=HTTPMethod.DELETE)
    assert len(result.root) == 1
    assert result.root[0].method == HTTPMethod.DELETE


def test_filter_by_status_code(endpoint_coverage_list: EndpointCoverageList):
    result = endpoint_coverage_list.filter(status_code=StatusCode(201))
    assert len(result.root) == 1
    assert result.root[0].status_code == 201


def test_filter_multiple_criteria(endpoint_coverage_list: EndpointCoverageList):
    result = endpoint_coverage_list.filter(
        service=ServiceKey("user-service"), method=HTTPMethod.POST
    )
    assert len(result.root) == 1
    assert result.root[0].name == "create_user"


def test_filter_case_insensitive(endpoint_coverage_list: EndpointCoverageList):
    result = endpoint_coverage_list.filter(service=ServiceKey("USER-SERVICE"))
    assert len(result.root) == 2
    assert all(c.service.lower() == "user-service" for c in result.root)


def test_filter_returns_empty_list(endpoint_coverage_list: EndpointCoverageList):
    result = endpoint_coverage_list.filter(service=ServiceKey("nonexistent"))
    assert isinstance(result, EndpointCoverageList)
    assert result.root == []


# -------------------------------
# TEST: properties
# -------------------------------

def test_total_cases(endpoint_coverage_list: EndpointCoverageList):
    assert endpoint_coverage_list.total_cases == 3


def test_unique_query_parameters(endpoint_coverage_list: EndpointCoverageList):
    params = endpoint_coverage_list.unique_query_parameters
    assert set(params) == {"limit", "offset", "verbose"}


def test_is_covered_true(endpoint_coverage_list: EndpointCoverageList):
    assert endpoint_coverage_list.is_covered is True


def test_is_covered_false():
    empty_list = EndpointCoverageList(root=[])
    assert empty_list.is_covered is False


def test_is_request_covered(endpoint_coverage_list: EndpointCoverageList):
    assert endpoint_coverage_list.is_request_covered is True


def test_is_response_covered(endpoint_coverage_list: EndpointCoverageList):
    assert endpoint_coverage_list.is_response_covered is True


def test_is_response_covered_false():
    only_uncovered = EndpointCoverageList(
        root=[
            EndpointCoverage(
                name=EndpointName("delete_user"),
                method=HTTPMethod.DELETE,
                service=ServiceKey("admin-service"),
                status_code=StatusCode(403),
                query_parameters=[],
                is_request_covered=False,
                is_response_covered=False,
            )
        ]
    )
    assert only_uncovered.is_response_covered is False
