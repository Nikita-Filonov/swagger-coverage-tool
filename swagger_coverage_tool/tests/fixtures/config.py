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
def coverage_history_settings(tmp_path: Path) -> Settings:
    config = Settings(
        services=[],
        results_dir=tmp_path / "results",
    )
    config.history_file = tmp_path / "history.json"
    config.history_retention_limit = 3
    return config
