import importlib.metadata
import importlib.resources
import os
from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import FilePath, HttpUrl, model_validator, BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    YamlConfigSettingsSource,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
)

from swagger_coverage_tool.src.tools.types import ServiceKey, ServiceName


class ServiceConfig(BaseModel):
    key: ServiceKey
    name: ServiceName
    tags: list[str] | None = None
    repository: HttpUrl | None = None
    swagger_url: HttpUrl | None = None
    swagger_file: FilePath | None = None

    @model_validator(mode='after')
    def validate_model(self) -> Self:
        if (not self.swagger_url) and (not self.swagger_file):
            raise ValueError(
                'Either `swagger_url` or `swagger_file` must be provided. '
                'Please provide one of them to load the Swagger configuration.'
            )

        return self


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='allow',

        env_file=os.path.join(os.getcwd(), ".env"),
        env_prefix="SWAGGER_COVERAGE_",
        env_file_encoding="utf-8",
        env_nested_delimiter=".",

        yaml_file=os.path.join(os.getcwd(), "swagger_coverage_config.yaml"),
        yaml_file_encoding="utf-8",

        json_file=os.path.join(os.getcwd(), "swagger_coverage_config.json"),
        json_file_encoding="utf-8"
    )

    services: list[ServiceConfig]

    results_dir: Path = Path(os.path.join(os.getcwd(), "coverage-results"))

    history_file: Path | None = Path(os.path.join(os.getcwd(), "coverage-history.json"))
    history_retention_limit: int = 30

    html_report_file: Path | None = Path(os.path.join(os.getcwd(), "index.html"))
    json_report_file: Path | None = Path(os.path.join(os.getcwd(), "coverage-report.json"))

    @property
    def html_report_template_file(self):
        try:
            return importlib.resources.files("swagger_coverage_tool.src.reports.templates") / "index.html"
        except importlib.metadata.PackageNotFoundError:
            return Path(os.path.join(os.getcwd(), "swagger_coverage_tool/src/reports/templates/index.html"))

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            YamlConfigSettingsSource(cls),
            JsonConfigSettingsSource(cls),
            env_settings,
            dotenv_settings,
            init_settings,
        )


@lru_cache(maxsize=None)
def get_settings() -> Settings:
    return Settings()
