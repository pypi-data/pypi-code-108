import logging
import os
from typing import Optional, Dict, Any

import mlflow
import pytorch_lightning.loggers as loggers
import pytorch_lightning.loggers.base as base
from mlflow.tracking import MlflowClient
from mlflow.utils.mlflow_tags import MLFLOW_RUN_NAME
from pytorch_lightning import Trainer, LightningModule
from pytorch_lightning.callbacks import ModelCheckpoint

import sfu_torch_lib.io as io


log = logging.getLogger(__name__)


class MLFlowLogger(loggers.MLFlowLogger):
    def __init__(
        self,
        run_name: Optional[str] = None,
        tracking_uri: Optional[str] = os.getenv('MLFLOW_TRACKING_URI'),
        tags: Optional[Dict[str, Any]] = None,
        save_dir: Optional[str] = './mlruns',
        prefix: str = "",
        artifact_location: Optional[str] = None,
    ) -> None:

        super().__init__(
            run_name=run_name,
            tracking_uri=tracking_uri,
            tags=tags,
            save_dir=save_dir,
            prefix=prefix,
            artifact_location=artifact_location,
        )

    @property  # type: ignore
    @base.rank_zero_experiment
    def experiment(self) -> MlflowClient:
        if self._run_id and self._experiment_id:
            return self._mlflow_client

        self.tags = self.tags or {}

        if self._run_name is not None:
            if MLFLOW_RUN_NAME in self.tags:
                log.warning(
                    f'The tag {MLFLOW_RUN_NAME} is found in tags. '
                    f'The value will be overridden by {self._run_name}.'
                )

            self.tags[MLFLOW_RUN_NAME] = self._run_name

        run = mlflow.active_run() if mlflow.active_run() else mlflow.start_run(tags=self.tags)

        self._run_id = run.info.run_id
        self._experiment_id = run.info.experiment_id
        self._experiment_name = mlflow.get_experiment(run.info.experiment_id).name

        return self._mlflow_client


class MLFlowModelCheckpoint(ModelCheckpoint):
    def __init__(self, patience: int = 0, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.patience = patience
        self.mlflow_epoch = 0
        self.mlflow_model_path = ''

    @staticmethod
    def log_artifact(local_file: str, filename: str = 'last.ckpt') -> None:
        bucket, key = io.get_bucket_and_key(mlflow.get_artifact_uri())
        destination_path = os.path.join(key, filename)

        io.upload_s3(bucket, destination_path, local_file)

    def on_train_epoch_end(self, trainer: Trainer, pl_module: LightningModule) -> None:
        super().on_train_epoch_end(trainer, pl_module)

        should_save = trainer.current_epoch - self.mlflow_epoch >= self.patience
        has_new_model = self.best_model_path and self.best_model_path != self.mlflow_model_path

        if should_save and has_new_model:
            self.log_artifact(self.best_model_path)

            self.mlflow_epoch = trainer.current_epoch
            self.mlflow_model_path = self.best_model_path

    def on_train_end(self, trainer: Trainer, pl_module: LightningModule) -> None:
        super().on_train_end(trainer, pl_module)

        self.log_artifact(self.best_model_path)
