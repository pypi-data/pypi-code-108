"""AOP Wiki module."""

import gzip
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

import requests
import xmltodict
from sqlalchemy import insert
from tqdm import tqdm

from aop2db.constants import (
    AOP_HASH,
    AOP_ID,
    AOP_JSON,
    AOP_JSONS,
    AOP_XML_DOWNLOAD,
    APPLICABILITY,
    CREATION,
    CREATION_TIMESTAMP,
    EVIDENCE,
    ID,
    KE_JSON,
    LAST_MODIFIED,
    LIFESTAGE,
    LM_TIMESTAMP,
    REFERENCES,
    SEX,
    STRESSOR_JSON,
    TAX_ID_LOOKUP,
    TAXONOMY,
)
from aop2db.defaults import AOP_DIR, AOP_XML_FILE, TAXONOMY_CACHE
from aop2db.orm.manager import engine, rebuild_database, session
from aop2db.orm.models import (
    Aop,
    AopKer,
    AopKeyEvent,
    AopStressor,
    BiologicalAction,
    BiologicalEvent,
    BiologicalObject,
    BiologicalProcess,
    CellTerm,
    Chemical,
    KeyEvent,
    KeyEventRelationship,
    LifeStage,
    LifeStageAop,
    LifeStageKeyEvent,
    LifeStageKeyEventRelationship,
    OrganTerm,
    Sex,
    SexAop,
    SexKeyEvent,
    SexKeyEventRelationship,
    Stressor,
    Synonym,
    Taxonomy,
    TaxonomyAop,
    TaxonomyKeyEvent,
    TaxonomyKeyEventRelationship,
)

logger = logging.getLogger(__name__)

__all__ = ["import_aop_data"]


def import_aop_data() -> None:
    """Parse and import AOP Wiki content into a relational database."""
    rebuild_database()

    ai = AopImporter()
    ai.import_aop_data()


