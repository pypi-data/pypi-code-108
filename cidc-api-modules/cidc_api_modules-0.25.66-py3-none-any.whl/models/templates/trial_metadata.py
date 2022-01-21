__all__ = [
    "Aliquot",
    "AssaysEnum",
    "ClinicalTrial",
    "Cohort",
    "CollectionEvent",
    "ConcentrationUnits",
    "MaterialUnits",
    "Participant",
    "Replacement",
    "Sample",
    "Shipment",
    "VolumeUnits",
]

import re
from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from sqlalchemy.dialects.postgresql import JSONB
from typing import List

from .model_core import MetadataModel, with_default_session

cimac_id_regex_pattern = "^C[A-Z0-9]{3}[A-Z0-9]{3}[A-Z0-9]{2}.[0-9]{2}$"
cimac_id_regex = re.compile(cimac_id_regex_pattern)

AssaysEnum = Enum(
    "ATACseq",
    "CyTOF",
    "ELISA",
    "H&E",
    "IHC",
    "mIF",
    "mIHC",
    "Olink",
    "RNAseq",
    "TCRseq",
    "WES",
    name="assay_enum",
)
ConcentrationUnits = Enum(
    "Nanogram per Microliter",
    "Milligram per Milliliter",
    "Micrograms per Microliter",
    "Cells per Vial",
    "Not Reported",
    "Other",
    name="concentration_units_enum",
)
MaterialUnits = Enum(
    "Microliters",
    "Milliliters",
    "Nanogram per Microliter",
    "Milligram per Milliliter",
    "Micrograms per Microliter",
    "Cells per Vial",
    "Slides",
    "Not Reported",
    "Other",
    name="material_units_enum",
)
Replacement = Enum(
    "Replacement Not Requested",
    "Replacement Requested",
    "Replacement Tested",
    "Not Reported",
    "Other",
    name="replace_enum",
)
VolumeUnits = Enum(
    "Microliters", "Milliliters", "Not Reported", "Other", name="volume_units_enum"
)


class ClinicalTrial(MetadataModel):
    """A clinical trial in the CIMAC-CIDC network."""

    __tablename__ = "clinical_trials"

    protocol_identifier = Column(
        String,
        primary_key=True,  # allows for use as Foreign Key
        doc="Trial identifier used by lead organization, ie. Center for Experimental Therapeutics Program (CTEP) ID or Industry Sponsored ID.  This is usually a short identifier. Example: E4412.",
    )
    nct_id = Column(String, doc="ClinicalTrials.gov identifier. Example: NCT03731260.")
    nci_id = Column(String, doc="NCI Trial Identifier. Example: NCI22345.")
    trial_name = Column(String, doc="Name of clinical trial.")
    trial_description = Column(String, doc="A brief description of the clinical trial.")
    trial_organization = Column(
        String,
        doc="Name of the primary organization that oversees the clinical trial. Example: ECOG-ACRIN, SWOG, etc.",
    )
    grant_or_affiliated_network = Column(
        String,
        doc="The primary organization providing grant funding and supporting the trial.",
    )
    trial_status = Column(
        String, doc="What stage the clinical trial is at in its process."
    )
    biobank = Column(
        String,
        doc="The primary organization responsible for storing biospecimens from this study.",
    )
    lead_cimac_pis = Column(
        String, doc="The PI(s) from the CIMAC-CIDC network responsible for this study."
    )
    lead_cimac_contacts = Column(String, doc="A list of contacts for this trial.")
    lead_trial_staff = Column(
        String, doc="The names of lead trial staff members other than the PIs."
    )
    justification = Column(
        String,
        doc="A description of the reasons why this study could provide insight into molecular biomarkers of immunotherapy.",
    )
    biomarker_plan = Column(
        String,
        doc="A description of the objectives and hypotheses for the proposed biomarkers.",
    )
    data_sharing_plan = Column(
        String,
        doc="A description of the rules governing data sharing and publications.",
    )

    # expected_assays : List[str], doc="A list of assays the CIDC expects to receive for this trial."
    # assays : List[Assay], doc="Assays for this trial"
    # analysis : List[Analysis], doc="Analyses for this trial"
    # clinical_data : ClinicalData, doc="Clinical data for this trial"
    # schema : artifact_image, doc="An image of the schema of this trial."

    cohorts = relationship(
        "Cohort",
        back_populates="trial",
        sync_backref=False,
        viewonly=True,
        doc="The collection of all cohorts related to this trial.",
    )
    collection_events = relationship(
        "CollectionEvent",
        back_populates="trial",
        sync_backref=False,
        viewonly=True,
        doc="The collection of all collection events related to this trial.",
    )
    shipments = relationship(
        "Shipment",
        back_populates="trial",
        sync_backref=False,
        viewonly=True,
        doc="The collection of all shipments related to this trial.",
    )
    participants = relationship(
        "Participant",
        back_populates="trial",
        sync_backref=False,
        viewonly=True,
        doc="The collection of participants in this trial.",
    )

    @property
    @with_default_session
    def allowed_cohort_names(self, *, session: Session) -> List[str]:
        """Allowed values for Participant.cohort_name for this trial."""
        return [
            c.cohort_name
            for c in session.query(Cohort)
            .filter(Cohort.trial_id == self.protocol_identifier)
            .all()
        ]

    @property
    @with_default_session
    def allowed_collection_event_names(self, *, session: Session) -> List[str]:
        """Allowed values for Sample.collection_event_name for this trial."""
        return [
            ce.event_name
            for ce in session.query(CollectionEvent)
            .filter(CollectionEvent.trial_id == self.protocol_identifier)
            .all()
        ]


