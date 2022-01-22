from allocation_language.alloc_lang_data_containers.event_dataclasses import EventData
from copy import copy
from typing import Iterable

def dict_iter_to_event_iter(items: Iterable[dict]):
    for item in items:
        yield EventData(data=copy(item))

def csv_to_event_list(csv_file_path):
    #TODO IMPLEMENT ME!
    return NotImplemented