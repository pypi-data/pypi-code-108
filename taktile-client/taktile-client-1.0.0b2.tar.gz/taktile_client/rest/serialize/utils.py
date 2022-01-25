"""
Rest serialization utils
"""
import typing as t

JSONObject = t.Dict[t.AnyStr, t.Any]
JSONArray = t.List[t.Any]
JSONStructure = t.Union[JSONArray, JSONObject]  # type: ignore
