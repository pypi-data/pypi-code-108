"""Test the AOP module methods and submodules."""
import pandas as pd
from sqlalchemy_utils import database_exists

from aop2db.orm.manager import engine, CONN
from aop2db.aop.importer import import_aop_data
from aop2db.aop.query import get_aops, get_chemicals, get_taxonomies, get_stressors, get_life_stages, \
    get_cell_terms, get_organ_terms, get_key_events, get_bio_events, get_bio_actions, get_bio_objects, \
    get_bio_processes, get_key_event_relationships, get_sexes


class TestImporter:
    """Tests for the importer submodule."""

    def test_importer(self):
        """Test the general import method."""
        import_aop_data()

        assert database_exists(CONN)

        required_tables = {
            "aop",
            "aop_bio_action",
            "aop_bio_event",
            "aop_bio_object",
            "aop_bio_process",
            "aop_cell_term",
            "aop_chemical",
            "aop_chemical_synonym",
            "aop_kers_aop_association",
            "aop_key_event",
            "aop_key_event_aop_association",
            "aop_key_event_relationship",
            "aop_life_stage",
            "aop_life_stage_aop_association",
            "aop_life_stage_ker_association",
            "aop_life_stage_key_event_association",
            "aop_organ_term",
            "aop_sex",
            "aop_sex_aop_association",
            "aop_sex_ker_association",
            "aop_sex_key_event_association",
            "aop_stressor",
            "aop_stressor_aop_association",
            "aop_taxonomy",
            "aop_taxonomy_aop_association",
            "aop_taxonomy_ker_association",
            "aop_taxonomy_key_event_association",
            "key_event_bio_event_association",
            "stressor_chemical_association",
            "stressor_key_event_association",
        }

        # Check tables are all there
        conn = engine.connect()
        if engine.name == "sqlite":
            query = "SELECT name FROM sqlite_master WHERE type='table';"

        else:
            query = "SHOW TABLES;"

        tables_in_db = set([x[0] for x in conn.execute(query).fetchall()])

        missing_tables = required_tables - tables_in_db
        assert not missing_tables

        # Check none of the tables are empty
        for table_name in required_tables:
            if table_name != "aop_taxonomy_aop_association":  # No entries at the moment
                entry = conn.execute(f"SELECT * FROM {table_name} LIMIT 1;").fetchone()
                assert entry


class TestQuery:
    """Tests for the query submodule."""

    @staticmethod
    def check_query_results(results: pd.DataFrame, expected_columns: list):
        """Helper method for checking results made by query functions."""
        assert isinstance(results, pd.DataFrame)

        for col in expected_columns:
            assert col in results.columns

        assert len(results) > 1

    def test_get_aops(self):
        """Test the get_aop method."""
        expected_cols = [
            'aop_id', 'aop_hash', 'title', 'background', 'short_name', 'abstract', 'source',
            'creation', 'last_modified', 'authors', 'wiki_status', 'oecd_status',
            'saaop_status', 'oecd_project', 'essentiality_support',
            'potential_applications', 'key_event_id', 'key_event_type',
            'stressor', 'stressor_evidence', 'life_stage'
        ]
        self.check_query_results(get_aops(), expected_cols)

    def test_get_chemicals(self):
        """Test the get_chemicals method."""
        expected_cols = [
            'aop_hash', 'casrn', 'jchem_inchi_key', 'indigo_inchi_key', 'name', 'dsstox_id'
        ]
        self.check_query_results(get_chemicals(), expected_cols)

    def test_get_stressors(self):
        """Test the get_stressors method."""
        expected_cols = [
            'aop_hash', 'name', 'chemical_name', 'chemical_casrn'
        ]
        self.check_query_results(get_stressors(), expected_cols)

    def test_get_taxonomies(self):
        """Test the get_taxonomies method."""
        expected_cols = [
            'aop_hash', 'source', 'source_id', 'tax_id', 'species', 'name'
        ]
        self.check_query_results(get_taxonomies(), expected_cols)

    def test_get_life_stages(self):
        """Test the get_life_stages method."""
        expected_cols = ['life_stage']
        self.check_query_results(get_life_stages(), expected_cols)

    def test_get_sexes(self):
        """Test the get_sexes method."""
        expected_cols = ['sex']
        self.check_query_results(get_sexes(), expected_cols)

    def test_get_cell_terms(self):
        """Test the get_cell_terms method."""
        expected_cols = ['source', 'source_id', 'name']
        self.check_query_results(get_cell_terms(), expected_cols)

    def test_get_organ_terms(self):
        """Test the get_organ_terms method."""
        expected_cols = ['source', 'source_id', 'name']
        self.check_query_results(get_organ_terms(), expected_cols)

    def test_get_key_events(self):
        """Test the get_key_events method."""
        expected_cols = [
            'aop_id', 'aop_hash', 'title', 'short_name', 'biological_organization_level', 'cell_term', 'organ_term', 'tax_id'
        ]
        self.check_query_results(get_key_events(), expected_cols)

    def test_get_key_event_relationships(self):
        """Test the get_key_event_relationships method."""
        expected_cols = [
            'aop_hash',
            'description',
            'quantitative_understanding',
            'evidence_supporting_taxonomic_applicability',
            'source',
            'creation',
            'last_modified',
            'up_event_id',
            'down_event_id',
            'evidence_value',
            'evidence_biological_plausibility',
            'evidence_emperical_support_linkage',
            'evidence_uncertainties_or_inconsistencies',
            'tax_id',
            'life_stage',
        ]
        self.check_query_results(get_key_event_relationships(), expected_cols)

    def test_get_bio_events(self):
        """Test the get_bio_events method."""
        expected_cols = ['bio_action', 'bio_process', 'bio_object', 'key_event_id']
        self.check_query_results(get_bio_events(), expected_cols)

    def test_get_bio_objects(self):
        """Test the get_bio_objects method."""
        expected_cols = ['aop_hash', 'source', 'source_id', 'name']
        self.check_query_results(get_bio_objects(), expected_cols)

    def test_get_bio_actions(self):
        """Test the get_bio_actions method."""
        expected_cols = ['aop_hash', 'source', 'source_id', 'name']
        self.check_query_results(get_bio_actions(), expected_cols)

    def test_get_bio_processes(self):
        """Test the get_bio_processes method."""
        expected_cols = ['aop_hash', 'source', 'source_id', 'name']
        self.check_query_results(get_bio_processes(), expected_cols)
