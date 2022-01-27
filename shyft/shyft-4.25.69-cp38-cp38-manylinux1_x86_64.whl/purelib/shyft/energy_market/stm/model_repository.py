from typing import List, Union
from .repository_interfaces import IModelRepository, IHydroPowerSystemRepository
from ..core import ModelInfo
from . import StmSystem, HydroPowerSystem
from pathlib import Path
import re
from shyft.time_series import byte_vector_from_file, byte_vector_to_file
import locale


def _is_a_valid_root_directory(model_root_directory: Path) -> None:
    """ common verification of type, existence and is a directory """
    if not isinstance(model_root_directory, Path):
        raise RuntimeError('the argument lacks proper Path type')
    if not model_root_directory.exists():
        raise RuntimeError(f"StmModel directory does not exists:'{model_root_directory}'")

    if not model_root_directory.is_dir():
        raise RuntimeError(f"Specified model directory is not a directory:'{model_root_directory}'")


class RepositoryImpl:

    def __init__(self, file_prefix: str, model_type: Union[StmSystem, HydroPowerSystem], model_root_directory: Path):
        _is_a_valid_root_directory(model_root_directory)
        self.model_root_directory: Path = model_root_directory
        self.model_type: Union[StmSystem, HydroPowerSystem] = model_type
        self.file_prefix: str = file_prefix
        self.file_pattern = f"{self.file_prefix}_*_*.blob"
        self.regex_pattern = fr"^{self.file_prefix}_(\d+)_(.+)$"

    def get_model_infos(self) -> List[ModelInfo]:
        """

        Returns
        -------
            list of type ModelInfo
        """
        r = list()
        for file in list(self.model_root_directory.glob(self.file_pattern)):
            file_name = file.name.replace('.blob', '')
            m = re.search(self.regex_pattern, file_name)
            if len(m.groups()) == 2:
                id = int(m.group(1))
                name = str(m.group(2))
                created_utc = int(Path(file).stat().st_ctime)
                r.append(ModelInfo(id, name, created_utc))
        return r

    def get_models(self, model_ids: List[int]) -> List[Union[StmSystem, HydroPowerSystem]]:
        """

        Parameters
        ----------
        model_ids : list(int)
            list with model-ids to be retrieved
        Returns
        -------
            a list of type StmSystem, containing the ltm-models for the model_ids requested

        """
        r = list()
        for model_id in model_ids:
            r.append(self.get_model(model_id))
        return r

    def get_model(self, model_id: int) -> Union[StmSystem, HydroPowerSystem]:
        """

        Parameters
        ----------
        model_id : int
            model id to retrieve

        Returns
        -------
            a model of type StmSystem
        """
        p = self.model_root_directory
        file_filter = self._make_model_file_name(model_id, '*')
        candidates = list(p.glob(file_filter))
        if len(candidates) == 0:
            raise Exception(f"No model with id {model_id} found in directory '{str(p)}'")
        if len(candidates) > 1:
            raise Exception(f"Multiple models matching {file_filter} found in directory '{str(p)}'")
        return self.model_type.from_blob(byte_vector_from_file(str(candidates[0]).encode(locale.getpreferredencoding())))

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
        for file in list(self.model_root_directory.glob(self._make_model_file_name(model_id, '*'))):
            file.unlink()

    def save_model(self, model: Union[StmSystem, HydroPowerSystem]) -> int:
        """

        Parameters
        ----------
        model :
            the model to be saved
            notice that if the model.id is set to a value > 0 , then it replaces any existing model with that id if it
            exists. if the model id is 0, it creates a new id equal to max(ids)+1

        Returns
        -------
            model_id:int, a unique handle that can be used with .get_model(id)/.get_models([id1,...]) and .delete_model(id)
        """
        if not isinstance(model, self.model_type):
            raise TypeError(f"model should be of type {self.model_type}")
        if len(model.name) == 0:
            raise Exception("model.name should be something")
        if model.id < 0:
            raise Exception("model.id should be > 0")
        minfos = self.get_model_infos()
        if model.id == 0:  # then select new model id
            ids = [m.id for m in minfos]
            model.id = max(ids) + 1 if ids else 1
        full_path = self.model_root_directory/self._make_model_file_name(model.id, model.name)
        byte_vector_to_file(str(full_path).encode(locale.getpreferredencoding()), model.to_blob())
        return model.id

    def _make_model_file_name(self, id: int, model_name: str) -> str:
        return f"{self.file_prefix}_{id}_{model_name}.blob"


class ModelRepository(IModelRepository):

    def __init__(self, model_root_directory: Path):
        """

        Parameters
        ----------
        model_root_directory: string
            a path to the directory where the model-files resides
        """
        self._impl: RepositoryImpl = RepositoryImpl("stm_system", StmSystem, model_root_directory)

    def get_model_infos(self) -> List[ModelInfo]:
        """

        Returns
        -------
            list of type ModelInfo
        """
        return self._impl.get_model_infos()

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
        return self._impl.get_models(model_ids)

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
        return self._impl.get_model(model_id)

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
        return self._impl.delete_model(model_id, keep_ts_data)

    def save_model(self, model: StmSystem) -> int:
        """

        Parameters
        ----------
        model : StmSystem
            the model to be saved
            notice that if the model.id is set to a value > 0 , then it replaces any existing model with that id if it
            exists. if the model id is 0, it creates a new id equal to max(ids)+1

        Returns
        -------
            model_id:int, a unique handle that can be used with .get_model(id)/.get_models([id1,...]) and .delete_model(id)
        """
        return self._impl.save_model(model)


class HydroPowerSystemRepository(IHydroPowerSystemRepository):

    def __init__(self, model_root_directory: Path):
        """

        Parameters
        ----------
        model_root_directory: string
            a path to the directory where the model-files resides
        """
        self._impl: RepositoryImpl = RepositoryImpl("stm_hydro_power", HydroPowerSystem, model_root_directory)

    def get_model_infos(self) -> List[ModelInfo]:
        """

        Returns
        -------
            list of type ModelInfo
        """
        return self._impl.get_model_infos()

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
        return self._impl.get_models(model_ids)

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
        return self._impl.get_model(model_id)

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
        return self._impl.delete_model(model_id, keep_ts_data)

    def save_model(self, model: StmSystem) -> int:
        """

        Parameters
        ----------
        model : StmSystem
            the model to be saved
            notice that if the model.id is set to a value > 0 , then it replaces any existing model with that id if it
            exists. if the model id is 0, it creates a new id equal to max(ids)+1

        Returns
        -------
            model_id:int, a unique handle that can be used with .get_model(id)/.get_models([id1,...]) and .delete_model(id)
        """
        return self._impl.save_model(model)