class Cohort(MetadataModel):
    __tablename__ = "cohorts"

    trial_id = Column(
        String, ForeignKey(ClinicalTrial.protocol_identifier), primary_key=True
    )
    cohort_name = Column(
        String, primary_key=True
    )  # both True allows for use as multi Foreign Key

    trial = relationship(
        ClinicalTrial, back_populates="cohorts", sync_backref=False, viewonly=True
    )
    participants = relationship(
        "Participant", back_populates="cohort", sync_backref=False, viewonly=True
    )


class CollectionEvent(MetadataModel):
    __tablename__ = "collection_events"

    trial_id = Column(
        String, ForeignKey(ClinicalTrial.protocol_identifier), primary_key=True
    )
    event_name = Column(
        String, primary_key=True
    )  # both True allows for use as multi Foreign Key

    samples = relationship(
        "Sample", back_populates="collection_event", sync_backref=False, viewonly=True
    )
    trial = relationship(
        ClinicalTrial,
        back_populates="collection_events",
        sync_backref=False,
        viewonly=True,
    )


class Shipment(MetadataModel):
    __tablename__ = "shipments"

    trial_id = Column(
        String, ForeignKey(ClinicalTrial.protocol_identifier), primary_key=True
    )
    manifest_id = Column(
        String,
        primary_key=True,  # both True allows for use as multi Foreign Key
        unique=True,
        doc="Filename of the manifest used to ship this sample. Example: E4412_PBMC.",
    )
    json_data = Column(JSONB, nullable=False, default={})

    __table_args__ = (
        UniqueConstraint(trial_id, manifest_id, name="unique_trial_manifest"),
    )

    assay_priority = Column(
        Enum(
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "Not Reported",
            "Other",
            name="assay_priority_enum",
        ),
        doc="Priority of the assay as it appears on the intake form.",
    )
    assay_type = Column(AssaysEnum, nullable=True, doc="Assay and sample type used.")
    courier = Column(
        Enum("FEDEX", "USPS", "UPS", "Inter-Site Delivery", name="courier_enum"),
        doc="Courier utilized for shipment.",
    )
    tracking_number = Column(
        String, doc="Air bill number assigned to shipment. Example: 4567788343.",
    )
    account_number = Column(
        String,
        doc="Courier account number to pay for shipping if available. Example: 45465732.",
    )
    shipping_condition = Column(
        Enum(
            "Frozen_Dry_Ice",
            "Frozen_Shipper",
            "Ice_Pack",
            "Ambient",
            "Not Reported",
            "Other",
            name="shipping_condition_enum",
        ),
        doc="Type of shipment made.",
    )
    date_shipped = Column(Date, doc="Date of shipment.")
    date_received = Column(Date, doc="Date of receipt.")
    quality_of_shipment = Column(
        Enum(
            "Specimen shipment received in good condition",
            "Specimen shipment received in poor condition",
            "Not Reported",
            "Other",
            name="quality_of_shipment_enum",
        ),
        doc="Indication that specimens were received in good condition.",
    )
    ship_from = Column(String, doc="Contact information for shipment.")
    ship_to = Column(String, doc="Physical shipping address of the destination.")
    receiving_party = Column(
        Enum(
            "MDA_Wistuba",
            "MDA_Bernatchez",
            "MDA_Al-Atrash",
            "MSSM_Gnjatic",
            "MSSM_Rahman",
            "MSSM_Kim-Schulze",
            "MSSM_Bongers",
            "DFCI_Wu",
            "DFCI_Hodi",
            "DFCI_Severgnini",
            "DFCI_Livak",
            "Broad_Cibulskis",
            "Stanf_Maecker",
            "Stanf_Bendall",
            "NCH",
            "Adaptive",
            "FNLCR_MoCha",
            name="receiving_party_enum",
        ),
        doc="Site where sample was shipped to be assayed.",
    )

    trial = relationship(
        ClinicalTrial, back_populates="shipments", sync_backref=False, viewonly=True
    )
    samples = relationship(
        "Sample", back_populates="shipment", sync_backref=False, viewonly=True
    )


