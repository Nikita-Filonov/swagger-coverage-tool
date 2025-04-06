def get_coverage_percent(total: int, covered: int) -> float:
    return round((covered / total) * 100, 2) if total else 0.0
