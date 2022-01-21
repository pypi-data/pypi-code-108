from anylearn.storage.db.db import DB
from anylearn.storage.db.models import SqlLocalTrainTask
from anylearn.interfaces.train_task import TrainTask
from tests.base_test_case import BaseTestCase


class TestDB(BaseTestCase):

    def create_train_task(self):
        db = DB()
        train_task0 = TrainTask(id="TRAI000", project_id="pro000",
                                state=0, secret_key="000sk")
        train_task1 = TrainTask(id="TRAI001", project_id="pro111",
                                state=1, secret_key="111sk")
        train_task2 = TrainTask(id="TRAI002", project_id="pro222",
                                state=2, secret_key="222sk")
        db.create_or_update_train_task(train_task=train_task0)
        db.create_or_update_train_task(train_task=train_task1)
        db.create_or_update_train_task(train_task=train_task2)

    def test_train_task_resume(self):
        self.create_train_task()

        train_task_lsit = DB().get_unfinished_train_tasks()
        if len(train_task_lsit):
            self.assertIsInstance(train_task_lsit[0], SqlLocalTrainTask)
            self.assertEqual((train_task_lsit[0]).id, "TRAI000")
            self.assertEqual(train_task_lsit[0].remote_state_sofar, 0)
