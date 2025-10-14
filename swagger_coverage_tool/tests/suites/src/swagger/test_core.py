import json
from pathlib import Path

import httpx
import pytest
from pydantic import HttpUrl

from swagger_coverage_tool.config import ServiceConfig
from swagger_coverage_tool.src.swagger.core import SwaggerLoader
from swagger_coverage_tool.src.swagger.models import SwaggerNormalized, SwaggerRaw
from swagger_coverage_tool.src.tools.types import ServiceKey, ServiceName


# -------------------------------
# HELPERS
# -------------------------------

def make_service_config_with_url(url: str = "https://example.com/swagger.json") -> ServiceConfig:
    return ServiceConfig(
        key=ServiceKey("test-service"),
        name=ServiceName("Test Service"),
        swagger_url=HttpUrl(url)
    )


def make_service_config_with_file(path: Path) -> ServiceConfig:
    if not path.exists():
        path.write_text("{}")

    return ServiceConfig(
        key=ServiceKey("test-service"),
        name=ServiceName("Test Service"),
        swagger_file=path
    )


# -------------------------------
# TEST: load
# -------------------------------

def test_load_prefers_url(monkeypatch: pytest.MonkeyPatch):
    called = {}

    config = make_service_config_with_url()
    loader = SwaggerLoader(config)
    monkeypatch.setattr(loader, "load_from_url", lambda: called.setdefault("called", True))

    loader.load()
    assert called["called"]


def test_load_prefers_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    file_path = tmp_path / "swagger.json"
    file_path.write_text("{}")

    config = make_service_config_with_file(file_path)
    config.swagger_url = None

    loader = SwaggerLoader(config)
    monkeypatch.setattr(loader, "load_from_file", lambda: "loaded_from_file")

    result = loader.load()
    assert result == "loaded_from_file"


def test_load_raises_if_no_source(caplog):
    config = make_service_config_with_url()
    config.swagger_url = None
    config.swagger_file = None

    loader = SwaggerLoader(config)

    with pytest.raises(ValueError, match="No Swagger URL or Swagger file specified"):
        loader.load()

    assert any("No Swagger URL" in m for m in caplog.messages)


# -------------------------------
# TEST: load_from_url
# -------------------------------

def test_load_from_url_success(monkeypatch: pytest.MonkeyPatch):
    schema = {"paths": {"/users": {"get": {"responses": {"200": {"description": "ok"}}}}}}
    service = make_service_config_with_url()
    loader = SwaggerLoader(service)

    class DummyResponse:
        text = json.dumps(schema)
        is_success = True
        status_code = 200

    monkeypatch.setattr(httpx, "get", lambda url: DummyResponse())
    monkeypatch.setattr(SwaggerRaw, "normalize", lambda self: SwaggerNormalized(endpoints=[]))

    result = loader.load_from_url()
    assert isinstance(result, SwaggerNormalized)


def test_load_from_url_fails_on_bad_status(monkeypatch: pytest.MonkeyPatch):
    service = make_service_config_with_url("https://bad.example.com")
    loader = SwaggerLoader(service)

    class DummyResponse:
        text = "{}"
        is_success = False
        status_code = 404

    monkeypatch.setattr(httpx, "get", lambda _: DummyResponse())

    with pytest.raises(ValueError, match="Failed to fetch Swagger schema"):
        loader.load_from_url()


def test_load_from_url_handles_request_error(monkeypatch: pytest.MonkeyPatch):
    service = make_service_config_with_url("https://boom.example.com")
    loader = SwaggerLoader(service)

    def raise_request_error(_):
        raise httpx.RequestError("network down")

    monkeypatch.setattr(httpx, "get", raise_request_error)

    with pytest.raises(ValueError, match="Error fetching Swagger schema"):
        loader.load_from_url()


def test_load_from_url_without_url_raises():
    service = make_service_config_with_url()
    service.swagger_url = None  # просто обнуляем поле
    loader = SwaggerLoader(service)

    with pytest.raises(ValueError, match="Swagger URL is not provided"):
        loader.load_from_url()


# -------------------------------
# TEST: load_from_file
# -------------------------------

def test_load_from_file_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    schema = {"paths": {"/users": {"get": {"responses": {"200": {"description": "ok"}}}}}}
    file_path = tmp_path / "swagger.json"
    file_path.write_text(json.dumps(schema))

    config = make_service_config_with_file(file_path)
    config.swagger_url = None
    loader = SwaggerLoader(config)
    monkeypatch.setattr(SwaggerRaw, "normalize", lambda self: SwaggerNormalized(endpoints=[]))

    result = loader.load_from_file()
    assert isinstance(result, SwaggerNormalized)


def test_load_from_file_not_found(tmp_path: Path):
    config = make_service_config_with_file(tmp_path / "missing.json")
    config.swagger_url = None
    loader = SwaggerLoader(config)

    with pytest.raises(ValueError, match="Error loading Swagger schema from file"):
        loader.load_from_file()


def test_load_from_file_without_path_raises():
    config = make_service_config_with_url()
    config.swagger_file = None
    loader = SwaggerLoader(config)

    with pytest.raises(ValueError, match="Swagger file is not provided"):
        loader.load_from_file()


def test_load_from_file_invalid_json(tmp_path: Path):
    file_path = tmp_path / "swagger.json"
    file_path.write_text("{ invalid json }")

    config = make_service_config_with_file(file_path)
    config.swagger_url = None
    loader = SwaggerLoader(config)

    with pytest.raises(ValueError, match="Error loading Swagger schema"):
        loader.load_from_file()
