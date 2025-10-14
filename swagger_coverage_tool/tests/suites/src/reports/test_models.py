from datetime import datetime

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.reports.models import (
    CoverageReportState,
    CoverageReportConfig,
    CoverageReportServiceConfig,
)


def test_init_creates_valid_report_state(settings: Settings):
    state = CoverageReportState.init(settings)

    assert isinstance(state, CoverageReportState)
    assert isinstance(state.config, CoverageReportConfig)
    assert isinstance(state.created_at, datetime)
    assert isinstance(state.services_coverage, dict)
    assert state.services_coverage == {}

    assert len(state.config.services) == len(settings.services)
    first_service = state.config.services[0]
    assert isinstance(first_service, CoverageReportServiceConfig)
    assert first_service.key == settings.services[0].key
    assert first_service.name == settings.services[0].name
    assert str(first_service.swagger_url) == str(settings.services[0].swagger_url)


def test_init_with_empty_settings():
    empty_settings = Settings(services=[])
    state = CoverageReportState.init(empty_settings)

    assert isinstance(state, CoverageReportState)
    assert state.config.services == []
    assert state.services_coverage == {}
    assert isinstance(state.created_at, datetime)


def test_init_creates_distinct_instances(settings: Settings):
    state1 = CoverageReportState.init(settings)
    state2 = CoverageReportState.init(settings)

    assert state1 is not state2
    assert state1.created_at != state2.created_at
    assert state1.config.services[0].key == state2.config.services[0].key
    assert isinstance(state1.config.services[0], CoverageReportServiceConfig)
