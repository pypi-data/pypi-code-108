import logging

logger = logging.getLogger(__name__)


class LibraryFactory:
    @staticmethod
    def get_library(project_token: str, lib: str, *args, **kwargs):
        if str(lib).lower() == "mlflow":
            from .mlflow import MlflowAdapter

            return MlflowAdapter(project_token=project_token, *args, **kwargs)  # type: ignore
        else:
            raise ValueError(f"Unsupported library: {lib}")
