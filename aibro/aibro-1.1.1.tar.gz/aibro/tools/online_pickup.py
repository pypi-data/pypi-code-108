import datetime
from time import sleep
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import History
from tensorflow.keras.losses import serialize as loss_serialize
from tensorflow.keras.metrics import serialize as metric_serialize
from tensorflow.keras.models import Model as TF_Model
from tensorflow.keras.optimizers import serialize as optimizer_serialize

from aibro.tools.auth import check_authentication
from aibro.tools.prints import print_err
from aibro.tools.prints import print_launching
from aibro.tools.prints import print_sending
from aibro.tools.service.api_service import aibro_client
from aibro.tools.spot import _stop_instance
from aibro.tools.spot import connect_to_spot_server_offline
from aibro.tools.spot import connect_to_spot_server_online
from aibro.tools.spot import save_cancel_job_reason
from aibro.tools.utils import datetime_to_timestamp_ms
from aibro.tools.utils import encode_data
from aibro.tools.utils import get_data_size_mb
from aibro.tools.utils import get_encoded_model_content


def train_on_server(  # noqa: C901
    batch_size: int,
    epochs: int,
    machine_ids: List[str],
    model: TF_Model = None,
    train_X=None,
    train_Y=None,
    validation_X=None,
    validation_Y=None,
    description="",
    fit_kwargs: Dict[str, Any] = {},
    cool_down_period: int = 0,
    fit_type: str = "online",
    job_created_at_ms: int = 0,
    wait_request_s: int = 30,
    wait_new_job_create_s: int = -1,
    wait_new_job_create_interval: int = 10,
    directory_to_save_log: str = None,
    record: bool = False,
    access_token: str = None,
) -> Tuple[Optional[str], Optional[History], Optional[bytes], Optional[str], int]:
    user_id = check_authentication(access_token)
    print("Please open https://aipaca.ai/training_jobs to track job status.")
    if not user_id:
        raise Exception()
    if record:
        print(
            "Turned on record mode. Your job data will be sent to the AIbro support team for debugging purposes."
        )
    history = None
    job_id = ""
    for i, machine_id in enumerate(machine_ids):
        try:
            last_try = i == len(machine_ids) - 1
            job_type = "training"
            data = {
                "user_id": user_id,
                "machine_id": machine_id,
                "description": description,
                "cool_down_period": cool_down_period,
                "fit_type": fit_type,
                "job_created_at_ms": job_created_at_ms,
                "wait_request_s": wait_request_s,
                "last_try": last_try,
                "job_type": job_type,
            }
            aibro_client.connect_to_socket()
            if i == 0:
                if wait_new_job_create_s <= 0:
                    wait_new_job_create_s = 99999999
                while wait_new_job_create_s:
                    resp = aibro_client.create_new_job(
                        data, endpoint="v1/training/create_new_job"
                    )
                    if resp.status_code == 403:
                        print_launching(
                            f"{resp.text} try again in another {wait_new_job_create_interval} seconds"
                        )
                        sleep(wait_new_job_create_interval)
                        wait_new_job_create_s -= wait_new_job_create_interval
                        continue
                    break
                if resp.status_code != 200:
                    raise Exception(resp.text)
                job_id = resp.json()["job_id"]
                print_launching(f"Starting training job: {job_id}")
            print_launching(f"Requesting {machine_id} to be ready...")
            data["job_id"] = job_id
            aibro_client.add_job_to_socket(data["job_id"])
            resp = aibro_client.request_instance(
                data, endpoint="v1/training/request_instance"
            )
            aibro_client.del_job_to_socket(data["job_id"])
            aibro_client.disconnect_socket()
            if resp.status_code != 200:
                if i == len(machine_ids) - 1:
                    raise Exception(resp.text)
                continue
            server_public_ip = resp.json()["server_public_ip"]
            was_idle = resp.json()["was_idle"]
            if was_idle:
                print(f"Found an cooling {machine_id}, ready to train now 🎉\n")
            else:
                data_spin_up = {
                    "job_id": job_id,
                }
                resp = aibro_client.spin_up_server(
                    data_spin_up, endpoint="v1/training/spin_up_server"
                )
                print(f"Your {machine_id} is now ready 🎉\n")

            print_sending("Serializing your model...")
            loss = model.loss  # type:ignore
            optimizer = model.optimizer  # type:ignore

            loss_config = loss_serialize(loss) if not isinstance(loss, str) else loss
            optimizer_config = (
                optimizer_serialize(optimizer)
                if not isinstance(optimizer, str)
                else optimizer
            )

            metrics = vars(model.compiled_metrics)["_metrics"]  # type:ignore
            metrics = list(np.array(metrics).flatten())
            metrics_config = [
                metric_serialize(metric) if not isinstance(metric, str) else metric
                for metric in metrics
            ]

            if model:
                encoded_model_file_content = get_encoded_model_content(model)

            train_X_shape = list(train_X.shape)
            train_Y_shape = list(train_Y.shape)
            valid_X_shape = None
            valid_Y_shape = None
            if validation_X is not None:
                valid_X_shape = list(validation_X.shape)
                valid_Y_shape = list(validation_Y.shape)

            print_sending("Serializing your data...")
            (
                encoded_train_X,
                encoded_train_Y,
                encoded_validation_X,
                encoded_validation_Y,
            ) = encode_data(train_X, train_Y, validation_X, validation_Y)
            m_d_serialized_at_ms = datetime_to_timestamp_ms(datetime.datetime.now())

            data = {
                "tensorflow_version": tf.__version__,
                "encoded_model_content": encoded_model_file_content if model else None,
                "encoded_train_X": encoded_train_X,
                "encoded_train_Y": encoded_train_Y,
                "encoded_validation_X": encoded_validation_X,
                "encoded_validation_Y": encoded_validation_Y,
                "train_X_shape": train_X_shape,
                "train_Y_shape": train_Y_shape,
                "valid_X_shape": valid_X_shape,
                "valid_Y_shape": valid_Y_shape,
                "user_id": user_id,
                "optimizer_config": optimizer_config,
                "loss_config": loss_config,
                "metrics_config": metrics_config,
                "batch_size": batch_size,
                "epochs": epochs,
                "fit_kwargs": fit_kwargs,
                "job_id": job_id,
                "m_d_serialized_at_ms": m_d_serialized_at_ms,
                "record": record,
            }
            print_sending("Sending model and data to the server to start training")

            if fit_type == "online":
                (
                    history,
                    model_file_content,
                    tensorboard_logs,
                    epoch,
                ) = connect_to_spot_server_online(
                    data=data,
                    endpoint="v1/model_and_dataset",
                    job_id=job_id,
                    server_public_ip=server_public_ip,
                    directory_to_save_log=directory_to_save_log,
                )
                results_received_at_ms = datetime_to_timestamp_ms(
                    datetime.datetime.now()
                )
                post_train_detail = {
                    "job_id": job_id,
                    "size_m_d_trans_mb": get_data_size_mb(data),
                    "results_received_at_ms": results_received_at_ms,
                }
                aibro_client.connect_to_socket()
                aibro_client.get_serialization_details(post_train_detail)
                aibro_client.disconnect_socket()

                return job_id, history, model_file_content, tensorboard_logs, epoch
            else:
                connect_to_spot_server_offline(
                    data,
                    endpoint="v1/model_and_dataset",
                    job_id=job_id,
                    server_public_ip=server_public_ip,
                )
                return job_id, None, None, None, -1

        except Exception as e:
            if "No enough" in str(e) and i < len(machine_ids) - 1:
                reason = (
                    f"machine_id: {machine_id} not available in AWS. Try the next one"
                )
                print_launching(reason)
                aibro_client.disconnect_socket()
                continue
            else:
                reason = f"{str(e)}"
                print_err(reason)
                if job_id:
                    save_cancel_job_reason(
                        job_id, reason, endpoint="v1/training/save_cancel_job_reason"
                    )
            aibro_client.disconnect_socket()
            return job_id, history, None, None, -1
        except KeyboardInterrupt:
            if job_id:
                print_err(f"Trying to cancelled online job: {job_id}")
                _stop_instance(
                    job_id,
                    "User KeyboardInterrupt",
                    endpoint="v1/training/stop_instance",
                )
                save_cancel_job_reason(
                    job_id,
                    "User KeyboardInterrupt",
                    endpoint="v1/training/save_cancel_job_reason",
                )
                print_err(f"Job {job_id} successfully canceled")
            else:
                print_err("Job cancelled before server is ready")
            return job_id, None, None, None, -1
    return job_id, None, None, None, -1
