import finesse
import numpy as np
from finesse.analysis.actions import Action, RunLocks, OptimiseRFReadoutPhaseDC


def make_aligo(RF_AS_readout=False, verbose=False):
    base = finesse.Model()
    base.parse(aligo_katscript)
    base.run(
        OptimiseRFReadoutPhaseDC(
            "CARM",
            "REFL9",
            "PRCL",
            "POP9",
            "SRCL",
            "POP45",
            "DARM",
            "AS45",
        )
    )

    set_lock_gains(base, verbose=verbose)

    if not RF_AS_readout:
        base.run(DARM_RF_to_DC())

    return base


class DARM_RF_to_DC(Action):
    """Locks a model using DARM RF readout then transitions the model into using a DC
    readout and locks."""

    def __init__(self, name="DarmRF2DC"):
        super().__init__(name)
        self.__lock_rf = RunLocks("DARM_rf_lock")
        self.__lock_dc = RunLocks("DARM_dc_lock")

    def _do(self, state):
        self.__lock_rf._do(state)
        state.model.DARM_rf_lock.disabled = True
        # kick lock away from zero tuning for DC lock to grab with
        state.model.DARM.DC += 0.5e-3
        # take a guess at the gain
        state.model.DARM_dc_lock.gain = -0.01
        state.model.DARM_dc_lock.disabled = False
        self.__lock_dc._do(state)
        return None

    def _requests(self, model, memo, first=True):
        self.__lock_rf._requests(model, memo)
        self.__lock_dc._requests(model, memo)
        return memo


class DRFPMI_state(Action):
    """Assumes a mode has a PRM, SRM, ITMX, ETMX, ITMY, and ETMY mirror elements in.
    This action will change the alignment state of these. The options are:

    'PRMI', 'SRMI', 'MI', 'FPMI', 'PRFPMI', 'SRFPMI', 'DRFPMI', 'XARM', 'YARM'

    This action will change the state of the model.
    """

    def __init__(self, state: str, name="drfpmi_state"):
        super().__init__(name)
        states = (
            "PRMI",
            "SRMI",
            "MI",
            "FPMI",
            "PRFPMI",
            "SRFPMI",
            "DRFPMI",
            "XARM",
            "YARM",
        )
        if state not in states:
            raise ValueError(f"State '{state}' is not a valid option: {states}")
        self.state = state

    def _do(self, state):
        if self.state == "PRMI":
            state.model.PRM.misaligned = 0
            state.model.SRM.misaligned = 1
            state.model.ETMX.misaligned = 1
            state.model.ITMX.misaligned = 0
            state.model.ETMY.misaligned = 1
            state.model.ITMY.misaligned = 0
        elif self.state == "SRMI":
            state.model.PRM.misaligned = 1
            state.model.SRM.misaligned = 0
            state.model.ETMX.misaligned = 1
            state.model.ITMX.misaligned = 0
            state.model.ETMY.misaligned = 1
            state.model.ITMY.misaligned = 0
        elif self.state == "MI":
            state.model.PRM.misaligned = 1
            state.model.SRM.misaligned = 1
            state.model.ETMX.misaligned = 1
            state.model.ITMX.misaligned = 0
            state.model.ETMY.misaligned = 1
            state.model.ITMY.misaligned = 0
        elif self.state == "FPMI":
            state.model.PRM.misaligned = 1
            state.model.SRM.misaligned = 1
            state.model.ETMX.misaligned = 0
            state.model.ITMX.misaligned = 0
            state.model.ETMY.misaligned = 0
            state.model.ITMY.misaligned = 0
        elif self.state == "PRFPMI":
            state.model.PRM.misaligned = 0
            state.model.SRM.misaligned = 1
            state.model.ETMX.misaligned = 0
            state.model.ITMX.misaligned = 0
            state.model.ETMY.misaligned = 0
            state.model.ITMY.misaligned = 0
        elif self.state == "SRFPMI":
            state.model.PRM.misaligned = 1
            state.model.SRM.misaligned = 0
            state.model.ETMX.misaligned = 0
            state.model.ITMX.misaligned = 0
            state.model.ETMY.misaligned = 0
            state.model.ITMY.misaligned = 0
        elif self.state == "DRFPMI":
            state.model.PRM.misaligned = 0
            state.model.SRM.misaligned = 0
            state.model.ETMX.misaligned = 0
            state.model.ITMX.misaligned = 0
            state.model.ETMY.misaligned = 0
            state.model.ITMY.misaligned = 0
        elif self.state == "YARM":
            state.model.PRM.misaligned = 1
            state.model.SRM.misaligned = 1
            state.model.ETMX.misaligned = 1
            state.model.ITMX.misaligned = 1
            state.model.ETMY.misaligned = 0
            state.model.ITMY.misaligned = 0
        elif self.state == "XARM":
            state.model.PRM.misaligned = 1
            state.model.SRM.misaligned = 1
            state.model.ETMX.misaligned = 0
            state.model.ITMX.misaligned = 0
            state.model.ETMY.misaligned = 1
            state.model.ITMY.misaligned = 1
        else:
            raise Exception(f"{self.state} not implemented")

    def _requests(self, model, memo, first=True):
        # changing the mirror misaligned parameter is essentially
        # changing the mirror reflectivity model parameter
        memo["changing_parameters"].extend(
            (
                "PRM.misaligned",
                "SRM.misaligned",
                "ETMX.misaligned",
                "ITMX.misaligned",
                "ETMY.misaligned",
                "ITMY.misaligned",
            )
        )
        return memo


