from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.history.endpoint import build_endpoint_key
from swagger_coverage_tool.src.history.models import CoverageHistoryState, ServiceCoverageHistory
from swagger_coverage_tool.src.reports.models import CoverageReportState
from swagger_coverage_tool.src.tools.logger import get_logger

logger = get_logger("SWAGGER_COVERAGE_HISTORY_STORAGE")


class SwaggerCoverageHistoryStorage:
    def __init__(self, settings: Settings):
        self.settings = settings

    def load(self):
        history_file = self.settings.history_file

        if not history_file:
            logger.debug("No history file path provided, returning empty history state")
            return CoverageHistoryState()

        if not history_file.exists():
            logger.debug("History file not found, returning empty history state")
            return CoverageHistoryState()

        try:
            logger.info(f"Loading history from file: {history_file}")
            return CoverageHistoryState.model_validate_json(history_file.read_text())
        except Exception as error:
            logger.error(f"Error loading history from file {history_file}: {error}")
            return CoverageHistoryState()

    def save(self, state: CoverageHistoryState):
        history_file = self.settings.history_file

        try:
            history_file.touch(exist_ok=True)
            history_file.write_text(state.model_dump_json(by_alias=True))
            logger.info(f"History state saved to file: {history_file}")
        except Exception as error:
            logger.error(f"Error saving history to file {history_file}: {error}")

    def save_from_report(self, report: CoverageReportState):
        state = CoverageHistoryState(
            services={
                service.key: ServiceCoverageHistory(
                    total_coverage_history=report.services_coverage[service.key].total_coverage_history,
                    endpoints_total_coverage_history={
                        build_endpoint_key(endpoint.name, endpoint.method): endpoint.total_coverage_history
                        for endpoint in report.services_coverage[service.key].endpoints
                    }
                )
                for service in self.settings.services
            }
        )
        self.save(state)
