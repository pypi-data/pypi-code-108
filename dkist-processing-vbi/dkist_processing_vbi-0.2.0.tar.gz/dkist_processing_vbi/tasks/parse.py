from typing import List

from dkist_processing_common.models.tags import StemName
from dkist_processing_common.parsers.dsps_repeat import DspsRepeatNumberFlower
from dkist_processing_common.parsers.dsps_repeat import TotalDspsRepeatsBud
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.time import ExposureTimeFlower
from dkist_processing_common.parsers.time import TaskExposureTimesBud
from dkist_processing_common.parsers.unique_bud import UniqueBud
from dkist_processing_common.tasks import ParseL0InputData
from dkist_processing_common.tasks.parse_l0_input_data import S

from dkist_processing_vbi.models.constants import VbiBudName
from dkist_processing_vbi.models.tags import VbiStemName
from dkist_processing_vbi.parsers.num_exp_per_dsp import NumExpPerDspBud
from dkist_processing_vbi.parsers.spectral_line import SpectralLineBud
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess


class ParseL0VbiInputData(ParseL0InputData):
    @property
    def fits_parsing_class(self):
        return VbiL0FitsAccess

    @property
    def constant_flowers(self) -> List[S]:
        return super().constant_flowers + [
            UniqueBud(
                constant_name=VbiBudName.num_spatial_steps.value,
                metadata_key="number_of_spatial_steps",
            ),
            TotalDspsRepeatsBud(),
            SpectralLineBud(),
            NumExpPerDspBud(),
            TaskExposureTimesBud(VbiBudName.gain_exposure_times.value, ip_task_type="GAIN"),
            TaskExposureTimesBud(VbiBudName.observe_exposure_times.value, ip_task_type="OBSERVE"),
        ]

    @property
    def tag_flowers(self) -> List[S]:
        return super().tag_flowers + [
            SingleValueSingleKeyFlower(
                tag_stem_name=VbiStemName.current_spatial_step.value,
                metadata_key="current_spatial_step",
            ),
            SingleValueSingleKeyFlower(
                tag_stem_name=StemName.task.value, metadata_key="ip_task_type"
            ),
            DspsRepeatNumberFlower(),
            ExposureTimeFlower(),
        ]
