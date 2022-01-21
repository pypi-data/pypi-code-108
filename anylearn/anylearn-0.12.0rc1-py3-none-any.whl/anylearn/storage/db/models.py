from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.sqltypes import Float

from anylearn.utils import utc_plus_8


Base = declarative_base()

class SqlLocalAlgorithm(Base):
    __tablename__ = 'local_algorithm'

    id = Column(String(32), primary_key=True)
    checksum = Column(String(128), nullable=False)


class SqlLocalDataset(Base):
    __tablename__ = 'local_dataset'

    id = Column(String(32), primary_key=True)
    checksum = Column(String(128), nullable=False)


class SqlLocalModel(Base):
    __tablename__ = 'local_model'

    id = Column(String(32), primary_key=True)
    checksum = Column(String(128), nullable=False)


class SqlLocalHpoExperiment(Base):
    __tablename__ = 'local_hpo_experiment'

    id = Column(String(8), primary_key=True)
    port = Column(Integer, nullable=False)
    mode = Column(String(8), nullable=False, default="maximize")
    status = Column(String(16), nullable=False, default="RUNNING")
    project_id = Column(String(32), nullable=False)
    project_name = Column(String(255), nullable=False)
    algorithm_id = Column(String(32), nullable=False)
    algorithm_dir = Column(String(4096), nullable=True)
    algorithm_archive = Column(String(4096), nullable=True)
    dataset_id = Column(String(32), nullable=False)
    dataset_dir = Column(String(4096), nullable=True)
    dataset_archive = Column(String(4096), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_plus_8())


class SqlLocalTrainTask(Base):
    __tablename__ = 'local_train_task'

    id = Column(String(32), primary_key=True)
    remote_state_sofar = Column(Integer, nullable=False)
    secret_key = Column(String(32), nullable=False)
    project_id = Column(String(32), nullable=False)
    hpo_id = Column(String(8), nullable=True)
    hpo_final_metric = Column(Float, nullable=True)

    def __repr__(self):
        return '<SqlLocalTrainTask %r %r>' % (self.id, self.remote_state_sofar)


class SqlTrainProfile(Base):
    __tablename__ = 'local_train_profile'

    id = Column(String(32), primary_key=True)
    train_task_id = Column(String(32), ForeignKey('local_train_task.id', ondelete="SET NULL"))
    train_task = relationship('SqlLocalTrainTask', backref=backref('train_profile', lazy="joined"), lazy="joined")
    algorithm_id = Column(String(32), nullable=False)
    algorithm_dir = Column(String(4096), nullable=True)
    algorithm_archive = Column(String(4096), nullable=True)
    dataset_id = Column(String(32), nullable=True)
    dataset_dir = Column(String(4096), nullable=True)
    dataset_archive = Column(String(4096), nullable=True)
    entrypoint = Column(String(4096), nullable=True)
    train_params = Column(String(4096), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_plus_8())

    def __repr__(self):
        return '<SqlTrainProfile %r %r>' % (self.id, self.train_task_id)
