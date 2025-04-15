from typing import Any

from pydantic import BaseModel, Field

from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import StatusCode, EndpointName, QueryParameter


class SwaggerNormalizedStatusCode(BaseModel):
    value: StatusCode
    description: str | None = None
    has_response: bool = False


class SwaggerNormalizedEndpoint(BaseModel):
    name: EndpointName
    method: HTTPMethod
    summary: str | None = None
    has_request: bool = False
    status_codes: list[SwaggerNormalizedStatusCode]
    query_parameters: list[QueryParameter] | None = None


class SwaggerNormalized(BaseModel):
    endpoints: list[SwaggerNormalizedEndpoint]


class SwaggerRawResponse(BaseModel):
    content: dict[str, Any] | None = None
    description: str


class SwaggerRawParameter(BaseModel):
    name: str
    inside: str = Field(alias="in")


class SwaggerRawEndpoint(BaseModel):
    summary: str | None = None
    request: dict[str, Any] | None = Field(alias="requestBody", default=None)
    responses: dict[str, SwaggerRawResponse]
    parameters: list[SwaggerRawParameter] | None = None

    def get_status_codes(self) -> list[SwaggerNormalizedStatusCode]:
        try:
            return [
                SwaggerNormalizedStatusCode(
                    value=StatusCode(int(status_code)),
                    description=response.description,
                    has_response=bool(response.content)
                )
                for status_code, response in self.responses.items()
            ]
        except ValueError:
            return []

    def get_query_parameters(self) -> list[QueryParameter]:
        raw_parameters = filter(lambda p: p.inside == "query", self.parameters or [])
        return [QueryParameter(parameter.name) for parameter in raw_parameters]


class SwaggerRaw(BaseModel):
    endpoints: dict[str, dict[str, SwaggerRawEndpoint]] = Field(alias="paths")

    def normalize(self):
        if not self.endpoints:
            raise ValueError("No endpoints found in Swagger schema")

        endpoints: list[SwaggerNormalizedEndpoint] = []

        for endpoint, methods in self.endpoints.items():
            for method, data in methods.items():
                endpoints.append(
                    SwaggerNormalizedEndpoint(
                        name=EndpointName(endpoint),
                        method=HTTPMethod(method.upper()),
                        summary=data.summary,
                        has_request=bool(data.request),
                        status_codes=data.get_status_codes(),
                        query_parameters=data.get_query_parameters()
                    )
                )

        return SwaggerNormalized(endpoints=endpoints)
