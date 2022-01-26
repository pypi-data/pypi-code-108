from edc_constants.constants import (
    DIABETES,
    HIV,
    HYPERTENSION,
    NO,
    NOT_APPLICABLE,
    OTHER,
    PURPOSIVELY_SELECTED,
    RANDOM_SAMPLING,
    UNKNOWN,
)

from .constants import (
    DIABETES_CLINIC,
    HIV_CLINIC,
    HYPERTENSION_CLINIC,
    INTEGRATED,
    NCD,
    NCD_CLINIC,
    NO_INTERRUPTION,
    SEQUENTIAL,
    SOME_INTERRUPTION,
    SYSTEMATIC,
)

CLINIC_CHOICES = (
    (HIV_CLINIC, "HIV Clinic"),
    (NCD_CLINIC, "NCD Clinic (Joint Diabetes/Hypertension)"),
    (DIABETES_CLINIC, "Diabetes Clinic"),
    (HYPERTENSION_CLINIC, "Hypertension Clinic"),
    (INTEGRATED, "Integrated Clinic"),
)

REFUSAL_REASONS = (
    ("unwilling_to_say", "Unwilling to give any reason"),
    ("worried_about_care", "Worried that he/she will not get the care needed"),
    (
        "mixing_and_stigme",
        "Does not want to mix with patients with other conditions "
        "because of concern around stigma",
    ),
    (
        "mixing_and_infection",
        "Does not want to mix with patients with other conditions because "
        "of concerns around contracting infections",
    ),
    (
        "happy_vertical_care",
        "Patient is happy with the care being given in vertical clinics",
    ),
    (
        "no_participant",
        "No longer wishes to be a study participant but is happy to continue "
        "receiving care in the integrated clinic",
    ),
    (
        "receives_community_care",
        "Patient is receiving HIV care in the community and does not wish "
        "to return to facility-based care",
    ),
    (
        "unable_to_contact",
        "Clinic was unable to contact the subject",
    ),
    (OTHER, "Other, please specify"),
)
REFUSAL_REASONS_SCREENING = REFUSAL_REASONS
CLINIC_DAYS = (
    (INTEGRATED, "Integrated care day (HIV, Diabetes, Hypertension)"),
    (NCD, "NCD day (Diabetes + Hypertension)"),
    (HIV, "HIV only day"),
    (DIABETES, "Diabetes only day"),
    (HYPERTENSION, "Hypertension only day"),
)

SELECTION_METHOD = (
    (RANDOM_SAMPLING, "Random sampling"),
    (SYSTEMATIC, "Systematically selected"),
    (SEQUENTIAL, "Sequentially selected"),
    (PURPOSIVELY_SELECTED, "Purposively selected"),
)

RESPONDENT_CHOICES = (
    ("patient", "Patient"),
    ("family", "Family"),
    ("friend", "friend"),
    ("other", "other"),
    (NOT_APPLICABLE, "Not applicable"),
)

CARE_SINCE_MOCCA = (
    (NO_INTERRUPTION, "Yes, without interruption"),
    (SOME_INTERRUPTION, "Yes, with some interruption"),
    (NO, "No, not since completing follow up with the MOCCA (original) trial."),
    (UNKNOWN, "Unknown"),
)

NOT_ICC_REASONS = (
    ("icc_not_available", "ICC not available (or closed) in this facility"),
    ("moved", "Moved out of area"),
    ("dont_want", "Personally chose not to continue with integrated care"),
    (
        "advised_to_vertical",
        "Healthcare staff asked patient to return to vertical care",
    ),
    ("referred_out", "Referred to another facility without an ICC"),
    (
        "receives_community_care",
        "Patient is currently receiving their HIV care in the community",
    ),
    (NOT_APPLICABLE, "Not applicable"),
)
