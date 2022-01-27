from cognite.well_model.client.utils.exceptions import CogniteInvalidInput
from cognite.well_model.models import DistanceUnitEnum


def create_distance_unit(unit: str) -> DistanceUnitEnum:
    try:
        return DistanceUnitEnum[unit]
    except KeyError:
        pass
    raise CogniteInvalidInput(f"Invalid distance unit '{unit}'")
