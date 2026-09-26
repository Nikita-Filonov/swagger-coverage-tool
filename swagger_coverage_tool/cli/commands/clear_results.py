import click

from swagger_coverage_tool.config import get_settings
from swagger_coverage_tool.src.tracker.storage import SwaggerCoverageTrackerStorage


def clear_results_command():
    settings = get_settings()
    try:
        SwaggerCoverageTrackerStorage(settings).clear()
    except OSError as error:
        raise click.ClickException(str(error)) from error
