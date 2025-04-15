from swagger_coverage_tool.src.tools.http import HTTPMethod
from swagger_coverage_tool.src.tools.types import EndpointName


def build_endpoint_key(name: EndpointName, method: HTTPMethod) -> str:
    return f'{method}_{name}'
