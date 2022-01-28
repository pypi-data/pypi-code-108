r"""
Base class for visualizing a certain stage of the results of the application of the sps-algorithm
"""
from abc import ABC, abstractmethod
from typing import List, Union, Tuple


class IVisStage(ABC):
    r"""
    Abstract base class for visualizing a certain stage
    """

    def __init__(self, strategy: int, camera_spin_files: Union[List[Tuple[float, float, float]], None] = None) -> None:
        r"""
        Initialize the visualization stage
        Args:
            strategy(int): for each stage a certain strategy was applied. The visualization also depends on these strategies.
        """
        self.strategy = strategy
        self.spincam = camera_spin_files

    @property
    @abstractmethod
    def stage(self) -> str:
        r"""
        Returns:
            the name of the stage
        """

    @abstractmethod
    def _stagestrategytext(self) -> str:
        r"""
        Returns:
            the strategy of the stage
        """

    def __repr__(self) -> None:
        r"""
        Represents the strategy for the stage in words.
        """
        print(f'Visualizer Stage: {self.stage}.')
        print(f'Strategy: {self._stagestrategytext()}')

    @abstractmethod
    def __call__(self) -> None:
        r"""
        Calls the certain visualization.
        """