class Participant(MetadataModel):
    __tablename__ = "participants"

    trial_id = Column(
        String, ForeignKey(ClinicalTrial.protocol_identifier), primary_key=True
    )
    cimac_participant_id = Column(
        String,
        CheckConstraint("cimac_participant_id ~ '^C[A-Z0-9]{3}[A-Z0-9]{3}$'"),
        primary_key=True,  # both True allows for use as multi Foreign Key
        doc="Participant identifier assigned by the CIMAC-CIDC Network. Formated as: C?????? (first 7 characters of CIMAC ID)",
    )
    trial_participant_id = Column(
        String,
        nullable=True,
        doc="Trial Participant Identifier. Crypto-hashed after upload.",
    )
    cohort_name = Column(String, nullable=True)
    json_data = Column(JSONB, nullable=False, default={})

    __table_args__ = (
        UniqueConstraint(
            trial_id, cimac_participant_id, name="unique_trial_participant"
        ),
        ForeignKeyConstraint(
            [trial_id, cohort_name], [Cohort.trial_id, Cohort.cohort_name]
        ),
    )

    gender = Column(
        Enum("Male", "Female", "Not Specified", "Other", name="gender_enum"),
        doc="Identifies the gender of the participant.",
    )
    race = Column(
        Enum(
            "American Indian/Alaska Native",
            "Asian",
            "Black/African American",
            "Native Hawaiian/Pacific Islander",
            "White",
            "Not Reported",
            "Unknown",
            "Other",
            name="race_enum",
        ),
        doc="NIH Racial and Ethnic Categories and Definitions for NIH Diversity Programs and for Other Reporting Purposes (NOT-OD-15-089),  Release Date: April 8, 2015.",
    )
    ethnicity = Column(
        Enum(
            "Hispanic or Latino",
            "Not Hispanic or Latino",
            "Not reported",
            "Unknown",
            "Other",
            name="ethnicity_enum",
        ),
        doc="NIH Racial and Ethnic Categories and Definitions for NIH Diversity Programs and for Other Reporting Purposes (NOT-OD-15-089),  Release Date: April 8, 2015.",
    )

    cohort = relationship(
        Cohort, back_populates="participants", sync_backref=False, viewonly=True
    )
    samples = relationship(
        "Sample", back_populates="participant", sync_backref=False, viewonly=True
    )
    trial = relationship(
        ClinicalTrial, back_populates="participants", sync_backref=False, viewonly=True
    )


