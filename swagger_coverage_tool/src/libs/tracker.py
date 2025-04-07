import functools
import inspect
from typing import Callable

import httpx
import requests

from swagger_coverage_tool.config import Settings, get_settings
from swagger_coverage_tool.src.libs.models import EndpointCoverage
from swagger_coverage_tool.src.libs.storage import SwaggerCoverageTrackerStorage
from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import EndpointName, ServiceKey, StatusCode


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

    def track_coverage_httpx(self, endpoint: str):
        def wrapper(func: Callable[..., httpx.Response]):
            signature = inspect.signature(func)

            @functools.wraps(func)
            def inner(*args, **kwargs):
                response = func(*args, **kwargs)

                self.storage.save(
                    EndpointCoverage(
                        name=EndpointName(endpoint),
                        method=response.request.method,
                        service=ServiceKey(self.service),
                        status_code=StatusCode(response.status_code),
                    )
                )

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

                self.storage.save(
                    EndpointCoverage(
                        name=EndpointName(endpoint),
                        method=response.request.method or HTTPMethod.GET,
                        service=ServiceKey(self.service),
                        status_code=StatusCode(response.status_code),
                    )
                )

                return response

            inner.__signature__ = signature
            return inner

        return wrapper
