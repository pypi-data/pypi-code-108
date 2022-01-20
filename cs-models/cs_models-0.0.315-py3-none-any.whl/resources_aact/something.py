from src.cs_models.aact_database import db_session
from src.cs_models.resources_aact.Study.models import StudyModel
from src.cs_models.resources_aact.Sponsor.models import SponsorModel
from src.cs_models.resources_aact.Intervention.models import InterventionModel
from src.cs_models.resources_aact.Condition.models import ConditionModel
from src.cs_models.resources_aact.StudyReference.models import (
    StudyReferenceModel,
)
from sqlalchemy.orm import aliased

study = aliased(StudyModel)
sponsor = aliased(SponsorModel)
intervention = aliased(InterventionModel)
study_ref = aliased(StudyReferenceModel)
condition = aliased(ConditionModel)
# q = db_session.query(
#     study).filter_by(nct_id='NCT03626311')

# q = db_session.query(
#         study.nct_id,
#         study.phase,
#         sponsor.name,
#         intervention.name,
#         study.official_title,
# ).join(sponsor, study.nct_id == sponsor.nct_id
# ).join(intervention, study.nct_id == intervention.nct_id
# ).filter(
#     intervention.name.op('~')('MRTX849')
# )

q = db_session.query(
    study.nct_id,
    study.phase,
    intervention.name,
    study_ref.pmid,
    sponsor.name,
    condition.name,
).join(
    sponsor,
    study.nct_id == sponsor.nct_id,
).outerjoin(
    intervention,
    study.nct_id == intervention.nct_id,
).outerjoin(
    study_ref,
    study.nct_id == study_ref.nct_id,
).outerjoin(
    condition,
    study.nct_id == condition.nct_id
).filter(
    intervention.name.op('~')('MRTX849')
    # study.nct_id == 'NCT04141787'
)

for rec in q.all():
    print(rec)
