"""
Workflow which exercises the common tasks in an end to end scenario
"""
from dkist_processing_common.tasks.l1_output_data import AddDatasetReceiptAccount
from dkist_processing_common.tasks.l1_output_data import PublishCatalogAndQualityMessages
from dkist_processing_common.tasks.l1_output_data import TransferL1Data
from dkist_processing_common.tasks.quality_metrics import QualityL0Metrics
from dkist_processing_common.tasks.quality_metrics import QualityL1Metrics
from dkist_processing_common.tasks.submit_quality import SubmitQuality
from dkist_processing_common.tasks.teardown import Teardown
from dkist_processing_common.tasks.transfer_input_data import TransferL0Data
from dkist_processing_core import Workflow

from dkist_processing_test.tasks.fake_science import GenerateCalibratedData
from dkist_processing_test.tasks.movie import AssembleTestMovie
from dkist_processing_test.tasks.movie import MakeTestMovieFrames
from dkist_processing_test.tasks.parse import ParseL0TestInputData
from dkist_processing_test.tasks.write_l1 import WriteL1Data

# TransferInputData Task
transfer_input_data = Workflow(
    process_category="test", process_name="transfer_input_data", workflow_package=__package__
)
transfer_input_data.add_node(task=TransferL0Data, upstreams=None)

# ParseInputData Task
parse_input_data = Workflow(
    process_category="test", process_name="parse_input_data", workflow_package=__package__
)
parse_input_data.add_node(task=ParseL0TestInputData, upstreams=None)

# L0Quality Task
quality_l0_metrics = Workflow(
    process_category="test", process_name="quality_l0_metrics", workflow_package=__package__
)
quality_l0_metrics.add_node(task=QualityL0Metrics, upstreams=None)

# L1Quality Task
quality_l1_metrics = Workflow(
    process_category="test", process_name="quality_l1_metrics", workflow_package=__package__
)
quality_l1_metrics.add_node(task=QualityL1Metrics, upstreams=None)

# SubmitQuality Task
quality_submit_metrics = Workflow(
    process_category="test", process_name="quality_submit_metrics", workflow_package=__package__
)
quality_submit_metrics.add_node(task=SubmitQuality, upstreams=None)

# GenerateL1CalibratedData Task
generate_calibrated_data = Workflow(
    process_category="test", process_name="generate_calibrated_data", workflow_package=__package__
)
generate_calibrated_data.add_node(task=GenerateCalibratedData, upstreams=None)

# MakeTestMovieFrames task
make_test_movie_frames = Workflow(
    process_category="test", process_name="make_test_movie_frames", workflow_package=__package__
)
make_test_movie_frames.add_node(task=MakeTestMovieFrames, upstreams=None)

# AssembleTestMovie Task
assemble_test_movie = Workflow(
    process_category="test", process_name="assemble_test_movie", workflow_package=__package__
)
assemble_test_movie.add_node(task=AssembleTestMovie, upstreams=None)

# WriteL1 Task
write_l1 = Workflow(process_category="test", process_name="write_l1", workflow_package=__package__)
write_l1.add_node(task=WriteL1Data, upstreams=None)

# TransferOutputData Task
transfer_output_data = Workflow(
    process_category="test", process_name="transfer_output_data", workflow_package=__package__
)
transfer_output_data.add_node(task=TransferL1Data, upstreams=None)

# AddDatasetReceiptAccount Task
add_dataset_receipt_account = Workflow(
    process_category="test",
    process_name="add_dataset_receipt_account",
    workflow_package=__package__,
)
add_dataset_receipt_account.add_node(task=AddDatasetReceiptAccount, upstreams=None)

# PublishCatalogAndQualityMessages Task
publish_catalog_messages = Workflow(
    process_category="test",
    process_name="publish_catalog_and_quality_messages",
    workflow_package=__package__,
)
publish_catalog_messages.add_node(task=PublishCatalogAndQualityMessages, upstreams=None)

# Teardown Task
teardown = Workflow(process_category="test", process_name="teardown", workflow_package=__package__)
teardown.add_node(task=Teardown, upstreams=None)
