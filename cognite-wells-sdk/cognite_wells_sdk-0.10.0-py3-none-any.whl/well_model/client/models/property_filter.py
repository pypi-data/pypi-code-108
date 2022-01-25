from enum import Enum
from typing import List, Optional, Union

from cognite.well_model.models import PropertyFilter as PropertyFilterModel


class PropertyFilterNotSet(Enum):
    NotSet = 1


NotSet = PropertyFilterNotSet.NotSet

PropertyFilter = Union[None, PropertyFilterNotSet, List[str]]


def filter_to_model(filter: PropertyFilter) -> Optional[PropertyFilterModel]:
    if filter is None:
        return None
    elif filter == NotSet:
        return PropertyFilterModel(is_set=False)
    else:
        return PropertyFilterModel(is_set=True, one_of=filter)
