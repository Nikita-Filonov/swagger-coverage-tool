from http import HTTPMethod
from typing import Self

from pydantic import BaseModel, RootModel

from swagger_coverage_tool.src.tools.types import ServiceKey, StatusCode, EndpointName, QueryParameter


class EndpointCoverage(BaseModel):
    name: EndpointName
    method: HTTPMethod
    service: ServiceKey
    status_code: StatusCode
    query_parameters: list[QueryParameter]
    is_request_covered: bool
    is_response_covered: bool


class EndpointCoverageList(RootModel):
    root: list[EndpointCoverage]

    def filter(
            self,
            name: EndpointName | None = None,
            method: HTTPMethod | None = None,
            service: ServiceKey | None = None,
            status_code: StatusCode | None = None
    ) -> Self:
        results = [
            coverage
            for coverage in self.root
            if (name is None or coverage.name.lower() == name.lower()) and
               (method is None or coverage.method.lower() == method.lower()) and
               (service is None or coverage.service.lower() == service.lower()) and
               (status_code is None or coverage.status_code == status_code)
        ]
        return EndpointCoverageList(root=results)

    @property
    def total_cases(self) -> int:
        return len(self.root)

    @property
    def unique_query_parameters(self) -> list[QueryParameter]:
        query_parameters = set(
            query_parameter
            for endpoint in self.root
            for query_parameter in endpoint.query_parameters
        )
        return list(query_parameters)

    @property
    def is_covered(self) -> bool:
        return len(self.root) > 0

    @property
    def is_request_covered(self) -> bool:
        return any(endpoint.is_request_covered for endpoint in self.root)

    @property
    def is_response_covered(self) -> bool:
        return any(endpoint.is_response_covered for endpoint in self.root)
