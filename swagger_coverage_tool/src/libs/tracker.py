from typing import Callable

import httpx
import requests

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.libs.models import EndpointCoverage
from swagger_coverage_tool.src.libs.storage import SwaggerCoverageTrackerStorage


class SwaggerCoverageTracker:
    def __init__(self, settings: Settings):
        self.storage = SwaggerCoverageTrackerStorage(settings)
        self.settings = settings

    def track_coverage_httpx(self, endpoint: str):
        def wrapper(func: Callable[..., httpx.Response]):
            def inner(*args, **kwargs):
                response = func(*args, **kwargs)

                self.storage.save(
                    EndpointCoverage(
                        name=endpoint,
                        method=response.request.method,
                        status_code=response.status_code,
                    )
                )

                return response

            return inner

        return wrapper

    def track_coverage_requests(self, endpoint: str):
        def wrapper(func: Callable[..., requests.Response]):
            def inner(*args, **kwargs):
                response = func(*args, **kwargs)

                self.storage.save(
                    EndpointCoverage(
                        name=endpoint,
                        method=response.request.method,
                        status_code=response.status_code,
                    )
                )

                return response

            return inner

        return wrapper
