from __future__ import annotations

__all__ = [
    "constant",
    "mass_action_1",
    "mass_action_2",
    "mass_action_3",
    "mass_action_4",
    "mass_action_variable",
    "reversible_mass_action_1_1",
    "reversible_mass_action_2_1",
    "reversible_mass_action_3_1",
    "reversible_mass_action_4_1",
    "reversible_mass_action_1_2",
    "reversible_mass_action_2_2",
    "reversible_mass_action_3_2",
    "reversible_mass_action_4_2",
    "reversible_mass_action_1_3",
    "reversible_mass_action_2_3",
    "reversible_mass_action_3_3",
    "reversible_mass_action_4_3",
    "reversible_mass_action_1_4",
    "reversible_mass_action_2_4",
    "reversible_mass_action_3_4",
    "reversible_mass_action_4_4",
    "reversible_mass_action_variable_1",
    "reversible_mass_action_variable_2",
    "reversible_mass_action_variable_3",
    "reversible_mass_action_variable_4",
    "reversible_mass_action_variable_5",
    "reversible_mass_action_variable_6",
    "reversible_mass_action_variable_7",
    "reversible_mass_action_variable_8",
    "michaelis_menten",
    "competitive_inhibition",
    "competitive_activation",
    "uncompetitive_inhibition",
    "uncompetitive_activation",
    "noncompetitive_inhibition",
    "noncompetitive_activation",
    "mixed_inhibition",
    "mixed_activation",
    "reversible_michaelis_menten",
    "reversible_uncompetitive_inhibition",
    "reversible_noncompetitive_inhibition",
    "reversible_michaelis_menten_keq",
    "reversible_uncompetitive_inhibition_keq",
    "reversible_noncompetitive_inhibition_keq",
    "ordered_2",
    "ordered_2_2",
    "random_order_2",
    "random_order_2_2",
    "ping_pong_2",
    "ping_pong_3",
    "ping_pong_4",
    "hill",
]


from functools import reduce
from operator import mul


def constant(k: float) -> float:
    return k


###############################################################################
# Mass Action
###############################################################################


def mass_action_1(S1: float, k_fwd: float) -> float:
    return k_fwd * S1


def mass_action_2(S1: float, S2: float, k_fwd: float) -> float:
    return k_fwd * S1 * S2


def mass_action_3(S1: float, S2: float, S3: float, k_fwd: float) -> float:
    return k_fwd * S1 * S2 * S3


def mass_action_4(S1: float, S2: float, S3: float, S4: float, k_fwd: float) -> float:
    return k_fwd * S1 * S2 * S3 * S4


def mass_action_variable(*args: float) -> float:
    return reduce(mul, args, 1)


###############################################################################
# Reversible Mass Action
###############################################################################


