# __all__ = [
#     "ClinicalData",
#     "ClinicalYesNoEnum",
#     "DiseaseStageEnum",
#     "DiseaseGradeEnum",
#     "EcogPsEnum",
#     "EthnicityEnum",
#     "GenderEnum",
#     "ModAnnArborEnum",
#     "MostRecentTreatmentEnum",
#     "PriorTherapyTypeEnum",
#     "RaceEnum",
#     "RecentTreatmentResponseEnum",
# ]

# from sqlalchemy import (
#     CheckConstraint,
#     Column,
#     Enum,
#     ForeignKeyConstraint,
#     Integer,
#     Numeric,
#     String,
# )

# from .model_core import MetadataModel
# from .trial_metadata import Participant

# RaceEnum = Enum(
#     "White",
#     "American Indian or Alaska Native",
#     "Black or African American",
#     "Asian",
#     "Native Hawaiian or Other Pacific Islander",
#     "Other",
#     "Unknown",
#     "Not reported",
#     "Not allowed to collect",
#     name="race_enum",
# )
# GenderEnum = Enum(
#     "Female", "Male", "Unknown", "Unspecified", "Not reported", name="gender_enum",
# )
# EthnicityEnum = Enum(
#     "Hispanic or Latino",
#     "Not Hispanic or Latino",
#     "Unknown",
#     "Not reported",
#     "Not allowed to collect",
#     name="ethnicity_enum",
# )
# ClinicalYesNoEnum = Enum(
#     "Yes", "No", "Unknown", "Not applicable", name="clinical_yes_no_enum",
# )
# PriorTherapyTypeEnum = Enum(
#     "Anti-Retroviral Therapy",
#     "Antisense",
#     "Bone Marrow Transplant",
#     "Chemotherapy not otherwise specified (NOS)",
#     "Chemotherapy multiple agents systemic",
#     "Chemotherapy non-cytotoxic",
#     "Chemotherapy single agent systemic",
#     "Drug and/or immunotherapy",
#     "Gene Transfer",
#     "Hematopoietic stem cell",
#     "Hormonal Therapy",
#     "Image Directed local therapy",
#     "No prior therapy",
#     "Oncolytic virotherapy",
#     "Prior therapy not otherwise specified (NOS)",
#     "Radiation Therapy",
#     "Surgery",
#     "Therapy (NOS)",
#     "Vaccine",
#     name="prior_therapy_type_enum",
# )

# ModAnnArborEnum = Enum(
#     "I", "II", "III", "IV", "Unknown", "Not Applicable", name="mod_ann_arbor_enum",
# )
# EcogPsEnum = Enum(
#     "0",
#     "1",
#     "2",
#     "3",
#     "4",
#     "5",
#     "Data Missing",
#     "Unknown",
#     "Not Applicable",
#     "Not Reported",
#     name="ecog_ps_enum",
# )
# MostRecentTreatmentEnum = Enum(
#     "ABVD",
#     "BEACOPP",
#     "MOPP",
#     "ICE",
#     "Gemcitabine",
#     "Vinblastine",
#     "Bendamustine",
#     "Brentuximab Vedotin",
#     "Lenalidomide (Revlimid)",
#     "RAD001 (Everolimus)",
#     "Rituximab",
#     "Autologous Stem Cell Transplant",
#     "Allogeneic Stem Cell Transplant",
#     "Other - Experimental Targeted",
#     "Therapy",
#     "Other - Immunotherapy",
#     "Other - not specified",
#     name="most_recent_treatment_enum",
# )
# RecentTreatmentResponseEnum = Enum(
#     "Complete Remission",
#     "Partial Remission",
#     "Stable Disease",
#     "Progressive Disease",
#     "Unevaluable",
#     "Not Reported",
#     "Unknown",
#     name="recent_treatment_response_enum",
# )
# DiseaseStageEnum = Enum(
#     "0",
#     "0a",
#     "0is",
#     "I",
#     "IA",
#     "IA1",
#     "IA2",
#     "IB",
#     "IB1",
#     "IB2",
#     "IC",
#     "II",
#     "IIA",
#     "IIA1",
#     "IIA2",
#     "IIB",
#     "IIC",
#     "IIC1",
#     "III",
#     "IIIA",
#     "IIIB",
#     "IIIC",
#     "IIIC1",
#     "IIIC2",
#     "IS",
#     "IV",
#     "IVA",
#     "IVB",
#     "IVC",
#     "Tis",
#     "X",
#     "Unknown",
#     "Not Reported",
#     name="disease_stage_enum",
# )
# DiseaseGradeEnum = Enum(
#     "G1",
#     "G2",
#     "G3",
#     "G4",
#     "GX",
#     "GB",
#     "High Grade",
#     "Low Grade",
#     "Unknown",
#     "Not Reported",
#     "Not Applicable",
#     "Data Missing",
#     name="disease_grade_enum",
# )


