import datetime
import os
import sarif_om as om
from checkov.common.output.report import Report
from checkov.common.util.docs_generator import get_checks
from jschema_to_python.to_json import to_json

from bridgecrew.version import version

TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
REVISION_ID = os.environ.get('GITHUB_SHA', '')
import uuid

GITHUB_RUN_ID = os.environ.get('GITHUB_RUN_ID', str(uuid.uuid4()))


# GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY', '')
# GITHUB_SERVER_URL = os.environ.get('GITHUB_SERVER_URL', '')

class SarifReport(Report):
    def __init__(self, check_type):
        super().__init__(check_type)
        self.passed_checks = []
        self.failed_checks = []
        self.skipped_checks = []
        self.parsing_errors = []
        self.repo_uri = ""
        self.branch = ""
        self.revision_id = REVISION_ID
        self.directory = ""

    def get_sarif_results(self):
        results = []
        rules = {}
        for check in self.failed_checks:
            result_record = self.check2result(check)
            results.append(result_record)
            rules[check.check_id] = om.ReportingDescriptor(id=check.check_id, name=check.check_name,
                                                           short_description={"text": check.check_name},
                                                           full_description={"text": check.guideline},
                                                           help={"text": check.check_name},
                                                           help_uri=check.guideline)
        for check in self.skipped_checks:
            result_record = self.check2result(check, state="skipped")
            results.append(result_record)
            rules[check.check_id] = om.ReportingDescriptor(id=check.check_id, name=check.check_name,
                                                           short_description={"text": check.check_name},
                                                           full_description={"text": check.guideline},
                                                           help={"text": check.check_name},
                                                           help_uri=check.guideline)

        return results, list(rules.values())

    def check2result(self, check, state="fail"):
        if isinstance(self.directory,list) and self.directory[0] != ".":
            path = self.directory[0] + check.file_path[1:]
        else:
            path = check.file_path[1:]
        location = om.Location(physical_location=om.PhysicalLocation(
            artifact_location=om.ArtifactLocation(uri=path, uri_base_id="PROJECTROOT"),
            region=om.Region(start_line=check.file_line_range[0], end_line=check.file_line_range[1], start_column=1,
                             end_column=1)))

        partial_fingerprints = {
            "primaryLocationLineHash": "{}#{}".format(path, check.resource)}
        if state == "skipped":
            suppression = om.Suppression(kind="inSource")
            if 'suppress_comment' in check.check_result:
                justification = check.check_result['suppress_comment']
                suppression = om.Suppression(justification=justification, kind="inSource")
            result_record = om.Result(rule_id=check.check_id, message=om.Message(text=check.check_name),
                                      # partial_fingerprints=partial_fingerprints,
                                      locations=[location],
                                      suppressions=[suppression])
        if state == "fail":
            result_record = om.Result(rule_id=check.check_id, message=om.Message(text=check.check_name),
                                      # partial_fingerprints=partial_fingerprints,
                                      locations=[location])
        if not check.guideline:
            check.guideline = "http://docs.bridgecrew.io"
        return result_record

    def print_sarif(self):
        results, rules = self.get_sarif_results()

        log = om.SarifLog(
            schema_uri="https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            version="2.1.0",
            runs=[
                om.Run(
                    automation_details=om.RunAutomationDetails(
                        description=om.Message(
                            text="Infrastructure as code static analysis results using Bridgecrew"
                        ),
                        id=GITHUB_RUN_ID
                    ),
                    tool=om.Tool(
                        driver=om.ToolComponent(
                            name="bridgecrew",
                            version=version,
                            rules=rules
                        )
                    ),
                    invocations=[
                        om.Invocation(
                            end_time_utc=datetime.datetime.utcnow().strftime(TS_FORMAT),
                            execution_successful=True,
                        )
                    ],
                    conversion={
                        "tool": om.Tool(
                            driver=om.ToolComponent(name="Bridgecrew")
                        ),
                        "invocation": om.Invocation(
                            execution_successful=True,
                            # working_directory=om.ArtifactLocation(uri=to_uri(wd_dir_log)),
                            end_time_utc=datetime.datetime.utcnow().strftime(TS_FORMAT),
                        ),
                    },
                    results=results,
                    original_uri_base_ids={
                        "PROJECTROOT": {
                            "uri": self.repo_uri
                        }},
                    version_control_provenance=[
                        om.VersionControlDetails(
                            repository_uri=self.repo_uri,
                            branch=self.branch,
                            revision_id=self.revision_id,
                            mapped_to={
                                "uriBaseId": "PROJECTROOT"
                            }
                        )
                    ],
                )
            ],
        )
        serialized_log = to_json(log)
        with open("results.sarif", "w") as f:
            f.write(serialized_log)
        self.print_console()

    def get_rules(self):
        get_checks("all")