class Sample(MetadataModel):
    __tablename__ = "samples"

    trial_id = Column(String, primary_key=True)
    cimac_id = Column(
        String,
        primary_key=True,  # both True allows for use as multi Foreign Key
        unique=True,
        doc="Specimen identifier assigned by the CIMAC-CIDC Network. Formatted as C????????.??",
    )
    cimac_participant_id = Column(String, nullable=False)
    manifest_id = Column(String, nullable=False)
    collection_event_name = Column(String, nullable=True)
    json_data = Column(JSONB, nullable=False, default={})

    __table_args__ = (
        ForeignKeyConstraint(
            [trial_id, cimac_participant_id],
            [Participant.trial_id, Participant.cimac_participant_id],
        ),
        ForeignKeyConstraint(
            [trial_id, collection_event_name],
            [CollectionEvent.trial_id, CollectionEvent.event_name],
        ),
        ForeignKeyConstraint(
            [trial_id, manifest_id], [Shipment.trial_id, Shipment.manifest_id]
        ),
        CheckConstraint("cimac_id ~ '^C[A-Z0-9]{3}[A-Z0-9]{3}[A-Z0-9]{2}.[0-9]{2}$'"),
    )

    shipping_entry_number = Column(
        Integer,
        doc="Provides a numbered identifier for patient (sample) entry in a shipment manifest.",
    )
    box_number = Column(
        String,
        doc="Identifier if sample shipment container includes multiple boxes for each assay.",
    )
    surgical_pathology_report_id = Column(
        String,
        doc="A unique identifier so someone can find the surgical pathology report.",
    )
    clinical_report_id = Column(
        String, doc="A unique identifier so someone can find the clinical report."
    )
    parent_sample_id = Column(
        String,
        doc="Sample identifier assigned by the biorepository site. Crypto-hashed after upload.",
    )
    processed_sample_id = Column(
        String,
        doc="Aliquot identifier assigned by the biorepository site. Crypto-hashed after upload.",
    )
    site_description = Column(
        String, doc="Descritpion of the topography category. e.g LUNG AND BRONCHUS"
    )
    topography_code = Column(
        String,
        doc="ICD-0-3 topography site code from which a specimen was isolated. e.g. C34.1",
    )
    topography_description = Column(
        String, doc="ICD-0-3 site code description. e.g. Upper lobe, lung"
    )
    histology_behavior = Column(
        String, doc="ICD-0-3 code for histology and behavior. e.g. 9665/3"
    )
    histology_behavior_description = Column(
        String,
        doc="ICD-0-3 histology and behavior code description. e.g. Hodgkin lymphoma, nod. scler., grade 1",
    )
    sample_location = Column(
        String, doc="Sample location within the shipping container. Example: A1.",
    )
    type_of_sample = Column(
        Enum(
            "Tumor Tissue",
            "Normal Tissue",
            "Skin Tissue",
            "Blood",
            "Bone Marrow",
            "Cerebrospinal Fluid",
            "Lymph Node",
            "Stool",
            "Cell Product",
            "White Blood Cell Apheresis",
            "Not Reported",
            "Other",
            name="sample_types_enum",
        ),
        nullable=True,
        doc="Type of sample sent.",
    )
    type_of_tumor_sample = Column(
        Enum(
            "Metastatic Tumor",
            "Primary Tumor",
            "Not Reported",
            "Other",
            name="type_of_tumor_sample_enum",
        ),
        doc="The type of tumor sample obtained (primary or metastatic).",
    )
    sample_collection_procedure = Column(
        Enum(
            "Blood Draw",
            "Excision",
            "Core Biopsy",
            "Punch Biopsy",
            "Endoscopic Biopsy",
            "Bone Marrow Core Biopsy",
            "Bone Marrow Aspirate",
            "Lumbar Puncture",
            "Aspirate",
            "Fine-Needle Aspiration",
            "Not Reported",
            "Other",
            name="sample_collection_procedure_enum",
        ),
        doc="Indicates the specimen source of the sample shipped. Example: Na Heparin blood draw aliquots (2 of three), FFPE block #52",
    )
    core_number = Column(
        Integer, doc="The biopsy core number from which the sample was used."
    )
    fixation_stabilization_type = Column(
        Enum(
            "Archival FFPE",
            "Fresh Specimen",
            "Frozen Specimen",
            "Formalin-Fixed Paraffin-Embedded",
            "Optimum cutting temperature medium",
            "Thaw-Lyse",
            "Not Reported",
            "Other",
            name="fixation_stabilization_type_enum",
        ),
        doc="Type of specimen fixation or stabilization that was employed by the site directly after collection.",
    )
    type_of_primary_container = Column(
        Enum(
            "Sodium heparin",
            "Blood specimen container with EDTA",
            "Potassium EDTA",
            "Streck Blood Collection Tube",
            "Stool collection container with DNA stabilizer",
            "Not Reported",
            "Other",
            name="type_of_primary_container_enum",
        ),
        CheckConstraint(
            "type_of_sample != 'blood' or type_of_primary_container is not null"
        ),
        doc="The format in which the sample was sent.",
    )
    sample_volume = Column(
        Numeric, doc="Volume of the parent sample (e.g. Heparin tube volume)"
    )
    sample_volume_units = Column(VolumeUnits, doc="Unit for the parent sample volume.")
    processed_sample_type = Column(
        Enum(
            "Whole Blood",
            "Plasma",
            "PBMC",
            "Buffy Coat",
            "Bone Marrow Mononuclear Cell",
            "Supernatant",
            "Cell Pellet",
            "H&E-Stained Fixed Tissue Slide Specimen",
            "Fixed Slide",
            "Tissue Scroll",
            "FFPE Punch",
            "Not Reported",
            "Other",
            name="processed_sample_type_enum",
        ),
        doc="The type of processing that was performed on the collected specimen by the Biobank for storage.",
    )
    processed_sample_volume = Column(Numeric, doc="Volume of the processed sample.")
    processed_sample_volume_units = Column(
        VolumeUnits, doc="Volume units of the processed sample."
    )
    processed_sample_concentration = Column(
        Numeric, doc="The concentration of the processed sample."
    )
    processed_sample_concentration_units = Column(
        ConcentrationUnits, doc="The concentration units for the processed sample."
    )
    processed_sample_quantity = Column(
        Numeric,
        doc="Quantity of the processed sample (e.g. number of slides cut for DNA extraction).",
    )
    processed_sample_derivative = Column(
        Enum(
            "Tumor DNA",
            "Tumor RNA",
            "Germline DNA",
            "Circulating Tumor-Derived DNA",
            "Not Reported",
            "Other",
            name="processed_sample_derivative_enum",
        ),
        doc="The type of derivative or analyte extracted from the specimen to be shipped for testing.",
    )
    sample_derivative_volume = Column(
        Numeric, doc="Volume of the analyte or derivative shipped."
    )
    sample_derivative_volume_units = Column(
        VolumeUnits, doc="Volume units of each analyte or derivative shipped."
    )
    sample_derivative_concentration = Column(
        Numeric, doc="The concentration of analyte or derivative shipped."
    )
    sample_derivative_concentration_units = Column(
        ConcentrationUnits,
        doc="The concentration units for the analyte or derivative shipped.",
    )
    tumor_tissue_total_area_percentage = Column(
        Numeric,
        CheckConstraint(
            "tumor_tissue_total_area_percentage >= 0 and tumor_tissue_total_area_percentage <= 100"
        ),
        doc="Score the percentage of tumor (including tumor bed) tissue area of the slide (e.g. vs non-malignant or normal tissue)",
    )
    viable_tumor_area_percentage = Column(
        Numeric,
        CheckConstraint(
            "viable_tumor_area_percentage >= 0 and viable_tumor_area_percentage <= 100"
        ),
        doc="Score the percentage of viable tumor cells comprising the tumor bed area",
    )
    viable_stroma_area_percentage = Column(
        Numeric,
        CheckConstraint(
            "viable_stroma_area_percentage >= 0 and viable_stroma_area_percentage <= 100"
        ),
        doc="Score the evaluation of stromal elements (this indicates the % area of tumor bed occupied by non-tumor cells, including inflammatory cells [lymphocytes, histiocytes, etc], endothelial cells, fibroblasts, etc)",
    )
    necrosis_area_percentage = Column(
        Numeric,
        CheckConstraint(
            "necrosis_area_percentage >= 0 and necrosis_area_percentage <= 100"
        ),
        doc="Score the percentage area of necrosis",
    )
    fibrosis_area_percentage = Column(
        Numeric,
        CheckConstraint(
            "fibrosis_area_percentage >= 0 and fibrosis_area_percentage <= 100"
        ),
        doc="Score the percentage area of Fibrosis",
    )
    din = Column(
        Numeric,
        CheckConstraint("din >= 0 and din <= 10"),
        doc="Provides a DNA Integrity Numeric as an indication of extraction quality (values of 1-10)",
    )
    a260_a280 = Column(
        Numeric,
        CheckConstraint("a260_a280 >= 0 and a260_a280 <= 2"),
        doc="Provides an absorbance percentage ratio indicating purity of DNA (values of 0 to 2)",
    )
    a260_a230 = Column(
        Numeric,
        CheckConstraint("a260_a230 >= 0 and a260_a230 <= 3"),
        doc="Provides an absorbance percentage ratio indicating presence of contaminants (values of 0 to 3)",
    )
    pbmc_viability = Column(
        Numeric,
        CheckConstraint("pbmc_viability >= 0 and pbmc_viability <= 100"),
        doc="Receiving site determines the percent recovered cells that are viable after thawing.",
    )
    pbmc_recovery = Column(
        Numeric,
        doc="Receiving site determines number for PBMCs per vial recovered upon receipt.",
    )
    pbmc_resting_period_used = Column(
        Enum(
            "Yes", "No", "Not Reported", "Other", name="pbmc_resting_period_used_enum"
        ),  # should be Boolean, nullable=True
        doc="Receiving site indicates if a resting period was used after PBMC recovery.",
    )
    material_used = Column(
        Numeric,
        doc="Receiving site indicates how much material was used for assay purposes.",
    )
    material_used_units = Column(
        MaterialUnits,
        doc="Units for the amount of material used; should be the same value as Specimen Analyte units.",
    )
    material_remaining = Column(
        Numeric,
        doc="Receiving site indicates how much material remains after assay use.",
    )
    material_remaining_units = Column(
        MaterialUnits, doc="Units for the amount of material remaining."
    )
    material_storage_condition = Column(
        Enum(
            "RT",
            "4oC",
            "(-20)oC",
            "(-80)oC",
            "LN",
            "Not Reported",
            "Other",
            name="material_storage_condition_enum",
        ),
        doc="Storage condition of the material once it was received.",
    )
    quality_of_sample = Column(
        Enum(
            "Pass", "Fail", "Not Reported", "Other", name="quality_of_sample_enum"
        ),  # could be Boolean, nullable=True
        doc="Final status of sample after QC and pathology review.",
    )
    sample_replacement = Column(
        Replacement, doc="Indication if sample replacement is/was requested."
    )
    residual_sample_use = Column(
        Enum(
            "Sample Returned",
            "Sample Sent to Another Lab",
            "Sample received from CIMAC",
            "Not Reported",
            "Other",
            name="residual_sample_use_enum",
        ),
        doc="Indication if sample was sent to another location or returned back to biorepository.",
    )
    comments = Column(String, doc="Comments on sample testing.")
    diagnosis_verification = Column(
        Enum(
            "Local review not consistent with diagnostic pathology report",
            "Local review consistent with diagnostic pathology report",
            "Not Available",
            "Not Reported",
            "Other",
            name="diagnosis_verification_enum",
        ),
        doc="Indicates whether the local pathology review was consistent with the diagnostic pathology report.",
    )
    intended_assay = Column(
        AssaysEnum,
        doc="The assay that this sample is expected to be used as input for.",
    )

    aliquots = relationship(
        "Aliquot",
        back_populates="sample",
        sync_backref=False,
        viewonly=True,
        doc="Pertaining to a portion (volume or weight) of the whole.",
    )
    collection_event = relationship(
        CollectionEvent, back_populates="samples", sync_backref=False, viewonly=True
    )
    participant = relationship(
        Participant, back_populates="samples", sync_backref=False, viewonly=True
    )
    shipment = relationship(
        Shipment, back_populates="samples", sync_backref=False, viewonly=True
    )


