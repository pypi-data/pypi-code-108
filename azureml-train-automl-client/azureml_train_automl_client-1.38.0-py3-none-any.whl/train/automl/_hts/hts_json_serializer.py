# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module holding the HTS related json encoder-decoder classes."""
from typing import Any, Dict, Optional
import copy
from json import JSONEncoder, JSONDecoder

from azureml.train.automl._hts.status_record import StatusRecord


class HTSEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        json_dict = copy.deepcopy(o.__dict__)
        if isinstance(o, StatusRecord):
            json_dict["__type__"] = StatusRecord.__name__
        return json_dict


class HTSDecoder(JSONDecoder):
    def __init__(self, object_hook=None, *args, **kwargs):
        if object_hook is None:
            super(HTSDecoder, self).__init__(object_hook=self.hts_object_hook, *args, **kwargs)
        else:
            super(HTSDecoder, self).__init__(object_hook=object_hook, *args, **kwargs)

    def hts_object_hook(self, dct: Dict[str, Any]) -> Any:
        if dct.get("__type__") == StatusRecord.__name__:
            return StatusRecord(*[dct.get(arg) for arg in StatusRecord.get_args_list()])  # type: ignore
        return dct
