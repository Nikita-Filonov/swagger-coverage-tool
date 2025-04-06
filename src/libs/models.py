from typing import Self

from pydantic import BaseModel, RootModel


class EndpointCoverage(BaseModel):
    name: str
    method: str
    status_code: int


class EndpointCoverageList(RootModel):
    root: list[EndpointCoverage]

    def filter(
            self,
            name: str | None = None,
            method: str | None = None,
            status_code: int | None = None
    ) -> Self:
        results = [
            coverage
            for coverage in self.root
            if (name is None or coverage.name.lower() == name.lower()) and
               (method is None or coverage.method.lower() == method.lower()) and
               (status_code is None or coverage.status_code == status_code)
        ]
        return EndpointCoverageList(root=results)

    @property
    def is_covered(self) -> bool:
        return len(self.root) > 0
