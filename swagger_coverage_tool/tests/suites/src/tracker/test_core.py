import httpx
import pytest
import requests

from swagger_coverage_tool import SwaggerCoverageTracker
from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.tools.types import ServiceKey, StatusCode
from swagger_coverage_tool.src.tracker.models import EndpointCoverage


# -------------------------------
# TEST: init
# -------------------------------

def test_init_with_valid_service(settings: Settings):
    tracker = SwaggerCoverageTracker("test-service", settings)
    assert tracker.service == "test-service"
    assert tracker.storage is not None


def test_init_with_invalid_service(settings: Settings):
    with pytest.raises(ValueError, match="not found"):
        SwaggerCoverageTracker("unknown-service", settings)


# -------------------------------
# TEST: build_endpoint_coverage_for_httpx
# -------------------------------

def test_build_endpoint_coverage_for_httpx(
        httpx_response: httpx.Response,
        coverage_tracker: SwaggerCoverageTracker,
):
    coverage = coverage_tracker.build_endpoint_coverage_for_httpx("get_users", httpx_response)

    assert isinstance(coverage, EndpointCoverage)
    assert coverage.name == "get_users"
    assert coverage.method == "GET"
    assert coverage.service == ServiceKey("test-service")
    assert coverage.status_code == StatusCode(200)
    assert "id" in coverage.query_parameters
    assert coverage.is_request_covered is False
    assert coverage.is_response_covered is True


def test_build_endpoint_coverage_for_httpx_handles_error(caplog, coverage_tracker: SwaggerCoverageTracker):
    bad_response = object()
    result = coverage_tracker.build_endpoint_coverage_for_httpx("broken", bad_response)  # noqa
    assert result is None
    assert any("Unable to build endpoint coverage" in message for message in caplog.messages)


# -------------------------------
# TEST: build_endpoint_coverage_for_requests
# -------------------------------

def test_build_endpoint_coverage_for_requests(
        coverage_tracker: SwaggerCoverageTracker,
        requests_response: requests.Response
):
    coverage = coverage_tracker.build_endpoint_coverage_for_requests("create_user", requests_response)

    assert isinstance(coverage, EndpointCoverage)
    assert coverage.name == "create_user"
    assert coverage.method == "POST"
    assert coverage.status_code == StatusCode(201)
    assert "verbose" in coverage.query_parameters
    assert coverage.is_request_covered is True
    assert coverage.is_response_covered is True


def test_build_endpoint_coverage_for_requests_handles_error(caplog, coverage_tracker: SwaggerCoverageTracker):
    bad_response = object()
    result = coverage_tracker.build_endpoint_coverage_for_requests("broken", bad_response)  # noqa
    assert result is None
    assert any("Unable to build endpoint coverage" in msg for msg in caplog.messages)


# -------------------------------
# TEST: track_coverage_httpx
# -------------------------------

def test_track_coverage_httpx_calls_storage_save(
        monkeypatch: pytest.MonkeyPatch,
        httpx_response: httpx.Response,
        coverage_tracker: SwaggerCoverageTracker,
):
    called = {}

    def mock_save(coverage: EndpointCoverage):
        called["saved"] = True
        assert isinstance(coverage, EndpointCoverage)

    monkeypatch.setattr(coverage_tracker.storage, "save", mock_save)

    @coverage_tracker.track_coverage_httpx("get_users")
    def fetch():
        return httpx_response

    response = fetch()
    assert response is httpx_response
    assert called.get("saved")


# -------------------------------
# TEST: track_coverage_requests
# -------------------------------

def test_track_coverage_requests_calls_storage_save(
        monkeypatch: pytest.MonkeyPatch,
        coverage_tracker: SwaggerCoverageTracker,
        requests_response: requests.Response,
):
    called = {}

    def mock_save(coverage: EndpointCoverage):
        called["saved"] = True
        assert isinstance(coverage, EndpointCoverage)

    monkeypatch.setattr(coverage_tracker.storage, "save", mock_save)

    @coverage_tracker.track_coverage_requests("create_user")
    def send_request():
        return requests_response

    response = send_request()
    assert response is requests_response
    assert called.get("saved")