class AopImporter:
    """Class for parsing and importing AOP Wiki content into a relational database."""

    class_mapper = {
        TAXONOMY: {
            KeyEvent: TaxonomyKeyEvent,
            KeyEventRelationship: TaxonomyKeyEventRelationship,
            Aop: TaxonomyAop,
        },
        SEX: {
            KeyEvent: SexKeyEvent,
            KeyEventRelationship: SexKeyEventRelationship,
            Aop: SexAop,
        },
        LIFESTAGE: {
            KeyEvent: LifeStageKeyEvent,
            KeyEventRelationship: LifeStageKeyEventRelationship,
            Aop: LifeStageAop,
        },
    }

    def __init__(self):
        """Init method."""
        # Get all AOP data as dict

        self.aop_data: dict = self.__xml_to_dict()["data"]
        self.json_data = self.create_json_data_mapper()
        self.session = session()  # SQL session

        self.organ_terms: dict = dict()  # Filled during import_key_events
        self.cell_terms: dict = dict()  # Filled during import_key_events
        self.bio_events: dict = dict()  # Filled during import_key_events

        self.taxonomies = None  # Filled during import_taxonomies
        self.sex_entries: dict = dict()
        self.life_stages: dict = dict()

        self.current_sex_cache = set()
        self.current_ls_cache = set()

    def create_json_data_mapper(self) -> dict:
        """Create dictionary with JSON data mapper."""
        self.__download_aop_json()  # Download JSON files
        json_data_mapper = dict()
        for file_name in (AOP_JSON, KE_JSON, STRESSOR_JSON):
            file_path = AOP_DIR.joinpath(Path(file_name).name)

            with file_path.open() as jsonf:
                content = json.load(jsonf)

            if file_name == STRESSOR_JSON:
                mapper = dict()
                for entry in content:
                    for chemical in entry["chemicals"]:
                        mapper[chemical["casrn"].strip()] = entry["id"]

            else:
                mapper = {entry["title"].strip(): entry["id"] for entry in content}

            json_data_mapper[file_name] = mapper

        return json_data_mapper

    def import_aop_data(self):
        """Import downloaded AOP data into database."""
        self.import_bio_classes()  # Dict => {bio class: inserted count}
        self.import_chemicals()
        self.import_taxonomies()
        self.import_stressors()
        self.import_key_events()
        self.import_bio_events()
        self.import_key_event_relationships()
        self.import_aops()

    def import_aops(self) -> int:
        """Import parsed AOP data into database and return number of rows imported."""
        parsed_aops = self.__parse_aops()
        logger.info("Importing AOPs")
        self.session.add_all(parsed_aops)
        self.session.commit()

        return len(parsed_aops)

    def __parse_aops(self) -> list:
        """Extract adverse outcome pathways to dict and map to connected tables."""
        logger.info("Parsing AOPs")
        aop_data = self.aop_data["aop"]
        ke_mapper = self.__get_aop_mapper(KeyEvent)
        ker_mapper = self.__get_aop_mapper(KeyEventRelationship)
        stressor_mapper = self.__get_aop_mapper(Stressor)

        aop_entries = []
        for aop in tqdm(aop_data, total=len(aop_data), desc="Importing AOPs"):
            # Discard unused columns
            aop.pop(
                "overall-assessment", None
            )  # TODO decide later if we want to include them

            # Extract useful information
            aop[AOP_ID] = self.__get_aop_id(AOP_JSON, aop["title"])
            aop[AOP_HASH] = aop.pop(ID)
            aop[LAST_MODIFIED] = datetime.fromisoformat(aop.pop(LM_TIMESTAMP, None))
            aop[CREATION] = datetime.fromisoformat(aop.pop(CREATION_TIMESTAMP, None))
            aop[REFERENCES] = aop.pop(REFERENCES)
            statuses = aop.pop("status")
            stressors = aop.pop("aop-stressors", None)
            kers = aop.pop("key-event-relationships")
            applicability = aop.pop(APPLICABILITY, None)

            kes = {
                "key_events": aop.pop("key-events", None),
                "aos": aop.pop("adverse-outcome", None),  # Adverse Outcomes
                "mies": aop.pop(
                    "molecular-initiating-event", None
                ),  # Molecular Initiating Events
            }

            # Create AOP object
            merged_aop = {**aop, **statuses}
            standardized_aop = self.__standardize_keys(merged_aop)
            aop_entry = Aop(**standardized_aop)

            if applicability:
                aop_entry = self.__parse_applicability(applicability, aop_entry)

            if stressors:
                aop_entry = self.__extract_aop_stressors(
                    stressors, aop_entry, stressor_mapper
                )

            aop_entry = self.__extract_aop_key_events(
                kes, aop_entry, ke_mapper
            )  # Method checks if data present

            if kers:
                aop_entry = self.__extract_aop_kers(kers, aop_entry, ker_mapper)

            aop_entries.append(aop_entry)

        return aop_entries

    def __extract_aop_key_events(
        self,
        ke_dict: Dict[str, Union[dict, list]],
        aop_entry: Aop,
        key_event_mapper: dict,
    ) -> Aop:
        """Extract and label all key event associations.

        This includes Adverse Outcomes, Molecular Initiating Events, and other Key Events.
        """
        ke_tags = {
            "mies": {
                EVIDENCE: "evidence-supporting-chemical-initiation",
                "ke_type": "molecular_initaiting_event",
            },
            "aos": {EVIDENCE: "examples", "ke_type": "adverse_outcome"},
        }

        for ke_type, ke_data in ke_dict.items():
            if ke_data:
                if ke_type == "key_events":
                    ke_aop_hashes = [
                        ke[ID] for ke in self._listify(ke_data["key-event"])
                    ]
                    ke_objs = [
                        key_event_mapper[ke_aop_hash] for ke_aop_hash in ke_aop_hashes
                    ]
                    for ke_obj in ke_objs:
                        aop_ke_asso = AopKeyEvent(key_event_type="key_event")
                        aop_ke_asso.key_event = ke_obj
                        aop_entry.key_events.append(aop_ke_asso)

                else:  # Either mies (molecular initiating events) or aos (adverse outcomes)
                    ke_data = self._listify(ke_data)
                    for special_event in ke_data:
                        ke_aop_hash = special_event["@key-event-id"]

                        key_event_type = ke_tags[ke_type]["ke_type"]
                        evidence_tag = ke_tags[ke_type][EVIDENCE]

                        evidence = special_event[evidence_tag]

                        ke_obj = key_event_mapper[ke_aop_hash]
                        aop_ke_asso = AopKeyEvent(
                            key_event_type=key_event_type, evidence=evidence
                        )
                        aop_ke_asso.key_event = ke_obj
                        aop_entry.key_events.append(aop_ke_asso)

        return aop_entry

    def __extract_aop_stressors(
        self, stressor_dict: dict, aop_entry: Aop, stressor_mapper: dict
    ) -> Aop:
        """Extract and add stressor_mapper to AOP entry."""
        stressors = self._listify(stressor_dict["aop-stressor"])
        for stressor in stressors:
            stressor_aop_hash = stressor["@stressor-id"]
            stressor_asso = AopStressor(
                description=stressor["description"], evidence=stressor[EVIDENCE]
            )
            stressor_asso.stressor = stressor_mapper[stressor_aop_hash]
            aop_entry.stressors.append(stressor_asso)

        return aop_entry

    def __extract_aop_kers(
        self, ker_dict: dict, aop_entry: Aop, ker_mapper: dict
    ) -> Aop:
        """Extract and add key event relationships to AOP entry."""
        ker_list = self._listify(ker_dict["relationship"])
        for ker in ker_list:
            ker_aop_hash = ker[ID]
            ker_asso = AopKer(
                adjacency=ker["adjacency"],
                quantitative_understanding_value=ker[
                    "quantitative-understanding-value"
                ],
                evidence=ker[EVIDENCE],
            )
            ker_asso.ker = ker_mapper[ker_aop_hash]
            aop_entry.kers.append(ker_asso)

        return aop_entry

    def import_key_event_relationships(self) -> int:
        """Import parsed key event relationship data into database and return number of rows imported."""
        parsed_kers = self.__parse_kers()
        logger.info("Importing key event relationships")
        self.session.add_all(parsed_kers)
        self.__update_sex_entries()  # New sex entries
        self.__update_life_stage_entries()  # New life stage entries
        self.session.commit()

        return len(parsed_kers)

    def __parse_kers(self) -> list:
        """Extract key events relationships to dict and map to connected tables.

        Key events need to have been imported already.
        """
        logger.info("Parsing key event relationships")
        kers = self.aop_data["key-event-relationship"]
        key_events = self.__get_aop_mapper(KeyEvent)

        ker_entires = []

        for ker in tqdm(
            kers, total=len(kers), desc="Importing key events relationships"
        ):
            ker[AOP_HASH] = ker.pop(ID)
            ker[REFERENCES] = ker.pop(REFERENCES)
            ker = self.__extract_weight_of_evidence_values(ker)
            ker[LAST_MODIFIED] = datetime.fromisoformat(ker.pop(LM_TIMESTAMP, None))
            ker[CREATION] = datetime.fromisoformat(ker.pop(CREATION_TIMESTAMP, None))
            ker["quantitative_understanding"] = ker.pop("quantitative-understanding")[
                "description"
            ]  # Get text
            applicability = ker.pop("taxonomic-applicability", None)
            related_kes = ker.pop("title")

            # Create KER obj and add up/down stream KEs
            ker = self.__standardize_keys(
                ker
            )  # only need to fix "evidence-supporting-taxonomic-applicability"
            ker_entry = KeyEventRelationship(**ker)
            ker_entry.up_event = key_events[related_kes["upstream-id"]]
            ker_entry.down_event = key_events[related_kes["downstream-id"]]

            if applicability:
                ker_entry = self.__parse_applicability(applicability, ker_entry)

            ker_entires.append(ker_entry)

        return ker_entires

    def __update_sex_entries(self):
        """Update the entries in the Sex table."""
        new_imports = []
        for sex_key, sex_entry in self.sex_entries.items():
            if (
                sex_key not in self.current_sex_cache
            ):  # Sex key is new and needs to be imported
                self.current_sex_cache.add(
                    sex_key
                )  # Add to current cache to indicate it is imported
                new_imports.append(sex_entry)

        self.session.add_all(new_imports)
        self.session.commit()

    def __update_life_stage_entries(self):
        """Update the entries in the LifeStage table."""
        new_imports = []
        for ls, ls_obj in self.life_stages.items():
            if (
                ls not in self.current_ls_cache
            ):  # Life stage is new and needs to be imported
                self.current_ls_cache.add(
                    ls
                )  # Add to current cache to indicate it is imported
                new_imports.append(ls_obj)

        self.session.add_all(new_imports)
        self.session.commit()

    @staticmethod
    def __extract_weight_of_evidence_values(ker_entry: dict) -> dict:
        """Extract weight-of-evidence values."""
        woe = ker_entry.pop("weight-of-evidence")
        ker_entry["evidence_value"] = woe["value"]
        ker_entry["evidence_biological_plausibility"] = woe["biological-plausibility"]
        ker_entry["evidence_emperical_support_linkage"] = woe[
            "emperical-support-linkage"
        ]
        ker_entry["evidence_uncertainties_or_inconsistencies"] = woe[
            "uncertainties-or-inconsistencies"
        ]
        return ker_entry

    def import_key_events(self) -> int:
        """Import parsed key event data into database and return number of rows imported.

        Imports KeyEvent entries as well as new Sex and LifeStage entries.
        """
        parsed_kes = self.__parse_key_events()
        logger.info("Importing key events")
        self.session.add_all(parsed_kes)
        self.__update_sex_entries()  # New sex entries
        self.__update_life_stage_entries()  # New life stage entries
        self.session.commit()

        return len(parsed_kes)

    def __parse_key_events(self) -> list:
        """Extract key events to dict and map to connected tables.

        This process involves parsing and importing organ and cell terms tables.

        There is always an action associated with a Key Event under "biological-events", object and process are
        optional. Observed combinations:
        ('@object-id', '@action-id'), ('@object-id', '@process-id', '@action-id'), ('@process-id', '@action-id')
        There are certain entries with a list of these combinations instead of a single combination!
        """
        logger.info("Parsing key events")
        key_events = self.aop_data["key-event"]
        stressor_mapper = self.__get_aop_mapper(Stressor)

        ke_entires = []

        for ke in tqdm(key_events, total=len(key_events), desc="Importing key events"):
            ke[AOP_ID] = self.__get_aop_id(KE_JSON, ke["title"])
            ke[AOP_HASH] = ke.pop(ID)
            ke[REFERENCES] = ke.pop(REFERENCES)

            # Pop out terms with table relationships
            cell_term_data = ke.pop("cell-term", None)
            organ_term_data = ke.pop("organ-term", None)
            bio_events_dict = ke.pop("biological-events", None)
            applicability = ke.pop(APPLICABILITY, None)
            stressors = ke.pop("key-event-stressors", None)

            standardized_ke_dict = self.__standardize_keys(ke)
            key_event = KeyEvent(**standardized_ke_dict)

            if cell_term_data:
                self.__create_modify_organ_cell_object(
                    cell_term_data, CellTerm, key_event
                )

            if organ_term_data:
                self.__create_modify_organ_cell_object(
                    organ_term_data, OrganTerm, key_event
                )

            if bio_events_dict:
                self.__parse_bio_events(bio_events_dict, ke[AOP_HASH])

            if applicability:
                key_event = self.__parse_applicability(applicability, key_event)

            if stressors:
                key_event = self.__add_stressor_to_ke(
                    stressors, key_event, stressor_mapper
                )

            ke_entires.append(key_event)

        return ke_entires

    def __add_stressor_to_ke(
        self, stressors: dict, key_event: KeyEvent, mapper: dict
    ) -> KeyEvent:
        """Get stressor obj and append to key event. Returns modified key event obj."""
        stressor_data = self._listify(stressors["key-event-stressor"])
        stressor_ids = [stressor["@stressor-id"] for stressor in stressor_data]
        stressor_objs = [mapper[aop_hash] for aop_hash in stressor_ids]
        key_event.stressors = stressor_objs
        return key_event

    def __parse_applicability(self, applicability_data: dict, new_entry):
        if TAXONOMY in applicability_data:
            asso_class = self.class_mapper[TAXONOMY][type(new_entry)]
            evidence_lines = self._listify(applicability_data[TAXONOMY])

            for evidence in evidence_lines:
                tax_aop_hash = evidence["@taxonomy-id"]
                tax_evidence = evidence[EVIDENCE]
                tax_asso = asso_class(
                    evidence=tax_evidence
                )  # Create new association object
                tax_asso.taxonomy = self.taxonomies[
                    tax_aop_hash
                ]  # Set Tax entry to mapped Taxonomy obj
                new_entry.taxonomies.append(
                    tax_asso
                )  # Append association object to KeyEvent obj

        if SEX in applicability_data:
            asso_class = self.class_mapper[SEX][type(new_entry)]
            evidence_lines = self._listify(applicability_data[SEX])

            for evidence in evidence_lines:
                sex = evidence[SEX]
                sex_evidence = evidence[EVIDENCE]

                if sex in self.sex_entries:
                    sex_row = self.sex_entries[sex]

                else:
                    sex_row = Sex(sex=sex)
                    self.sex_entries[sex] = sex_row  # Add to cache

                sex_asso = asso_class(evidence=sex_evidence)  # New association obj
                sex_asso.sex = sex_row
                new_entry.sexes.append(sex_asso)

        if LIFESTAGE in applicability_data:
            asso_class = self.class_mapper[LIFESTAGE][type(new_entry)]
            evidence_lines = self._listify(applicability_data[LIFESTAGE])

            for evidence in evidence_lines:
                ls = evidence[LIFESTAGE]
                ls_evidence = evidence[EVIDENCE]

                if ls in self.life_stages:
                    ls_row = self.life_stages[ls]

                else:
                    ls_row = LifeStage(life_stage=ls)
                    self.life_stages[ls] = ls_row  # Add to cache

                ls_asso = asso_class(evidence=ls_evidence)  # New association obj
                ls_asso.life_stage = ls_row
                new_entry.life_stages.append(ls_asso)

        return new_entry

    def import_bio_events(self):
        """Import parsed bio events data into database and return number of rows imported.

        This depends on first importing key events to generate the bio_events attribute.
        """
        bio_mapper = (
            self.__query_bio_classes()
        )  # Bio class AOP IDs as keys and Bio class Objs as values
        key_event_mapper = self.__get_aop_mapper(KeyEvent)

        bio_event_entries = []
        for be_identifier, ke_ids in tqdm(
            self.bio_events.items(),
            total=len(self.bio_events),
            desc="Importing bio events",
        ):
            bio_class_objs = [
                bio_mapper[bio_key] for bio_key in be_identifier
            ]  # List of bio class objects
            key_events = [
                key_event_mapper[ke_id] for ke_id in ke_ids
            ]  # List of KeyEvent objects

            new_be = BiologicalEvent()
            for bio_class_obj in bio_class_objs:  # Compile BiologicalEvent
                if isinstance(bio_class_obj, BiologicalObject):
                    new_be.bio_object = bio_class_obj

                elif isinstance(bio_class_obj, BiologicalAction):
                    new_be.bio_action = bio_class_obj

                elif isinstance(bio_class_obj, BiologicalProcess):
                    new_be.bio_process = bio_class_obj

                else:
                    logger.error(f"Bad bio class obj called: {bio_class_obj}")

            new_be.key_events = key_events
            bio_event_entries.append(new_be)

        self.session.add_all(bio_event_entries)
        self.session.commit()

    def __parse_bio_events(self, bio_events: dict, key_event_aop_hash: str):
        """Parse bio event information in key events."""
        logger.info("Parsing biological events")
        bes = self._listify(bio_events["biological-event"])
        for be in bes:
            be_key = self.__create_unique_key(
                be
            )  # Sort bio AOP IDs into tuple and use as key

            if be_key in self.bio_events:
                self.bio_events[be_key].append(
                    key_event_aop_hash
                )  # Add KeyEvent obj to list

            else:
                self.bio_events[be_key] = [key_event_aop_hash]  # Start new list

    def __create_modify_organ_cell_object(
        self, term_values: dict, table, key_event: KeyEvent
    ):
        """Sanitize keys and values for an Organ or Cell Term and create/modify ORM obj.

        This method checks whether there already exists an ORM object to be added to the DB in the cache. If not,
        it will create a new one and add the key_event link. If there is an object, it simply appends the key event to
        the existing object.
        """
        term_cache_mapper = {CellTerm: self.cell_terms, OrganTerm: self.organ_terms}
        term_values["source_id"] = self.__split_source_id(term_values.pop("source-id"))
        unique_key = (
            term_values["name"],
            term_values["source"],
            term_values["source_id"],
        )

        if (
            unique_key in term_cache_mapper[table]
        ):  # Source/Source ID/Name already in term cache
            term_obj = term_cache_mapper[table][unique_key]
            term_obj.key_events.append(key_event)  # Add key event to obj
            term_cache_mapper[table][
                unique_key
            ] = term_obj  # Overwrite old cache obj with new modified one

        else:
            new_orm_obj = table(**term_values)  # Create new ORM obj
            new_orm_obj.key_events.append(key_event)  # Add key event to obj
            term_cache_mapper[table][unique_key] = new_orm_obj  # Add to cache

    def __query_bio_classes(self) -> dict:
        """Query database for IDs and objects for each bio class to use during KE parsing.

        Generate a dictionary of Bio Table AOP IDs as keys and the table object as values.
        """
        bas = self.__get_aop_mapper(BiologicalAction)
        bos = self.__get_aop_mapper(BiologicalObject)
        bps = self.__get_aop_mapper(BiologicalProcess)
        bio_results = {**bas, **bos, **bps}
        return bio_results

    def import_stressors(self) -> int:
        """Import parsed stressor data into database and return number of rows imported.

        WARNING: This only works correctly if chemical data has been imported into table.
        """
        parsed_stressors = self.__parse_stressors()
        logger.info("Importing stressors")
        self.session.add_all(parsed_stressors)
        self.session.commit()
        return len(parsed_stressors)

    def __parse_stressors(self):
        """Extract stressor information to dict and map to Chemical entries."""
        logger.info("Parsing stressors")

        chem_mapper = self.__get_aop_mapper(Chemical)
        if not chem_mapper:  # Chemicals weren't imported
            logger.warning(
                """Attempting to import stressor data into DB before chemicals. Stressors will not be
            properly mapped to chemicals!"""
            )

        stressor_entries = []
        stressors = self.aop_data["stressor"]
        for stressor in stressors:
            # stressor[AOP_ID] = self.__get_aop_id(STRESSOR_JSON, stressor["casrn"])  #TODO Parse chemicals for CASRN
            stressor[AOP_HASH] = stressor.pop(ID)
            chemical_data = stressor.pop("chemicals", None)
            stressor[CREATION] = datetime.fromisoformat(
                stressor.pop(CREATION_TIMESTAMP)
            )
            stressor[LAST_MODIFIED] = datetime.fromisoformat(stressor.pop(LM_TIMESTAMP))
            standardized_stressor_dict = self.__standardize_keys(stressor)
            stressor_entry = Stressor(**standardized_stressor_dict)

            if chemical_data:
                chem_inits = self._listify(
                    chemical_data["chemical-initiator"]
                )  # Map to list

                chemical_objs = []
                for val in chem_inits:
                    try:
                        chemical_objs.append(chem_mapper[val["@chemical-id"]])

                    except KeyError:
                        logger.error(
                            f"{val['@chemical-id']} not found in chemical dataset. Are chemicals imported?"
                        )

                stressor_entry.chemicals = chemical_objs

            stressor_entries.append(stressor_entry)

        return stressor_entries

    def __get_aop_id(self, json_url: str, map_key: str) -> Optional[int]:
        """Get the AOP ID from the downloaded JSON content."""
        if map_key in self.json_data[json_url]:
            return self.json_data[json_url][map_key]

    def import_chemicals(self) -> dict:
        """Import parsed chemical data into database and return number of rows imported for chemicals and synonyms."""
        parsed_chemicals = self.__parse_chemicals()

        synonym_rows = []
        with engine.connect() as conn:
            # Add chem to DB one at a time to get chem IDs for synonyms
            for aop_hash, chem_data in tqdm(
                parsed_chemicals.items(),
                total=len(parsed_chemicals),
                desc="Importing chemicals and synonyms",
            ):
                logger.info("Importing chemicals")
                # Format data
                chem_data[AOP_HASH] = aop_hash
                synonyms = chem_data.pop("synonyms")
                standardize_data = self.__standardize_keys(chem_data)
                standardize_data["name"] = standardize_data.pop("preferred_name")
                chem_result = conn.execute(insert(Chemical).values(standardize_data))

                # Add links to synonyms
                chem_row_id = chem_result.inserted_primary_key[0]
                for syn in synonyms:
                    synonym_rows.append({"term": syn, "chemical_id": chem_row_id})

            logger.info("Importing synonyms")
            synonyms_insert_result = conn.execute(insert(Synonym), synonym_rows)

        return {
            "chemicals": chem_result.rowcount,
            "synonyms": synonyms_insert_result.rowcount,
        }

    def __parse_chemicals(self) -> dict:
        """Extract chemicals into dictionary."""
        logger.info("Parsing chemicals")
        chemicals = self.aop_data["chemical"]
        parsed_chemicals = dict()
        for chem in chemicals:
            chem_id = chem.pop("@id")

            synonyms = []
            if "synonyms" in chem:
                synonyms = chem["synonyms"]["synonym"]

            chem["synonyms"] = [synonyms] if isinstance(synonyms, str) else synonyms

            parsed_chemicals[chem_id] = chem

        return parsed_chemicals

    def import_bio_classes(self) -> dict:
        """Parse and import bio classes and return number of rows imported.

        This includes bio object, action, and process.
        """
        bio_class_metadata = {
            "biological_object": {
                "aop_key": "biological-object",
                "table": BiologicalObject,
            },
            "biological_action": {
                "aop_key": "biological-action",
                "table": BiologicalAction,
            },
            "biological_process": {
                "aop_key": "biological-process",
                "table": BiologicalProcess,
            },
        }

        parsed_bio_data = self.__parse_bio_classes(bio_class_metadata)

        counts = dict()
        for bio_class, parsed_entries in tqdm(
            parsed_bio_data.items(),
            total=len(parsed_bio_data),
            desc="Importing bio tables",
        ):
            table = bio_class_metadata[bio_class]["table"]
            inserted = self.__import_simple_rows(entries=parsed_entries, table=table)
            logger.info(f"Inserted {inserted} rows into {bio_class}")
            counts[bio_class] = inserted

        return counts

    def __parse_bio_classes(self, bio_classes: dict) -> dict:
        """Extract bio class data into dictionaries. Returns dict of metadata information."""
        parsed_bio_data = dict()
        for (
            bio_class,
            metadata,
        ) in bio_classes.items():  # All bio classes structured similarly
            logger.info(f"Parsing {bio_class}")
            parsed_entries = dict()
            aop_entries = self.aop_data[metadata["aop_key"]]

            for entry in aop_entries:  # Iterate through class entries
                aop_hash = entry.pop(ID)
                source_id = entry.pop("source-id")
                entry["source_id"] = self.__split_source_id(source_id)
                parsed_entries[aop_hash] = entry

            parsed_bio_data[bio_class] = parsed_entries

        return parsed_bio_data

    def __parse_taxonomies(self) -> dict:
        """Extract taxonomies into dictionary."""
        taxos = self.aop_data["taxonomy"]
        species_names = self.__get_tax_id_cache()
        logger.info("Parsing taxonomies")

        parsed_taxos = dict()
        for taxo in taxos:
            entry_id = taxo.pop(ID)
            source_id = taxo.pop("source-id")
            parsed_id = self.__split_source_id(source_id)

            if parsed_id.startswith("WikiUser"):
                taxo[
                    "source_id"
                ] = parsed_id  # Only use "source_id" with WikiUser entries, all others are tax IDs
                taxo["tax_id"] = None
                taxo["species"] = None

            else:
                taxo["source_id"] = None
                taxo["tax_id"] = int(parsed_id)

                if (
                    parsed_id not in species_names
                ):  # Check cache first and if not there, query EnsEMBL
                    species_name = self.__lookup_species(parsed_id)
                    taxo["species"] = species_name
                    species_names[parsed_id] = species_name

                else:
                    taxo["species"] = species_names[parsed_id]

            parsed_taxos[entry_id] = taxo

        # Write parsed/queried taxonomies to cache file
        with open(TAXONOMY_CACHE, "w") as tax_file:
            json.dump(species_names, tax_file)

        return parsed_taxos

    def import_taxonomies(self) -> int:
        """Import parsed taxonomy data into database and return number of rows imported."""
        parsed_taxos = self.__parse_taxonomies()  # Writes taxonomy data to attribute
        inserted = self.__import_simple_rows(entries=parsed_taxos, table=Taxonomy)
        logger.info(f"Inserted {inserted} rows into taxonomy")
        self.taxonomies = self.__get_aop_mapper(Taxonomy)
        return inserted

    @staticmethod
    def _listify(entry: Union[dict, list]):
        """Return entry as list if not already."""
        return [entry] if isinstance(entry, dict) else entry

    @staticmethod
    def __import_simple_rows(entries: dict, table) -> int:
        """Import entries into specified table. Only works with simple tables. Returns number of rows inserted."""
        table_rows = []
        for aop_hash, entry_data in entries.items():
            entry_data[AOP_HASH] = aop_hash
            table_rows.append(entry_data)

        with engine.connect() as conn:
            result = conn.execute(insert(table), table_rows)

        return result.rowcount

    @staticmethod
    def __get_tax_id_cache() -> dict:
        """Import cached taxonomy IDs if JSON exists, else returns empty dict."""
        tax_cache = dict()
        if Path(TAXONOMY_CACHE).is_file():
            with open(TAXONOMY_CACHE, "r") as tax_file:
                tax_cache = json.load(tax_file)

        return tax_cache

    @staticmethod
    def __lookup_species(tax_id: str) -> Optional[str]:
        """Get species name from ensembl using tax ID."""
        logger.info(f"Querying EnsEMBL for {tax_id}")
        resp = requests.get(TAX_ID_LOOKUP.format(tax_id))
        if resp.ok:
            species = resp.json()["name"]
            return species

    @staticmethod
    def __standardize_keys(entry: dict) -> dict:
        """Replace "-" with "_" in the parsed metadata."""
        standardized_dict = dict()

        for key, value_dict in entry.items():
            standardized_dict[key.replace("-", "_")] = value_dict

        return standardized_dict

    def __get_aop_mapper(self, table) -> dict:
        """Generate a mapper with AOP IDs as keys and ORM objs as values for a specified table."""
        results = self.session.query(table.aop_hash, table).all()
        return {x[0]: x[1] for x in results}

    @staticmethod
    def __split_source_id(source_id: str) -> Union[str, int]:
        """Split the source ID to remove the prefix if it exists."""
        split_terms = re.split(r"_|:", source_id)

        if (
            len(split_terms) > 1 and split_terms[0] != "WikiUser"
        ):  # WikiUser for taxonomy
            return split_terms[1]

        else:  # No delim in term
            return source_id

    @staticmethod
    def __download_aop_xml():
        """Download the default AOP XML file to data directory."""
        if not Path(AOP_XML_FILE).is_file():
            logger.info(f"Downloading {AOP_XML_DOWNLOAD}")
            resp = requests.get(AOP_XML_DOWNLOAD)
            if resp.ok:
                with open(AOP_XML_FILE, "wb") as aopf:
                    aopf.write(resp.content)
                logger.info(f"{Path(AOP_XML_DOWNLOAD).name} saved to {AOP_XML_FILE}")

            else:
                logger.warning(f"Could not download {AOP_XML_DOWNLOAD}!")

    @staticmethod
    def __download_aop_json():
        """Download the AOP JSON to get AOP IDs."""
        downloaded_files = [file_path.name for file_path in AOP_DIR.iterdir()]
        for download_path in AOP_JSONS:
            json_file_name = Path(download_path).name
            if json_file_name not in downloaded_files:
                resp = requests.get(download_path)

                if resp.ok:
                    with open(AOP_DIR.joinpath(json_file_name), "w") as jsonf:
                        json.dump(resp.json(), jsonf)

                    logger.info(
                        f"{json_file_name} saved to {AOP_DIR.joinpath(json_file_name)}"
                    )

                else:
                    logger.warning(f"Could not download {json_file_name}!")

    @staticmethod
    def __create_unique_key(value_dict: dict) -> tuple:
        """Generate a qunique key by taking values form a dictionary, sorting them, and return the tuple."""
        return tuple(sorted(list(value_dict.values())))

    def annotate_term(self, source: str, term: Union[str, int]) -> str:
        """Get additional metadata on referenced term.

        Parameters
        ----------
        source : str
            Namespace of term e.g. CHEBI, MESH, etc
        term : Union[str, int]
            Value of term i.e. the identifier used to find term in namespace.

        Returns
        -------
        str
            New metadata on term.
        """
        pass

    def __xml_to_dict(self) -> dict:
        """Read and convert AOP XML to a dictionary, then write to JSON if not there. Returns XML content as dict."""
        self.__download_aop_xml()
        json_file_path = str(AOP_XML_FILE) + ".json"
        if not Path(json_file_path).is_file():
            with gzip.open(AOP_XML_FILE, "rb") as aopf:
                content = aopf.read()

            aop_dict = xmltodict.parse(content)

            with open(json_file_path, "w") as aopjson:
                json.dump(aop_dict, aopjson)

            logger.info(f"AOP JSON written to {json_file_path}")

        with open(json_file_path, "r") as aopjson:
            content_as_json = json.load(aopjson)

        return content_as_json


if __name__ == "__main__":
    import_aop_data()
