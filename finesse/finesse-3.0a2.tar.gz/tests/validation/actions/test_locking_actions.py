import finesse
from finesse.analysis.actions import (
    RunLocks,
    DragLocks,
)
import pytest

finesse.configure(plotting=True)


@pytest.fixture
def locks_model():
    kat = finesse.Model()
    kat.parse(
        """
        l L0 P=1
        s l_mod1 L0.p1 eo1.p1
        mod eo1 10M 0.1

        s s0 eo1.p2 BS.p1
        bs BS R=0.5 T=0.5

        s s1 BS.p2 NI.p1
        m NI R=0.99 T=0.01 Rc=1429 phi=90
        s CAV NI.p2 NE.p1 L=10
        m NE R=0.991 T=0.009 Rc=1430 phi=90

        s s2 BS.p3 EI.p1
        m EI R=0.99 T=0.01 Rc=1429 phi=0
        s CAV2 EI.p2 EE.p1 L=10
        m EE R=0.991 T=0.009 Rc=1430 phi=0

        dof NEz NE.dofs.z +1
        dof EEz EE.dofs.z +1
        dof NIz NI.dofs.z +1

        readout_rf rd_pdh1 NI.p1.o f=10M
        readout_rf rd_pdh2 EI.p1.o f=10M
        readout_rf rd_DF BS.p4.o f=10M

        lock cav1_lock rd_pdh1.outputs.I NEz.DC 1 1e-9
        lock cav2_lock rd_pdh2.outputs.I EEz.DC 1 1e-9
        lock DF_lock rd_DF.outputs.I NIz.DC 1 1e-9

        cav cav1 NI.p2.o
        cav cav2 EI.p2.o
        """
    )
    return kat


def test_run_locks_newton_method(locks_model):
    sol = locks_model.run(RunLocks(method="newton", display_progress=False))
    assert sol.iters < 10


def test_drag_locks_newton_method(locks_model):
    sol = locks_model.run(
        DragLocks(
            method='newton',
            parameters=["BS.xbeta"],
            stop_points=[2e-6],
            display_progress=False,
            relative=True,
        )
    )
    assert sol.iters < 10
