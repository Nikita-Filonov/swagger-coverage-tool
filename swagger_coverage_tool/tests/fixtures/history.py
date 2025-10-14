import pytest

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.history.builder import SwaggerServiceCoverageHistoryBuilder
from swagger_coverage_tool.src.history.models import ServiceCoverageHistory
from swagger_coverage_tool.src.history.storage import SwaggerCoverageHistoryStorage


@pytest.fixture
def service_coverage_history() -> ServiceCoverageHistory:
    return ServiceCoverageHistory()


@pytest.fixture
def coverage_history_storage(coverage_history_settings: Settings) -> SwaggerCoverageHistoryStorage:
    return SwaggerCoverageHistoryStorage(coverage_history_settings)


@pytest.fixture
def service_coverage_history_builder(
        service_coverage_history: ServiceCoverageHistory,
        coverage_history_settings: Settings
) -> SwaggerServiceCoverageHistoryBuilder:
    return SwaggerServiceCoverageHistoryBuilder(
        history=service_coverage_history,
        settings=coverage_history_settings
    )
