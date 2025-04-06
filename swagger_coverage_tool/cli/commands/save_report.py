from swagger_coverage_tool.config import get_settings
from swagger_coverage_tool.src.coverage.builder import SwaggerServiceCoverageBuilder
from swagger_coverage_tool.src.history.core import SwaggerServiceCoverageHistory
from swagger_coverage_tool.src.history.models import ServiceCoverageHistory
from swagger_coverage_tool.src.history.storage import SwaggerCoverageHistoryStorage
from swagger_coverage_tool.src.libs.storage import SwaggerCoverageTrackerStorage
from swagger_coverage_tool.src.reports.models import CoverageReportState
from swagger_coverage_tool.src.reports.storage import SwaggerReportsStorage
from swagger_coverage_tool.src.swagger.core import SwaggerLoader
from swagger_coverage_tool.src.tools.logger import get_logger

logger = get_logger("SAVE_REPORT")


def save_report_command():
    logger.info("Starting to save the report")

    settings = get_settings()

    reports_storage = SwaggerReportsStorage(settings=settings)
    history_storage = SwaggerCoverageHistoryStorage(settings=settings)
    tracker_storage = SwaggerCoverageTrackerStorage(settings=settings)

    report_state = CoverageReportState.init(settings)
    history_state = history_storage.load()
    tracker_state = tracker_storage.load()
    for service in settings.services:
        swagger_loader = SwaggerLoader(service)

        service_coverage_history = SwaggerServiceCoverageHistory(
            history=history_state.services.get(service.key, ServiceCoverageHistory()),
            settings=settings,
        )
        service_coverage_builder = SwaggerServiceCoverageBuilder(
            swagger=swagger_loader.load(),
            service_history=service_coverage_history,
            endpoint_coverage_list=tracker_state
        )
        report_state.services_coverage[service.key] = service_coverage_builder.build()

    history_storage.save_from_report(report_state)
    reports_storage.save_json_report(report_state)
    reports_storage.save_html_report(report_state)

    logger.info("Report saving process completed")