def reversible_mass_action_1_1(
    S1: float,
    P1: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 - k_bwd * P1


def reversible_mass_action_2_1(
    S1: float,
    S2: float,
    P1: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 - k_bwd * P1


def reversible_mass_action_3_1(
    S1: float,
    S2: float,
    S3: float,
    P1: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 * S3 - k_bwd * P1


def reversible_mass_action_4_1(
    S1: float,
    S2: float,
    S3: float,
    S4: float,
    P1: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 * S3 * S4 - k_bwd * P1


def reversible_mass_action_1_2(
    S1: float,
    P1: float,
    P2: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 - k_bwd * P1 * P2


def reversible_mass_action_2_2(
    S1: float,
    S2: float,
    P1: float,
    P2: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 - k_bwd * P1 * P2


def reversible_mass_action_3_2(
    S1: float,
    S2: float,
    S3: float,
    P1: float,
    P2: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 * S3 - k_bwd * P1 * P2


def reversible_mass_action_4_2(
    S1: float,
    S2: float,
    S3: float,
    S4: float,
    P1: float,
    P2: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 * S3 * S4 - k_bwd * P1 * P2


def reversible_mass_action_1_3(
    S1: float,
    P1: float,
    P2: float,
    P3: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 - k_bwd * P1 * P2 * P3


def reversible_mass_action_2_3(
    S1: float,
    S2: float,
    P1: float,
    P2: float,
    P3: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 - k_bwd * P1 * P2 * P3


def reversible_mass_action_3_3(
    S1: float,
    S2: float,
    S3: float,
    P1: float,
    P2: float,
    P3: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 * S3 - k_bwd * P1 * P2 * P3


def reversible_mass_action_4_3(
    S1: float,
    S2: float,
    S3: float,
    S4: float,
    P1: float,
    P2: float,
    P3: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 * S3 * S4 - k_bwd * P1 * P2 * P3


def reversible_mass_action_1_4(
    S1: float,
    P1: float,
    P2: float,
    P3: float,
    P4: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 - k_bwd * P1 * P2 * P3 * P4


def reversible_mass_action_2_4(
    S1: float,
    S2: float,
    P1: float,
    P2: float,
    P3: float,
    P4: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 - k_bwd * P1 * P2 * P3 * P4


def reversible_mass_action_3_4(
    S1: float,
    S2: float,
    S3: float,
    P1: float,
    P2: float,
    P3: float,
    P4: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 * S3 - k_bwd * P1 * P2 * P3 * P4


def reversible_mass_action_4_4(
    S1: float,
    S2: float,
    S3: float,
    S4: float,
    P1: float,
    P2: float,
    P3: float,
    P4: float,
    k_fwd: float,
    k_bwd: float,
) -> float:
    return k_fwd * S1 * S2 * S3 * S4 - k_bwd * P1 * P2 * P3 * P4


def reversible_mass_action_variable_1(*args: float) -> float:
    *metabolites, k_fwd, k_bwd = args
    substrates = metabolites[:1]
    products = metabolites[1:]
    return k_fwd * reduce(mul, substrates, 1) - k_bwd * reduce(mul, products, 1)


def reversible_mass_action_variable_2(*args: float) -> float:
    *metabolites, k_fwd, k_bwd = args
    substrates = metabolites[:2]
    products = metabolites[2:]
    return k_fwd * reduce(mul, substrates, 1) - k_bwd * reduce(mul, products, 1)


def reversible_mass_action_variable_3(*args: float) -> float:
    *metabolites, k_fwd, k_bwd = args
    substrates = metabolites[:3]
    products = metabolites[3:]
    return k_fwd * reduce(mul, substrates, 1) - k_bwd * reduce(mul, products, 1)


def reversible_mass_action_variable_4(*args: float) -> float:
    *metabolites, k_fwd, k_bwd = args
    substrates = metabolites[:4]
    products = metabolites[4:]
    return k_fwd * reduce(mul, substrates, 1) - k_bwd * reduce(mul, products, 1)


def reversible_mass_action_variable_5(*args: float) -> float:
    *metabolites, k_fwd, k_bwd = args
    substrates = metabolites[:5]
    products = metabolites[5:]
    return k_fwd * reduce(mul, substrates, 1) - k_bwd * reduce(mul, products, 1)


def reversible_mass_action_variable_6(*args: float) -> float:
    *metabolites, k_fwd, k_bwd = args
    substrates = metabolites[:6]
    products = metabolites[6:]
    return k_fwd * reduce(mul, substrates, 1) - k_bwd * reduce(mul, products, 1)


def reversible_mass_action_variable_7(*args: float) -> float:
    *metabolites, k_fwd, k_bwd = args
    substrates = metabolites[:7]
    products = metabolites[7:]
    return k_fwd * reduce(mul, substrates, 1) - k_bwd * reduce(mul, products, 1)


def reversible_mass_action_variable_8(*args: float) -> float:
    *metabolites, k_fwd, k_bwd = args
    substrates = metabolites[:8]
    products = metabolites[8:]
    return k_fwd * reduce(mul, substrates, 1) - k_bwd * reduce(mul, products, 1)


###############################################################################
# Michaelis Menten
###############################################################################


def michaelis_menten(S: float, vmax: float, km: float) -> float:
    return S * vmax / (S + km)


def competitive_inhibition(S: float, I: float, vmax: float, km: float, ki: float) -> float:
    return vmax * S / (S + km * (1 + I / ki))


def competitive_activation(S: float, A: float, vmax: float, km: float, ka: float) -> float:
    return vmax * S / (S + km * (1 + ka / A))


def uncompetitive_inhibition(S: float, I: float, vmax: float, km: float, ki: float) -> float:
    return vmax * S / (S * (1 + I / ki) + km)


def uncompetitive_activation(S: float, A: float, vmax: float, km: float, ka: float) -> float:
    return vmax * S / (S * (1 + ka / A) + km)


def noncompetitive_inhibition(S: float, I: float, vmax: float, km: float, ki: float) -> float:
    return vmax * S / ((S + km) * (1 + I / ki))


def noncompetitive_activation(S: float, A: float, vmax: float, km: float, ka: float) -> float:
    return vmax * S / ((S + km) * (1 + ka / A))


def mixed_inhibition(S: float, I: float, vmax: float, km: float, ki: float) -> float:
    return vmax * S / (S * (1 + I / ki) + km * (1 + I / ki))


def mixed_activation(S: float, A: float, vmax: float, km: float, ka: float) -> float:
    return vmax * S / (S * (1 + ka / A) + km * (1 + ka / A))


###############################################################################
# Reversible Michaelis-Menten
###############################################################################


def reversible_michaelis_menten(
    S: float,
    P: float,
    vmax_fwd: float,
    vmax_bwd: float,
    kms: float,
    kmp: float,
) -> float:
    return (vmax_fwd * S / kms - vmax_bwd * P / kmp) / (1 + S / kms + P / kmp)


def reversible_uncompetitive_inhibition(
    S: float,
    P: float,
    I: float,
    vmax_fwd: float,
    vmax_bwd: float,
    kms: float,
    kmp: float,
    ki: float,
) -> float:
    return (vmax_fwd * S / kms - vmax_bwd * P / kmp) / (1 + (S / kms) + (P / kmp) * (1 + I / ki))


def reversible_noncompetitive_inhibition(
    S: float,
    P: float,
    I: float,
    vmax_fwd: float,
    vmax_bwd: float,
    kms: float,
    kmp: float,
    ki: float,
) -> float:
    return (vmax_fwd * S / kms - vmax_bwd * P / kmp) / ((1 + S / kms + P / kmp) * (1 + I / ki))


def reversible_michaelis_menten_keq(
    S: float,
    P: float,
    vmax_fwd: float,
    kms: float,
    kmp: float,
    keq: float,
) -> float:
    return vmax_fwd / kms * (S - P / keq) / (1 + S / kms + P / kmp)


def reversible_uncompetitive_inhibition_keq(
    S: float,
    P: float,
    I: float,
    vmax_fwd: float,
    kms: float,
    kmp: float,
    ki: float,
    keq: float,
) -> float:
    return vmax_fwd / kms * (S - P / keq) / (1 + (S / kms) + (P / kmp) * (1 + I / ki))


def reversible_noncompetitive_inhibition_keq(
    S: float,
    P: float,
    I: float,
    vmax_fwd: float,
    kms: float,
    kmp: float,
    ki: float,
    keq: float,
) -> float:
    return vmax_fwd / kms * (S - P / keq) / ((1 + S / kms + P / kmp) * (1 + I / ki))


###############################################################################
# Multi-substrate
###############################################################################


def ordered_2(
    A: float,
    B: float,
    vmax: float,
    kmA: float,
    kmB: float,
    kiA: float,
) -> float:
    return vmax * A * B / (A * B + kmB * A + kmA * B + kiA * kmB)


def ordered_2_2(
    A: float,
    B: float,
    P: float,
    Q: float,
    vmaxf: float,
    vmaxr: float,
    kmA: float,
    kmB: float,
    kmP: float,
    kmQ: float,
    kiA: float,
    kiB: float,
    kiP: float,
    kiQ: float,
) -> float:
    nominator = vmaxf * A * B / (kiA * kmB) - vmaxr * P * Q / (kmP * kiQ)
    denominator = (
        1
        + (A / kiA)
        + (kmA * B / (kiA * kmB))
        + (kmQ * P / (kmP * kiQ))
        + (Q / kiQ)
        + (A * B / (kiA * kmB))
        + (kmQ * A * P / (kiA * kmP * kiQ))
        + (kmA * B * Q / (kiA * kmB * kiQ))
        + (P * Q / (kmP * kiQ))
        + (A * B * P / (kiA * kmB * kiP))
        + (B * P * Q) / (kiB * kmP * kiQ)
    )
    return nominator / denominator


def random_order_2(
    A: float,
    B: float,
    vmax: float,
    kmA: float,
    kmB: float,
    kiA: float,
) -> float:
    return vmax * A * B / (A * B + kmB * A + kmA * B + kiA * kmB)


def random_order_2_2(
    A: float,
    B: float,
    P: float,
    Q: float,
    vmaxf: float,
    vmaxr: float,
    kmB: float,
    kmP: float,
    kiA: float,
    kiB: float,
    kiP: float,
    kiQ: float,
) -> float:
    nominator = vmaxf * A * B / (kiA * kmB) - vmaxr * P * Q / (kmP * kiQ)
    denominator = (
        1 + (A / kiA) + (B / kiB) + (P / kiP) + (Q / kiQ) + (A * B / (kiA * kmB)) + (P * Q / (kmP * kiQ))
    )
    return nominator / denominator


def ping_pong_2(
    A: float,
    B: float,
    vmax: float,
    kmA: float,
    kmB: float,
) -> float:
    return vmax * A * B / (A * B + kmA * B + kmB * A)


def ping_pong_3(
    A: float,
    B: float,
    C: float,
    vmax: float,
    kmA: float,
    kmB: float,
    kmC: float,
) -> float:
    return (vmax * A * B * C) / (A * B * C + (kmA * B * C) + (kmB * A * C) + (kmC * A * B))


def ping_pong_4(
    A: float,
    B: float,
    C: float,
    D: float,
    vmax: float,
    kmA: float,
    kmB: float,
    kmC: float,
    kmD: float,
) -> float:
    return (vmax * A * B * C * D) / (
        A * B * C * D + (kmA * B * C * D) + (kmB * A * C * D) + (kmC * A * B * D) + (kmD * A * B * C)
    )


###############################################################################
# Cooperativity
###############################################################################


def hill(S: float, vmax: float, kd: float, n: float) -> float:
    return vmax * S ** n / (kd + S ** n)


###############################################################################
# Generalised
###############################################################################

# def hanekom()-> float:
#     pass

# def convenience()-> float:
#     pass
