from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from edc_constants.constants import MOBILE_NUMBER, NO, NOT_APPLICABLE, YES
from edc_lab.constants import LT
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED
from faker import Faker
from model_bakery.recipe import Recipe, seq

from mocca_consent.models import SubjectConsent, SubjectReconsent
from mocca_subject.constants import THIS_CLINIC
from mocca_subject.models import (  # TODO: Confirm removal of HealthEconomicsRevised recipe
    ClinicalReview,
    ClinicalReviewBaseline,
    HivInitialReview,
    HtnInitialReview,
)

from .models import SubjectRequisition, SubjectVisit

fake = Faker()


subjectvisit = Recipe(SubjectVisit, reason=SCHEDULED)

subjectrequisition = Recipe(SubjectRequisition)

subjectconsent = Recipe(
    SubjectConsent,
    assessment_score=YES,
    confirm_identity=seq("12315678"),
    consent_copy=YES,
    consent_datetime=get_utcnow(),
    consent_reviewed=YES,
    consent_signature=YES,
    dob=get_utcnow() - relativedelta(years=25),
    first_name=fake.first_name,
    gender="M",
    identity=seq("12315678"),
    identity_type=MOBILE_NUMBER,
    initials="XX",
    is_dob_estimated="-",
    is_incarcerated=NO,
    is_literate=YES,
    last_name=fake.last_name,
    screening_identifier=None,
    study_questions=YES,
    site=Site.objects.get_current(),
    subject_identifier=None,
)

subjectreconsent = Recipe(
    SubjectReconsent,
    site=Site.objects.get_current(),
    consent_reviewed=YES,
    assessment_score=YES,
    study_questions=YES,
    consent_copy=YES,
    action_identifier=None,
    tracking_identifier=None,
)

clinicalreviewbaseline = Recipe(
    ClinicalReviewBaseline,
    site=Site.objects.get_current(),
    hiv_test=YES,
    hiv_test_ago="5y",
    hiv_dx=YES,
    htn_test=NO,
    htn_test_ago=None,
    hypertension=NOT_APPLICABLE,
    dm_test=NO,
    dm_test_ago=None,
    diabetes=NOT_APPLICABLE,
    health_insurance=YES,
    patient_club=YES,
)

clinicalreview = Recipe(
    ClinicalReview,
    site=Site.objects.get_current(),
    hiv_test=NOT_APPLICABLE,
    hiv_test_date=None,
    hiv_dx=NOT_APPLICABLE,
    htn_test=NO,
    htn_test_date=None,
    htn_dx=NOT_APPLICABLE,
    dm_test=NO,
    dm_test_date=None,
    dm_dx=NOT_APPLICABLE,
    health_insurance=YES,
    patient_club=YES,
)

hivinitialreview = Recipe(
    HivInitialReview,
    site=Site.objects.get_current(),
    dx_ago="5y",
    receives_care=YES,
    clinic=THIS_CLINIC,
    arv_initiation_ago="4y",
    has_vl=YES,
    vl=50,
    vl_quantifier=LT,
    has_cd4=NO,
)

htninitialreview = Recipe(
    HtnInitialReview,
    site=Site.objects.get_current(),
    dx_ago="1y",
    receives_care=YES,
    clinic=THIS_CLINIC,
)
