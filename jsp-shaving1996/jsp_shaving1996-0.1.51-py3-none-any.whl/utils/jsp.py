from jsp_exp import Operation, Job
from typing import List


def create_new_job(r_list: List[int], p_list: List[int], q_list: List[int]) -> Job:
    # NOTE: 想定通りに動いている
    job = Job([
        Operation('M1', f"O_{i}", r, p, q)
        for i, (r, p, q) in enumerate(zip(r_list, p_list, q_list))
    ])
    return job
