import pytest

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.history.builder import SwaggerServiceCoverageHistoryBuilder
from swagger_coverage_tool.src.history.models import ServiceCoverageHistory


@pytest.fixture
def service_coverage_history() -> ServiceCoverageHistory:
    return ServiceCoverageHistory()


@pytest.fixture
def service_coverage_history_builder(
        service_coverage_history: ServiceCoverageHistory,
        coverage_history_settings: Settings
) -> SwaggerServiceCoverageHistoryBuilder:
    return SwaggerServiceCoverageHistoryBuilder(
        history=service_coverage_history,
        settings=coverage_history_settings
    )
