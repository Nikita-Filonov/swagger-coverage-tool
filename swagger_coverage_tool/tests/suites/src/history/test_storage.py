import json
from datetime import datetime
from pathlib import Path

import pytest

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.history.endpoint import build_endpoint_key
from swagger_coverage_tool.src.history.models import CoverageHistoryState, ServiceCoverageHistory, CoverageHistory
from swagger_coverage_tool.src.history.storage import SwaggerCoverageHistoryStorage
from swagger_coverage_tool.src.reports.models import CoverageReportState
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import ServiceKey, CoveragePercent, EndpointName


# -------------------------------
# TEST: load
# -------------------------------

def test_load_returns_empty_if_no_history_file(
        coverage_history_storage: SwaggerCoverageHistoryStorage,
        coverage_history_settings: Settings,
):
    coverage_history_settings.history_file = None

    result = coverage_history_storage.load()
    assert isinstance(result, CoverageHistoryState)
    assert result.services == {}


def test_load_returns_empty_if_file_not_exists(
        coverage_history_storage: SwaggerCoverageHistoryStorage,
        coverage_history_settings: Settings,
):
    assert not coverage_history_settings.history_file.exists()

    result = coverage_history_storage.load()
    assert isinstance(result, CoverageHistoryState)
    assert result.services == {}


def test_load_reads_and_parses_valid_json(
        coverage_history_storage: SwaggerCoverageHistoryStorage,
        coverage_history_settings: Settings,
):
    state = CoverageHistoryState(
        services={
            ServiceKey("test-service"): ServiceCoverageHistory(
                total_coverage_history=[
                    CoverageHistory(created_at=datetime.now(), total_coverage=CoveragePercent(90.0))
                ]
            )
        }
    )
    coverage_history_settings.history_file.write_text(state.model_dump_json(by_alias=True))

    result = coverage_history_storage.load()
    assert isinstance(result, CoverageHistoryState)
    assert "test-service" in result.services


def test_load_handles_invalid_json(
        coverage_history_storage: SwaggerCoverageHistoryStorage,
        coverage_history_settings: Settings,
):
    coverage_history_settings.history_file.write_text("{ invalid json }")

    result = coverage_history_storage.load()
    assert isinstance(result, CoverageHistoryState)
    assert result.services == {}


# -------------------------------
# TEST: save
# -------------------------------

def test_save_creates_and_writes_file(
        coverage_history_storage: SwaggerCoverageHistoryStorage,
        coverage_history_settings: Settings,
):
    state = CoverageHistoryState(
        services={
            ServiceKey("test-service"): ServiceCoverageHistory(
                total_coverage_history=[
                    CoverageHistory(created_at=datetime.now(), total_coverage=CoveragePercent(75.0))
                ]
            )
        }
    )

    coverage_history_storage.save(state)

    assert coverage_history_settings.history_file.exists()
    content = json.loads(coverage_history_settings.history_file.read_text())
    assert "services" in content


def test_save_logs_error(
        caplog,
        monkeypatch: pytest.MonkeyPatch,
        coverage_history_storage: SwaggerCoverageHistoryStorage,
):
    state = CoverageHistoryState()

    def mock_write_text(_):
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", mock_write_text)
    coverage_history_storage.save(state)

    assert any("Error saving history" in message for message in caplog.messages)


# -------------------------------
# TEST: save_from_report
# -------------------------------

def test_save_from_report_builds_correct_state(
        monkeypatch: pytest.MonkeyPatch,
        coverage_report_state: CoverageReportState,
        coverage_history_storage: SwaggerCoverageHistoryStorage,
):
    called = {}

    def mock_save(state: CoverageHistoryState):
        called["state"] = state

    monkeypatch.setattr(coverage_history_storage, "save", mock_save)

    coverage_history_storage.save_from_report(coverage_report_state)

    assert "state" in called
    state = called["state"]

    assert isinstance(state, CoverageHistoryState)

    service_key = ServiceKey("test-service")
    assert service_key in state.services

    service_state = state.services[service_key]
    assert isinstance(service_state, ServiceCoverageHistory)
    assert service_state.total_coverage_history[0].total_coverage == 88.0

    key = build_endpoint_key(EndpointName("get_users"), HTTPMethod.GET)
    assert key in service_state.endpoints_total_coverage_history
    assert service_state.endpoints_total_coverage_history[key][0].total_coverage == 55.0
