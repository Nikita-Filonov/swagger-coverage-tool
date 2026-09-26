import json
import re
from pathlib import Path

import httpx
import pytest
from click.testing import CliRunner

from swagger_coverage_tool.cli.main import cli
from swagger_coverage_tool.config import ServiceConfig, Settings
from swagger_coverage_tool.src.history.endpoint import build_endpoint_key
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tracker.core import SwaggerCoverageTracker

runner = CliRunner()


def test_clear_results_reports_deletion_error(
        settings: Settings,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    file = settings.results_dir / "123e4567-e89b-42d3-a456-426614174000.json"
    file.write_text("keep", encoding="utf-8")
    monkeypatch.setattr("swagger_coverage_tool.cli.commands.clear_results.get_settings", lambda: settings)

    def fail_unlink(self: Path) -> None:
        raise OSError("permission denied")

    monkeypatch.setattr(Path, "unlink", fail_unlink)

    result = runner.invoke(cli, ["clear-results"])

    assert result.exit_code != 0
    assert "permission denied" in result.output
    assert file.exists()


def test_print_config_outputs_resolved_settings(
        settings: Settings,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr("swagger_coverage_tool.cli.commands.print_config.get_settings", lambda: settings)

    result = runner.invoke(cli, ["print-config"])

    assert result.exit_code == 0
    config = json.loads(next(record.message for record in caplog.records if record.name == "PRINT_CONFIG"))
    assert config["services"][0]["key"] == "test-service"
    assert config["results_dir"] == str(settings.results_dir)


def test_copy_report_updates_template(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "submodules/swagger-coverage-report/build/index.html"
    destination = tmp_path / "swagger_coverage_tool/src/reports/templates/index.html"
    source.parent.mkdir(parents=True)
    destination.parent.mkdir(parents=True)
    source.write_text("<html>new template</html>", encoding="utf-8")
    destination.write_text("old template", encoding="utf-8")

    result = runner.invoke(cli, ["copy-report"])

    assert result.exit_code == 0
    assert destination.read_text(encoding="utf-8") == "<html>new template</html>"


def test_copy_report_keeps_template_when_build_is_missing(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    destination = tmp_path / "swagger_coverage_tool/src/reports/templates/index.html"
    destination.parent.mkdir(parents=True)
    destination.write_text("current template", encoding="utf-8")

    result = runner.invoke(cli, ["copy-report"])

    assert result.exit_code == 0
    assert destination.read_text(encoding="utf-8") == "current template"


def test_copy_report_logs_copy_error(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "submodules/swagger-coverage-report/build/index.html"
    source.parent.mkdir(parents=True)
    source.write_text("new template", encoding="utf-8")

    def fail_copy(*args, **kwargs) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("swagger_coverage_tool.cli.commands.copy_report.shutil.copy", fail_copy)

    result = runner.invoke(cli, ["copy-report"])

    assert result.exit_code == 0
    assert any("Error copying the report: disk full" in message for message in caplog.messages)


@pytest.fixture
def report_template(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    template = tmp_path / "template.html"
    template.write_text(
        '<html><body><script id="state" type="application/json">OLD_STATE</script></body></html>',
        encoding="utf-8",
    )
    monkeypatch.setattr(Settings, "html_report_template_file", template)
    return template


@pytest.fixture
def local_swagger(tmp_path: Path) -> Path:
    swagger_file = tmp_path / "swagger.json"
    swagger_file.write_text(
        json.dumps({
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {"description": "Users", "content": {"application/json": {}}},
                            "404": {"description": "Not found"},
                        },
                        "parameters": [{"name": "id", "in": "query"}],
                    },
                    "post": {
                        "requestBody": {"content": {"application/json": {}}},
                        "responses": {
                            "201": {"description": "Created", "content": {"application/json": {}}},
                        },
                    },
                },
                "/health": {"get": {"responses": {"200": {"description": "Healthy"}}}},
            },
        }),
        encoding="utf-8",
    )
    return swagger_file


def track_request(
        tracker: SwaggerCoverageTracker,
        method: str = "GET",
        status_code: int = 200,
        query: str = "",
        content: bytes = b"",
        request_content: bytes = b"",
) -> None:
    @tracker.track_coverage_httpx("/users")
    def request() -> httpx.Response:
        return httpx.Response(
            status_code,
            request=httpx.Request(method, f"https://example.com/users{query}", content=request_content),
            content=content,
        )

    request()


def test_save_report_builds_separate_service_reports_and_embeds_json(
        reports_settings: Settings,
        report_template: Path,
        local_swagger: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    reports_settings.services = [
        ServiceConfig(key=key, name=key, swagger_file=local_swagger)
        for key in ("test-service", "second-service", "empty-service")
    ]
    monkeypatch.setattr("swagger_coverage_tool.cli.commands.save_report.get_settings", lambda: reports_settings)

    first = SwaggerCoverageTracker(service="test-service", settings=reports_settings)
    track_request(first, query="?id=5", content=b"users")
    track_request(first, query="?id=6", content=b"users")
    track_request(first, method="POST", status_code=201, content=b"created", request_content=b"payload")
    second = SwaggerCoverageTracker(service="second-service", settings=reports_settings)
    track_request(second)

    result = runner.invoke(cli, ["save-report"])

    assert result.exit_code == 0, result.output
    report = json.loads(reports_settings.json_report_file.read_text(encoding="utf-8"))
    assert set(report["servicesCoverage"]) == {"test-service", "second-service", "empty-service"}

    first_coverage = report["servicesCoverage"]["test-service"]
    endpoints = {(endpoint["name"], endpoint["method"]): endpoint for endpoint in first_coverage["endpoints"]}
    users = endpoints[("/users", "GET")]
    assert users["totalCases"] == 2
    assert [status["totalCases"] for status in users["statusCodes"]] == [2, 0]
    assert users["statusCodes"][0]["responseCoverage"] == "COVERED"
    assert users["queryParameters"] == [{"name": "id", "coverage": "COVERED"}]
    assert endpoints[("/users", "POST")]["totalCases"] == 1
    assert endpoints[("/users", "POST")]["requestCoverage"] == "COVERED"
    assert endpoints[("/health", "GET")]["coverage"] == "UNCOVERED"

    second_coverage = report["servicesCoverage"]["second-service"]
    assert second_coverage["endpoints"][0]["totalCases"] == 1
    empty_coverage = report["servicesCoverage"]["empty-service"]
    assert empty_coverage["totalCoverage"] == 0
    assert empty_coverage["totalCoverageHistory"] == []
    assert all(endpoint["totalCases"] == 0 for endpoint in empty_coverage["endpoints"])

    html = reports_settings.html_report_file.read_text(encoding="utf-8")
    match = re.search(r'<script id="state" type="application/json">(.*?)</script>', html)
    assert match is not None
    assert json.loads(match.group(1)) == report
    history = json.loads(reports_settings.history_file.read_text(encoding="utf-8"))
    assert history["services"]["test-service"]["totalCoverageHistory"] == first_coverage["totalCoverageHistory"]


def test_clear_results_between_reports_excludes_previous_run(
        reports_settings: Settings,
        report_template: Path,
        local_swagger: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    reports_settings.services = [ServiceConfig(key="test-service", name="Test Service", swagger_file=local_swagger)]
    monkeypatch.setattr("swagger_coverage_tool.cli.commands.clear_results.get_settings", lambda: reports_settings)
    monkeypatch.setattr("swagger_coverage_tool.cli.commands.save_report.get_settings", lambda: reports_settings)
    tracker = SwaggerCoverageTracker(service="test-service", settings=reports_settings)

    track_request(tracker, query="?id=5", content=b"users")
    assert runner.invoke(cli, ["save-report"]).exit_code == 0
    previous_history = reports_settings.history_file.read_bytes()
    previous_report = reports_settings.json_report_file.read_bytes()
    assert runner.invoke(cli, ["clear-results"]).exit_code == 0
    assert reports_settings.history_file.read_bytes() == previous_history
    assert reports_settings.json_report_file.read_bytes() == previous_report
    track_request(tracker, status_code=404)
    assert runner.invoke(cli, ["save-report"]).exit_code == 0

    report = json.loads(reports_settings.json_report_file.read_text(encoding="utf-8"))
    service = report["servicesCoverage"]["test-service"]
    endpoint = service["endpoints"][0]
    assert endpoint["totalCases"] == 1
    assert [status["totalCases"] for status in endpoint["statusCodes"]] == [0, 1]
    assert [entry["totalCoverage"] for entry in endpoint["totalCoverageHistory"]] == [75, 25]
    assert len(service["totalCoverageHistory"]) == 2
    history = json.loads(reports_settings.history_file.read_text(encoding="utf-8"))
    endpoint_key = build_endpoint_key("/users", HTTPMethod.GET)
    assert history["services"]["test-service"]["endpointsTotalCoverageHistory"][endpoint_key] == endpoint["totalCoverageHistory"]


def test_save_report_preserves_history_across_runs_with_retention_limit(
        reports_settings: Settings,
        report_template: Path,
        local_swagger: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    reports_settings.services = [ServiceConfig(key="test-service", name="Test Service", swagger_file=local_swagger)]
    reports_settings.history_retention_limit = 2
    monkeypatch.setattr("swagger_coverage_tool.cli.commands.save_report.get_settings", lambda: reports_settings)
    tracker = SwaggerCoverageTracker(service="test-service", settings=reports_settings)

    for status_code, query, content in [(200, "", b""), (200, "", b"users"), (404, "?id=5", b"")]:
        track_request(tracker, status_code=status_code, query=query, content=content)
        result = runner.invoke(cli, ["save-report"])
        assert result.exit_code == 0, result.output

    report = json.loads(reports_settings.json_report_file.read_text(encoding="utf-8"))
    service = report["servicesCoverage"]["test-service"]
    endpoint = service["endpoints"][0]
    assert endpoint["totalCases"] == 3
    assert [entry["totalCoverage"] for entry in endpoint["totalCoverageHistory"]] == [50, 100]
    assert len(service["totalCoverageHistory"]) == 2

    history = json.loads(reports_settings.history_file.read_text(encoding="utf-8"))
    assert history["services"]["test-service"]["totalCoverageHistory"] == service["totalCoverageHistory"]
    endpoint_key = build_endpoint_key("/users", HTTPMethod.GET)
    assert history["services"]["test-service"]["endpointsTotalCoverageHistory"][endpoint_key] == endpoint["totalCoverageHistory"]
