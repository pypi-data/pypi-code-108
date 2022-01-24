from abc import abstractmethod
from typing import Tuple, List, Sequence, Union, Dict


class NehushtanHTTPRoute:
    """
    Since 0.4.0
    """

    def __init__(self):
        self.matched_arguments = []
        self.matched_keyed_arguments = {}

    @abstractmethod
    def match_request(self, method: str, path: str) -> bool:
        pass

    @abstractmethod
    def get_filter_list(self) -> Sequence[Union[type, str]]:
        pass

    @abstractmethod
    def get_controller_target(self) -> Tuple[Union[type, str], str]:
        pass

    def get_matched_arguments(self) -> List[str]:
        return self.matched_arguments

    def get_matched_keyed_arguments(self) -> Dict[str, str]:
        return self.matched_keyed_arguments
