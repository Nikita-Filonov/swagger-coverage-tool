import httpx

from swagger_coverage_tool.config import ServiceConfig
from swagger_coverage_tool.src.swagger.models import SwaggerNormalized, SwaggerRaw
from swagger_coverage_tool.src.tools.logger import get_logger

logger = get_logger("SWAGGER_LOADER")


class SwaggerLoader:
    def __init__(self, service: ServiceConfig):
        self.service = service

    def load(self) -> SwaggerNormalized:
        logger.info("Starting to load Swagger schema")

        if self.service.swagger_url:
            return self.load_from_url()

        if self.service.swagger_file:
            return self.load_from_file()

        logger.error("No Swagger URL or Swagger file specified")
        raise ValueError("No Swagger URL or Swagger file specified")

    def load_from_url(self) -> SwaggerNormalized:
        if not self.service.swagger_url:
            logger.error("Swagger URL is not provided")
            raise ValueError("Swagger URL is not provided")

        try:
            logger.info(f"Fetching Swagger schema from URL: {self.service.swagger_url}")
            response = httpx.get(str(self.service.swagger_url))

            if not response.is_success:
                logger.error(
                    f"Failed to fetch Swagger schema from URL: {self.service.swagger_url} "
                    f"with status {response.status_code}"
                )
                raise ValueError(f"Failed to fetch Swagger schema from URL: {self.service.swagger_url}")

            logger.info(f"Swagger schema successfully fetched from URL: {self.service.swagger_url}")
            raw = SwaggerRaw.model_validate_json(response.text)
            return raw.normalize()

        except httpx.RequestError as error:
            logger.error(f"Error during request to {self.service.swagger_url}: {error}")
            raise ValueError(f"Error fetching Swagger schema from URL: {self.service.swagger_url}")

    def load_from_file(self) -> SwaggerNormalized:
        if not self.service.swagger_file:
            logger.error("Swagger file is not provided")
            raise ValueError("Swagger file is not provided")

        if not self.service.swagger_file.exists():
            logger.error(f"Swagger file not found: {self.service.swagger_file}")
            raise ValueError(f"Swagger file not found: {self.service.swagger_file}")

        try:
            logger.info(f"Reading Swagger schema from file: {self.service.swagger_file}")
            raw = SwaggerRaw.model_validate_json(self.service.swagger_file.read_text())
            logger.info(f"Swagger schema successfully loaded from file: {self.service.swagger_file}")
            return raw.normalize()

        except Exception as e:
            logger.error(f"Error reading Swagger file {self.service.swagger_file}: {e}")
            raise ValueError(f"Error loading Swagger schema from file: {self.service.swagger_file}")
