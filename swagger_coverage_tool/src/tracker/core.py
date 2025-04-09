import functools
import inspect
from typing import Callable
from urllib.parse import urlparse, parse_qs

import httpx
import requests

from swagger_coverage_tool.config import Settings, get_settings
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.logger import get_logger
from swagger_coverage_tool.src.tools.types import EndpointName, ServiceKey, StatusCode, QueryParameter
from swagger_coverage_tool.src.tracker.models import EndpointCoverage
from swagger_coverage_tool.src.tracker.storage import SwaggerCoverageTrackerStorage

logger = get_logger("SWAGGER_COVERAGE_TRACKER")


class SwaggerCoverageTracker:
    def __init__(self, service: str, settings: Settings | None = None):
        self.service = service
        self.settings = settings or get_settings()

        services = [service_config.key for service_config in self.settings.services]
        if service not in services:
            raise ValueError(
                f"Service with key '{service}' not found in settings.\n"
                f"Available services: {', '.join(services) or []}"
            )

        self.storage = SwaggerCoverageTrackerStorage(self.settings)

    def build_endpoint_coverage_for_httpx(
            self,
            endpoint: str,
            response: httpx.Response
    ) -> EndpointCoverage | None:
        try:
            return EndpointCoverage(
                name=EndpointName(endpoint),
                method=response.request.method,
                service=ServiceKey(self.service),
                status_code=StatusCode(response.status_code),
                query_parameters=response.request.url.params.keys(),
                is_request_covered=bool(response.request.read()),
                is_response_covered=bool(response.content),
            )
        except Exception as error:
            logger.error(f"Unable to build endpoint coverage for HTTPX: {error}")

    def build_endpoint_coverage_for_requests(
            self,
            endpoint: str,
            response: requests.Response
    ) -> EndpointCoverage | None:
        try:
            parsed_url = urlparse(response.request.url)

            return EndpointCoverage(
                name=EndpointName(endpoint),
                method=response.request.method or HTTPMethod.GET,
                service=ServiceKey(self.service),
                status_code=StatusCode(response.status_code),
                query_parameters=list[QueryParameter](parse_qs(parsed_url.query).keys()),
                is_request_covered=bool(response.request.body),
                is_response_covered=bool(response.content),
            )
        except Exception as error:
            logger.error(f"Unable to build endpoint coverage for HTTPX: {error}")

    def track_coverage_httpx(self, endpoint: str):
        def wrapper(func: Callable[..., httpx.Response]):
            signature = inspect.signature(func)

            @functools.wraps(func)
            def inner(*args, **kwargs):
                response = func(*args, **kwargs)

                if coverage := self.build_endpoint_coverage_for_httpx(endpoint, response):
                    self.storage.save(coverage)

                return response

            inner.__signature__ = signature
            return inner

        return wrapper

    def track_coverage_requests(self, endpoint: str):
        def wrapper(func: Callable[..., requests.Response]):
            signature = inspect.signature(func)

            @functools.wraps(func)
            def inner(*args, **kwargs):
                response = func(*args, **kwargs)

                if coverage := self.build_endpoint_coverage_for_requests(endpoint, response):
                    self.storage.save(coverage)

                return response

            inner.__signature__ = signature
            return inner

        return wrapper
