from checkov.common.output.report import Report
from checkov.common.runners.runner_registry import RunnerRegistry, OUTPUT_CHOICES

from bridgecrew.output.sarif import SarifReport
from bridgecrew.banner import banner, tool


class CustomRunnerRegistry(RunnerRegistry):
    def __init__(self, banner, runner_filter, *runners):
        super().__init__(banner, runner_filter, *runners)
        OUTPUT_CHOICES.append("sarif")
        self.tool = tool

    def print_reports(self, scan_reports, args, url=None, created_baseline_path=None, baseline=None):
        exit_codes = []
        if args.output == 'sarif':
            merged_reports = self.merge_reports(scan_reports)
            report = self.report2sarif_report(merged_reports, args)
            report.print_sarif()
            exit_codes.append(report.get_exit_code(args.soft_fail))
            if url:
                print("More details: {}".format(url))
        else:
            exit_codes = [super().print_reports(scan_reports, args, url, created_baseline_path, baseline)]
        exit_code = 1 if 1 in exit_codes else 0
        return exit_code

    @staticmethod
    def merge_reports(reports):
        merged_report = Report("merged")
        for r in reports:
            merged_report.skipped_checks.extend(r.skipped_checks)
            merged_report.parsing_errors.extend(r.parsing_errors)
            merged_report.passed_checks.extend(r.passed_checks)
            merged_report.failed_checks.extend(r.failed_checks)
        return merged_report

    @staticmethod
    def report2sarif_report(report, args):
        sarif_report = SarifReport(report.check_type)
        sarif_report.passed_checks = report.passed_checks
        sarif_report.skipped_checks = report.skipped_checks
        sarif_report.failed_checks = report.failed_checks
        sarif_report.parsing_errors = report.parsing_errors
        sarif_report.repo_uri = "https://github.com/{}/".format(args.repo_id)
        sarif_report.branch = args.branch
        sarif_report.directory = args.directory
        return sarif_report
