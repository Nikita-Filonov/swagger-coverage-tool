from pydantic import BaseModel, Field

from src.tools.methods import HTTPMethod


class SwaggerNormalizedStatusCode(BaseModel):
    value: int
    description: str | None = None


class SwaggerNormalizedEndpoint(BaseModel):
    name: str
    method: HTTPMethod
    summary: str | None = None
    status_codes: list[SwaggerNormalizedStatusCode]


class SwaggerNormalized(BaseModel):
    endpoints: list[SwaggerNormalizedEndpoint]


class SwaggerRawResponse(BaseModel):
    description: str


class SwaggerRawEndpoint(BaseModel):
    summary: str | None = None
    responses: dict[str, SwaggerRawResponse]

    def get_status_codes(self) -> list[SwaggerNormalizedStatusCode]:
        return [
            SwaggerNormalizedStatusCode(value=int(status_code), description=response.description)
            for status_code, response in self.responses.items()
        ]


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
                        name=endpoint,
                        method=HTTPMethod(method.upper()),
                        summary=data.summary,
                        status_codes=data.get_status_codes()
                    )
                )

        return SwaggerNormalized(endpoints=endpoints)
