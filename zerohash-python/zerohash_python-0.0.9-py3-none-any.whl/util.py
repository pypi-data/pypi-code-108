from zerohash.zerohash_object import ZerohashObject
from zerohash.zerohash_response import ZerohashResponse


def convert_to_zerohash_object(obj, credentials=None):
    """
    For a given object, obj, convert it into the appropriate zerohash object (if applicable)

    If a ZerohashResponse is passed, return the ZerohashObject associated with it

    Otherwise derive a ZerohashObject from the object passed
    """

    if isinstance(obj, ZerohashResponse):
        zerohash_response = obj
        obj = zerohash_response.data
    if isinstance(obj, list):
        return [convert_to_zerohash_object(r, credentials) for r in obj]
    # elif get_object_classes().get(klass_name) is not None:
    #     return get_object_classes().get(klass_name).construct_from(response, credentials)
    elif isinstance(obj, dict) and not isinstance(obj, ZerohashObject):

        return ZerohashObject.construct_from(obj, credentials)
    elif isinstance(obj, dict):
        return ZerohashObject.construct_from(obj, credentials)
    else:
        return obj
