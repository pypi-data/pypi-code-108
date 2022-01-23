import os
from typing import Type

import mlflow
import torch
from pytorch_lightning import LightningModule

import sfu_torch_lib.io as io


def load_model(run_id: str, module_class: Type[LightningModule], filename: str = 'last') -> LightningModule:
    run = mlflow.get_run(run_id)

    model_path = os.path.join(run.info.artifact_uri, f'{filename}.ckpt')

    with io.open(model_path) as model_file:
        model = module_class.load_from_checkpoint(model_file)

    return model


def load_state(run_id: str, model: LightningModule, filename: str = 'last') -> None:
    device = torch.device('cuda') if torch.cuda.device_count() else torch.device('cpu')

    run = mlflow.get_run(run_id)

    model_path = os.path.join(run.info.artifact_uri, f'{filename}.ckpt')

    with io.open(model_path) as model_file:
        checkpoint = torch.load(model_file, device)

    model.load_state_dict(checkpoint['state_dict'])