def set_lock_gains(model, d_dof=1e-6, gain_scale=1, verbose=False):
    """For the current state of the model each lock will have its gain computed. This is
    done by computing the gradient of the error signal with respect to the set feedback.

    The optical gain is then computed as -1/(slope).

    This function alters the state of the provided model.

    Parameters
    ----------
    model : Model
        Model to set the lock gains of
    d_dof : double
        step size for computing the slope of the error signals
    verbose : boolean
        Prints information when true
    """
    from finesse.analysis.actions import Xaxis, Series
    from finesse.components.readout import ReadoutDetectorOutput

    for lock in model.locks:
        # Make sure readouts being used have their outputs enabled
        if type(lock.error_signal) is ReadoutDetectorOutput:
            lock.error_signal.readout.output_detectors = True

    # Use a flattened series analysis as it only creates one model
    # and xaxis resets all the parameters each time
    analysis = Series(
        *(
            Xaxis(lock.feedback, "lin", -d_dof, d_dof, 1, relative=True, name=lock.name)
            for lock in model.locks
        ),
        flatten=True,
    )
    sol = model.run(analysis)

    for lock in model.locks:
        lock_sol = sol[lock.name]
        x = lock_sol.x1
        error = lock_sol[lock.error_signal.name] + lock.offset
        grad = np.gradient(error, x[1] - x[0]).mean()
        if grad == 0:
            lock.gain = np.NaN
        else:
            lock.gain = -1 / grad * gain_scale

        if verbose:
            print(lock, lock.error_signal.name, lock.gain)


def get_lock_error_signals(model, dof_range, steps=1000, verbose=False):
    from finesse.analysis.actions import Xaxis, Series
    from finesse.components.readout import ReadoutDetectorOutput

    for lock in model.locks:
        # Make sure readouts being used have their outputs enabled
        if type(lock.error_signal) is ReadoutDetectorOutput:
            lock.error_signal.readout.output_detectors = True

    # Use a flattened series analysis as it only creates one model
    # and xaxis resets all the parameters each time
    analysis = Series(
        *(
            Xaxis(
                lock.feedback,
                "lin",
                -dof_range,
                dof_range,
                steps,
                relative=True,
                name=lock.feedback.owner.name,
            )
            for lock in model.locks
        ),
        flatten=True,
    )
    sol = model.run(analysis)
    return sol


