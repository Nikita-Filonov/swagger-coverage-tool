from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, FilePath, HttpUrl

from swagger_coverage_tool.config import ServiceConfig, Settings
from swagger_coverage_tool.src.coverage.models import ServiceCoverage
from swagger_coverage_tool.src.tools.types import ServiceKey


class CoverageReportServiceConfig(ServiceConfig):
    model_config = ConfigDict(populate_by_name=True)

    swagger_url: HttpUrl | None = Field(alias="swaggerUrl", default=None)
    swagger_file: FilePath | None = Field(alias="swaggerFile", default=None)


class CoverageReportConfig(BaseModel):
    services: list[CoverageReportServiceConfig]


class CoverageReportState(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config: CoverageReportConfig
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.now)
    services_coverage: dict[ServiceKey, ServiceCoverage] = Field(alias="servicesCoverage", default_factory=dict)

    @classmethod
    def init(cls, settings: Settings):
        return CoverageReportState(
            config=CoverageReportConfig(
                services=[CoverageReportServiceConfig(**service.model_dump()) for service in settings.services]
            )
        )
