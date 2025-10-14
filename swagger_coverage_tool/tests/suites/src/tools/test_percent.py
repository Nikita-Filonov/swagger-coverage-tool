import pytest

from swagger_coverage_tool.src.tools.percent import get_coverage_percent


@pytest.mark.parametrize(
    "total, covered, expected",
    [
        (100, 50, 50.0),
        (100, 100, 100.0),
        (100, 0, 0.0),
        (0, 0, 0.0),
        (200, 123, 61.5),
        (3, 2, 66.67),
    ],
)
def test_get_coverage_percent(total: int, covered: int, expected: float):
    result = get_coverage_percent(total, covered)
    assert result == expected
