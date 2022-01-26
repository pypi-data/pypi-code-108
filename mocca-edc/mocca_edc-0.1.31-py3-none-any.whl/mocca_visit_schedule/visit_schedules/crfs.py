from edc_visit_schedule import Crf, FormsCollection

crfs_prn = FormsCollection(
    Crf(show_order=212, model="mocca_subject.bloodresultslipid"),
    Crf(show_order=214, model="mocca_subject.cd4result"),
    Crf(show_order=215, model="mocca_subject.glucosefollowup"),
    Crf(show_order=216, model="mocca_subject.viralloadresult"),
    name="prn",
)

all_crfs = [
    Crf(show_order=110, model="mocca_subject.clinicalreview"),
    Crf(show_order=111, model="mocca_subject.indicators"),
    Crf(show_order=112, model="mocca_subject.hivinitialreview", required=False),
    Crf(show_order=114, model="mocca_subject.dminitialreview", required=False),
    Crf(show_order=116, model="mocca_subject.htninitialreview", required=False),
    Crf(show_order=118, model="mocca_subject.cholinitialreview", required=False),
    Crf(show_order=120, model="mocca_subject.hivreview", required=False),
    Crf(show_order=130, model="mocca_subject.dmreview", required=False),
    Crf(show_order=140, model="mocca_subject.htnreview", required=False),
    Crf(show_order=142, model="mocca_subject.cholreview", required=False),
    Crf(show_order=145, model="mocca_subject.medications"),
    Crf(show_order=150, model="mocca_subject.drugrefillhtn", required=False),
    Crf(show_order=160, model="mocca_subject.drugrefilldm", required=False),
    Crf(show_order=170, model="mocca_subject.drugrefillhiv", required=False),
    Crf(show_order=175, model="mocca_subject.drugrefillchol", required=False),
    Crf(show_order=185, model="mocca_subject.hivmedicationadherence", required=False),
    Crf(show_order=190, model="mocca_subject.dmmedicationadherence", required=False),
    Crf(show_order=195, model="mocca_subject.htnmedicationadherence", required=False),
    Crf(show_order=197, model="mocca_subject.cholmedicationadherence", required=False),
    Crf(show_order=200, model="mocca_subject.complicationsfollowup", required=False),
    Crf(show_order=230, model="mocca_subject.nextappointment"),
]
crfs = FormsCollection(*all_crfs, name="all")

crfs_unscheduled = FormsCollection(
    *all_crfs,
    name="unscheduled",
)

crfs_missed = FormsCollection(
    Crf(show_order=10, model="mocca_subject.subjectvisitmissed"),
    name="missed",
)


crfs_d1 = FormsCollection(
    Crf(show_order=100, model="mocca_subject.clinicalreviewbaseline"),
    Crf(show_order=110, model="mocca_subject.indicators"),
    Crf(show_order=120, model="mocca_subject.hivinitialreview", required=False),
    Crf(show_order=130, model="mocca_subject.dminitialreview", required=False),
    Crf(show_order=140, model="mocca_subject.htninitialreview", required=False),
    Crf(show_order=142, model="mocca_subject.cholinitialreview", required=False),
    Crf(show_order=143, model="mocca_subject.medications"),
    Crf(show_order=145, model="mocca_subject.drugrefillhtn", required=False),
    Crf(show_order=150, model="mocca_subject.drugrefilldm", required=False),
    Crf(show_order=155, model="mocca_subject.drugrefillhiv", required=False),
    Crf(show_order=157, model="mocca_subject.drugrefillchol", required=False),
    Crf(show_order=160, model="mocca_subject.hivmedicationadherence", required=False),
    Crf(show_order=162, model="mocca_subject.dmmedicationadherence", required=False),
    Crf(show_order=164, model="mocca_subject.htnmedicationadherence", required=False),
    Crf(show_order=166, model="mocca_subject.cholmedicationadherence", required=False),
    Crf(show_order=168, model="mocca_subject.otherbaselinedata"),
    Crf(show_order=170, model="mocca_subject.complicationsbaseline"),
    Crf(show_order=171, model="mocca_subject.glucosebaseline"),
    Crf(show_order=212, model="mocca_subject.bloodresultslipid"),
    Crf(show_order=400, model="mocca_subject.nextappointment"),
    name="day1",
)
