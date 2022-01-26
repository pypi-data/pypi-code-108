from edc_lab import RequisitionPanel
from edc_lab_panel.processing_profiles import lipids_processing

lipids_panel = RequisitionPanel(
    name="chemistry",
    verbose_name="Chemistry: Lipids",
    abbreviation="LIPIDS",
    processing_profile=lipids_processing,
    utest_ids=["ldl", "hdl", "trig", "chol"],
    reference_range_collection_name="mocca",
)
