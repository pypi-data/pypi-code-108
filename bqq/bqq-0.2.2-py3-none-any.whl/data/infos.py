from typing import List, Optional

from tinydb import Query, TinyDB

from bqq import const
from bqq.types import JobInfo


class Infos:
    def __init__(self) -> None:
        self.InfoQuery = Query()
        self._db = None

    @property
    def db(self):
        if not self._db:
            self._db = TinyDB(const.BQQ_INFOS)
        return self._db

    def clear(self):
        self.db.clear_cache()
        self.db.truncate()

    def find_by_id(self, job_id: str) -> Optional[JobInfo]:
        job_info = None
        try:
            job_info = JobInfo.from_document(self.db.search(self.InfoQuery.job_id == job_id)[0])
        except IndexError:
            job_info = None
        return job_info

    def update_has_result(self, job_id: str, has_result: bool):
        self.db.update({"has_result": has_result}, self.InfoQuery.job_id == job_id)

    def search(self, project: str) -> List[JobInfo]:
        infos = []
        for row in self.db.search(self.InfoQuery.project == project):
            infos.append(JobInfo.from_document(row))
        return infos

    def get_all(self) -> List[JobInfo]:
        all = []
        for row in self.db.all():
            all.append(JobInfo.from_document(row))
        return all

    def insert(self, info: JobInfo):
        self.db.insert(info.mapping)

    def upsert(self, info: JobInfo):
        self.db.upsert(info.mapping, self.InfoQuery.job_id == info.job_id)

    def remove(self, info: JobInfo):
        self.db.remove(self.InfoQuery.job_id == info.job_id)
