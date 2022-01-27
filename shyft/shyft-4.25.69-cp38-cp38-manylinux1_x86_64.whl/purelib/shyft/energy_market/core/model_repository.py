from typing import List
from .repository_interfaces import IModelRepository
from . import ModelInfo
from . import Model
from pathlib import Path
import re
from shyft.time_series import byte_vector_from_file, byte_vector_to_file


class ModelRepository(IModelRepository):
    def __init__(self, model_root_directory: str):
        """

        Parameters
        ----------
        model_root_directory: string
            a path to the directory where the model-files resides
        """
        self.model_root_directory = model_root_directory
        self.file_pattern = r"model_*_*.blob"
        self.regex_pattern = r"^model_(\d+)_(.+)$"

    def get_path_to_model_service_directory(self) -> Path:
        """

        Parameters
        ----------
            None
        Returns
        -------
        p: pathlib.Path
            The path to the directory where the model service writes its data
        """
        p = Path(self.model_root_directory)
        return p

    def get_model_infos(self) -> List[ModelInfo]:
        """

        Returns
        -------
            list of type ModelInfo
        """
        r = list()
        p = self.get_path_to_model_service_directory()
        for file in list(p.glob(self.file_pattern)):
            file_name = file.name.replace('.blob', '')
            m = re.search(self.regex_pattern, file_name)
            if len(m.groups()) == 2:
                id = int(m.group(1))
                name = str(m.group(2))
                created_utc = int(Path(file).stat().st_ctime)
                r.append(ModelInfo(id, name, created_utc))
        return r

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
        r = list()
        for model_id in model_ids:
            r.append(self.get_model(model_id))
        return r

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
        p = self.get_path_to_model_service_directory()
        file_filter = self._make_model_file_name(model_id, '*')
        candidates = list(p.glob(file_filter))
        if len(candidates) == 0:
            raise Exception(
                "No model with id {1} found in directory '{0}'".format(str(p), model_id))
        if len(candidates) > 1:
            raise Exception(
                "Multiple emps models matching {1} found in directory '{0}'".format(str(p), file_filter))

        return Model.from_blob(byte_vector_from_file(str(candidates[0])))

    def delete_model(self, model_id: int, keep_ts_data: bool = False) -> None:
        """
        Parameters
        ----------
        model_id : int
            identifier of the model to delete
        Returns
        -------
            None
        """
        p = self.get_path_to_model_service_directory()
        for file in list(p.glob(self._make_model_file_name(model_id, '*'))):
            file.unlink()

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
        if not isinstance(model, Model):
            raise TypeError("model should be of type Model")
        if len(model.name) == 0:
            raise Exception("model.name should be something")
        if model.id < 0:
            raise Exception("model.id should be > 0")
        minfos = self.get_model_infos()
        id = 1
        for m_id in [m.id for m in minfos]:
            self.delete_model(m_id)
        model.id = id
        p = self.get_path_to_model_service_directory()
        full_path = p.joinpath(self._make_model_file_name(model.id, model.name))
        byte_vector_to_file(str(full_path), model.to_blob())
        return model.id

    def _make_model_file_name(self, id: int, model_name: str) -> str:
        return f"model_{id}_{model_name}.blob"
