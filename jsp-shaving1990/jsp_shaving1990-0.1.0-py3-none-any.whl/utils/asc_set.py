from typing import Dict, List, NewType, Tuple

from jsp_exp import Operation

TimeInterval = NewType('TimeInterval', Tuple[int, int])


def calc_Kc_plus(opc: Operation, sorted_ops: List[Operation]) -> List[Operation]:
    # Kc_plusはqの昇順である必要はないが，後で結局昇順で取り出すことになるので，昇順であることを仮定する
    return [op for op in sorted_ops if op.p_plus > 0 and op is not opc]


def find_Kc_ast(opc: Operation, Kc_plus: List[Operation], UB: int) -> List[Operation]:
    sum_p_plus = sum(op.p_plus for op in Kc_plus)

    for j in range(len(Kc_plus)):
        if opc.r + opc.p + sum_p_plus + Kc_plus[j].q > UB:
            return Kc_plus[j:]

        sum_p_plus -= Kc_plus[j].p_plus
    else:  # Kc_astは存在しない
        return list()


def forward_to_rc(schedule: Dict[TimeInterval, Operation], rc: int) -> None:
    # rcまでJackson's Preemptive Scheduleを進める
    while schedule:
        l, r = next(iter(schedule))
        if l == rc:
            break
        schedule[l, r].p_plus -= r - l
        schedule.pop((l, r))


def get_C_ast(Kc_ast: List[Operation]) -> int:
    return max(op.C for op in Kc_ast)
