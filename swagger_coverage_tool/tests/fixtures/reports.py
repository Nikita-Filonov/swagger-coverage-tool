from datetime import datetime

import pytest

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.coverage.models import ServiceCoverage, ServiceEndpointCoverage
from swagger_coverage_tool.src.coverage.status import ServiceEndpointCoverageStatus
from swagger_coverage_tool.src.history.models import CoverageHistory
from swagger_coverage_tool.src.reports.models import CoverageReportState
from swagger_coverage_tool.src.reports.storage import SwaggerReportsStorage
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import ServiceKey, CoveragePercent, EndpointName


@pytest.fixture
def coverage_report_state(coverage_history_settings: Settings) -> CoverageReportState:
    service_key = ServiceKey("test-service")

    fake_service_coverage = ServiceCoverage(
        total_coverage_history=[
            CoverageHistory(created_at=datetime.now(), total_coverage=CoveragePercent(88.0))
        ],
        endpoints=[
            ServiceEndpointCoverage(
                name=EndpointName("get_users"),
                method=HTTPMethod.GET,
                coverage=ServiceEndpointCoverageStatus.COVERED,
                total_cases=1,
                status_codes=[],
                query_parameters=[],
                request_coverage=ServiceEndpointCoverageStatus.COVERED,
                total_coverage_history=[
                    CoverageHistory(
                        created_at=datetime.now(),
                        total_coverage=CoveragePercent(55.0),
                    )
                ],
            )
        ],
    )

    report = CoverageReportState.init(coverage_history_settings)
    report.services_coverage = {service_key: fake_service_coverage}
    return report


@pytest.fixture
def reports_storage(reports_settings: Settings) -> SwaggerReportsStorage:
    return SwaggerReportsStorage(reports_settings)
