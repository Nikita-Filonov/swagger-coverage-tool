import json
from pathlib import Path

import pytest

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.tracker.models import EndpointCoverage, EndpointCoverageList
from swagger_coverage_tool.src.tracker.storage import SwaggerCoverageTrackerStorage


# -------------------------------
# TEST: clear
# -------------------------------

def test_clear_removes_result_json_and_preserves_other_files(
        settings: Settings,
        endpoint_coverage: EndpointCoverage,
        coverage_tracker_storage: SwaggerCoverageTrackerStorage,
        caplog: pytest.LogCaptureFixture,
) -> None:
    settings.history_file = settings.results_dir / "history.json"
    settings.json_report_file = settings.results_dir / "report.json"
    settings.history_file.write_text("history", encoding="utf-8")
    settings.json_report_file.write_text("report", encoding="utf-8")
    (settings.results_dir / "notes.txt").write_text("keep", encoding="utf-8")
    (settings.results_dir / "other.json").write_text("remove", encoding="utf-8")
    nested_dir = settings.results_dir / "nested.json"
    nested_dir.mkdir()
    (nested_dir / "other.json").write_text("keep", encoding="utf-8")
    coverage_tracker_storage.save(endpoint_coverage)
    coverage_tracker_storage.save(endpoint_coverage)

    coverage_tracker_storage.clear()

    assert sorted(file.name for file in settings.results_dir.glob("*.json")) == [
        "history.json", "nested.json", "report.json"
    ]
    assert (settings.results_dir / "notes.txt").read_text(encoding="utf-8") == "keep"
    assert (nested_dir / "other.json").read_text(encoding="utf-8") == "keep"
    assert any("Removed 3 coverage files" in message for message in caplog.messages)


def test_clear_succeeds_when_directory_is_missing(
        settings: Settings,
        coverage_tracker_storage: SwaggerCoverageTrackerStorage,
) -> None:
    settings.results_dir = settings.results_dir / "missing"

    coverage_tracker_storage.clear()

    assert not settings.results_dir.exists()


def test_clear_without_history_or_json_report(
        settings: Settings,
        endpoint_coverage: EndpointCoverage,
        coverage_tracker_storage: SwaggerCoverageTrackerStorage,
) -> None:
    settings.history_file = None
    settings.json_report_file = None
    coverage_tracker_storage.save(endpoint_coverage)

    coverage_tracker_storage.clear()

    assert settings.results_dir.is_dir()
    assert list(settings.results_dir.iterdir()) == []


def test_clear_raises_when_path_is_not_a_directory(
        settings: Settings,
        coverage_tracker_storage: SwaggerCoverageTrackerStorage,
        tmp_path: Path,
) -> None:
    settings.results_dir = tmp_path / "results.json"
    settings.results_dir.write_text("keep", encoding="utf-8")

    with pytest.raises(NotADirectoryError, match="not a directory"):
        coverage_tracker_storage.clear()

    assert settings.results_dir.read_text(encoding="utf-8") == "keep"


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
