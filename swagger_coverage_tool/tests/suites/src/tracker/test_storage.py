import json
from pathlib import Path

import pytest

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.tracker.models import EndpointCoverage, EndpointCoverageList
from swagger_coverage_tool.src.tracker.storage import SwaggerCoverageTrackerStorage


# -------------------------------
# TEST: save
# -------------------------------

def test_save_creates_file(
        settings: Settings,
        endpoint_coverage: EndpointCoverage,
        coverage_tracker_storage: SwaggerCoverageTrackerStorage
):
    coverage_tracker_storage.save(endpoint_coverage)

    files = list(settings.results_dir.glob("*.json"))
    assert len(files) == 1

    content = json.loads(files[0].read_text())
    assert content["name"] == "get_user"
    assert content["service"] == "user-service"
    assert content["status_code"] == 200


def test_save_creates_dir_if_missing(
        caplog,
        tmp_path: Path,
        settings: Settings,
        endpoint_coverage: EndpointCoverage
):
    settings.results_dir = tmp_path / "nonexistent"
    storage = SwaggerCoverageTrackerStorage(settings)

    assert not settings.results_dir.exists()
    storage.save(endpoint_coverage)

    assert settings.results_dir.exists()
    assert any("creating" in msg for msg in caplog.messages)
    assert list(settings.results_dir.glob("*.json"))


def test_save_handles_write_error(
        caplog,
        monkeypatch: pytest.MonkeyPatch,
        endpoint_coverage: EndpointCoverage,
        coverage_tracker_storage: SwaggerCoverageTrackerStorage
):
    def mock_open(*args, **kwargs):
        raise OSError("Disk full")

    monkeypatch.setattr("builtins.open", mock_open)

    coverage_tracker_storage.save(endpoint_coverage)

    assert any("Error saving coverage data" in msg for msg in caplog.messages)


# -------------------------------
# TEST: load
# -------------------------------

def test_load_returns_empty_if_dir_missing(caplog, tmp_path: Path, settings: Settings):
    settings.results_dir = tmp_path / "missing"
    storage = SwaggerCoverageTrackerStorage(settings)

    result = storage.load()

    assert isinstance(result, EndpointCoverageList)
    assert result.root == []
    assert any("does not exist" in message for message in caplog.messages)


def test_load_reads_all_json_files(
        endpoint_coverage: EndpointCoverage,
        coverage_tracker_storage: SwaggerCoverageTrackerStorage
):
    for _ in range(3):
        coverage_tracker_storage.save(endpoint_coverage)

    result = coverage_tracker_storage.load()

    assert isinstance(result, EndpointCoverageList)
    assert len(result.root) == 3
    assert all(isinstance(e, EndpointCoverage) for e in result.root)
    assert result.root[0].name == "get_user"


def test_load_ignores_non_json_files(
        settings: Settings,
        endpoint_coverage: EndpointCoverage,
        coverage_tracker_storage: SwaggerCoverageTrackerStorage
):
    coverage_tracker_storage.save(endpoint_coverage)
    (settings.results_dir / "note.txt").write_text("not json")

    result = coverage_tracker_storage.load()

    assert len(result.root) == 1
    assert result.root[0].name == "get_user"
