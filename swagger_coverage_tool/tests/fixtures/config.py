from pathlib import Path

import pytest
from pydantic import HttpUrl

from swagger_coverage_tool.config import Settings, ServiceConfig
from swagger_coverage_tool.src.tools.types import ServiceKey, ServiceName


@pytest.fixture
def settings() -> Settings:
    return Settings(
        services=[
            ServiceConfig(
                key=ServiceKey("test-service"),
                name=ServiceName("Test Service"),
                swagger_url=HttpUrl("https://example.com/swagger.json"),
            )
        ],
    )


@pytest.fixture
def coverage_history_settings(tmp_path: Path, settings: Settings) -> Settings:
    settings.results_dir = tmp_path / "results"
    settings.history_file = tmp_path / "history.json"
    settings.history_retention_limit = 3
    return settings


@pytest.fixture
def reports_settings(tmp_path: Path, coverage_history_settings: Settings) -> Settings:
    coverage_history_settings.json_report_file = tmp_path / "report.json"
    coverage_history_settings.html_report_file = tmp_path / "report.html"
    return coverage_history_settings
