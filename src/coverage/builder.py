from src.coverage.models import ServiceCoverage, ServiceEndpointStatusCodeCoverage, ServiceEndpointCoverage
from src.history.core import SwaggerServiceCoverageHistory
from src.libs.models import EndpointCoverageList
from src.swagger.models import SwaggerNormalized


class SwaggerServiceCoverageBuilder:
    def __init__(
            self,
            swagger: SwaggerNormalized,
            service_history: SwaggerServiceCoverageHistory,
            endpoint_coverage_list: EndpointCoverageList
    ):
        self.swagger = swagger
        self.service_history = service_history
        self.endpoint_coverage_list = endpoint_coverage_list

    def build(self) -> ServiceCoverage:
        result: ServiceCoverage = ServiceCoverage(endpoints=[])

        for endpoint in self.swagger.endpoints:
            coverage_list = self.endpoint_coverage_list.filter(
                name=endpoint.name,
                method=endpoint.method
            )

            service_endpoint_coverage = ServiceEndpointCoverage(
                name=endpoint.name,
                method=endpoint.method,
                summary=endpoint.summary,
                covered=coverage_list.is_covered,
                total_cases=len(coverage_list.root),
                status_codes=[
                    ServiceEndpointStatusCodeCoverage(
                        value=status_code.value,
                        covered=coverage_list.filter(status_code=status_code.value).is_covered,
                        description=status_code.description
                    )
                    for status_code in endpoint.status_codes
                ],
                total_coverage_history=[]
            )
            service_endpoint_coverage.total_coverage_history = self.service_history.get_endpoint_total_coverage_history(
                name=endpoint.name,
                method=endpoint.method,
                total_coverage=service_endpoint_coverage.total_coverage
            )

            result.endpoints.append(service_endpoint_coverage)

        result.total_coverage_history = self.service_history.get_total_coverage_history(result.total_coverage)

        return result
