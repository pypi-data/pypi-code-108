from pymongo.collection import Collection

from fastel import collections


def get_collection(name: str) -> Collection:
    return collections.get_collection(name)
