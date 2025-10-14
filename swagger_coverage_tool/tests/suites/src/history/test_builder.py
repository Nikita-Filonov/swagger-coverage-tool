from datetime import datetime, timedelta

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.history.builder import SwaggerServiceCoverageHistoryBuilder
from swagger_coverage_tool.src.history.endpoint import build_endpoint_key
from swagger_coverage_tool.src.history.models import CoverageHistory, ServiceCoverageHistory
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import CoveragePercent, EndpointName


# -------------------------------
# TEST: build_history
# -------------------------------

def test_build_history_creates_coverage_history(
        service_coverage_history_builder: SwaggerServiceCoverageHistoryBuilder
):
    result = service_coverage_history_builder.build_history(CoveragePercent(75.5))

    assert isinstance(result, CoverageHistory)
    assert result.total_coverage == 75.5
    assert abs((result.created_at - service_coverage_history_builder.created_at).total_seconds()) < 1


def test_build_history_clamps_to_100(
        service_coverage_history_builder: SwaggerServiceCoverageHistoryBuilder
):
    result = service_coverage_history_builder.build_history(CoveragePercent(150))
    assert result.total_coverage == 100


# -------------------------------
# TEST: append_history
# -------------------------------

def test_append_history_appends_and_sorts(
        service_coverage_history_builder: SwaggerServiceCoverageHistoryBuilder
):
    old_history = CoverageHistory(created_at=datetime.now() - timedelta(days=1), total_coverage=10)
    new_history = service_coverage_history_builder.append_history([old_history], CoveragePercent(90))

    assert len(new_history) == 2
    assert all(isinstance(item, CoverageHistory) for item in new_history)
    assert new_history[0].total_coverage == 10
    assert new_history[1].total_coverage == 90


def test_append_history_returns_empty_if_no_history_file(service_coverage_history: ServiceCoverageHistory):
    settings = Settings(services=[])
    settings.history_file = None
    builder = SwaggerServiceCoverageHistoryBuilder(service_coverage_history, settings)

    result = builder.append_history([], CoveragePercent(50))
    assert result == []


def test_append_history_does_not_add_zero_coverage(
        service_coverage_history_builder: SwaggerServiceCoverageHistoryBuilder
):
    history = [CoverageHistory(created_at=datetime.now(), total_coverage=10)]
    result = service_coverage_history_builder.append_history(history, CoveragePercent(0))
    assert result == history


# -------------------------------
# TEST: get_total_coverage_history
# -------------------------------

def test_get_total_coverage_history_adds_record(
        service_coverage_history_builder: SwaggerServiceCoverageHistoryBuilder
):
    result = service_coverage_history_builder.get_total_coverage_history(CoveragePercent(85))
    assert isinstance(result, list)
    assert result[-1].total_coverage == 85


# -------------------------------
# TEST: get_endpoint_total_coverage_history
# -------------------------------

def test_get_endpoint_total_coverage_history_creates_new_entry(
        service_coverage_history_builder: SwaggerServiceCoverageHistoryBuilder
):
    result = service_coverage_history_builder.get_endpoint_total_coverage_history(
        name=EndpointName("get_users"),
        method=HTTPMethod.GET,
        total_coverage=CoveragePercent(50),
    )
    assert isinstance(result, list)
    assert result[-1].total_coverage == 50


def test_get_endpoint_total_coverage_history_uses_existing_data(
        service_coverage_history_builder: SwaggerServiceCoverageHistoryBuilder
):
    endpoint_key = build_endpoint_key(EndpointName("get_users"), HTTPMethod.GET)

    old_history = [
        CoverageHistory(created_at=datetime.now() - timedelta(days=2), total_coverage=10)
    ]
    service_coverage_history_builder.history.endpoints_total_coverage_history[endpoint_key] = old_history

    result = service_coverage_history_builder.get_endpoint_total_coverage_history(
        name=EndpointName("get_users"),
        method=HTTPMethod.GET,
        total_coverage=CoveragePercent(20),
    )

    assert len(result) == 2
    assert result[0].total_coverage == 10
    assert result[1].total_coverage == 20
