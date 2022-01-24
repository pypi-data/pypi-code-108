# Copyright 2019 Splunk Inc. All rights reserved.
"""
Splunk AppInspect certification events listeners/handlers for precert mode
"""
import collections
import logging
import sys
import threading

import click
import painter

import splunk_appinspect
import splunk_appinspect.main

from . import listener

logger = logging.getLogger(__name__)


class CertStatusListener(listener.Listener):
    """
    pre cert mode certification status listener class
    """

    def __init__(
        self,
        stream=sys.stdout,
        max_report_messages=splunk_appinspect.main.MAX_MESSAGES_DEFAULT,
    ):
        """
        :param stream The output to write to
        :param max_messages the maximum number of messages to return for a single check
        """
        self.lock = threading.Lock()
        self.stream = stream
        self.counts = collections.defaultdict(int)
        self.failures = []
        self.exit_status = 0
        self.max_messages = max_report_messages

    @staticmethod
    def on_start_app(app):
        """Returns None

        :param app (App) The app object representing the Splunk Application.
        """
        command_line_output = f"Validating: {app.name} Version: {app.version}"
        click.echo(command_line_output)

    def on_finish_check(self, check, reporter):
        """Returns None

        :param check (Check) The check object that was executed.
        :param reporter (Reporter) The reporter object that contains the results
            of the check that was executed.
        """
        with self.lock:
            result = reporter.state()
            glyph = click.style(
                splunk_appinspect.command_line_helpers.glyphs[result],
                **splunk_appinspect.command_line_helpers.result_colors[result],
            )

            self.counts[result] += 1
            if result == "failure":
                self.failures.append((check, reporter))
                self.exit_status += 1
            elif result == "error":
                self.exit_status += 1000

            format_string = splunk_appinspect.command_line_helpers.format_cli_string(
                check.doc(), left_padding=12
            ).lstrip()

            check_output = (
                f"[ {glyph} ] - {painter.paint.cyan(check.name)} - {format_string}"
            )
            click.echo(check_output)

    def on_finish_app(self, app, application_validation_report):
        """Return None.

        Prints out the output of failed checks with respect to their group.

        :param app (App) The app object being validated
        :param application_validation_report (ApplicationValidationReport) The
            application validation report that contains the results of the
            validation.
        """
        result_types = ["warning", "error", "failure", "manual_check", "skipped"]
        message_types = ["warning", "error", "failure", "manual_check"]

        click.echo("\n")
        splunk_appinspect.command_line_helpers.print_result_records(
            application_validation_report,
            max_messages=self.max_messages,
            result_types=result_types,
            message_types=message_types,
        )
        click.echo("\n")
        summary_header = f"{app.name} Report Summary"
        splunk_appinspect.command_line_helpers.output_summary(
            application_validation_report.get_summary(), summary_header=summary_header
        )
        click.echo("\n")

    @staticmethod
    def on_enable_python_analyzer():
        """Returns None"""
        click.echo("Enable Python analyzer.")
