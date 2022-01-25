__all__ = [
    # "ClinicalDataTemplate",
    "PbmcManifest",
    "TissueSlideManifest",
]

from sqlalchemy import Column
from typing import Any, Dict, List

from .core import Entry, MetadataTemplate, WorksheetConfig
from .model_core import cimac_id_to_cimac_participant_id, identity

from .trial_metadata import Participant, Sample, Shipment

# from .extra_metadata import ClinicalData


# ClinicalDataTemplate = MetadataTemplate(
#     upload_type="clinical_data",
#     purpose="manifest",
#     worksheet_configs=[
#         WorksheetConfig(
#             "Tier 1",
#             [Entry(ClinicalData.trial_id, name="Protocol identifier")],
#             {
#                 "Demographics": [
#                     Entry(
#                         Participant.cimac_participant_id,
#                         process_as={ClinicalData.cimac_participant_id: identity},
#                     ),
#                     Entry(ClinicalData.race),
#                     Entry(ClinicalData.gender, name="Sex",),
#                     Entry(ClinicalData.ethnicity, name="Ethnic group"),
#                     Entry(ClinicalData.age),
#                 ],
#                 "History": [
#                     Entry(ClinicalData.prior_surgery),
#                     Entry(ClinicalData.prior_radiation_therapy),
#                     Entry(ClinicalData.prior_immunotherapy),
#                     Entry(ClinicalData.number_prior_systemic_treatments),
#                     Entry(ClinicalData.prior_therapy_type),
#                 ],
#                 "Disease & Baseline": [
#                     Entry(
#                         ClinicalData.mod_ann_arbor_stage,
#                         name="Modified Ann Arbor Stage",
#                     ),
#                     Entry(ClinicalData.ecog_ps),
#                     Entry(ClinicalData.years_from_initial_diagnosis),
#                     Entry(ClinicalData.type_of_most_recent_treatment),
#                     Entry(ClinicalData.response_to_most_recent_treatment),
#                     Entry(ClinicalData.duration_of_remission),
#                     Entry(ClinicalData.years_from_recent_treatment),
#                     Entry(ClinicalData.disease_stage),
#                     Entry(ClinicalData.disease_grade),
#                 ],
#             },
#         ),
#     ],
# )

# To share the base WorksheetConfig's between all of the templates
# we'll use variables to represent where we can add custom elements
# into the otherwise static configs and then return the object
# # not using a subclass so that they are still MetadataTemplate's
# PREFERED: changes may need to be made here to allow for new custom elements
# ALERNATE: can add as post-hoc modifications to individual manifest templates
def _BaseManifestTemplate(
    upload_type: str,
    filled_by_biorepository: List[Entry],
    filled_by_cimac_lab: List[Entry],
    essential_patient_data: bool = False,
    constants: Dict[Column, Any] = {},
):
    worksheets = [
        WorksheetConfig(
            "Shipment",
            [
                Entry(
                    Shipment.trial_id,
                    name="Protocol identifier",
                    process_as={
                        Participant.trial_id: identity,
                        Sample.trial_id: identity,
                    },
                ),
                Entry(Shipment.manifest_id, process_as={Sample.manifest_id: identity},),
                Entry(Shipment.assay_priority, deprecated=True),
                Entry(
                    Shipment.assay_type,
                    process_as={Sample.intended_assay: identity},
                    deprecated=True,
                ),
                Entry(Shipment.receiving_party, deprecated=True),
                Entry(Shipment.courier, deprecated=True),
                Entry(Shipment.tracking_number, deprecated=True),
                Entry(Shipment.account_number, deprecated=True),
                Entry(Shipment.shipping_condition, deprecated=True),
                Entry(Shipment.date_shipped, deprecated=True),
                Entry(Shipment.date_received, deprecated=True),
                Entry(Shipment.quality_of_shipment, deprecated=True),
                Entry(Shipment.ship_from, deprecated=True),
                Entry(Shipment.ship_to, deprecated=True),
            ],
            {},
        ),
        WorksheetConfig(
            "Samples",
            [],
            {
                "IDs": [
                    Entry(
                        Sample.shipping_entry_number, name="Entry (#)", deprecated=True
                    ),
                    Entry(Sample.collection_event_name),
                    Entry(Participant.cohort_name),
                    Entry(
                        Participant.trial_participant_id,
                        name="Participant id",
                        deprecated=True,
                    ),
                    Entry(Sample.parent_sample_id, deprecated=True),
                    Entry(Sample.processed_sample_id, deprecated=True),
                    Entry(
                        Sample.cimac_id,
                        process_as={
                            Sample.cimac_participant_id: cimac_id_to_cimac_participant_id,
                            Participant.cimac_participant_id: cimac_id_to_cimac_participant_id,
                        },
                    ),
                ],
                "Filled by Biorepository": filled_by_biorepository,
                "Filled by CIMAC Lab": filled_by_cimac_lab,
            },
        ),
    ]
    if essential_patient_data:
        worksheets.append(
            WorksheetConfig(
                "Essential Patient Data",
                [],
                {
                    "Path Concordance Verification": [
                        Entry(
                            Sample.shipping_entry_number,
                            name="Entry (#)",
                            deprecated=True,
                        ),
                        Entry(
                            Participant.trial_participant_id,
                            name="Participant id",
                            deprecated=True,
                        ),
                        Entry(
                            Sample.cimac_id,
                            process_as={
                                Participant.cimac_participant_id: cimac_id_to_cimac_participant_id,
                                Sample.cimac_participant_id: cimac_id_to_cimac_participant_id,
                            },
                        ),
                        Entry(Sample.surgical_pathology_report_id, deprecated=True),
                        Entry(Sample.clinical_report_id, deprecated=True),
                        Entry(Sample.collection_event_name),
                        Entry(Sample.diagnosis_verification, deprecated=True),
                    ],
                    "ICD-0-3 Code/Description": [
                        Entry(Sample.site_description, deprecated=True),
                        Entry(Sample.topography_code, deprecated=True),
                        Entry(Sample.topography_description, deprecated=True),
                        Entry(
                            Sample.histology_behavior,
                            name="Histology/behavior",
                            deprecated=True,
                        ),
                        Entry(
                            Sample.histology_behavior_description,
                            name="Histology/behavior description",
                            deprecated=True,
                        ),
                    ],
                    "Demographics": [
                        Entry(Participant.gender, name="Sex", deprecated=True),
                        Entry(Participant.race, deprecated=True),
                        Entry(
                            Participant.ethnicity, name="Ethnic group", deprecated=True
                        ),
                    ],
                },
            )
        )
    return MetadataTemplate(
        upload_type=upload_type,
        purpose="manifest",
        worksheet_configs=worksheets,
        constants=constants,
    )


