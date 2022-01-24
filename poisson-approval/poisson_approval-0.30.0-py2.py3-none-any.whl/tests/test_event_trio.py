from poisson_approval import TauVector, EventTrio


def test():
    tau = TauVector({
        'a': 1 - 11e-9,
        'ab': 7e-09,
        'ac': 1e-09,
        'b': 2e-09,
        'bc': 1e-09,
        'c': 0
    })
    assert tau.trio.phi_a <= 1
    assert tau.trio.phi_b <= 1
    assert tau.trio.psi_c >= 1
    _ = tau.pivot_weak_ac
    _ = tau.d_ranking_best_response['acb']
