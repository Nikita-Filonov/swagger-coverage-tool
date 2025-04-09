from typing import Self

from swagger_coverage_tool.config import ServiceConfig, Settings
from swagger_coverage_tool.src.coverage.models import (
    ServiceCoverage,
    ServiceEndpointCoverage,
    ServiceEndpointStatusCodeCoverage,
    ServiceEndpointQueryParametersCoverage
)
from swagger_coverage_tool.src.history.core import SwaggerServiceCoverageHistory
from swagger_coverage_tool.src.history.models import CoverageHistoryState, ServiceCoverageHistory
from swagger_coverage_tool.src.swagger.models import (
    SwaggerNormalized,
    SwaggerNormalizedEndpoint,
    SwaggerNormalizedStatusCode
)
from swagger_coverage_tool.src.tools.types import ServiceKey
from swagger_coverage_tool.src.tracker.models import EndpointCoverageList


class SwaggerServiceCoverageBuilder:
    def __init__(
            self,
            service: ServiceKey,
            swagger: SwaggerNormalized,
            service_history: SwaggerServiceCoverageHistory,
            endpoint_coverage_list: EndpointCoverageList
    ):
        self.service = service
        self.swagger = swagger
        self.service_history = service_history
        self.endpoint_coverage_list = endpoint_coverage_list

    @classmethod
    def from_service_factory(
            cls,
            service: ServiceConfig,
            swagger: SwaggerNormalized,
            settings: Settings,
            history_state: CoverageHistoryState,
            endpoint_coverage_list: EndpointCoverageList,
    ) -> Self:
        return SwaggerServiceCoverageBuilder(
            service=service.key,
            swagger=swagger,
            service_history=SwaggerServiceCoverageHistory(
                history=history_state.services.get(service.key, ServiceCoverageHistory()),
                settings=settings,
            ),
            endpoint_coverage_list=endpoint_coverage_list,
        )

    @classmethod
    def build_status_code_coverage(
            cls,
            endpoint: SwaggerNormalizedEndpoint,
            status_code: SwaggerNormalizedStatusCode,
            coverage_list: EndpointCoverageList,
    ) -> ServiceEndpointStatusCodeCoverage:
        status_code_coverage = coverage_list.filter(status_code=status_code.value)

        return ServiceEndpointStatusCodeCoverage(
            value=status_code.value,
            is_covered=status_code_coverage.is_covered,
            total_cases=status_code_coverage.total_cases,
            description=status_code.description,
            is_response_covered=status_code_coverage.is_response_covered if endpoint.has_request else True
        )

    @classmethod
    def build_status_codes(
            cls,
            endpoint: SwaggerNormalizedEndpoint,
            coverage_list: EndpointCoverageList
    ) -> list[ServiceEndpointStatusCodeCoverage]:
        return [
            cls.build_status_code_coverage(
                endpoint=endpoint,
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
                is_covered=query_parameter in unique_query_parameters
            )
            for query_parameter in endpoint.query_parameters
        ]

    def build(self) -> ServiceCoverage:
        result: ServiceCoverage = ServiceCoverage(endpoints=[])

        for endpoint in self.swagger.endpoints:
            coverage_list = self.endpoint_coverage_list.filter(
                name=endpoint.name,
                method=endpoint.method,
                service=self.service
            )

            service_endpoint_coverage = ServiceEndpointCoverage(
                name=endpoint.name,
                method=endpoint.method,
                summary=endpoint.summary,
                is_covered=coverage_list.is_covered,
                total_cases=coverage_list.total_cases,
                status_codes=self.build_status_codes(endpoint, coverage_list),
                query_parameters=self.build_query_parameters(endpoint, coverage_list),
                is_request_covered=coverage_list.is_request_covered if endpoint.has_request else True,
            )
            service_endpoint_coverage.total_coverage_history = self.service_history.get_endpoint_total_coverage_history(
                name=endpoint.name,
                method=endpoint.method,
                total_coverage=service_endpoint_coverage.total_coverage
            )

            result.endpoints.append(service_endpoint_coverage)

        result.total_coverage_history = self.service_history.get_total_coverage_history(result.total_coverage)

        return result
