from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import traceback
from typing import Optional, TYPE_CHECKING, Union

import sqlalchemy

from anylearn.config import AnylearnConfig
from anylearn.storage.db.models import (
    Base,
    SqlLocalAlgorithm,
    SqlLocalDataset,
    SqlLocalHpoExperiment,
    SqlLocalModel,
    SqlLocalTrainTask,
    SqlTrainProfile,
)
from anylearn.utils import logger
from anylearn.utils.errors import AnyLearnException
from anylearn.utils.singleton import Singleton

if TYPE_CHECKING:
    # Avoid circular import for type hinting (ENFER)
    from anylearn.applications.hpo_experiment import HpoExperiment
    from anylearn.interfaces import TrainTask


def _get_session(SessionMaker, db_type):
    """
    Creates a factory for producing exception-safe SQLAlchemy sessions that are made available
    using a context manager. Any session produced by this factory is automatically committed
    if no exceptions are encountered within its associated context. If an exception is
    encountered, the session is rolled back. Finally, any session produced by this factory is
    automatically closed when the session's associated context is exited.
    Credit: mlflow@/mlflow/store/db/utils.py
    """

    @contextmanager
    def make_managed_session():
        """Provide a transactional scope around a series of operations."""
        session = SessionMaker()
        try:
            if db_type == "sqlite":
                session.execute("PRAGMA foreign_keys = ON;")
                session.execute("PRAGMA case_sensitive_like = true;")
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    return make_managed_session


