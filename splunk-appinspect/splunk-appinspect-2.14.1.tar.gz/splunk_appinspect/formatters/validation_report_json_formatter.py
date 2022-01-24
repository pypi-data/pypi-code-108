"""
Splunk AppInspect Json report formatter
"""

# Copyright 2019 Splunk Inc. All rights reserved.

import json

import splunk_appinspect

from . import date_time_encoder, validation_report_formatter


class ValidationReportJSONFormatter(
    validation_report_formatter.ValidationReportFormatter
):
    """
    Splunk AppInspect Json report formatter
    """

    @staticmethod
    def format_app_information(application_validation_report):
        """
        Format application report basic metadata
        """
        dict_to_return = {
            "app_author": application_validation_report.app_author,
            "app_description": application_validation_report.app_description,
            "app_hash": application_validation_report.app_hash,
            "app_name": application_validation_report.app_name,
            "app_version": application_validation_report.app_version,
            "app_package_id": application_validation_report.package_id,
        }

        return dict_to_return

    @staticmethod
    def format_metrics(application_validation_report):
        """
        Format runtime metrics
        """
        dict_to_return = {
            "metrics": application_validation_report.metrics,
        }
        return dict_to_return

    @staticmethod
    def format_run_parameters(application_validation_report):
        """
        Format input parameters
        """
        dict_to_return = {
            "run_parameters": application_validation_report.run_parameters,
        }
        return dict_to_return

    @staticmethod
    def format_groups(application_validation_report, max_messages):
        """
        Format check result by group
        """
        groupings = application_validation_report.groups()
        groups = []
        for grouping in groupings:
            group_checks = []
            for group, check, reporter in grouping:
                # Builds the Check's Reporter messages
                report_records = [
                    {
                        "code": report_record.code,
                        "filename": report_record.filename,
                        "line": report_record.line,
                        "message": report_record.message,
                        "result": report_record.result,
                        "message_filename": report_record.message_filename,
                        "message_line": report_record.message_line,
                    }
                    for report_record in reporter.report_records(
                        max_records=max_messages
                    )
                ]
                # Builds the Group's checks
                check_dict = {
                    "description": check.doc(),
                    "messages": report_records,
                    "name": check.name,
                    "tags": check.tags,
                    "result": reporter.state(),
                }
                group_checks.append(check_dict)
            group_dict = {
                "checks": group_checks,
                "description": group.doc(),
                "name": group.name,
            }
            groups.append(group_dict)

        dict_to_return = {
            "groups": groups,
        }

        return dict_to_return

    def format_application_validation_report(
        self, application_validation_report, max_messages=None
    ):
        """
        Format application validation report
        """
        if max_messages is None:
            max_messages = splunk_appinspect.main.MAX_MESSAGES_DEFAULT

        app_information = self.format_app_information(application_validation_report)
        app_metrics = self.format_metrics(application_validation_report)
        run_parameters = self.format_run_parameters(application_validation_report)
        groups = self.format_groups(application_validation_report, max_messages)
        summary = self.format_summary(application_validation_report)

        formatted_output = {}
        formatted_output.update(app_information)
        formatted_output.update(app_metrics)
        formatted_output.update(run_parameters)
        formatted_output.update(groups)
        formatted_output.update(summary)

        return formatted_output

    def format_application_validation_reports(
        self, validation_report, max_messages=None
    ):
        """
        Format application validation reports from each formatted validation report
        """
        reports_to_return = []

        if max_messages is None:
            max_messages = splunk_appinspect.main.MAX_MESSAGES_DEFAULT

        for (
            application_validation_report
        ) in validation_report.application_validation_reports:
            reports_to_return.append(
                self.format_application_validation_report(
                    application_validation_report, max_messages
                )
            )
        return reports_to_return

    @staticmethod
    def format_summary(application_validation_report):
        """
        Format result summary
        """
        summary_dict = {"summary": application_validation_report.get_summary()}
        return summary_dict

    def format(self, validation_report, max_messages=None):  # pylint: disable=W0221
        """
        Dump json string for entire report
        """
        if max_messages is None:
            max_messages = splunk_appinspect.main.MAX_MESSAGES_DEFAULT
        report_dict = {
            "request_id": None,
            "reports": self.format_application_validation_reports(
                validation_report, max_messages
            ),
            "summary": validation_report.get_summary(),
            "metrics": validation_report.metrics,
        }

        return json.dumps(report_dict, cls=date_time_encoder.DateTimeEncoder)
