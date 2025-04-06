import click

from swagger_coverage_tool.cli.commands.copy_report import copy_report_command
from swagger_coverage_tool.cli.commands.print_config import print_config_command
from swagger_coverage_tool.cli.commands.save_report import save_report_command


@click.command(name="save-report")
def save_report():
    save_report_command()


@click.command(name="copy-report")
def copy_report():
    copy_report_command()


@click.command(name="print-config")
def show_config():
    print_config_command()


@click.group()
def cli():
    pass


cli.add_command(save_report)
cli.add_command(copy_report)
cli.add_command(show_config)

if __name__ == '__main__':
    cli()
