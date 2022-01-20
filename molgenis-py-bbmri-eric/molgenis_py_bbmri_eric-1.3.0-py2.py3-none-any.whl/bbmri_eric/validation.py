import re
from typing import List, Set

from molgenis.bbmri_eric.errors import EricWarning
from molgenis.bbmri_eric.model import NodeData, Table, TableType
from molgenis.bbmri_eric.printer import Printer


class Validator:
    """
    This class is responsible for validating the data in a single node. Validation
    consists of:
    1. Checking the validity of all identifiers
    2. Checking if there are rows that reference rows with invalid identifiers
    """

    ALLOWS_EU_PREFIXES = {TableType.PERSONS, TableType.NETWORKS}

    def __init__(self, node_data: NodeData, printer: Printer):
        self.printer = printer
        self.node_data = node_data
        self.invalid_ids: Set[str] = set()
        self.warnings: List[EricWarning] = list()

    def validate(self) -> List[EricWarning]:
        for table in self.node_data.import_order:
            self._validate_ids(table)

        self._validate_networks()
        self._validate_biobanks()
        self._validate_collections()

        return self.warnings

    def _validate_ids(self, table: Table):
        for row in table.rows:
            id_ = row["id"]
            errors = self._validate_id(table, row["id"])
            if errors:
                self._add_invalid_id(id_, errors)

    def _validate_networks(self):
        for network in self.node_data.networks.rows:
            self._validate_xref(network, "contact")
            self._validate_mref(network, "parent_network")

    def _validate_biobanks(self):
        for biobank in self.node_data.biobanks.rows:
            self._validate_xref(biobank, "contact")
            self._validate_mref(biobank, "network")

    def _validate_collections(self):
        for collection in self.node_data.collections.rows:
            self._validate_xref(collection, "contact")
            self._validate_xref(collection, "biobank")
            self._validate_xref(collection, "parent_collection")
            self._validate_mref(collection, "networks")

    def _validate_xref(self, row: dict, ref_attr: str):
        if ref_attr in row:
            self._validate_ref(row, row[ref_attr])

    def _validate_mref(self, row: dict, mref_attr: str):
        if mref_attr in row:
            for ref_id in row[mref_attr]:
                self._validate_ref(row, ref_id)

    def _validate_ref(self, row: dict, ref_id: str):
        if ref_id in self.invalid_ids:
            warning = EricWarning(f"{row['id']} references invalid id: {ref_id}")
            self.printer.print_warning(warning)
            self.warnings.append(warning)

    def _validate_id(self, table: Table, id_: str) -> List[EricWarning]:
        errors = []

        self._validate_id_prefix(errors, id_, table)
        self._validate_id_chars(errors, id_, table)

        return errors

    def _validate_id_prefix(self, errors: List[EricWarning], id_: str, table: Table):
        node = self.node_data.node

        prefix = node.get_id_prefix(table.type)
        if table.type in self.ALLOWS_EU_PREFIXES:
            eu_prefix = node.get_eu_id_prefix(table.type)
            if not id_.startswith((prefix, eu_prefix)):
                warning = EricWarning(
                    f"{id_} in entity: {table.full_name} does not start with {prefix} "
                    f"or {eu_prefix}"
                )
                self.printer.print_warning(warning)
                errors.append(warning)
        else:
            if not id_.startswith(prefix):
                warning = EricWarning(
                    f"{id_} in entity: {table.full_name} does not start with {prefix}"
                )
                self.printer.print_warning(warning)
                errors.append(warning)

    def _validate_id_chars(self, errors: List[EricWarning], id_: str, table: Table):
        if not re.search("^[A-Za-z0-9-_:]+$", id_):
            warning = EricWarning(
                f"{id_} in entity: {table.full_name} contains"
                f" invalid characters. Only alphanumerics and -_: are allowed."
            )
            self.printer.print_warning(warning)
            errors.append(warning)

    def _add_invalid_id(self, id_: str, warnings: List[EricWarning]):
        self.invalid_ids.add(id_)
        self.warnings.extend(warnings)
