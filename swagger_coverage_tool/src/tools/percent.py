from swagger_coverage_tool.src.tools.types import CoveragePercent


def get_coverage_percent(total: int, covered: int) -> CoveragePercent:
    return CoveragePercent(round((covered / total) * 100, 2) if total else 0.0)
