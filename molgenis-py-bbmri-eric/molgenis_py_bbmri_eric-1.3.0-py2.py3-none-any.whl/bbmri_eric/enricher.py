from molgenis.bbmri_eric.errors import EricWarning
from molgenis.bbmri_eric.model import Node, NodeData, QualityInfo, Table
from molgenis.bbmri_eric.printer import Printer


class Enricher:
    """
    The published tables have a few extra attributes that the staging tables do not.
    This class is responsible for adding those attributes so the staging tables can be
    published correctly.
    """

    def __init__(
        self,
        node_data: NodeData,
        quality: QualityInfo,
        printer: Printer,
        existing_biobanks: Table,
        eu_node_data: NodeData,
    ):
        self.node_data = node_data
        self.quality = quality
        self.printer = printer
        self.existing_biobanks = existing_biobanks.rows_by_id
        self.eu_node_data = eu_node_data
        self.warnings = []

    def enrich(self):
        """
        Enriches the data of a node:
        1. Sets the commercial use boolean
        2. Adds the national node code to all rows
        3. Sets the quality info field for biobanks and collections
        4. Adds PIDs to biobanks
        5. Replaces a node's EU rows with the data from node EU's staging area
        """
        self._set_national_node_code()
        self._replace_eu_rows()
        self._set_commercial_use_bool()
        self._set_quality_info()
        self._set_biobank_pids()
        return self.warnings

    def _set_commercial_use_bool(self):
        """
        Takes the data of a Node and sets the commercial_use boolean of all collections
        based on a set of criteria.
        """

        self.printer.print("Setting 'commercial_use' booleans")
        for collection in self.node_data.collections.rows:

            def is_true(row: dict, attr: str):
                # if the value is not entered, it is also considered true
                return attr not in row or row[attr] is True

            biobank_id = collection["biobank"]
            biobank = self.node_data.biobanks.rows_by_id[biobank_id]

            collection["commercial_use"] = is_true(
                biobank, "collaboration_commercial"
            ) and is_true(collection, "collaboration_commercial")

    def _set_national_node_code(self):
        """
        Adds the national node code to each row of every table of a node.
        """
        self.printer.print("Adding national node codes")
        for table in self.node_data.import_order:
            for row in table.rows:
                row["national_node"] = self.node_data.node.code

    def _set_quality_info(self):
        """
        Adds the one_to_many "quality" field to the biobank and collection tables based
        on the quality info tables.
        """
        self.printer.print("Adding quality information")
        self._set_quality_for_table(self.node_data.biobanks)
        self._set_quality_for_table(self.node_data.collections)

    def _set_quality_for_table(self, table: Table):
        for row in table.rows:
            qualities = self.quality.get_qualities(table.type)
            quality_ids = qualities.get(row["id"], [])
            if quality_ids:
                row["quality"] = quality_ids

    def _set_biobank_pids(self):
        """
        Adds the PIDs for existing biobanks.
        """
        self.printer.print("Adding existing PIDs to biobanks")
        for biobank in self.node_data.biobanks.rows:
            biobank_id = biobank["id"]
            if biobank_id in self.existing_biobanks:
                existing_biobank = self.existing_biobanks[biobank_id]
                if "pid" in existing_biobank:
                    biobank["pid"] = existing_biobank["pid"]

    def _replace_eu_rows(self):
        """
        Replaces a node's EU networks and persons with data from the EU staging node.
        """
        node_data = self.node_data
        node = node_data.node
        if node.code == "EU":
            return

        self.printer.print("Replacing EU networks and persons")
        self._replace_rows(node, node_data.persons, self.eu_node_data.persons)
        self._replace_rows(node, node_data.networks, self.eu_node_data.networks)

    def _replace_rows(self, node: Node, table: Table, eu_table: Table):
        eu_prefix = node.get_eu_id_prefix(table.type)
        for network in table.rows:
            id_ = network["id"]
            if id_.startswith(eu_prefix):
                if id_ in eu_table.rows_by_id:
                    table.rows_by_id[id_] = eu_table.rows_by_id[id_]

                    # overwrite EU code that was added in previous enrichment step
                    table.rows_by_id[id_]["national_node"] = self.eu_node_data.node.code
                else:
                    warning = EricWarning(
                        f"{id_} is not present in {eu_table.type.base_id}"
                    )
                    self.printer.print_warning(warning, indent=1)
                    self.warnings.append(warning)
