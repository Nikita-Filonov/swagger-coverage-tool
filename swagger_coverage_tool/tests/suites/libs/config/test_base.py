from pathlib import Path

from swagger_coverage_tool.libs.config.base import (
    ConfigEnv,
    get_config_file_or_default,
    get_env_config_file_or_default,
    get_json_config_file_or_default,
    get_yaml_config_file_or_default,
)


def test_get_config_file_or_default_uses_cwd_when_env_not_set(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CUSTOM_CONFIG_VAR", raising=False)

    result = get_config_file_or_default("CUSTOM_CONFIG_VAR", "config.yaml")

    assert result == str(tmp_path / "config.yaml")


def test_get_config_file_or_default_uses_env_when_set(monkeypatch, tmp_path: Path):
    custom_path = tmp_path / "custom" / "config.yaml"
    monkeypatch.setenv("CUSTOM_CONFIG_VAR", str(custom_path))

    result = get_config_file_or_default("CUSTOM_CONFIG_VAR", "config.yaml")

    assert result == str(custom_path)


def test_get_yaml_config_file_or_default(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(ConfigEnv.YAML, raising=False)

    assert get_yaml_config_file_or_default() == str(tmp_path / "swagger_coverage_config.yaml")


def test_get_yaml_config_file_or_default_from_env(monkeypatch, tmp_path: Path):
    custom_path = tmp_path / "ci" / "swagger_coverage_config.yaml"
    monkeypatch.setenv(ConfigEnv.YAML, str(custom_path))

    assert get_yaml_config_file_or_default() == str(custom_path)


def test_get_json_config_file_or_default(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(ConfigEnv.JSON, raising=False)

    assert get_json_config_file_or_default() == str(tmp_path / "swagger_coverage_config.json")


def test_get_env_config_file_or_default(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(ConfigEnv.ENV, raising=False)

    assert get_env_config_file_or_default() == str(tmp_path / ".env")
