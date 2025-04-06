from pydantic import BaseModel, computed_field, Field, ConfigDict

from swagger_coverage_tool.src.history.models import CoverageHistory
from swagger_coverage_tool.src.tools.methods import HTTPMethod
from swagger_coverage_tool.src.tools.percent import get_coverage_percent


class ServiceEndpointStatusCodeCoverage(BaseModel):
    value: int
    covered: bool
    description: str | None = None


class ServiceEndpointCoverage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    method: HTTPMethod
    summary: str | None = None
    covered: bool
    total_cases: int = Field(alias="totalCases")
    status_codes: list[ServiceEndpointStatusCodeCoverage] = Field(alias="statusCodes")
    total_coverage_history: list[CoverageHistory] = Field(alias="totalCoverageHistory", default_factory=list)

    @computed_field(alias="totalCoverage")
    @property
    def total_coverage(self) -> float:
        total = len(self.status_codes)
        if not total:
            return 0.0

        covered = len(list(filter(lambda e: e.covered, self.status_codes)))
        return get_coverage_percent(total=total, covered=covered)


class ServiceCoverage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    endpoints: list[ServiceEndpointCoverage] = Field(default_factory=list)
    total_coverage_history: list[CoverageHistory] = Field(
        alias="totalCoverageHistory", default_factory=list
    )

    @computed_field(alias="totalCoverage")
    @property
    def total_coverage(self) -> float:
        total = len(self.endpoints)
        if not total:
            return 0.0

        covered = len(list(filter(lambda e: e.covered, self.endpoints)))
        return get_coverage_percent(total=total, covered=covered)