class Aliquot(MetadataModel):
    __tablename__ = "aliquots"

    sample_id = Column(String, ForeignKey(Sample.cimac_id), primary_key=True)
    slide_number = Column(
        String,  # should be Integer
        CheckConstraint(
            "slide_number ~ '^[0-9]{1,2}$'"
        ),  # should be "slide_number >= 0 and slide_number < 100"
        primary_key=True,  # both True allows for use as multi Foreign Key
        doc="Two digit number that indicates the sequential order of slide cuts, assigned by the CIMAC-CIDC Network.",
    )
    quantity = Column(Integer, doc="Quantity of each aliquot shipped.")
    aliquot_replacement = Column(
        Replacement, doc="Status of aliquot if replacement is/was requested.",
    )
    aliquot_status = Column(
        Enum(
            "Aliquot Returned",
            "Aliquot Exhausted",
            "Remainder used for other Assay",
            "Aliquot Leftover",
            "Other",
            name="aliquot_status_enum",
        ),
        doc="Status of aliquot used for other assay, exhausted, destroyed, or returned.",
    )
    material_extracted = Column(
        Enum("DNA", "RNA", "cfDNA", "Other", name="material_extracted_enum"),
        doc="The type of biological material that was extracted from this aliquot.",
    )
    extracted_concentration = Column(
        String,
        doc="The concentration of biological material that was extracted from this aliquot.",
    )
    aliquot_amount = Column(
        String, doc="The amount of extracted aliquot shipped. Example: 400 ng"
    )  # RECHECK Should this be moved to Sample or renamed?
    lymphocyte_influx = Column(
        String,
        doc="Extent of lymphocytic infiltration into the tumor stroma or surrounding environment. Example: 2",
    )

    sample = relationship(
        Sample, back_populates="aliquots", sync_backref=False, viewonly=True
    )
