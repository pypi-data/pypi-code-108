from typing import List, Optional

from .error import APIError

class Delete():

    def __init__(self):
        from .connection import Connection
        from pyrasgo.config import get_session_api_key

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)

    def collection(self, id: int) -> str:
        """
        Permanently delete a Rasgo Collection. There is no way to undo this operation.
        """
        try:
            response = self.api._delete(f"/models/{id}", api_version=1)
            if response.status_code == 200:
                return f"Collection {id} successfully deleted"
            if response.status_code == 403:
                raise APIError(f"User does not have access to delete Collection {id}")
            raise APIError(f"Problem deleting Collection {id}.")
        except:
            raise APIError(f"Problem deleting Collection {id}.")

    def dataset_snapshot(self, dataset_id: int, index: int):
        return self.api._delete(f"/datasets/{dataset_id}/snapshots/{index}", api_version=2).json()

    def data_source(self, id: int) -> str:
        """
        Permanently delete a Rasgo DataSource. There is no way to undo this operation.
        """
        try:
            response = self.api._delete(f"/data-source/{id}", api_version=1)
            if response.status_code == 200:
                return f"DataSource {id} successfully deleted"
            if response.status_code == 403:
                raise APIError(f"User does not have access to delete DataSource {id}")
            return f"Problem deleting DataSource {id}."
        except:
            return f"Problem deleting DataSource {id}."

    def feature(self, id: int) -> str:
        """
        Permanently delete a Rasgo Feature. There is no way to undo this operation.
        """
        try:
            response = self.api._delete(f"/features/{id}", api_version=1)
            if response.status_code == 200:
                return f"Feature {id} successfully deleted"
            if response.status_code == 403:
                raise APIError(f"User does not have access to delete Feature {id}")
            return f"Problem deleting Feature {id}."
        except:
            return f"Problem deleting Feature {id}."

    def transform(self, transform_id: int) -> str:
        """
        Delete a Rasgo User Defined Transform
        """
        # NOTE: We print out error msgs on the API side
        # in the function self.api._raise_internal_api_error_if_any(response)
        # so no need to print out logic like above
        response = self.api._delete(f"/transform/{transform_id}", api_version=1)
        if response.status_code == 200:
            return f"Transform with id '{transform_id}' successfully deleted"
        if response.status_code == 403:
            raise APIError(f"User does not have access to delete Transform "
                           f"with id '{transform_id}'")
        return f"Problem deleting Transform {transform_id}."

    def dataset(self, dataset_id: int) -> str:
        """
        Delete a Dataset in Rasgo
        """
        response = self.api._delete(f"/datasets/{dataset_id}", api_version=2)
        if response.status_code == 200:
            return f"Dataset with id '{dataset_id}' successfully deleted"
        return f"Problem deleting Dataset {dataset_id}."

