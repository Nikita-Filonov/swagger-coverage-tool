from datetime import datetime

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.history.models import CoverageHistory, ServiceCoverageHistory
from swagger_coverage_tool.src.tools.types import CoveragePercent


class SwaggerServiceCoverageHistory:
    def __init__(self, history: ServiceCoverageHistory, settings: Settings):
        self.history = history
        self.settings = settings
        self.created_at = datetime.now()

    def build_history(self, total_coverage: CoveragePercent) -> CoverageHistory:
        total_coverage = min(total_coverage, 100)
        return CoverageHistory(created_at=self.created_at, total_coverage=total_coverage)

    def append_history(self, history: list[CoverageHistory], total_coverage: CoveragePercent) -> list[CoverageHistory]:
        if not self.settings.history_file:
            return []

        if total_coverage <= 0:
            return history

        result = [*history, self.build_history(total_coverage)]
        result = sorted(result, key=lambda r: r.created_at)

        return result[-self.settings.history_retention_limit:]

    def get_total_coverage_history(self, total_coverage: CoveragePercent) -> list[CoverageHistory]:
        return self.append_history(self.history.total_coverage_history, total_coverage)

    def get_endpoint_total_coverage_history(
            self,
            name: str,
            method: str,
            total_coverage: CoveragePercent
    ) -> list[CoverageHistory]:
        history = self.history.endpoints_total_coverage_history.get(f'{method}_{name}', [])
        return self.append_history(history, total_coverage)
