from jsp_exp import Job
from jsp_shaving1990 import iterated_shaving


def has_schedule(job: Job, UB: int) -> bool:
    res = iterated_shaving(job.attrtolist('r'), job.attrtolist('p'), job.attrtolist('q'), UB)
    return res is not None
