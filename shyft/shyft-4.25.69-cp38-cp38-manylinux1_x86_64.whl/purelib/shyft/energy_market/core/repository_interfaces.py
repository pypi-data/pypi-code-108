from typing import List
from . import Model, ModelInfo
from abc import ABCMeta, abstractmethod


class IModelRepository:
    """

    The Ltm Model Repository contains needed functions to retrieve, manipulate and store
    all aspects of a Ltm  EMPS Model.

    The current version only allow you to store and retrieve complete models.
    The api could/should be extended with methods that allow safe manipulation of the
    various aspects of the model.

    typical usage patterns:

     model = ltm_models.get_model(model_id)
     :
     # manipulating the model through the api like this.
     ltm_model.add_power_module( model.area, PowerModule('renewable.wind.smøla.3'..))
     :
     ltm_model.add_area(model,ModelArea(...))
     :
     # manipulating attributes (time-series, constants, strings etc.) of the existing objects
     ltm_model.set_inflow(model.area['sørland'].detailed_hydro['blåsjø'], scenario_ts_list)
     inflow_scenanrio_ts = ltm_model.get_inflow(model.area['sørland'.detailed_hydro['blåsjø'])
     last_updated = ltm_model.get_inflow_last_updated(model.area['sørland'.detailed_hydro['blåsjø'])

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
    def get_models(self, model_ids: List[int]) -> List[Model]:
        """

        Parameters
        ----------
        model_ids : list(int)
            list with model-ids to be retrieved
        Returns
        -------
            a list of type Model, containing the ltm-models for the model_ids requested

        """

    @abstractmethod
    def get_model(self, model_id: int) -> Model:
        """

        Parameters
        ----------
        model_id : int
            model id to retrieve

        Returns
        -------
            a model of type Model
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
    def save_model(self, model: Model) -> int:
        """

        Parameters
        ----------
        model : Model
            the model to be saved
            notice that if the model.id is set to a value > 0 , then it replaces any existing model with that id if it
            exists.

        Returns
        -------
            model_id:int, a unique handle that can be used with .get_model(id)/.get_models([id1,...]) and .delete_model(id)
        """
