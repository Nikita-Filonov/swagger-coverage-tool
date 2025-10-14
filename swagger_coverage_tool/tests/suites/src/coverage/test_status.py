import pytest

from swagger_coverage_tool.src.coverage.status import ServiceEndpointCoverageStatus


def test_is_missing_and_is_covered_properties():
    assert ServiceEndpointCoverageStatus.MISSING.is_missing
    assert not ServiceEndpointCoverageStatus.MISSING.is_covered

    assert ServiceEndpointCoverageStatus.COVERED.is_covered
    assert not ServiceEndpointCoverageStatus.COVERED.is_missing

    assert not ServiceEndpointCoverageStatus.UNCOVERED.is_covered
    assert not ServiceEndpointCoverageStatus.UNCOVERED.is_missing


def test_from_bool_returns_expected_status():
    assert ServiceEndpointCoverageStatus.from_bool(True) == ServiceEndpointCoverageStatus.COVERED
    assert ServiceEndpointCoverageStatus.from_bool(False) == ServiceEndpointCoverageStatus.UNCOVERED


@pytest.mark.parametrize(
    "value,has_item,expected",
    [
        (True, True, ServiceEndpointCoverageStatus.COVERED),
        (False, True, ServiceEndpointCoverageStatus.UNCOVERED),
        (True, False, ServiceEndpointCoverageStatus.MISSING),
        (False, False, ServiceEndpointCoverageStatus.MISSING),
    ]
)
def test_from_has_item_combinations(value: bool, has_item: bool, expected: ServiceEndpointCoverageStatus):
    result = ServiceEndpointCoverageStatus.from_has_item(value, has_item)
    assert result == expected
