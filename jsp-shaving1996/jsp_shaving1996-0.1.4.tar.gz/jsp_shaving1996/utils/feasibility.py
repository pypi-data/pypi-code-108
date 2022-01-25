from jsp_exp import Job
from jsp_shaving1990 import iterated_full_shaving


def has_schedule(job: Job, UB: int) -> bool:
    result_list, _, _ = iterated_full_shaving(job.attrtolist('r'), job.attrtolist('p'), job.attrtolist('q'), UB)
    return True if result_list else False
