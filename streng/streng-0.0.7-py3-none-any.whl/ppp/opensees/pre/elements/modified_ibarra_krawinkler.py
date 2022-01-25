from dataclasses import dataclass
from openseespy import opensees

@dataclass
class ModifiedIbarraKrawinkler:
    n: float  # Usual value = 10

    E: float  # Modulus of elasticity
    I: float  # Moment of inertia
    L: float  # Element length
    # Positive moments data
    My_P: float  # yield moment
    McMy_P: float  # ratio of capping moment to yield moment, Mc / My
    th_pP: float  # plastic rot capacity
    th_pcP: float  # post-capping rot capacity
    th_uP: float  # ultimate rot capacity
    # Negative moments data
    My_N: float
    McMy_N: float
    th_pN: float
    th_pcN: float
    th_uN: float

    LS: float = 1000.0  # basic strength deterioration (a very large # = no cyclic deterioration)
    LK: float = 1000.0  # unloading stiffness deterioration (a very large # = no cyclic deterioration)
    LA: float = 1000.0  # accelerated reloading stiffness deterioration (a very large # = no cyclic deterioration)
    LD: float = 1000.0  # post-capping strength deterioration (a very large # = no deterioration)
    cS: float = 1.0  # exponent for basic strength deterioration (c = 1.0 for no deterioration)
    cK: float = 1.0  # exponent for unloading stiffness deterioration (c = 1.0 for no deterioration)
    cA: float = 1.0  # exponent for accelerated reloading stiffness deterioration (c = 1.0 for no deterioration)
    cD: float = 1.0  # exponent for post-capping strength deterioration (c = 1.0 for no deterioration)
    ResP: float = 0.4  # residual strength ratio for pos loading
    ResN: float = 0.4  # residual strength ratio for neg loading
    DP: float = 1.0  # rate of cyclic deterioration for pos loading (this parameter is used to create assymetric hysteretic behavior for the case of a composite beam). For symmetric hysteretic response use 1.0
    DN: float = 1.0  # rate of cyclic deterioration for neg loading (this parameter is used to create assymetric hysteretic behavior for the case of a composite beam). For symmetric hysteretic response use 1.0

    def __post_init__(self):
        self.calc()

    def calc(self):
        self.Imod = self.I * (self.n + 1) / self.n
        self.K = self.n * 6 * self.E * self.Imod / self.L

        # strain hardening ratio of spring
        self.a_memPos = (self.n + 1.) * self.My_P * (self.McMy_P - 1.0) / (self.K * self.th_pP)
        self.a_memNeg = (self.n + 1.) * abs(self.My_N) * (self.McMy_N - 1.0) / (self.K * self.th_pN)

        # modified strain hardening ratio of spring (Ibarra & Krawinkler 2005, note: Eqn B.5 is incorrect)
        self.asPos = self.a_memPos / (1. + self.n * (1. - self.a_memPos))
        self.asNeg = self.a_memNeg / (1. + self.n * (1. - self.a_memNeg))

    def opensees_bilin_py(self, eleID, nodeStart, nodeEnd, change_order=False):
        opensees.uniaxialMaterial('Bilin', eleID, self.K, self.asPos, self.asNeg, self.My_P, self.My_N,
                                  self.LS, self.LK, self.LA, self.LD, self.cS, self.cK, self.cA, self.cD,
                                  self.th_pP, self.th_pN, self.th_pcP, self.th_pcN,
                                  self.ResP, self.ResN, self.th_uP, self.th_uN, self.DP, self.DN)

        #         print(f'{eleID}, {self.K}, {self.asPos}, {self.asNeg}, {self.My_P}, {self.My_N},'+
        #                 f'{self.LS}, {self.LK}, {self.LA}, {self.LD}, {self.cS}, {self.cK}, {self.cA}, {self.cD},'+
        #                 f'{self.th_pP}, {self.th_pN}, {self.th_pcP}, {self.th_pcN},'+
        #                 f'{self.ResP}, {self.ResN}, {self.th_uP}, {self.th_uN}, {self.DP}, {self.DN}')

        opensees.element('zeroLength', eleID, nodeStart, nodeEnd, '-mat', eleID, '-dir', 6)
        if change_order == False:
            opensees.equalDOF(nodeStart, nodeEnd, 1, 2)
        else:
            opensees.equalDOF(nodeEnd, nodeStart, 1, 2)

    def opensees_peak_py(self, eleID, nodeStart, nodeEnd, change_order=False):
        opensees.uniaxialMaterial('ModIMKPeakOriented', eleID, self.K, self.asPos, self.asNeg, self.My_P, self.My_N,
                                  self.LS, self.LK, self.LA, self.LD, self.cS, self.cK, self.cA, self.cD,
                                  self.th_pP, self.th_pN, self.th_pcP, self.th_pcN,
                                  self.ResP, self.ResN, self.th_uP, self.th_uN, self.DP, self.DN)

        #         print(f'{eleID}, {self.K}, {self.asPos}, {self.asNeg}, {self.My_P}, {self.My_N},'+
        #                 f'{self.LS}, {self.LK}, {self.LA}, {self.LD}, {self.cS}, {self.cK}, {self.cA}, {self.cD},'+
        #                 f'{self.th_pP}, {self.th_pN}, {self.th_pcP}, {self.th_pcN},'+
        #                 f'{self.ResP}, {self.ResN}, {self.th_uP}, {self.th_uN}, {self.DP}, {self.DN}')

        opensees.element('zeroLength', eleID, nodeStart, nodeEnd, '-mat', eleID, '-dir', 6)
        if change_order == False:
            opensees.equalDOF(nodeStart, nodeEnd, 1, 2)
        else:
            opensees.equalDOF(nodeEnd, nodeStart, 1, 2)

    def opensees_command_tcl(self, eleID, nodeR, nodeC):
        return f'rotSpring2DModIKModel {eleID:7} {nodeR:5} {nodeC:7} ' \
            f'{self.K:11.1f} {self.asPos:12.4e} {self.asNeg:12.4e} {self.My_P:10.3f} {self.My_N:10.3f} ' \
            f'{self.LS:9.2f} {self.LK:9.2f} {self.LA:9.2f} {self.LD:9.2f} ' \
            f'{self.cS:6.3f} {self.cK:6.3f} {self.cA:6.3f} {self.cD:6.3f} ' \
            f'{self.th_pP:10.3e} {self.th_pN:10.3e} {self.th_pcP:10.3e} {self.th_pcN:10.3e} ' \
            f'{self.ResP:6.3f} {self.ResN:6.3f} {self.th_uP:10.3e} {self.th_uN:10.3e} {self.DP:6.3f} {self.DN:6.3f};'
