from dkist_processing_common.models.tags import StemName
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)

from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess


def parse_header_ip_task(fits_obj: VispL0FitsAccess) -> str:
    """ Function that contains logic to parse ViSP tasks and subtasks """
    if (
        fits_obj.ip_task_type == "gain"
        and fits_obj.gos_level3_status == "lamp"
        and fits_obj.gos_level3_lamp_status == "on"
    ):
        return "LAMP_GAIN"
    if (
        fits_obj.ip_task_type == "gain"
        and fits_obj.gos_level3_status == "clear"
        and fits_obj.scanning_mode in ["Raster", "Random", "Spiral"]
    ):
        return "SOLAR_GAIN"
    return fits_obj.ip_task_type


class VispTaskTypeFlower(SingleValueSingleKeyFlower):
    def __init__(self):
        super().__init__(tag_stem_name=StemName.task.value, metadata_key="ip_task_type")

    def setter(self, fits_obj: VispL0FitsAccess):
        return parse_header_ip_task(fits_obj)
