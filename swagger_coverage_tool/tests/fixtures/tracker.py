from pathlib import Path

import pytest

from swagger_coverage_tool import SwaggerCoverageTracker
from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import ServiceKey, EndpointName, QueryParameter, StatusCode
from swagger_coverage_tool.src.tracker.models import EndpointCoverageList, EndpointCoverage
from swagger_coverage_tool.src.tracker.storage import SwaggerCoverageTrackerStorage


@pytest.fixture
def endpoint_coverage() -> EndpointCoverage:
    return EndpointCoverage(
        name=EndpointName("get_user"),
        method=HTTPMethod.GET,
        service=ServiceKey("user-service"),
        status_code=StatusCode(200),
        query_parameters=[QueryParameter("id")],
        is_request_covered=True,
        is_response_covered=False,
    )


@pytest.fixture
def endpoint_coverage_list() -> EndpointCoverageList:
    data = [
        EndpointCoverage(
            name=EndpointName("get_users"),
            method=HTTPMethod.GET,
            service=ServiceKey("user-service"),
            status_code=StatusCode(200),
            query_parameters=[QueryParameter("limit"), QueryParameter("offset")],
            is_request_covered=True,
            is_response_covered=True,
        ),
        EndpointCoverage(
            name=EndpointName("create_user"),
            method=HTTPMethod.POST,
            service=ServiceKey("user-service"),
            status_code=StatusCode(201),
            query_parameters=[QueryParameter("verbose")],
            is_request_covered=True,
            is_response_covered=False,
        ),
        EndpointCoverage(
            name=EndpointName("delete_user"),
            method=HTTPMethod.DELETE,
            service=ServiceKey("admin-service"),
            status_code=StatusCode(403),
            query_parameters=[],
            is_request_covered=False,
            is_response_covered=False,
        ),
    ]
    return EndpointCoverageList(root=data)


@pytest.fixture
def coverage_tracker(tmp_path: Path, settings: Settings) -> SwaggerCoverageTracker:
    settings.results_dir = tmp_path / "results"
    settings.results_dir.mkdir(parents=True, exist_ok=True)
    return SwaggerCoverageTracker("test-service", settings)


@pytest.fixture
def coverage_tracker_storage(tmp_path: Path, settings: Settings) -> SwaggerCoverageTrackerStorage:
    settings.results_dir = tmp_path / "results"
    settings.results_dir.mkdir(parents=True, exist_ok=True)
    return SwaggerCoverageTrackerStorage(settings)
