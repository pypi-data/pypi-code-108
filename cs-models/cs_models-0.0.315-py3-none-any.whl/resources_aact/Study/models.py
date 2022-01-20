from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Text,
    DateTime,
    Boolean,
    PrimaryKeyConstraint,
)

from ...aact_database import Base


class StudyModel(Base):

    __tablename__ = 'studies'
    __table_args__ = (
        PrimaryKeyConstraint('nct_id'),
        {'schema': 'ctgov'},
    )

    nct_id = Column(String, primary_key=True)
    nlm_download_date_description = Column(String)
    study_first_submitted_date = Column(Date)
    last_update_submitted_date = Column(Date)
    results_first_submitted_date = Column(Date)
    disposition_first_submitted_date = Column(Date)
    start_month_year = Column(String)
    start_date = Column(Date)
    start_date_type = Column(String)
    verification_month_year = Column(String)
    verification_date = Column(Date)
    completion_month_year = Column(String)
    completion_date = Column(Date)
    completion_date_type = Column(String)
    primary_completion_month_year = Column(String)
    primary_completion_date = Column(Date)
    primary_completion_date_type = Column(String)
    study_first_submitted_qc_date = Column(Date)
    study_first_posted_date = Column(Date)
    study_first_posted_date_type = Column(String)
    results_first_submitted_qc_date = Column(Date)
    results_first_posted_date = Column(Date)
    results_first_posted_date_type = Column(String)
    disposition_first_submitted_qc_date = Column(Date)
    disposition_first_posted_date = Column(Date)
    disposition_first_posted_date_type = Column(String)
    last_update_submitted_qc_date = Column(Date)
    last_update_posted_date = Column(Date)
    last_update_posted_date_type = Column(String)
    target_duration = Column(String)
    study_type = Column(String)
    acronym = Column(String)
    baseline_population = Column(Text)
    brief_title = Column(Text)
    official_title = Column(Text)
    overall_status = Column(String)
    last_known_status = Column(String)
    phase = Column(String)
    enrollment = Column(Integer)
    enrollment_type = Column(String)
    source = Column(String)
    limitations_and_caveats = Column(String)
    number_of_arms = Column(Integer)
    number_of_groups = Column(Integer)
    why_stopped = Column(String)
    has_expanded_access = Column(Boolean)
    expanded_access_type_individual = Column(Boolean)
    expanded_access_type_intermediate = Column(Boolean)
    expanded_access_type_treatment = Column(Boolean)
    has_dmc = Column(Boolean)
    is_fda_regulated_drug = Column(Boolean)
    is_fda_regulated_device = Column(Boolean)
    is_unapproved_device = Column(Boolean)
    is_ppsd = Column(Boolean)
    is_us_export = Column(Boolean)
    biospec_retention = Column(String)
    biospec_description = Column(Text)
    plan_to_share_ipd = Column(String)
    plan_to_share_ipd_description = Column(String)
    ipd_time_frame = Column(String)
    ipd_access_criteria = Column(String)
    ipd_url = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self):
        return "<Study(nct_id='{}', official_title='{}', phase={}, " \
               "start_date={})>".format(self.nct_id,
                                        self.official_title,
                                        self.phase,
                                        self.start_date,
                                        )
