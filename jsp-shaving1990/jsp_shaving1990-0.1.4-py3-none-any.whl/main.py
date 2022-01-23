import jps_algo
from typing import List, Tuple

from .utils import asc_set
from .utils import sort


def shaving(r_list: List[int], p_list: List[int], q_list: List[int], UB: int) -> List[int]:
    unsorted_ops, schedule, makespan = jps_algo.jackson_preemptive_algorithm(r_list, p_list, q_list)
    sorted_ops_by_r = sort.sort_ops_by('r', unsorted_ops)
    sorted_ops_by_q = sort.sort_ops_by('q', unsorted_ops)
    for opc in sorted_ops_by_r:
        asc_set.forward_to_rc(schedule, rc=opc.r)
        Kc_plus = asc_set.calc_Kc_plus(opc, sorted_ops_by_q)
        Kc_ast = asc_set.find_Kc_ast(opc, Kc_plus, UB=UB)
        C_ast = asc_set.get_C_ast(Kc_ast) if Kc_ast else opc.r
        opc.r = C_ast

    if makespan > UB or any(op.r > UB - op.p - op.q for op in unsorted_ops):
        # この時点でinfeasibleなので空のlistを返すこととする
        return list()
    else:
        return [op.r for op in unsorted_ops]


def adjust_heads(r_list: List[int], p_list: List[int], q_list: List[int], UB: int) -> List[int]:
    return shaving(r_list, p_list, q_list, UB)


def adjust_tails(r_list: List[int], p_list: List[int], q_list: List[int], UB: int) -> List[int]:
    return shaving(q_list, p_list, r_list, UB)


def iterated_shaving(r_list: List[int], p_list: List[int], q_list: List[int], UB: int) -> List[int]:
    pre_r_list, new_r_list = list(), r_list
    while pre_r_list != new_r_list:
        shaved_r_list = shaving(new_r_list, p_list, q_list, UB)
        if not shaved_r_list:
            # これもinfeasibleだったら空のlistを返す
            return list()
        pre_r_list, new_r_list = new_r_list, shaved_r_list
        # for i in range(len(p_list)):
        #     if new_r_list[i] > UB - p_list[i] - q_list[i]:
        #         # 一つでもrの値がUBを超えてしまったらscheduling出来ない
        #         return list()
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
