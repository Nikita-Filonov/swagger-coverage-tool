from pydantic import BaseModel, computed_field, Field, ConfigDict

from swagger_coverage_tool.src.history.models import CoverageHistory
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.percent import get_coverage_percent
from swagger_coverage_tool.src.tools.types import StatusCode, EndpointName, CoveragePercent, QueryParameter


class ServiceEndpointStatusCodeCoverage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: StatusCode
    is_covered: bool = Field(alias="isCovered")
    total_cases: int = Field(alias="totalCases")
    description: str | None = None
    is_response_covered: bool = Field(alias="isResponseCovered")


class ServiceEndpointQueryParametersCoverage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: QueryParameter
    is_covered: bool = Field(alias="isCovered")


class ServiceEndpointCoverage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: EndpointName
    method: HTTPMethod
    summary: str | None = None
    is_covered: bool = Field(alias="isCovered")
    total_cases: int = Field(alias="totalCases")
    status_codes: list[ServiceEndpointStatusCodeCoverage] = Field(alias="statusCodes")
    query_parameters: list[ServiceEndpointQueryParametersCoverage] = Field(alias="queryParameters")
    is_request_covered: bool = Field(alias="isRequestCovered")
    total_coverage_history: list[CoverageHistory] = Field(alias="totalCoverageHistory", default_factory=list)

    @computed_field(alias="totalCoverage")
    @property
    def total_coverage(self) -> CoveragePercent:
        total = len(self.status_codes)
        if not total:
            return CoveragePercent(0.0)

        covered = len(list(filter(lambda e: e.is_covered, self.status_codes)))
        return get_coverage_percent(total=total, covered=covered)


class ServiceCoverage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    endpoints: list[ServiceEndpointCoverage] = Field(default_factory=list)
    total_coverage_history: list[CoverageHistory] = Field(
        alias="totalCoverageHistory", default_factory=list
    )

    @computed_field(alias="totalCoverage")
    @property
    def total_coverage(self) -> CoveragePercent:
        total = len(self.endpoints)
        if not total:
            return CoveragePercent(0.0)

        covered = len(list(filter(lambda e: e.is_covered, self.endpoints)))
        return get_coverage_percent(total=total, covered=covered)
