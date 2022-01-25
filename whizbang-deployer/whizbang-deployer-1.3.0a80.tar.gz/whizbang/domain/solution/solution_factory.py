from abc import ABC, abstractmethod
from typing import Optional, Type

from dependency_injector.providers import ConfigurationOption

from whizbang.config.environment_config import EnvironmentConfig
from whizbang.domain.handler.handler_facade import IHandlerFacade
from whizbang.domain.shared_types.named_solutions import NamedSolutions
from whizbang.domain.solution.deployment_solution_base import DeploymentSolutionBase


class ISolutionFactory(ABC):
    """"""

    @abstractmethod
    def get_solution(self, solution_name: str) -> Optional[DeploymentSolutionBase]:
        """"""


class SolutionFactory(ISolutionFactory):
    def __init__(self, environment_config: EnvironmentConfig, handler: IHandlerFacade):
        self.__handler = handler
        self.__environment_config = environment_config

    # def get_solution(self, solution_name: str) -> Optional[DeploymentSolutionBase]:
    #     if solution_name == NamedSolutions.cortex_accelerator:
    #         return CortexAcceleratorSolution(self.__environment_config self.__handler)
    #     return None

    def get_solution(self, solution_type: Type[DeploymentSolutionBase]) -> Optional[DeploymentSolutionBase]:
        return solution_type(self.__environment_config, self.__handler)
