from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CoverageHistory(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    created_at: datetime = Field(alias="createdAt")
    total_coverage: float = Field(alias="totalCoverage")


class ServiceCoverageHistory(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_coverage_history: list[CoverageHistory] = Field(
        alias="totalCoverageHistory",
        default_factory=list
    )
    endpoints_total_coverage_history: dict[str, list[CoverageHistory]] = Field(
        alias="endpointsTotalCoverageHistory",
        default_factory=dict
    )


class CoverageHistoryState(BaseModel):
    services: dict[str, ServiceCoverageHistory] = Field(default_factory=dict)