# class ClinicalData(MetadataModel):
#     __tablename__ = "clinical_data"

#     trial_id = Column(String, primary_key=True)
#     cimac_participant_id = Column(String, primary_key=True)

#     __table_args__ = (
#         ForeignKeyConstraint(
#             [trial_id, cimac_participant_id],
#             [Participant.trial_id, Participant.cimac_participant_id],
#         ),
#     )

#     # demographics
#     race = Column(
#         RaceEnum,
#         doc="An arbitrary classification based on physical characteristics; a group of persons related by common descent or heredity (U.S. Center for Disease Control).",
#     )
#     gender = Column(GenderEnum, doc="Sex of the participant.",)
#     ethnicity = Column(EthnicityEnum, doc="Ethnicity of the participant.",)
#     age = Column(
#         Numeric,
#         CheckConstraint("age >= 0"),
#         doc="The age of the subject expressed in years",
#     )

#     # history
#     prior_surgery = Column(
#         ClinicalYesNoEnum,
#         doc="An indication whether or not there was any surgery history to report.",
#     )
#     prior_radiation_therapy = Column(
#         ClinicalYesNoEnum,
#         doc="An indication whether or not there was any radiation therapy history to report.",
#     )
#     prior_immunotherapy = Column(
#         ClinicalYesNoEnum,
#         doc="An indication whether or not there was any immunotherapy history to report.",
#     )
#     number_prior_systemic_treatments = Column(
#         Integer,
#         CheckConstraint("number_prior_systemic_treatments >= 0"),
#         doc="Total number of patient's prior systemic treatments, if any.",
#     )
#     prior_therapy_type = Column(
#         PriorTherapyTypeEnum,
#         doc="Text term that describes the kind of treatment administered.",
#     )

#     # disease & baseline
#     mod_ann_arbor_stage = Column(
#         ModAnnArborEnum,
#         doc="Text term that represents the clinical stage for lymphoma using the Ann Arbor Lymphoma Staging System.",
#     )
#     ecog_ps = Column(
#         EcogPsEnum,
#         doc="The ECOG functional performance status of the patient/participant.",
#     )
#     years_from_initial_diagnosis = Column(
#         Numeric,
#         CheckConstraint("years_from_initial_diagnosis >= 0"),
#         doc="Time at enrollment since initial diagnosis, in years.",
#     )
#     type_of_most_recent_treatment = Column(
#         MostRecentTreatmentEnum,
#         doc="Type of most recent treatment administered to the patient.",
#     )
#     response_to_most_recent_treatment = Column(
#         RecentTreatmentResponseEnum,
#         doc="Type of most recent treatment administered to the patient.",
#     )
#     duration_of_remission = Column(
#         Numeric,
#         CheckConstraint("duration_of_remission >= 0"),
#         doc="Duration of remission, in months.",
#     )
#     years_from_recent_treatment = Column(
#         Numeric,
#         CheckConstraint("years_from_recent_treatment >= 0"),
#         doc="Time at enrollment since most recent treatment, in years.",
#     )
#     disease_stage = Column(
#         DiseaseStageEnum,
#         doc="Neoplasm American Joint Committee on Cancer Clinical Group Stage. Stage group determined from clinical information on the tumor (T), regional node (N) and metastases (M) and by grouping cases with similar prognosis for cancer.",
#     )
#     disease_grade = Column(
#         DiseaseGradeEnum,
#         doc="Numeric value to express the degree of abnormality of cancer cells, a measure of differentiation and aggressiveness.",
#     )
