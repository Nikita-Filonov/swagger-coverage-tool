from pydantic import BaseModel, computed_field, Field, ConfigDict

from swagger_coverage_tool.src.coverage.status import ServiceEndpointCoverageStatus
from swagger_coverage_tool.src.history.models import CoverageHistory
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.percent import get_coverage_percent
from swagger_coverage_tool.src.tools.types import StatusCode, EndpointName, CoveragePercent, QueryParameter


class ServiceEndpointStatusCodeCoverage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: StatusCode
    total_cases: int = Field(alias="totalCases")
    description: str | None = None
    response_coverage: ServiceEndpointCoverageStatus = Field(alias="responseCoverage")
    status_code_coverage: ServiceEndpointCoverageStatus = Field(alias="statusCodeCoverage")


class ServiceEndpointQueryParametersCoverage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: QueryParameter
    coverage: ServiceEndpointCoverageStatus


class ServiceEndpointCoverage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: EndpointName
    method: HTTPMethod
    summary: str | None = None
    coverage: ServiceEndpointCoverageStatus
    total_cases: int = Field(alias="totalCases")
    status_codes: list[ServiceEndpointStatusCodeCoverage] = Field(alias="statusCodes")
    query_parameters: list[ServiceEndpointQueryParametersCoverage] = Field(alias="queryParameters")
    request_coverage: ServiceEndpointCoverageStatus = Field(alias="requestCoverage")
    total_coverage_history: list[CoverageHistory] = Field(alias="totalCoverageHistory", default_factory=list)

    @property
    def number_of_covered_responses(self) -> int:
        return len(list(
            filter(
                lambda e: e.response_coverage.is_covered and not e.response_coverage.is_missing,
                self.status_codes
            )
        ))

    @property
    def number_of_covered_status_codes(self) -> int:
        return len(list(filter(lambda e: e.status_code_coverage.is_covered, self.status_codes)))

    @property
    def number_of_covered_query_parameters(self) -> int:
        return len(list(filter(lambda e: e.coverage.is_covered, self.query_parameters)))

    @property
    def total_status_codes(self) -> int:
        return len(self.status_codes)

    @property
    def total_responses(self) -> int:
        return len(list(filter(lambda e: not e.response_coverage.is_missing, self.status_codes)))

    @property
    def total_query_parameters(self) -> int:
        return len(self.query_parameters)

    @computed_field(alias="totalCoverage")
    @property
    def total_coverage(self) -> CoveragePercent:
        total_units: int = 0
        covered_units: int = 0

        total_units += self.total_responses
        covered_units += self.number_of_covered_responses

        total_units += self.total_status_codes
        covered_units += self.number_of_covered_status_codes

        if not self.request_coverage.is_missing:
            total_units += 1
            covered_units += int(self.request_coverage.is_covered)

        total_units += self.total_query_parameters
        covered_units += self.number_of_covered_query_parameters

        return get_coverage_percent(total=total_units, covered=covered_units)


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

        covered = len(list(filter(lambda e: e.coverage.is_covered, self.endpoints)))
        return get_coverage_percent(total=total, covered=covered)
