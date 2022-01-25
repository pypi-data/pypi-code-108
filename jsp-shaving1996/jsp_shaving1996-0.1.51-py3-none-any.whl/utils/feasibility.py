from jsp_exp import Job
from jsp_shaving1990 import iterated_full_shaving

DEBUG = False


def has_schedule(job: Job, UB: int) -> bool:
    result_list, _, _ = iterated_full_shaving(job.attrtolist('r'), job.attrtolist('p'), job.attrtolist('q'), UB)
    if result_list:
        if DEBUG:
            print('has schedule')
        return True
    else:
        if DEBUG:
            print('no schedule')
        return False
