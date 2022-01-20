# from daybook.service_layer.services import (
#     create_reading_log,
#     select_reading_log_by_reader,
# )
from daybook.service_layer.unit_of_work import AbstractUnitOfWork
from daybook.adapters.repository import FakeRepository

# from .config import TEST_READER_1, TEST_READER_2


class FakeUnitOrWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.reading_logs = FakeRepository()

    def __enter__(self) -> None:
        self.committed = False
        super().__init__()

    def _commit(self):
        self.committed = True

    def _rollback(self):
        pass


class TestServices:
    def test_create_reading_log(self):
        # uow = FakeUnitOrWork()
        # create_reading_log(TEST_READER_1, uow)
        # assert uow.reading_logs.get(TEST_READER_1)
        pass

    def test_select_reading_log_by_reader(self):
        # uow = FakeUnitOrWork()
        # create_reading_log(TEST_READER_1, uow)
        # create_reading_log(TEST_READER_2, uow)
        # actual_1 = select_reading_log_by_reader(TEST_READER_1, uow)
        # assert TEST_READER_1 == actual_1.reader
        # actual_2 = select_reading_log_by_reader(TEST_READER_2, uow)
        # assert TEST_READER_2 == actual_2.reader
        pass
