from typing import List
from . import StmSystem, HydroPowerSystem
from ..core import ModelInfo
from abc import ABCMeta, abstractmethod


class IModelRepository:
    """

    The StmSystem Repository contains needed functions to retrieve, manipulate and store
    all aspects of a a StmSystem

    The current version only allow you to store and retrieve complete models.
    The api could/should be extended with methods that allow safe manipulation of the
    various aspects of the model.

    typical usage patterns:

     model = stm_models.get_model(model_id)
     :
     # manipulating the model through the api like this.
     stm_model.create_reservoir( ...)
     :
     stm_model.create_power_station(..)
     :

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_model_infos(self) -> List[ModelInfo]:
        """

        Returns
        -------
            list of type ModelInfo
        """

    @abstractmethod
    def get_models(self, model_ids: List[int]) -> List[StmSystem]:
        """

        Parameters
        ----------
        model_ids : list(int)
            list with model-ids to be retrieved
        Returns
        -------
            a list of type StmSystem, containing the ltm-models for the model_ids requested

        """

    @abstractmethod
    def get_model(self, model_id: int) -> StmSystem:
        """

        Parameters
        ----------
        model_id : int
            model id to retrieve

        Returns
        -------
            a model of type StmSystem
        """

    @abstractmethod
    def delete_model(self, model_id: int) -> None:
        """
        Parameters
        ----------
        model_id : int
            identifier of the model to delete
        Returns
        -------
            None
        """

    @abstractmethod
    def save_model(self, model: StmSystem) -> int:
        """

        Parameters
        ----------
        model : StmSystem
            the model to be saved
            notice that if the model.id is set to a value > 0 , then it replaces any existing model with that id if it
            exists.

        Returns
        -------
            model_id:int, a unique handle that can be used with .get_model(id)/.get_models([id1,...]) and .delete_model(id)
        """


class IHydroPowerSystemRepository:
    """

    The HydroPowerSystem Repository contains needed functions to retrieve, manipulate and store
    all aspects of a a HydroPowerSystem

    The current version only allow you to store and retrieve complete models.
    The api could/should be extended with methods that allow safe manipulation of the
    various aspects of the model.

    typical usage patterns:

     m = hydro_power_models.get_model(model_id)
     :
     # manipulating the model through the api like this.
     m.create_reservoir( ...)
     :
     m.create_power_station(..)
     :

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_model_infos(self) -> List[ModelInfo]:
        """

        Returns
        -------
            list of type ModelInfo
        """

    @abstractmethod
    def get_models(self, model_ids: List[int]) -> List[HydroPowerSystem]:
        """

        Parameters
        ----------
        model_ids : list(int)
            list with model-ids to be retrieved
        Returns
        -------
            a list of type HydroPowerSystem, containing the models for the model_ids requested

        """

    @abstractmethod
    def get_model(self, model_id: int) -> HydroPowerSystem:
        """

        Parameters
        ----------
        model_id : int
            model id to retrieve

        Returns
        -------
            a model of type StmSystem
        """

    @abstractmethod
    def delete_model(self, model_id: int) -> None:
        """
        Parameters
        ----------
        model_id : int
            identifier of the model to delete
        Returns
        -------
            None
        """

    @abstractmethod
    def save_model(self, model: HydroPowerSystem) -> int:
        """

        Parameters
        ----------
        model : HydroPowerSystem
            the model to be saved
            notice that if the model.id is set to a value > 0 , then it replaces any existing model with that id if it
            exists.

        Returns
        -------
            model_id:int, a unique handle that can be used with .get_model(id)/.get_models([id1,...]) and .delete_model(id)
        """