PbmcManifest = _BaseManifestTemplate(
    upload_type="pbmc",
    filled_by_biorepository=[
        Entry(Sample.box_number, deprecated=True),
        Entry(Sample.sample_location, deprecated=True),
        Entry(Sample.type_of_sample, deprecated=True),
        Entry(Sample.sample_collection_procedure, deprecated=True),
        Entry(Sample.type_of_primary_container, deprecated=True),
        Entry(Sample.processed_sample_type, deprecated=True),
        Entry(Sample.processed_sample_volume, deprecated=True),
        Entry(Sample.processed_sample_volume_units, deprecated=True),
        Entry(Sample.processed_sample_concentration, deprecated=True),
        Entry(Sample.processed_sample_concentration_units, deprecated=True),
        Entry(Sample.processed_sample_derivative, deprecated=True),
        Entry(Sample.sample_derivative_volume, deprecated=True),
        Entry(Sample.sample_derivative_volume_units, deprecated=True),
        Entry(Sample.sample_derivative_concentration, deprecated=True),
        Entry(Sample.sample_derivative_concentration_units, deprecated=True),
    ],
    filled_by_cimac_lab=[
        Entry(Sample.pbmc_viability, deprecated=True),
        Entry(Sample.pbmc_recovery, deprecated=True),
        Entry(Sample.pbmc_resting_period_used, deprecated=True),
        Entry(Sample.material_used, deprecated=True),
        Entry(Sample.material_remaining, deprecated=True),
        Entry(Sample.material_storage_condition, deprecated=True),
        Entry(Sample.quality_of_sample, deprecated=True),
        Entry(Sample.sample_replacement, deprecated=True),
        Entry(Sample.residual_sample_use, deprecated=True),
        Entry(Sample.comments, deprecated=True),
    ],
    essential_patient_data=True,
)

TissueSlideManifest = _BaseManifestTemplate(
    upload_type="tissue_slide",
    filled_by_biorepository=[
        Entry(Sample.box_number, deprecated=True),
        Entry(Sample.sample_location, deprecated=True),
        Entry(Sample.type_of_sample, deprecated=True),
        Entry(Sample.type_of_tumor_sample, deprecated=True),
        Entry(Sample.sample_collection_procedure, deprecated=True),
        Entry(Sample.core_number, deprecated=True),
        Entry(
            Sample.fixation_stabilization_type,
            name="Fixation/stabilization type",
            deprecated=True,
        ),
        Entry(Sample.processed_sample_type, deprecated=True),
        Entry(Sample.processed_sample_quantity, deprecated=True),
    ],
    filled_by_cimac_lab=[
        Entry(Sample.material_used, deprecated=True),
        Entry(Sample.material_used_units, deprecated=True),
        Entry(Sample.material_remaining, deprecated=True),
        Entry(Sample.material_remaining_units, deprecated=True),
        Entry(Sample.material_storage_condition, deprecated=True),
        Entry(Sample.quality_of_sample, deprecated=True),
        Entry(Sample.sample_replacement, deprecated=True),
        Entry(Sample.residual_sample_use, deprecated=True),
        Entry(Sample.comments, deprecated=True),
    ],
    essential_patient_data=False,
)
