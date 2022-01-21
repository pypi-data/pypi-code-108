from __future__ import annotations
from datetime import datetime
from typing import Optional

from anylearn.utils.errors import AnyLearnException
from anylearn.storage.db import DB
from anylearn.utils import utc_plus_8


class TrainProfile:
    """
    训练任务描述类。

    一个训练任务的描述包括了
    训练任务命令、
    训练参数、
    算法、
    数据集、
    训练的元信息
    等几方面，
    用户可以根据这些信息可以在多次训练之间进行区别和回忆。
    任务描述中封装了一些与训练相关的功能，
    如：获取本地训练的训练描述集合、创建训练描述、获取某一训练任务的训练描述等等，
    以便对任一训练任务的生命周期进行完整的回溯和管理。

    Attributes
    ----------
    id : :obj:`str`
        训练任务描述ID。
    train_task_id : :obj:`str`
        训练任务ID。
    entrypoint : :obj:`str`, optional
        启动训练的入口命令。
    train_params : :obj:`str`
        训练任务参数。
    algorithm_id : :obj:`str`
        已在Anylearn远程注册的算法ID。
    algorithm_dir : :obj:`str`, optional
        本地算法目录路径。
    algorithm_archive : :obj:`str`, optional
        本地算法压缩包路径。
    dataset_id : :obj:`str`
        已在Anylearn远程注册的数据集ID。
    dataset_dir : :obj:`str`, optional
        本地数据集目录路径。
    dataset_archive : :obj:`str`, optional
        本地数据集压缩包路径。
    created_at : :obj:`str`, optional
        调参实验的创建时间。
        默认为东八时区的当前时间。
    """

    def __init__(self,
                 id: str,
                 train_task_id: str,
                 entrypoint: Optional[str] = None,
                 algorithm_id: Optional[str] = None,
                 dataset_id: Optional[str] = None,
                 train_params: Optional[str] = None,
                 algorithm_dir: Optional[str] = None,
                 algorithm_archive: Optional[str] = None,
                 dataset_dir: Optional[str] = None,
                 dataset_archive: Optional[str] = None,
                 created_at: Optional[datetime] = utc_plus_8()):
        """
        Parameters
        ----------
        id : :obj:`str`
            训练任务描述ID。
        train_task_id : :obj:`str`
            训练任务ID。
        entrypoint : :obj:`str`, optional
            启动训练的入口命令。
        train_params : :obj:`str`
            训练任务参数。
        algorithm_id : :obj:`str`
            已在Anylearn远程注册的算法ID。
        algorithm_dir : :obj:`str`, optional
            本地算法目录路径。
        algorithm_archive : :obj:`str`, optional
            本地算法压缩包路径。
        dataset_id : :obj:`str`
            已在Anylearn远程注册的数据集ID。
        dataset_dir : :obj:`str`, optional
            本地数据集目录路径。
        dataset_archive : :obj:`str`, optional
            本地数据集压缩包路径。
        created_at : :obj:`str`, optional
            调参实验的创建时间。
            默认为东八时区的当前时间。
        """
        self.id = id
        self.train_task_id = train_task_id
        self.entrypoint = entrypoint
        self.train_params = train_params
        self.algorithm_id = algorithm_id
        self.dataset_id = dataset_id
        self.algorithm_dir = algorithm_dir
        self.algorithm_archive = algorithm_archive
        self.dataset_dir = dataset_dir
        self.dataset_archive = dataset_archive
        self.created_at = created_at

    @classmethod
    def get(cls, id: str=None, train_task_id: str=None):
        """
        以训练任务ID或描述ID获取该训练的描述。

        Parameters
        ----------
        id : :obj:`str`
            训练描述的ID。
        train_task_id : :obj:`str`
            训练任务的ID。

        Returns
        -------
        TrainProfile
            符合传入ID的训练描述对象。
        """
        if train_task_id:
            local_train_task = DB().get_train_task(id=train_task_id)
            if not local_train_task:
                raise AnyLearnException(f"资源{train_task_id}未找到")
            sql_train_profile = local_train_task.train_profile
        else:
            sql_train_profile = DB().get_train_profile(id=id)
        if not len(sql_train_profile):
            raise AnyLearnException(
                f"资源{train_task_id if train_task_id else id}未找到TrainProfile")
        return cls.from_sql(sql_train_profile[0])

    @classmethod
    def from_sql(cls, sql_train_profile):
        """
        从本地数据库模型映射对一个训练任务描述进行实例化。

        Parameters
        ----------
        sql_train_profile : :obj:`SqlTrainProfile`
            本地数据库映射对象。
        
        Returns
        -------
        TrainProfile
            符合传入映射的训练描述对象。
        """
        return TrainProfile(
            id=sql_train_profile.id,
            train_task_id=sql_train_profile.train_task_id,
            entrypoint=sql_train_profile.entrypoint,
            train_params=sql_train_profile.train_params,
            algorithm_id=sql_train_profile.algorithm_id,
            dataset_id=sql_train_profile.dataset_id,
            algorithm_dir=sql_train_profile.algorithm_dir,
            algorithm_archive=sql_train_profile.algorithm_archive,
            dataset_dir=sql_train_profile.dataset_dir,
            dataset_archive=sql_train_profile.dataset_archive,
            created_at=sql_train_profile.created_at,
        ) if sql_train_profile else None

    def create_in_db(self):
        """
        将训练任务描述写入本地数据库。
        """
        DB().create_train_profile(
            id=self.id,
            train_task_id=self.train_task_id,
            entrypoint=self.entrypoint,
            train_params=self.train_params,
            algorithm_id=self.algorithm_id,
            algorithm_dir=self.algorithm_dir,
            algorithm_archive=self.algorithm_archive,
            dataset_id=self.dataset_id,
            dataset_dir=self.dataset_dir,
            dataset_archive=self.dataset_archive,
        )

    @classmethod
    def get_train_profiles(cls, local_train_tasks=None):
        """
        以训练任务集合获取他们所有的训练描述。

        Parameters
        ----------
        local_train_tasks : :obj:`List[SqlLocalTrainTask]`
            本地训练任务集合。

        Returns
        -------
        List[TrainProfile]
        """
        return [cls.from_sql(local_train_task.train_profile[0] if len(local_train_task.train_profile) else None)
                for local_train_task in local_train_tasks]

    def __repr__(self) -> str:
        kv = (
            f"    id='{self.id}',\n"
            f"    train_task_id={self.train_task_id},\n"
            f"    entrypoint='{self.entrypoint}',\n"
            f"    train_params='{self.train_params}',\n"
            f"    algorithm_id='{self.algorithm_id}',\n"
            f"    algorithm_dir='{self.algorithm_dir}',\n"
            f"    algorithm_archive='{self.algorithm_archive}',\n"
            f"    dataset_id='{self.dataset_id}',\n"
            f"    dataset_dir='{self.dataset_dir}',\n"
            f"    dataset_archive='{self.dataset_archive}',\n"
            f"    created_at=datetime.strptime('{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}', '%Y-%m-%d %H:%M:%S'),\n"
        )
        return f"TrainProfile(\n{kv})"
