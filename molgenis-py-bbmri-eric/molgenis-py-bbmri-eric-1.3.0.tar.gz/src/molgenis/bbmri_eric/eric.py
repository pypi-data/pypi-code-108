from typing import List, Optional

from molgenis.bbmri_eric.bbmri_client import EricSession
from molgenis.bbmri_eric.errors import EricError, ErrorReport, requests_error_handler
from molgenis.bbmri_eric.model import ExternalServerNode, Node, NodeData
from molgenis.bbmri_eric.pid_service import BasePidService
from molgenis.bbmri_eric.printer import Printer
from molgenis.bbmri_eric.publisher import Publisher
from molgenis.bbmri_eric.stager import Stager
from molgenis.bbmri_eric.validation import Validator
from molgenis.client import MolgenisRequestError


class Eric:
    """
    Main class for doing operations on the ERIC directory.
    """

    def __init__(
        self, session: EricSession, pid_service: Optional[BasePidService] = None
    ):
        """
        :param BbmriSession session: an authenticated session with an ERIC directory
        """
        self.session = session
        self.printer = Printer()
        self.pid_service: Optional[BasePidService] = pid_service

    def stage_external_nodes(self, nodes: List[ExternalServerNode]) -> ErrorReport:
        """
        Stages all data from the provided external nodes in the ERIC directory.

        Parameters:
            nodes (List[ExternalServerNode]): The list of external nodes to stage
        """
        report = ErrorReport(nodes)
        for node in nodes:
            self.printer.print_node_title(node)
            try:
                self._stage_node(node)
            except EricError as e:
                self.printer.print_error(e)
                report.add_error(node, e)

        self.printer.print_summary(report)
        return report

    def publish_nodes(self, nodes: List[Node]) -> ErrorReport:
        """
        Publishes data from the provided nodes to the production tables in the ERIC
        directory.

        Parameters:
            nodes (List[Node]): The list of nodes to publish
        """
        if not self.pid_service:
            raise ValueError("A PID service is required to publish nodes")

        report = ErrorReport(nodes)
        publisher = Publisher(self.session, self.printer, self.pid_service)
        for node in nodes:
            self.printer.print_node_title(node)
            try:
                self._publish_node(node, report, publisher)
            except EricError as e:
                self.printer.print_error(e)
                report.add_error(node, e)

        self.printer.print_summary(report)
        return report

    @requests_error_handler
    def _publish_node(self, node: Node, report: ErrorReport, publisher: Publisher):
        # Stage the data if this node has an external server
        if isinstance(node, ExternalServerNode):
            self._stage_node(node)

        # Get the data from the staging area
        node_data = self._get_node_data(node)

        # Validate all the rows in the staging area
        self._validate_node(node_data, report)

        # Copy the data from staging to the combined tables
        self._publish_node_data(node_data, publisher, report)

    @requests_error_handler
    def _stage_node(self, node: ExternalServerNode):
        self.printer.print_sub_header(f"📥 Staging data of node {node.code}")
        with self.printer.indentation():
            Stager(self.session, self.printer).stage(node)

    def _publish_node_data(
        self, node_data: NodeData, publisher: Publisher, report: ErrorReport
    ):
        self.printer.print_sub_header(f"📤 Publishing node {node_data.node.code}")
        with self.printer.indentation():
            warnings = publisher.publish(node_data)
            report.add_warnings(node_data.node, warnings)

    def _validate_node(self, node_data: NodeData, report: ErrorReport):
        self.printer.print_sub_header(
            f"🔎 Validating staging data of node {node_data.node.code}"
        )
        with self.printer.indentation():
            warnings = Validator(node_data, self.printer).validate()
            if warnings:
                report.add_warnings(node_data.node, warnings)

    def _get_node_data(self, node: Node) -> NodeData:
        try:
            self.printer.print_sub_header(
                f"📦 Retrieving staging data of node {node.code}"
            )
            return self.session.get_staging_node_data(node)
        except MolgenisRequestError as e:
            raise EricError(f"Error retrieving data of node {node.code}") from e
