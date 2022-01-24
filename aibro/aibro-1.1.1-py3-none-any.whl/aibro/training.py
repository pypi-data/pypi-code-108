import datetime
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
from tensorflow.keras.callbacks import History
from tensorflow.keras.models import load_model
from tensorflow.keras.models import Model as TF_Model

from aibro.comm import available_machines
from aibro.tools.auth import check_authentication
from aibro.tools.helpers.input_assertions import assert_batch_size_type
from aibro.tools.helpers.input_assertions import assert_data_type
from aibro.tools.helpers.input_assertions import assert_epochs_type
from aibro.tools.helpers.input_assertions import assert_is_tf_model
from aibro.tools.marketplace import _check_machines_exist
from aibro.tools.online_pickup import train_on_server
from aibro.tools.prints import print_err
from aibro.tools.prints import print_receiving
from aibro.tools.service.api_service import aibro_client
from aibro.tools.spot import _stop_instance
from aibro.tools.spot import save_cancel_job_reason
from aibro.tools.utils import datetime_to_timestamp_ms
from aibro.tools.utils import save_tensorboard_logs


class Training(object):
    @staticmethod
    def online_fit(
        model: TF_Model,
        train_X: np.ndarray,
        train_Y: np.ndarray,
        machine_ids: List[str] = None,
        batch_size: int = 1,
        epochs: int = 1,
        validation_data: Tuple[np.ndarray, np.ndarray] = None,
        description: str = "",
        cool_down_period_s: int = 0,
        fit_kwargs: Dict[str, Any] = {},
        directory_to_save_ckpt: str = None,
        directory_to_save_log: str = None,
        wait_request_s: int = 30,
        wait_new_job_create_s: int = -1,
        wait_new_job_create_interval: int = 10,
        record: bool = False,
        access_token=None,
    ):
        """[reference]
        https://doc.aipaca.ai/#online_fit
        """
        return online_fit(
            model,
            train_X,
            train_Y,
            machine_ids,
            batch_size,
            epochs,
            validation_data,
            description,
            cool_down_period_s,
            fit_kwargs,
            directory_to_save_ckpt,
            directory_to_save_log,
            wait_request_s,
            wait_new_job_create_s,
            wait_new_job_create_interval,
            record,
            access_token,
        )


def online_fit(
    model: TF_Model,
    train_X: np.ndarray,
    train_Y: np.ndarray,
    machine_ids: List[str] = None,
    batch_size: int = 1,
    epochs: int = 1,
    validation_data: Tuple[np.ndarray, np.ndarray] = None,
    description: str = "",
    cool_down_period_s: int = 0,
    fit_kwargs: Dict[str, Any] = {},
    directory_to_save_ckpt: str = None,
    directory_to_save_log: str = None,
    wait_request_s: int = 30,
    wait_new_job_create_s: int = -1,
    wait_new_job_create_interval: int = 10,
    record: bool = False,
    access_token: str = None,
) -> Tuple[Optional[str], Optional[TF_Model], Optional[History]]:
    job_id, trained_model, history = None, None, None
    try:
        # Check input types
        job_created_at_ms = datetime_to_timestamp_ms(datetime.datetime.now())
        train_X, train_Y, validation_data = _data_validation(
            model, train_X, train_Y, batch_size, epochs, validation_data
        )

        validation_X, validation_Y = None, None
        if validation_data:
            validation_X, validation_Y = validation_data

        job_id, history, model_file_content, tensorboard_logs, epoch = train_on_server(
            model=model,
            train_X=train_X,
            train_Y=train_Y,
            machine_ids=_check_machine_ids(machine_ids),
            batch_size=batch_size,
            epochs=epochs,
            validation_X=validation_X,
            validation_Y=validation_Y,
            description=description,
            fit_kwargs=fit_kwargs,
            cool_down_period=cool_down_period_s,
            job_created_at_ms=job_created_at_ms,
            wait_request_s=wait_request_s,
            wait_new_job_create_s=wait_new_job_create_s,
            wait_new_job_create_interval=wait_new_job_create_interval,
            directory_to_save_log=directory_to_save_log,
            record=record,
            access_token=access_token,
        )

        # if save ckpt not provided default not saving h5
        not_save_as_h5 = not directory_to_save_ckpt
        not_save_log = not directory_to_save_log
        # temperarily to save the model to '.' which will later get deleted
        # if not provided
        directory_to_save_ckpt = (
            directory_to_save_ckpt if directory_to_save_ckpt else "."
        )
        trained_model = _get_model_from_file(
            model_file_content=model_file_content,
            not_save_as_h5=not_save_as_h5,
            directory_to_save_ckpt=directory_to_save_ckpt,
            epoch=epoch,
        )
        save_tensorboard_logs(
            tensorboard_logs, not_save_log, directory_to_save_log, job_id
        )
        return job_id, trained_model, history

    except Exception as e:
        print_err(str(e))
        return job_id, trained_model, history