aligo_katscript = """
# modulators for core interferometer sensing - Advanced LIGO, CQG, 2015
# http://iopscience.iop.org/article/10.1088/0264-9381/32/7/074001/meta#cqg507871s4-8
# 9MHz (CARM, PRC, SRC loops)
variable f1 9099471
variable f2 5*&f1
variable nsilica 1.45
variable Mloss 30u
###############################################################################
###   length definitions
###############################################################################
variable Larm 3994
variable LPR23 16.164  # distance between PR2 and PR3
variable LSR23 15.443  # distance between SR2 and SR3
variable LPR3BS 19.538 # distance between PR3 and BS
variable LSR3BS 19.366 # distance between SR3 and BS
variable lmich 5.342   # average length of MICH
variable lschnupp 0.08
variable lPRC (3+0.5)*c0/(2*&f1) # T1000298 Eq2.1, N=3
variable lSRC (17)*c0/(2*&f2) # T1000298 Eq2.2, M=3
###############################################################################
###   laser
###############################################################################
laser L0 P=125
mod mod1 f=&f1 midx=0.18 order=1 mod_type=pm
mod mod2 f=&f2 midx=0.18 order=1 mod_type=pm
link(L0, mod1, mod2)
###############################################################################
###   PRC
###############################################################################
s sPRCin mod2.p2 PRMAR.p1
m PRMAR R=0 L=40u xbeta=&PRM.xbeta ybeta=&PRM.ybeta phi=&PRM.phi
s sPRMsub1 PRMAR.p2 PRM.p1 L=0.0737 nr=&nsilica
m PRM T=0.03 L=8.5u Rc=11.009
s lp1 PRM.p2 PR2.p1 L=&lPRC-&LPR3BS-&LPR23-&lmich
bs PR2 T=250u L=&Mloss alpha=-0.79 Rc=-4.545
s lp2 PR2.p2 PR3.p1 L=&LPR23
bs PR3 T=0 L=&Mloss alpha=0.615 Rc=36.027
s lp3 PR3.p2 BS.p1 L=&LPR3BS
###############################################################################
###   BS
###############################################################################
bs BS R=0.5 L=&Mloss alpha=45
s BSsub1 BS.p3 BSAR1.p1 L=0.0687 nr=&nsilica
s BSsub2 BS.p4 BSAR2.p2 L=0.0687 nr=&nsilica
bs BSAR1 L=50u R=0 alpha=-29.195
bs BSAR2 L=50u R=0 alpha=29.195
###############################################################################
###   Yarm
###############################################################################
# Distance from beam splitter to Y arm input mirror
s ly1 BS.p2 ITMYlens.p1 L=&lmich-&lschnupp/2-&ITMYsub.L*&ITMXsub.nr
lens ITMYlens f=34500
s ly2 ITMYlens.p2 ITMYAR.p1
m ITMYAR R=0 L=20u xbeta=&ITMY.xbeta ybeta=&ITMY.ybeta phi=&ITMY.phi
s ITMYsub ITMYAR.p2 ITMY.p1 L=0.2 nr=&nsilica
m ITMY T=0.014 L=&Mloss Rc=-1934
s LY ITMY.p2 ETMY.p1 L=&Larm
m ETMY T=5u L=&Mloss Rc=2245
s ETMYsub ETMY.p2 ETMYAR.p1 L=0.2 nr=&nsilica
m ETMYAR 0 500u xbeta=&ETMY.xbeta ybeta=&ETMY.ybeta phi=&ETMY.phi
cav cavYARM ETMY.p1.o
###############################################################################
###   Xarm
###############################################################################
# Distance from beam splitter to X arm input mirror
s lx1 BSAR1.p3 ITMXlens.p1 L=&lmich+&lschnupp/2-&ITMXsub.L*&ITMXsub.nr-&BSsub1.L*&BSsub1.nr
lens ITMXlens f=34500
s lx2 ITMXlens.p2 ITMXAR.p1
m ITMXAR R=0 L=20u xbeta=&ITMX.xbeta ybeta=&ITMX.ybeta phi=&ITMX.phi
s ITMXsub ITMXAR.p2 ITMX.p1 L=0.2 nr=&nsilica
m ITMX T=0.014 L=&Mloss Rc=-1934
s LX ITMX.p2 ETMX.p1 L=&Larm
m ETMX T=5u L=&Mloss Rc=2245
s ETMXsub ETMX.p2 ETMXAR.p1 L=0.2 nr=&nsilica
m ETMXAR 0 500u xbeta=&ETMX.xbeta ybeta=&ETMX.ybeta phi=&ETMX.phi
cav cavXARM ETMX.p1.o
###############################################################################
###   SRC
###############################################################################
s ls3 BSAR2.p4 SR3.p1 L=&LSR3BS
bs SR3 T=0 L=&Mloss alpha=0.785 Rc=35.972841
s ls2 SR3.p2 SR2.p1 L=&LSR23
bs SR2 T=0 L=&Mloss alpha=-0.87 Rc=-6.406
s ls1 SR2.p2 SRM.p1 L=&lSRC-&LSR3BS-&LSR23-&BSsub2.L*&BSsub2.nr-&lmich
m SRM T=0.2 L=8.7u Rc=-5.6938
s SRMsub SRM.p2 SRMAR.p1 L=0.0749 nr=&nsilica
m SRMAR R=0 L=50n
###############################################################################
###   OMC
###############################################################################
# Here we just use some simple filter to approximate an OMC for filtering
# out RF fields, this doesn't filter HOMs!
dbs OFI
sq sqz db=6 angle=90.0
obp OMC fc=0 bandwidth=1M filter_hom=[0,0]
link(sqz, OFI.p2)
link(SRMAR.p2, OFI.p1)
link(OFI.p3, OMC)

    ###############################################################################
### Length sensing and control
###############################################################################
dof XARM ETMX.dofs.z
dof YARM ETMY.dofs.z
dof CARM ETMX.dofs.z +1 ETMY.dofs.z +1
dof DARM ETMX.dofs.z +1 ETMY.dofs.z -1
dof PRCL PRM.dofs.z +1
dof SRCL SRM.dofs.z +1 DC=90
dof MICH BS.dofs.z +1
dof MICH2 ITMY.dofs.z +1 ETMY.dofs.z +1 ITMX.dofs.z -1 ETMX.dofs.z -1
dof STRAIN LX.dofs.h +1 LY.dofs.h -1
dof FRQ L0.dofs.frq
dof RIN L0.dofs.amp

readout_rf REFL9 PRMAR.p1.o f=&f1
readout_rf REFL18 PRMAR.p1.o f=3*&f1
readout_rf REFL45 PRMAR.p1.o f=5*&f1
readout_rf POP9  PR2.p3.o   f=&f1
readout_rf POP45 PR2.p3.o   f=&f2
readout_rf AS45  SRMAR.p2.o f=&f2
readout_dc AS    OMC.p2.o

lock CARM_lock REFL9.outputs.I CARM.DC -0.1 1e-6
lock MICH_lock POP45.outputs.Q MICH.DC -15 1e-6
lock PRCL_lock POP9.outputs.I PRCL.DC 2.8 1e-6
lock SRCL_lock POP45.outputs.I SRCL.DC 42 1e-6
lock DARM_rf_lock AS45.outputs.I DARM.DC -0.003 1e-6
lock DARM_dc_lock AS.outputs.DC DARM.DC -0.003 1e-6 offset=20m disabled=true
###############################################################################
### DC power measurements
###############################################################################
pd Px ETMX.p1.i
pd Py ETMX.p1.i
pd Pprc PRM.p2.o
pd Psrc SRM.p1.i
pd Prefl ETMX.p1.i
pd Pas OMC.p2.o
"""
