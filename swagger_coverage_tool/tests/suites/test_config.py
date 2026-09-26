import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from swagger_coverage_tool.config import ServiceConfig, Settings, get_settings


@pytest.fixture
def config_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    files = {
        "yaml_file": tmp_path / "swagger_coverage_config.yaml",
        "json_file": tmp_path / "swagger_coverage_config.json",
        "env_file": tmp_path / ".env",
    }
    for source, path in files.items():
        monkeypatch.setitem(Settings.model_config, source, str(path))
    return files


def test_settings_loads_yaml_before_json_and_init_values(config_files: dict[str, Path]) -> None:
    config_files["yaml_file"].write_text(
        "services:\n"
        "  - key: yaml-service\n"
        "    name: YAML Service\n"
        "    swagger_url: https://yaml.example.com\n"
        "results_dir: ./yaml-results\n",
        encoding="utf-8",
    )
    config_files["json_file"].write_text(
        json.dumps({
            "services": [{"key": "json-service", "name": "JSON Service", "swagger_url": "https://json.example.com"}],
            "history_retention_limit": 12,
        }),
        encoding="utf-8",
    )

    settings = Settings(
        services=[{"key": "init-service", "name": "Init Service", "swagger_url": "https://init.example.com"}],
        history_retention_limit=3,
    )

    assert [service.key for service in settings.services] == ["yaml-service"]
    assert settings.results_dir == Path("yaml-results")
    assert settings.history_retention_limit == 12


def test_settings_loads_json_when_yaml_is_missing(config_files: dict[str, Path]) -> None:
    config_files["json_file"].write_text(
        json.dumps({
            "services": [{"key": "json-service", "name": "JSON Service", "swagger_url": "https://json.example.com"}],
            "history_file": None,
        }),
        encoding="utf-8",
    )

    settings = Settings()

    assert settings.services[0].key == "json-service"
    assert settings.history_file is None


def test_settings_env_overrides_dotenv_and_init_values(
        config_files: dict[str, Path],
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_files["env_file"].write_text(
        'SWAGGER_COVERAGE_SERVICES=[{"key":"dotenv-service","name":"Dotenv Service","swagger_url":"https://dotenv.example.com"}]\n'
        "SWAGGER_COVERAGE_HISTORY_RETENTION_LIMIT=7\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(
        "SWAGGER_COVERAGE_SERVICES",
        json.dumps([{"key": "env-service", "name": "Env Service", "swagger_url": "https://env.example.com"}]),
    )

    settings = Settings(
        services=[{"key": "init-service", "name": "Init Service", "swagger_url": "https://init.example.com"}],
        history_retention_limit=3,
    )

    assert [service.key for service in settings.services] == ["env-service"]
    assert settings.history_retention_limit == 7


def test_settings_finds_packaged_html_template(config_files: dict[str, Path]) -> None:
    settings = Settings(services=[])

    assert settings.html_report_template_file.is_file()
    assert '<script id="state" type="application/json">' in settings.html_report_template_file.read_text(
        encoding="utf-8"
    )


def test_get_settings_reloads_config_after_cache_is_cleared(config_files: dict[str, Path]) -> None:
    def write_config(key: str) -> None:
        config_files["json_file"].write_text(
            json.dumps({"services": [{"key": key, "name": key, "swagger_url": "https://example.com"}]}),
            encoding="utf-8",
        )

    write_config("first-service")
    get_settings.cache_clear()
    try:
        first = get_settings()
        write_config("second-service")

        assert get_settings() is first
        assert first.services[0].key == "first-service"

        get_settings.cache_clear()
        assert get_settings().services[0].key == "second-service"
    finally:
        get_settings.cache_clear()


def test_service_requires_a_swagger_source() -> None:
    with pytest.raises(ValidationError, match="Either `swagger_url` or `swagger_file` must be provided"):
        ServiceConfig(key="test-service", name="Test Service")


def test_service_accepts_a_local_swagger_file(tmp_path: Path) -> None:
    swagger_file = tmp_path / "swagger.json"
    swagger_file.write_text('{"paths": {}}', encoding="utf-8")

    service = ServiceConfig(key="test-service", name="Test Service", swagger_file=swagger_file)

    assert service.swagger_file == swagger_file
    assert service.swagger_url is None


def test_service_rejects_a_missing_swagger_file(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="Path does not point to a file"):
        ServiceConfig(key="test-service", name="Test Service", swagger_file=tmp_path / "missing.json")


def test_settings_loads_results_directory_from_environment(
        config_files: dict[str, Path],
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "SWAGGER_COVERAGE_SERVICES",
        json.dumps([{"key": "test-service", "name": "Test Service", "swagger_url": "https://example.com"}]),
    )
    monkeypatch.setenv("SWAGGER_COVERAGE_RESULTS_DIR", "./custom-results")

    settings = Settings()

    assert settings.services[0].key == "test-service"
    assert settings.results_dir == Path("custom-results")
