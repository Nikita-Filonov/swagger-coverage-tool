from swagger_coverage_tool.src.coverage.models import (
    ServiceCoverage,
    ServiceEndpointCoverage,
    ServiceEndpointStatusCodeCoverage,
    ServiceEndpointQueryParametersCoverage
)
from swagger_coverage_tool.src.coverage.status import ServiceEndpointCoverageStatus
from swagger_coverage_tool.src.history.builder import SwaggerServiceCoverageHistoryBuilder
from swagger_coverage_tool.src.swagger.models import (
    SwaggerNormalized,
    SwaggerNormalizedEndpoint,
    SwaggerNormalizedStatusCode
)
from swagger_coverage_tool.src.tracker.models import EndpointCoverageList


class SwaggerServiceCoverageBuilder:
    def __init__(
            self,
            swagger: SwaggerNormalized,
            history_builder: SwaggerServiceCoverageHistoryBuilder,
            endpoint_coverage_list: EndpointCoverageList
    ):
        self.swagger = swagger
        self.history_builder = history_builder
        self.endpoint_coverage_list = endpoint_coverage_list

    @classmethod
    def build_status_code_coverage(
            cls,
            status_code: SwaggerNormalizedStatusCode,
            coverage_list: EndpointCoverageList,
    ) -> ServiceEndpointStatusCodeCoverage:
        status_code_coverage = coverage_list.filter(status_code=status_code.value)

        return ServiceEndpointStatusCodeCoverage(
            value=status_code.value,
            total_cases=status_code_coverage.total_cases,
            description=status_code.description,
            response_coverage=ServiceEndpointCoverageStatus.from_has_item(
                status_code_coverage.is_response_covered, status_code.has_response
            ),
            status_code_coverage=ServiceEndpointCoverageStatus.from_bool(status_code_coverage.is_covered)
        )

    @classmethod
    def build_status_codes(
            cls,
            endpoint: SwaggerNormalizedEndpoint,
            coverage_list: EndpointCoverageList
    ) -> list[ServiceEndpointStatusCodeCoverage]:
        return [
            cls.build_status_code_coverage(
                status_code=status_code,
                coverage_list=coverage_list
            )
            for status_code in endpoint.status_codes
        ]

    @classmethod
    def build_query_parameters(
            cls,
            endpoint: SwaggerNormalizedEndpoint,
            coverage_list: EndpointCoverageList
    ) -> list[ServiceEndpointQueryParametersCoverage]:
        unique_query_parameters = coverage_list.unique_query_parameters

        return [
            ServiceEndpointQueryParametersCoverage(
                name=query_parameter,
                coverage=ServiceEndpointCoverageStatus.from_bool(query_parameter in unique_query_parameters)
            )
            for query_parameter in endpoint.query_parameters
        ]

    def build(self) -> ServiceCoverage:
        result: ServiceCoverage = ServiceCoverage(endpoints=[])

        for endpoint in self.swagger.endpoints:
            coverage_list = self.endpoint_coverage_list.filter(name=endpoint.name, method=endpoint.method)

            service_endpoint_coverage = ServiceEndpointCoverage(
                name=endpoint.name,
                method=endpoint.method,
                summary=endpoint.summary,
                coverage=ServiceEndpointCoverageStatus.from_bool(coverage_list.is_covered),
                total_cases=coverage_list.total_cases,
                status_codes=self.build_status_codes(endpoint, coverage_list),
                query_parameters=self.build_query_parameters(endpoint, coverage_list),
                request_coverage=ServiceEndpointCoverageStatus.from_has_item(
                    coverage_list.is_request_covered, endpoint.has_request
                )
            )
            service_endpoint_coverage.total_coverage_history = self.history_builder.get_endpoint_total_coverage_history(
                name=endpoint.name,
                method=endpoint.method,
                total_coverage=service_endpoint_coverage.total_coverage
            )

            result.endpoints.append(service_endpoint_coverage)

        result.total_coverage_history = self.history_builder.get_total_coverage_history(result.total_coverage)

        return result
