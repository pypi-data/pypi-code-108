from dkist_processing_common.tasks import AddDatasetReceiptAccount
from dkist_processing_common.tasks import PublishCatalogAndQualityMessages
from dkist_processing_common.tasks import Teardown
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferL1Data
from dkist_processing_common.tasks.quality_metrics import QualityL0Metrics
from dkist_processing_common.tasks.quality_metrics import QualityL1Metrics
from dkist_processing_common.tasks.submit_quality import SubmitQuality
from dkist_processing_core import Workflow

from dkist_processing_vbi.tasks.assemble_movie import AssembleVbiMovie
from dkist_processing_vbi.tasks.dark import DarkCalibration
from dkist_processing_vbi.tasks.gain import GainCalibration
from dkist_processing_vbi.tasks.make_movie_frames import MakeVbiMovieFrames
from dkist_processing_vbi.tasks.parse import ParseL0VbiInputData
from dkist_processing_vbi.tasks.science import ScienceCalibration
from dkist_processing_vbi.tasks.write_l1 import VbiWriteL1Frame

l0_pipeline = Workflow(
    process_category="vbi",
    process_name="l0_pipeline",
    workflow_package=__package__,
)

l0_pipeline.add_node(task=TransferL0Data, upstreams=None)
l0_pipeline.add_node(task=ParseL0VbiInputData, upstreams=TransferL0Data)
l0_pipeline.add_node(task=QualityL0Metrics, upstreams=ParseL0VbiInputData)
l0_pipeline.add_node(task=DarkCalibration, upstreams=ParseL0VbiInputData)
l0_pipeline.add_node(task=GainCalibration, upstreams=DarkCalibration)
l0_pipeline.add_node(task=ScienceCalibration, upstreams=GainCalibration)
l0_pipeline.add_node(task=VbiWriteL1Frame, upstreams=ScienceCalibration)
l0_pipeline.add_node(task=MakeVbiMovieFrames, upstreams=VbiWriteL1Frame)
l0_pipeline.add_node(task=AssembleVbiMovie, upstreams=MakeVbiMovieFrames)
l0_pipeline.add_node(task=AddDatasetReceiptAccount, upstreams=AssembleVbiMovie)
l0_pipeline.add_node(task=TransferL1Data, upstreams=AssembleVbiMovie)
l0_pipeline.add_node(task=QualityL1Metrics, upstreams=VbiWriteL1Frame)
l0_pipeline.add_node(task=SubmitQuality, upstreams=[QualityL0Metrics, QualityL1Metrics])
l0_pipeline.add_node(
    task=PublishCatalogAndQualityMessages,
    upstreams=[TransferL1Data, AddDatasetReceiptAccount, SubmitQuality],
)
l0_pipeline.add_node(task=Teardown, upstreams=PublishCatalogAndQualityMessages)
