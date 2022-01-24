# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module holding the HTS runtime related json encoder-decoder classes."""
from typing import Any, Dict
import copy

from azureml.train.automl._hts.hts_json_serializer import HTSEncoder, HTSDecoder
from azureml.train.automl.runtime._hts.content_hash_vocabulary import ContentHashVocabulary
from azureml.train.automl.runtime._hts.node_columns_info import NodeColumnsInfo


class HTSRuntimeEncoder(HTSEncoder):
    def default(self, o: Any) -> Any:
        json_dict = copy.deepcopy(o.__dict__)
        if isinstance(o, ContentHashVocabulary):
            json_dict["__type__"] = ContentHashVocabulary.__name__
            return json_dict
        elif isinstance(o, NodeColumnsInfo):
            json_dict["__type__"] = NodeColumnsInfo.__name__
            return json_dict
        else:
            return super(HTSRuntimeEncoder, self).default(o)


class HTSRuntimeDecoder(HTSDecoder):
    def __init__(self, *args, **kwargs):
        super(HTSRuntimeDecoder, self).__init__(object_hook=self.hts_runtime_object_hook, *args, **kwargs)

    def hts_runtime_object_hook(self, dct: Dict[str, Any]) -> Any:
        if dct.get("__type__") == ContentHashVocabulary.__name__:
            return ContentHashVocabulary(
                *[dct.get(arg) for arg in ContentHashVocabulary.get_args_list()])  # type: ignore
        elif dct.get("__type__") == NodeColumnsInfo.__name__:
            return NodeColumnsInfo(
                *[dct.get(arg) for arg in NodeColumnsInfo.get_args_list()])  # type: ignore
        return super(HTSRuntimeDecoder, self).hts_object_hook(dct)
