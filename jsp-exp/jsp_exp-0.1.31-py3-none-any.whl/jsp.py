import dataclasses
from typing import Any, List, Optional

from .job import Job


@dataclasses.dataclass
class JSP(object):
    jobs: Optional[List[Job]] = None

    def __iter__(self):
        self.__i = 0
        return self

    def __getitem__(self, idx: int):
        return self.jobs[idx]

    def __next__(self):
        if self.__i == len(self):
            raise StopIteration
        job = self.jobs[self.__i]
        self.__i += 1
        return job

    def __len__(self):
        return len(self.jobs)

    def append(self, job: Job) -> None:
        if self.jobs is None:
            self.jobs = [job]
        else:
            self.jobs.append(job)