def _pick_machine_id():
    available_machines()
    machine_id = input("Enter machine_id: ")
    print(f"You have selected {machine_id}\n")
    return machine_id


def _check_machine_ids(machine_ids: List[str] = None) -> List[str]:
    while not machine_ids or len(machine_ids) == 0:
        print(
            "We detected that you didn't select a cloud machine. Please select one of the followings:"
        )
        machine_ids = [_pick_machine_id()]
    marketplace = aibro_client.get("v1/marketplace_machines").json()
    new_machine_ids: List[str] = [
        m for m in machine_ids if _check_machines_exist(m, marketplace)
    ]
    while len(new_machine_ids) == 0:
        print(
            "We detected that the cloud machine you selected is not available. \
                    Please select one of the followings:"
        )
        new_machine_ids = [_pick_machine_id()]
        if not _check_machines_exist(new_machine_ids[0], marketplace):
            new_machine_ids = []
    return new_machine_ids


def _get_model_from_file(
    model_file_content: Optional[bytes],
    not_save_as_h5: bool,
    directory_to_save_ckpt: Optional[str],
    epoch: int,
) -> Optional[TF_Model]:
    model = None
    if model_file_content:
        file_name = f"{directory_to_save_ckpt}/model_{epoch:04d}.h5"
        f = open(file_name, "wb")
        f.write(model_file_content)
        f.close()
        model = load_model(file_name)

        if not_save_as_h5:
            os.remove(file_name)
        else:
            print_receiving(f"Saved ckpt file to {file_name}")

    return model


def _data_validation(
    model: TF_Model,
    train_X: np.ndarray,
    train_Y: np.ndarray,
    batch_size: int = 1,
    epochs: int = 1,
    validation_data: Tuple[np.ndarray, np.ndarray] = None,
):
    assert_is_tf_model(model)
    train_X = assert_data_type(train_X, "train_X")
    train_Y = assert_data_type(train_Y, "train_Y")
    assert_batch_size_type(batch_size)
    assert_epochs_type(epochs)

    validation_X, validation_Y = None, None
    if validation_data is not None:
        validation_X, validation_Y = validation_data
        validation_X = assert_data_type(validation_X, "validation_X")
        validation_Y = assert_data_type(validation_Y, "validation_Y")
    return train_X, train_Y, (validation_X, validation_Y)


def cancel_job(job_id: str, e: str):
    check_authentication()
    try:
        print_err(f"Trying to cancel offline job: {job_id}")
        _stop_instance(job_id, e, endpoint="v1/training/stop_instance")
        save_cancel_job_reason(
            job_id,
            "User Called Cancel Job",
            endpoint="v1/training/save_cancel_job_reason",
        )
        print_err(f"Job {job_id} canceled successfully")
    except Exception as e:
        print_err(f"Canceling job failed: {str(e)}")


# def offline_fit(
#     model: TF_Model,
#     train_X: np.ndarray,
#     train_Y: np.ndarray,
#     machine_ids: List[str] = None,
#     batch_size: int = 1,
#     epochs: int = 1,
#     validation_data: Tuple[np.ndarray, np.ndarray] = None,
#     description="",
#     fit_kwargs: Dict[str, Any] = {},
#     cool_down_period_s: int = 0,
#     save_data=False,
#     data_name=None,
# ):
#     job_id = None
#     try:
#         # Check input types
#         _data_validation(model, train_X, train_Y, batch_size, epochs, validation_data)
#         validation_X, validation_Y = None, None
#         if validation_data:
#             validation_X, validation_Y = validation_data

#         job_id, _, _, _, _ = train_on_server(
#             model=model,
#             train_X=train_X,
#             train_Y=train_Y,
#             machine_ids=_check_machine_ids(machine_ids),
#             batch_size=batch_size,
#             epochs=epochs,
#             validation_X=validation_X,
#             validation_Y=validation_Y,
#             description=description,
#             fit_kwargs=fit_kwargs,
#             cool_down_period=cool_down_period_s,
#             fit_type="offline",
#         )
#         return job_id

#     except Exception as e:
#         print_err(str(e))
#         aibro_client.disconnect_socket()
#         return job_id
