from concurrent.futures import Future, as_completed
from typing import Dict


def create_exception_map(
        future_map: Dict[Future, str]) -> Dict[str, Exception]:
    id_exception_map = {}
    for future in as_completed(future_map):
        id = future_map[future]
        try:
            future.result()
        except Exception as exc:
            id_exception_map[id] = exc
    return id_exception_map
