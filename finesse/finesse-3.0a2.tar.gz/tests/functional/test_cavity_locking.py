"""Tests for locking a Fabry-Perot cavity by applying feedback signal to ITM detuning when \
scanning ETM detuning."""

import pytest
import finesse
from finesse.analysis.actions import RunLocks, Sweep

finesse.plotting.init()


@pytest.fixture(scope="module")
def fabry_perot_with_length_lock():
    """Fabry-Perot model and analysis results."""
    kat = finesse.Model()
    kat.parse(
        """
        l L0 P=1
        s s0 L0.p1 EOM1.p1
        mod EOM1 f=100M midx=0.1 order=1 mod_type=pm
        s s1 EOM1.p2 ITM.p1

        m ITM R=0.99 T=0.01
        s sCAV ITM.p2 ETM.p1 L=1
        m ETM R=1 T=0 phi=0

        pd1 REFL_I ITM.p2.o &EOM1.f 0

        lock lock_length REFL_I ETM.phi -1 1e-5

        #xaxis ETM.phi lin -1 1 100
        """
    )
    return kat

def test_xaxis_lock(fabry_perot_with_length_lock):
    kat = fabry_perot_with_length_lock.deepcopy()
    kat.parse("xaxis(ETM.phi, lin, -1, 1, 100, pre_step=run_locks())")
    sol = kat.run()
    # Check error signal is kept within accuracy limits
    assert all(sol[kat.lock_length.error_signal.name] <= kat.lock_length.accuracy)

def test_pre_step_action(fabry_perot_with_length_lock):
    kat = fabry_perot_with_length_lock.deepcopy()
    lock = RunLocks(kat.lock_length)
    step = Sweep("ITM.phi", (0.0, 1.0, 2.0), False, pre_step=lock)
    kat.run(step)
    # If lock works then ETM phi tracks ITM phi
    assert abs(kat.ITM.phi - kat.ETM.phi) <= kat.lock_length.accuracy

def test_lock_action(fabry_perot_with_length_lock):
    """Checks lock fixes initial offset and lock running in serial.
    Mirror should be brought back to the zero position"""
    kat = fabry_perot_with_length_lock.deepcopy()
    kat.ETM.phi = 0.1
    kat.lock_length.accuracy = 1e-15
    lock = RunLocks(kat.lock_length)
    kat.run(lock)
    assert abs(kat.ETM.phi.value) <= kat.lock_length.accuracy * 10


@pytest.fixture(scope="module")
def lock_action_parsed():
    kat = finesse.Model()
    kat.parse(
        """
        l L0 P=1
        s s0 L0.p1 EOM1.p1
        mod EOM1 f=100M midx=0.1 order=1 mod_type=pm
        s s1 EOM1.p2 ITM.p1

        m ITM R=0.99 T=0.01
        s sCAV ITM.p2 ETM.p1 L=1
        m ETM R=1 T=0 phi=0.1

        pd1 REFL_I ITM.p2.o &EOM1.f 0

        lock lock_length REFL_I ETM.phi -1 1e-15

        run_locks(lock_length)
        """
    )
    return kat

def test_lock_action_parsed(lock_action_parsed):
    lock_action_parsed.run()
    assert (
        abs(lock_action_parsed.ETM.phi.value)
        <= lock_action_parsed.lock_length.accuracy * 10
    )
