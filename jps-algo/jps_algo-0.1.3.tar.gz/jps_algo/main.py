from typing import Dict, List, NewType, Tuple

from .utils.operation import Operation, create_operations
from .utils import algo

TimeInterval = NewType('TimeInterval', Tuple[int, int])


def jackson_preemptive_algorithm(r_list: List[int], p_list: List[int], q_list: List[int]) -> Tuple[List[Operation], Dict[TimeInterval, Operation], int]:
    def complete(op: Operation, alpha: List[int], schedule: Dict[TimeInterval, Operation], t: int, makespan: int) -> int:
        Cjk = t + op.p_plus
        op.C, op.p_plus = Cjk, 0
        alpha[k] += 1
        alpha[k] = alpha[k] if alpha[k] < 2 ** k else None
        schedule[(t, Cjk)] = op
        return Cjk, max(Cjk + op.q, makespan)

    def preempt(op: Operation, alpha: List[int], schedule: Dict[TimeInterval, Operation], t: int) -> int:
        next_t = sorted_ops[m].r
        op.p_plus -= next_t - t
        schedule[(t, next_t)] = op
        return next_t

    def get_max_q_from_S(k: int) -> int:
        Sk = S[k]
        max_q_idx = alpha[k]
        max_q_op = Sk[max_q_idx]
        max_q = sorted_ops[max_q_op].q
        return max_q

    unsorted_ops = create_operations(r_list, p_list, q_list)
    sorted_ops = sorted(unsorted_ops, key=lambda op: op.r)
    m, n, t, p = algo.setup_params(sorted_ops)
    alpha, S, schedule = algo.setup_container(p)

    makespan = -1
    while True:
        # Does job m+1 belong to S?
        # belong
        if m < n and sorted_ops[m].r <= t:
            # Insertion of a job in S
            for k in range(n):
                if len(S[k]) == 0:
                    algo.update_S(S, sorted_ops, alpha, k, m)
                    m += 1
                    break

        ## not belong
        else:
            # Selection of job j

            # all jobs in I are scheduled
            if all(op.is_done() for op in unsorted_ops):
                for op in unsorted_ops:
                    op.p_plus = op.p
                return unsorted_ops, schedule, makespan

            # all jobs in S are scheduled
            is_scheduled_for_all_jobs = list()
            for Sk in S:
                for idx in Sk:
                    is_scheduled_for_all_jobs.append(sorted_ops[idx].is_done())
            if all(is_scheduled_for_all_jobs):
                t = sorted_ops[m].r
                continue

            k = max([k for k in range(p + 1) if alpha[k] is not None], key=get_max_q_from_S)
            jk = S[k][alpha[k]]

            op = sorted_ops[jk]
            if m >= n:
                t, makespan = complete(op, alpha, schedule, t, makespan)
            else:
                if t + op.p_plus <= sorted_ops[m].r:
                    t, makespan = complete(op, alpha, schedule, t, makespan)
                else:
                    t = preempt(op, alpha, schedule, t)