class DB(metaclass=Singleton):
    def __init__(self):
        AnylearnConfig.init_workspace()
        self.alembic_ini = (
            Path(__file__).parent /
            "migrations" /
            "alembic.ini"
        )

        # DB physical concerns
        self.engine = sqlalchemy.create_engine(AnylearnConfig.db_uri)
        self.__upgrade_tables()

        # ORM logical concerns
        Base.metadata.bind = self.engine
        # Instance <xxx> is not bound to a Session; attribute refresh operation cannot proceed
        SessionMaker = sqlalchemy.orm.sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = _get_session(SessionMaker, "sqlite")

    def __upgrade_tables(self):
        from alembic import command

        logger.info("Upgrading database tables...")
        config = self.__get_alembic_config()
        with self.engine.begin() as connection:
            config.attributes["connection"] = connection # type: ignore
            config.attributes['configure_logger'] = False # type: ignore
            command.upgrade(config, "heads")

    def __get_alembic_config(self):
        from alembic.config import Config
        config = Config(self.alembic_ini)
        config.set_main_option('script_location', str(self.alembic_ini.parent))
        config.set_main_option('sqlalchemy.url', AnylearnConfig.db_uri)
        return config

    def force_init(self):
        self.__init__()

    def _save_to_db(self, session, objs):
        if type(objs) is list:
            session.add_all(objs)
        else:
            session.add(objs)

    def create_or_update_train_task(self,
                                    train_task: TrainTask,
                                    hpo_id: Optional[str] = None):
        with self.session() as s:
            train_task_obj = s.get(SqlLocalTrainTask, train_task.id)
            if train_task_obj:
                self.update_train_task(train_task=train_task)
            else:
                self.create_train_task(train_task=train_task, hpo_id=hpo_id)

    def create_train_task(self,
                          train_task: TrainTask,
                          hpo_id: Optional[str]=None):
        with self.session() as s:
            s.add(
                SqlLocalTrainTask(
                    id=train_task.id,
                    remote_state_sofar=train_task.state,
                    secret_key=train_task.secret_key,
                    project_id=train_task.project_id,
                    hpo_id=hpo_id,
                    hpo_final_metric=train_task.final_metric,
                )
            )
            try:
                s.commit()
            except Exception as e:
                traceback.format_exc()
                traceback.print_exc()
                logger.error(e)
                s.rollback()
                raise

    def delete_train_task(self, id: str):
        with self.session() as s:
            s.query(SqlLocalTrainTask)\
                .filter(SqlLocalTrainTask.id == id)\
                .delete()

    def delete_train_task_all(self):
        with self.session() as s:
            s.query(SqlLocalTrainTask).delete()

    def update_train_task(self, train_task: TrainTask):
        with self.session() as s:
            local_train_task = s.query(SqlLocalTrainTask)\
                .filter(SqlLocalTrainTask.id == train_task.id)\
                .first()
            if local_train_task:
                try:
                    local_train_task.id = train_task.id
                    local_train_task.remote_state_sofar = train_task.state
                    local_train_task.secret_key = train_task.secret_key
                    local_train_task.project_id = train_task.project_id
                    local_train_task.hpo_final_metric = train_task.final_metric
                except Exception as e:
                    traceback.format_exc()
                    traceback.print_exc()
                    logger.error(e)
                    s.rollback()
                    raise

    def get_unfinished_train_tasks(self):
        with self.session() as s:
            obj_list = s.query(SqlLocalTrainTask)\
                .filter(SqlLocalTrainTask.remote_state_sofar.in_([
                    # TODO: this is a work-around, make this generic
                    0,1
                ]))\
                .all()
            return obj_list

    def get_all_train_tasks(self):
        with self.session() as s:
            obj_list = s.query(SqlLocalTrainTask).all()
            return obj_list

    def get_train_task(self, id: str):
        with self.session() as s:
            obj = s.get(SqlLocalTrainTask, id)
            return obj
    
    def _check_resource_class(self, resource_class: type):
        if resource_class not in [
            SqlLocalAlgorithm,
            SqlLocalDataset,
            SqlLocalModel,
        ]:
            raise AnyLearnException((
                "'resource_class' must be one of "
                "["
                "SqlLocalAlgorithm,"
                "SqlLocalDataset,"
                "SqlLocalModel,"
                "]"
            ))

    def create_local_algorithm(self, id: Optional[str]=None, checksum: Optional[str]=None):
        return self._create_resource(
            resource_class=SqlLocalAlgorithm,
            resource_id=id,
            resource_checksum=checksum
        )

    def create_local_dataset(self, id: Optional[str]=None, checksum: Optional[str]=None):
        return self._create_resource(
            resource_class=SqlLocalDataset,
            resource_id=id,
            resource_checksum=checksum
        )

    def create_local_model(self, id: Optional[str]=None, checksum: Optional[str]=None):
        return self._create_resource(
            resource_class=SqlLocalModel,
            resource_id=id,
            resource_checksum=checksum
        )

    def _create_resource(self, resource_class: type, resource_id: Optional[str]=None,
                        resource_checksum: Optional[str]=None):
        self._check_resource_class(resource_class)
        with self.session() as s:
            s.add(
                resource_class(
                    id=resource_id,
                    checksum=resource_checksum,
                )
            )
            try:
                s.commit()
            except Exception as e:
                traceback.format_exc()
                traceback.print_exc()
                logger.error(e)
                s.rollback()
                raise

    def find_local_algorithm_by_checksum(self, checksum: str):
        return self._find_resource_by_checksum(
            resource_class=SqlLocalAlgorithm,
            checksum=checksum
        )

    def find_local_dataset_by_checksum(self, checksum: str):
        return self._find_resource_by_checksum(
            resource_class=SqlLocalDataset,
            checksum=checksum
        )

    def find_local_model_by_checksum(self, checksum: str):
        return self._find_resource_by_checksum(
            resource_class=SqlLocalModel,
            checksum=checksum
        )

    def _find_resource_by_checksum(self,
                                   resource_class: Union[
                                       SqlLocalAlgorithm,
                                       SqlLocalDataset,
                                       SqlLocalModel
                                   ],
                                   checksum: str):
        self._check_resource_class(resource_class)
        with self.session() as s:
            res = s.query(resource_class)\
                .filter(resource_class.checksum == checksum)\
                .first()
            return res.id if res else None

    def delete_local_algorithm(self, id: str):
        return self._delete_resource(
            resource_class=SqlLocalAlgorithm,
            id=id
        )

    def delete_local_dataset(self, id: str):
        return self._delete_resource(
            resource_class=SqlLocalDataset,
            id=id
        )

    def delete_local_model(self, id: str):
        return self._delete_resource(
            resource_class=SqlLocalModel,
            id=id
        )

    def _delete_resource(self, resource_class: type, id: str):
        self._check_resource_class(resource_class)
        with self.session() as s:
            res = s.query(resource_class)\
                .filter_by(id=id)\
                .delete()
            return res == 1

    def get_hpo_best_train_task(self,
                                project_id: str,
                                hpo_mode: str) -> TrainTask:
        orderby = (
            sqlalchemy.desc(SqlLocalTrainTask.hpo_final_metric)
            if hpo_mode == "maximize"
            else sqlalchemy.asc(SqlLocalTrainTask.hpo_final_metric)
        )
        with self.session() as s:
            res = s.query(SqlLocalTrainTask)\
                .filter_by(project_id=project_id)\
                .order_by(orderby)\
                .first()
            return TrainTask.from_sql(sql_local_train_task=res)

    def get_hpo_experiments(self) -> list[SqlLocalHpoExperiment]:
        with self.session() as s:
            return s.query(SqlLocalHpoExperiment).all()

    def get_hpo_experiment(self, id: str) -> SqlLocalHpoExperiment:
        with self.session() as s:
            return s.get(SqlLocalHpoExperiment, id)

    def create_hpo_experiment(self,
                              id: Optional[str]=None,
                              port: Optional[int]=None,
                              mode: Optional[str]=None,
                              status: Optional[str]=None,
                              project_id: Optional[str]=None,
                              project_name: Optional[str]=None,
                              algorithm_id: Optional[str]=None,
                              dataset_id: Optional[str]=None,
                              algorithm_dir: Optional[str]=None,
                              algorithm_archive: Optional[str]=None,
                              dataset_dir: Optional[str]=None,
                              dataset_archive: Optional[str]=None,
                              created_at: Optional[datetime]=None):
        with self.session() as s:
            exp = SqlLocalHpoExperiment(
                id=id,
                port=port,
                mode=mode,
                status=status,
                project_id=project_id,
                project_name=project_name,
                algorithm_id=algorithm_id,
                algorithm_dir=algorithm_dir,
                algorithm_archive=algorithm_archive,
                dataset_id=dataset_id,
                dataset_dir=dataset_dir,
                dataset_archive=dataset_archive,
                created_at=created_at,
            )
            self._save_to_db(objs=exp, session=s)

    def update_hpo_experiment_status(self, id: str, status: str):
        with self.session() as s:
            exp = s.get(SqlLocalHpoExperiment, id)
            if not exp:
                raise AnyLearnException(f"Local HPO experiment {id} does not exist")
            exp.status = status
            self._save_to_db(objs=exp, session=s)

    def update_hpo_experiment_port(self, id: str, port: int):
        with self.session() as s:
            exp = s.get(SqlLocalHpoExperiment, id)
            if not exp:
                raise AnyLearnException(f"Local HPO experiment {id} does not exist")
            exp.port = port
            self._save_to_db(objs=exp, session=s)

    def get_train_profile(self, id: Optional[str] = None) -> SqlTrainProfile:
        with self.session() as s:
            return s.get(SqlTrainProfile, id)

    def create_train_profile(self,
                             id: str,
                             train_task_id: str,
                             algorithm_id: Optional[str] = None,
                             algorithm_dir: Optional[str] = None,
                             algorithm_archive: Optional[str] = None,
                             dataset_id: Optional[str] = None,
                             dataset_dir: Optional[str] = None,
                             dataset_archive: Optional[str] = None,
                             entrypoint: Optional[str] = None,
                             train_params: Optional[str] = None,):
        with self.session() as s:
            exp = SqlTrainProfile(
                id=id,
                train_task_id=train_task_id,
                entrypoint=entrypoint,
                train_params=train_params,
                algorithm_id=algorithm_id,
                algorithm_dir=algorithm_dir,
                algorithm_archive=algorithm_archive,
                dataset_id=dataset_id,
                dataset_dir=dataset_dir,
                dataset_archive=dataset_archive,
            )
            self._save_to_db(objs=exp, session=s)
