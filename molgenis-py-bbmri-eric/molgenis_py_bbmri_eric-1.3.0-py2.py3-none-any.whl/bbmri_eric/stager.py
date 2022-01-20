from molgenis.bbmri_eric import utils
from molgenis.bbmri_eric.bbmri_client import EricSession, ExternalServerSession
from molgenis.bbmri_eric.errors import EricError
from molgenis.bbmri_eric.model import ExternalServerNode, TableType
from molgenis.bbmri_eric.printer import Printer
from molgenis.client import MolgenisRequestError


class Stager:
    """
    This class is responsible for copying data from a node with an external server to
    its staging area in the BBMRI ERIC directory.
    """

    def __init__(self, session: EricSession, printer: Printer):
        self.session = session
        self.printer = printer

    def stage(self, node: ExternalServerNode):
        """
        Stages all data from the provided external node in the BBMRI-ERIC directory.
        """
        self.printer.print(f"🗑 Clearing staging area of {node.code}")
        self._clear_staging_area(node)

        self.printer.print(
            f"📩 Importing data from {node.url} to staging area of {node.code}"
        )
        with self.printer.indentation():
            self._import_node(node)

    def _clear_staging_area(self, node: ExternalServerNode):
        """
        Deletes all data in the staging area of an external node.
        """
        try:
            for table_type in reversed(TableType.get_import_order()):
                self.session.delete(node.get_staging_id(table_type))
        except MolgenisRequestError as e:
            raise EricError(f"Error clearing staging area of node {node.code}") from e

    def _import_node(self, node: ExternalServerNode):
        """
        Copies the data from the external server to the staging area.
        """
        try:
            source_session = ExternalServerSession(node=node)
            source_data = source_session.get_node_data()
        except MolgenisRequestError as e:
            raise EricError(f"Error getting data from {node.url}") from e

        try:
            for table in source_data.import_order:
                target_name = node.get_staging_id(table.type)

                self.printer.print(f"Importing data to {target_name}")
                self.session.add_batched(
                    target_name, utils.remove_one_to_manys(table.rows, table.meta)
                )
        except MolgenisRequestError as e:
            raise EricError(f"Error copying from {node.url} to staging area") from e
