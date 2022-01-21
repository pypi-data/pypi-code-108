import os

from anylearn.config import AnylearnConfig, init_sdk_incontainer
from anylearn.interfaces import TrainTask
from anylearn.utils import logger
from anylearn.utils.errors import AnyLearnException


INCONTAINER_TRAIN_TASK_ID = os.environ.get('task_id', None)
INCONTAINER_TRAIN_TASK_SECRET = os.environ.get('secret_key', None)


def report_intermediate_metric(metric: float):
    """
    向Anylearn后端引擎汇报模型训练的中间结果指标。

    Parameters
    ----------
    metric:
        中间结果指标的值，浮点数类型。
    """
    __init()
    train_task = get_incontainer_train_task()
    if train_task and train_task.id:
        train_task.report_intermediate_metric(metric)
    else:
        logger.info(f"Reported intermediate metric: {metric}")


def report_final_metric(metric: float):
    """
    向Anylearn后端引擎汇报模型训练的最终结果指标。

    Parameters
    ----------
    metric:
        最终结果指标的值，浮点数类型。
    """
    __init()
    train_task = get_incontainer_train_task()
    if train_task and train_task.id:
        train_task.report_final_metric(metric)
    else:
        logger.info(f"Reported final metric: {metric}")


def get_incontainer_train_task():
    """
    从Anylearn后端引擎的当前训练环境（容器）中获取训练任务对象。

    Returns
    -------
    TrainTask
        当前训练环境中的训练对象。
    """
    if not all([
        INCONTAINER_TRAIN_TASK_ID,
        INCONTAINER_TRAIN_TASK_SECRET,
    ]):
        raise AnyLearnException("无法获取训练环境")
    return TrainTask(id=INCONTAINER_TRAIN_TASK_ID,
                     secret_key=INCONTAINER_TRAIN_TASK_SECRET)


def __init():
    if AnylearnConfig.cluster_address:
        return
    namespace = os.environ.get('BACKEND_NAMESPACE', "STANDALONE")
    init_sdk_incontainer(f"http://anylearn-backend.{namespace}")
