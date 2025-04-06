from http import HTTPMethod
from typing import Self

from pydantic import BaseModel, RootModel

from swagger_coverage_tool.src.tools.types import ServiceKey, StatusCode, EndpointName


class EndpointCoverage(BaseModel):
    name: EndpointName
    method: HTTPMethod
    service: ServiceKey
    status_code: StatusCode


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
    def is_covered(self) -> bool:
        return len(self.root) > 0
