from datetime import datetime

import pytest

from swagger_coverage_tool.src.coverage.models import (
    ServiceEndpointCoverage,
    ServiceEndpointStatusCodeCoverage,
    ServiceEndpointQueryParametersCoverage
)
from swagger_coverage_tool.src.coverage.status import ServiceEndpointCoverageStatus
from swagger_coverage_tool.src.history.models import CoverageHistory
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import StatusCode, QueryParameter, EndpointName, CoveragePercent


@pytest.fixture
def service_endpoint_coverage() -> ServiceEndpointCoverage:
    status_codes = [
        ServiceEndpointStatusCodeCoverage(
            value=StatusCode(200),
            total_cases=5,
            response_coverage=ServiceEndpointCoverageStatus.COVERED,
            status_code_coverage=ServiceEndpointCoverageStatus.COVERED,
        ),
        ServiceEndpointStatusCodeCoverage(
            value=StatusCode(400),
            total_cases=3,
            response_coverage=ServiceEndpointCoverageStatus.UNCOVERED,
            status_code_coverage=ServiceEndpointCoverageStatus.UNCOVERED,
        ),
        ServiceEndpointStatusCodeCoverage(
            value=StatusCode(500),
            total_cases=2,
            response_coverage=ServiceEndpointCoverageStatus.MISSING,
            status_code_coverage=ServiceEndpointCoverageStatus.COVERED,
        ),
    ]

    query_parameters = [
        ServiceEndpointQueryParametersCoverage(
            name=QueryParameter("limit"),
            coverage=ServiceEndpointCoverageStatus.COVERED,
        ),
        ServiceEndpointQueryParametersCoverage(
            name=QueryParameter("offset"),
            coverage=ServiceEndpointCoverageStatus.UNCOVERED,
        ),
    ]

    return ServiceEndpointCoverage(
        name=EndpointName("get_users"),
        method=HTTPMethod.GET,
        coverage=ServiceEndpointCoverageStatus.COVERED,
        total_cases=10,
        status_codes=status_codes,
        query_parameters=query_parameters,
        request_coverage=ServiceEndpointCoverageStatus.COVERED,
        total_coverage_history=[
            CoverageHistory(created_at=datetime.now(), total_coverage=CoveragePercent(75.0))
        ],
    )
