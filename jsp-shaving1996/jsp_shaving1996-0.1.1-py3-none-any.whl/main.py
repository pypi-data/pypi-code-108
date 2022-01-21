from jsp_exp import Job
from typing import List, Optional, Tuple

from .utils import backward
from .utils import forward
from .utils.feasibility import has_schedule
from .utils import jsp


def bsearch(job: Job, UB: int, fw: int, bu: int, bw: int):
    if has_schedule(job, UB):
        # shaving出来る
        return backward.get_next_interval(bw + 1, fw)
    else:
        # shaving出来ない
        return backward.get_next_interval(bu, bw)


def shaving(r_list: List[int], p_list: List[int], q_list: List[int], UB: int):
    def calc_q(p: int, w: int) -> int: return UB - p - w

    job = jsp.create_new_job(r_list, p_list, q_list)
    for op in job.ops:
        # forward
        fu = fw = op.r
        org_q = op.q
        v = calc_q(op.p, org_q)
        while True:
            op.r, op.q = fu, calc_q(op.p, fw)
            if has_schedule(job, UB):
                break
            else:
                tu, tw = forward.get_next_interval(fu, fw)
                if tw > v:
                    break
                else:
                    fu, fw = tu, tw

        # backward
        bu, bw = backward.get_next_interval(fu, fw)
        while bu != bw:
            op.r, op.q = bu, calc_q(op.p, bw)
            bu, bw = bsearch(job, UB, fw, bu, bw)

        op.r = bu if has_schedule(job, UB) else bu + 1
        op.q = org_q
    return job.attrtolist('r')


def adjust_heads(r_list: List[int], p_list: List[int], q_list: List[int], UB: int):
    return shaving(r_list, p_list, q_list, UB)


def adjust_tails(r_list: List[int], p_list: List[int], q_list: List[int], UB: int):
    return shaving(q_list, p_list, r_list, UB)


def iterated_shaving(r_list: List[int], p_list: List[int], q_list: List[int], UB: int) -> Optional[List[int]]:
    pre_r_list, new_r_list = list(), r_list
    while pre_r_list != new_r_list:
        shaved_r_list = shaving(new_r_list, p_list, q_list, UB)
        pre_r_list, new_r_list = new_r_list, shaved_r_list
        for i in range(len(p_list)):
            if new_r_list[i] > UB - p_list[i] - q_list[i]:
                # 一つでもrの値がUBを超えてしまったらscheduling出来ない
                return None
    return new_r_list


def iterated_full_shaving(r_list: List[int], p_list: List[int], q_list: List[int], UB: int) -> Tuple[List[int], List[int], List[int]]:
    pre_r_list, new_r_list, pre_q_list, new_q_list = list(), r_list, list(), q_list
    while pre_r_list != new_r_list or pre_q_list != new_q_list:
        shaved_r_list = iterated_shaving(new_r_list, p_list, new_q_list, UB)
        if shaved_r_list is None:
            return list(), list(), list()
        pre_r_list, new_r_list = new_r_list, shaved_r_list

        shaved_q_list = iterated_shaving(new_q_list, p_list, new_r_list, UB)
        if shaved_q_list is None:
            return list(), list(), list()
        pre_q_list, new_q_list = new_q_list, shaved_q_list
    return new_r_list, p_list, new_q_list
