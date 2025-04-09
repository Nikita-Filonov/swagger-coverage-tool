import uuid

from swagger_coverage_tool.config import Settings
from swagger_coverage_tool.src.tools.logger import get_logger
from swagger_coverage_tool.src.tracker.models import EndpointCoverageList, EndpointCoverage

logger = get_logger("SWAGGER_COVERAGE_TRACKER_STORAGE")


class SwaggerCoverageTrackerStorage:
    def __init__(self, settings: Settings):
        self.settings = settings

    def load(self) -> EndpointCoverageList:
        results_dir = self.settings.results_dir
        logger.info(f"Loading coverage results from directory: {results_dir}")

        if not results_dir.exists():
            logger.warning(f"Results directory does not exist: {results_dir}")
            return EndpointCoverageList(root=[])

        results = [
            EndpointCoverage.model_validate_json(file.read_text())
            for file in results_dir.glob("*.json") if file.is_file()
        ]

        logger.info(f"Loaded {len(results)} coverage files from directory: {results_dir}")
        return EndpointCoverageList(root=results)

    def save(self, coverage: EndpointCoverage):
        results_dir = self.settings.results_dir

        if not results_dir.exists():
            logger.info(f"Results directory does not exist, creating: {results_dir}")
            results_dir.mkdir(exist_ok=True)

        result_file = results_dir.joinpath(f'{uuid.uuid4()}.json')

        try:
            with open(result_file, 'w+') as file:
                file.write(coverage.model_dump_json())

        except Exception as error:
            logger.error(f"Error saving coverage data to file {result_file}: {error}")
