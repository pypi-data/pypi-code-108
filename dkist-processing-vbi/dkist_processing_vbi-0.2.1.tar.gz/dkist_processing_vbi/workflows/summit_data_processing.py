"""
Workflow which exercises the common tasks in an end to end scenario
"""
from dkist_processing_common.tasks import AddDatasetReceiptAccount
from dkist_processing_common.tasks import PublishCatalogAndQualityMessages
from dkist_processing_common.tasks import Teardown
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferL1Data
from dkist_processing_common.tasks.quality_metrics import QualityL1Metrics
from dkist_processing_common.tasks.submit_quality import SubmitQuality
from dkist_processing_core import Workflow

from dkist_processing_vbi.tasks.assemble_movie import AssembleVbiMovie
from dkist_processing_vbi.tasks.make_movie_frames import MakeVbiMovieFrames
from dkist_processing_vbi.tasks.parse import ParseL0VbiInputData
from dkist_processing_vbi.tasks.process_summit_processed import GenerateL1SummitData
from dkist_processing_vbi.tasks.write_l1 import VbiWriteL1Frame

summit_processed_data = Workflow(
    process_category="vbi",
    process_name="summit_processed_data",
    workflow_package=__package__,
)
summit_processed_data.add_node(task=TransferL0Data, upstreams=None)
summit_processed_data.add_node(task=ParseL0VbiInputData, upstreams=TransferL0Data)
summit_processed_data.add_node(task=GenerateL1SummitData, upstreams=ParseL0VbiInputData)
summit_processed_data.add_node(task=VbiWriteL1Frame, upstreams=GenerateL1SummitData)
summit_processed_data.add_node(task=MakeVbiMovieFrames, upstreams=VbiWriteL1Frame)
summit_processed_data.add_node(task=AssembleVbiMovie, upstreams=MakeVbiMovieFrames)
summit_processed_data.add_node(task=AddDatasetReceiptAccount, upstreams=AssembleVbiMovie)
summit_processed_data.add_node(task=TransferL1Data, upstreams=AssembleVbiMovie)
summit_processed_data.add_node(task=QualityL1Metrics, upstreams=VbiWriteL1Frame)
summit_processed_data.add_node(task=SubmitQuality, upstreams=QualityL1Metrics)
summit_processed_data.add_node(
    task=PublishCatalogAndQualityMessages,
    upstreams=[TransferL1Data, AddDatasetReceiptAccount, SubmitQuality],
)
summit_processed_data.add_node(task=Teardown, upstreams=PublishCatalogAndQualityMessages)
