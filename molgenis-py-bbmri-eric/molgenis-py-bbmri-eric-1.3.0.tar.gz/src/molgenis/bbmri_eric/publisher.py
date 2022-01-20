from typing import List

from molgenis.bbmri_eric.bbmri_client import EricSession
from molgenis.bbmri_eric.enricher import Enricher
from molgenis.bbmri_eric.errors import EricError, EricWarning
from molgenis.bbmri_eric.model import NodeData, QualityInfo, Table, TableType
from molgenis.bbmri_eric.pid_manager import PidManagerFactory
from molgenis.bbmri_eric.pid_service import BasePidService
from molgenis.bbmri_eric.printer import Printer
from molgenis.client import MolgenisRequestError


class Publisher:
    """
    This class is responsible for copying data from the staging areas to the combined
    public tables.
    """

    def __init__(
        self, session: EricSession, printer: Printer, pid_service: BasePidService
    ):
        self.session = session
        self.printer = printer
        self.pid_service = pid_service
        self.pid_manager = PidManagerFactory.create(pid_service, printer)
        self.warnings: List[EricWarning] = []
        self.quality_info: QualityInfo = session.get_quality_info()
        self.eu_node_data: NodeData = session.get_staging_node_data(
            session.get_node("EU")
        )

    def publish(self, node_data: NodeData) -> List[EricWarning]:
        """
        Publishes data from the provided node to the production tables. Before being
        copied over, the data is enriched with additional information.
        """
        self.warnings = []
        node = node_data.node

        self.printer.print(f"📦 Retrieving existing published data of node {node.code}")
        existing_node_data = self.session.get_published_node_data(node)

        self.printer.print("✏️ Preparing data")
        with self.printer.indentation():
            self.warnings += Enricher(
                node_data=node_data,
                quality=self.quality_info,
                printer=self.printer,
                existing_biobanks=existing_node_data.biobanks,
                eu_node_data=self.eu_node_data,
            ).enrich()

        self.printer.print("🆔 Managing PIDs")
        with self.printer.indentation():
            self.warnings += self.pid_manager.assign_biobank_pids(node_data.biobanks)
            self.pid_manager.update_biobank_pids(
                node_data.biobanks, existing_node_data.biobanks
            )

        self.printer.print("💾 Copying data to combined tables")
        with self.printer.indentation():
            self._copy_node_data(node_data, existing_node_data)
        return self.warnings

    def _copy_node_data(self, node_data: NodeData, existing_node_data: NodeData):
        """
        Copies the data of a staging area to the combined tables. This happens in two
        phases:
        1. New/existing rows are upserted in the combined tables
        2. Removed rows are deleted from the combined tables
        """
        for table in node_data.import_order:
            self.printer.print(f"Upserting rows in {table.type.base_id}")
            try:
                self.session.upsert_batched(table.type.base_id, table.rows)
            except MolgenisRequestError as e:
                raise EricError(f"Error upserting rows to {table.type.base_id}") from e

        for table in reversed(node_data.import_order):
            self.printer.print(f"Deleting rows in {table.type.base_id}")
            try:
                with self.printer.indentation():
                    self._delete_rows(
                        table, existing_node_data.table_by_type[table.type]
                    )
            except MolgenisRequestError as e:
                raise EricError(f"Error deleting rows from {table.type.base_id}") from e

    def _delete_rows(self, table: Table, existing_table: Table):
        """
        Deletes rows from a combined table that are not present in the staging area's
        table. If a row is referenced from the quality info tables, it is not deleted
        but a warning will be raised.

        :param Table table: the staging area's table
        :node Node node: the Node that is being published
        """
        # Compare the ids from staging and production to see what was deleted
        staging_ids = {row["id"] for row in table.rows}
        production_ids = set(existing_table.rows_by_id.keys())
        deleted_ids = production_ids.difference(staging_ids)

        # Remove ids that we are not allowed to delete
        undeletable_ids = self.quality_info.get_qualities(table.type).keys()
        deletable_ids = deleted_ids.difference(undeletable_ids)

        # For deleted biobanks, update the handle
        if table.type == TableType.BIOBANKS:
            self.pid_manager.terminate_biobanks(
                [existing_table.rows_by_id[id_]["pid"] for id_ in deletable_ids]
            )

        # Actually delete the rows in the combined tables
        if deletable_ids:
            self.printer.print(
                f"Deleting {len(deletable_ids)} row(s) in {table.type.base_id}"
            )
            self.session.delete_list(table.type.base_id, list(deletable_ids))

        # Show warning for every id that we prevented deletion of
        if deleted_ids != deletable_ids:
            for id_ in undeletable_ids:
                if id_ in deleted_ids:
                    warning = EricWarning(
                        f"Prevented the deletion of a row that is referenced from "
                        f"the quality info: {table.type.value} {id_}."
                    )
                    self.printer.print_warning(warning)
                    self.warnings.append(warning)
