import numpy as np
import math
import pandas as pd
from dataclasses import dataclass, astuple, field
from typing import List
from goto import with_goto
from . import rcinput
from .concrete_models import Kappos91, KentPark71
from .rcsubs import BUCKL, PLCENT, STRESS, STRHRD, CFRCR, CFRCS, YLDDUC, DUCTLE, SHEAR
from .rcsubs import init_arrays_no_length


@dataclass
class Rccola:
    outtxt: List[str] = field(default_factory=list)
    outfilename: str = 'pyrcout'
    input: rcinput.RccolaInput = None
    uniaxial_bending_ini_dfs: List[pd.DataFrame] = field(default_factory=list)
    uniaxial_bending_conf_dfs: List[pd.DataFrame] = field(default_factory=list)
    uniaxial_bending_dfs: List[pd.DataFrame] = field(default_factory=list)

    def write_out(self):
        file = open(self.outfilename, 'w')
        file.write('\n'.join(self.outtxt))
        file.close()

    def calc(self):
        self.main()

        NLOAD = self.input.second_row.NLOAD
        if NLOAD == 0:
            NLOAD = 15

        for i, (df_ini, df_conf) in enumerate(zip(self.uniaxial_bending_ini_dfs, self.uniaxial_bending_conf_dfs)):
            df_ini_sorted = df_ini.sort_values(by=['εc'])
            df_conf_sorted = df_conf.sort_values(by=['εc'])

            df_join1 = df_ini_sorted.where(df_ini_sorted['εc']<=0.0035).dropna()
            df_join2 = df_conf_sorted.where(df_conf_sorted['εc']>0.0035).dropna()

            self.uniaxial_bending_dfs.append(df_join1.append(df_join2))
            


    @with_goto
    def main(self):
        # Read input data
        TYPEC, TYPES, ISPALL, ICSTR, ICSTRS, NPTS, NPTSS, ITCONF, ISSTL, IECU, ISSTR, IGRAPH = astuple(
            self.input.first_row)
        NLOAD, NLAYER, NDATA1, NDATA2, NSTRNI, NSTRNC, NITT = astuple(
            self.input.second_row)
        T, B, TC, BC = astuple(self.input.conc_sect_info)
        if TYPES != 3:
            GT, NB1, AS1, NB2, AS2, NBAR, AF = astuple(
                self.input.reinf_place_info_TYPES12)
        else:
            NL, NBAR, YS, AS, NBS, IBUC, YSS, ASS, NBSS = astuple(
                self.input.reinf_place_info_TYPES3)
        FYS, YMS, ESH, YSH, ESU, FSU, ESDYN = astuple(
            self.input.long_reinf_props)
        FYSTRP, ASSTRP, S, XL, XSTRP, ESUSTRP = astuple(
            self.input.trans_reinf_info)
        # Στα παρακάτω ορίζεται 2η φορά το S...δεν πειράζε...αλλά δεν υπάρχει και λόγος
        if ICSTR in [2, 3, 4, 8]:
            FCJ, S, PPP = astuple(self.input.conc_props_ICSTR2348)
        if ICSTRS == 2:
            FCJS, SS, PPX, NSP = astuple(
                self.input.conc_unconfined_props_ICSTRS2)
        STRN = self.input.strains
        if TYPEC == 3:
            AA, N1, A1, AAc, N1c = astuple(
                self.input.geometry_conc_crossec_info)

        abc = ['', 'A', 'B', 'C']
        default_norm_axials = np.array(
            [1., 0.8, 0.6, 0.5, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.])

        axial_loads = self.input.axials

        if axial_loads is None or len(axial_loads) == 0:
            axial_loads = np.array([])

        if NLOAD == 0:
            NLOAD = 15

        if NLAYER == 0:
            NLAYER = 150

        if NITT == 0:
            NITT = 15

        if NSTRNC < NSTRNI:
            NSTRNC = NSTRNI

        if NSTRNC + NSTRNI == 0:
            STRN = [0, 0.0005]
            STRN.extend([0.0015 + 0.0005 * i for i in range(0, 8)])
            STRN.extend([0.006 + 0.001 * i for i in range(0, 5)])
            STRN.extend([0.015 + 0.005 * i for i in range(0, 8)])
            NSTRNI = 7
            NSTRNC = 22

        JJ = NSTRNI + 3
        JJJ = NSTRNC + 3

        # Initialize some variables ....μάλλον δεν χρειάζεται
        AAC = 0.
        DUCMXI = 0.0
        DUCMXC = 0.0

        FCJ1 = 0.0
        ECULT = 0.0

        A4I = 0.0
        A4C = 0.0
        A4S = 0.0
        A4SS = 0.0

        # Initialize arrays
        EC = []
        FC = []
        ECS = []
        FCS = []

        VI = np.zeros(len(STRN) + 4)

        XPCALC = np.zeros(NLOAD + 1)

        VMI = np.zeros((NLOAD + 1, len(STRN) + 4))
        XXMI = np.zeros((NLOAD + 1, len(STRN) + 4))
        PHII = np.zeros((NLOAD + 1, len(STRN) + 4))
        DUCTI = np.zeros((NLOAD + 1, len(STRN) + 4))

        VC = np.zeros(len(STRN) + 4)

        VMC = np.zeros((NLOAD + 1, len(STRN) + 4))
        XXMC = np.zeros((NLOAD + 1, len(STRN) + 4))
        PHIC = np.zeros((NLOAD + 1, len(STRN) + 4))
        DUCTC = np.zeros((NLOAD + 1, len(STRN) + 4))

        A = np.zeros(NLAYER + 1)
        Y = np.zeros(NLAYER + 1)
        AC = np.zeros(NLAYER + 1)
        YC = np.zeros(NLAYER + 1)

        # YS = np.zeros(NL)
        # AS = np.zeros(NL)
        # NBS = np.zeros(NL)
        # IBUC = np.zeros(NL)
        # if TYPES == 3:
        #     AA = np.zeros(NL)

        ASS = np.zeros(ISSTL + 1)
        YSS = np.zeros(ISSTL + 1)

        ES = np.zeros(32)
        AREA = np.zeros(32)
        CCC = np.zeros(32)
        EES = np.zeros(32)
        ECC = np.zeros(32)
        DUCT1 = np.zeros(32)
        O = np.zeros(32)

        if ISPALL == 1:
            ITCONF = 0

        self.outtxt.append(
            " R E I N F O R C E D   C O N C R E T E   C O L U M N   A N A L Y S I S  ")
        self.outtxt.append(
            " PROGRAM RCCOLA-90    PROPERTIES OF REINFORCED CONCRETE CROSS-SECTIONS")
        self.outtxt.append("")
        self.outtxt.append("")
        self.outtxt.append(
            " ***********************************************************************")
        self.outtxt.append(" Title ")
        self.outtxt.append(
            " ***********************************************************************")
        self.outtxt.append("")
        self.outtxt.append("")

        if TYPEC == 1:
            self.outtxt.append(" RECTANGULAR CROSS-SECTION")
            self.outtxt.append(f"   DEPTH = {T:10.4f}  m")
            self.outtxt.append(f"   WIDTH = {B:10.4f}  m")
            self.outtxt.append("")
            self.outtxt.append("")

        if TYPES == 1:
            self.outtxt.append(" RECTANGULAR STEEL PLACEMENT")
            self.outtxt.append(f"   GT               ={GT:10.4f}  m")
            self.outtxt.append(f"   TC               ={TC:10.4f}  m")
            self.outtxt.append(f"   BC               ={BC:10.4f}  m")
            self.outtxt.append("   MAIN REINFORCING")
            self.outtxt.append(f"     NUMBER OF BARS ={NB1:10.4f}")
            self.outtxt.append(f"     BAR AREA       ={AS1:10.4f} cm**2")
            self.outtxt.append("   SIDE REINFORCING")
            self.outtxt.append(f"     NUMBER OF BARS ={NB2:10.4f}")
            self.outtxt.append(f"     BAR AREA       ={AS2:10.4f} cm**2")
            self.outtxt.append("")
            self.outtxt.append("")

            AS1 = 0.0001 * AS1
            AS2 = 0.0001 * AS2
            ASTOT = NB1 * AS1 + NB2 * AS2

        if TYPES == 3:
            self.outtxt.append(" GENERAL STEEL PLACEMENT")
            self.outtxt.append("")
            self.outtxt.append("   DEPTH  NO OF BARS  ' BAR AREA     IBUC")
            self.outtxt.append("    (m)                 (cm**2)")
            for i in range(0, NL):
                self.outtxt.append(
                    f"{YS[i]:8.3f}{NBS[i]:8}{AS[i]:14.4f}{IBUC[i]}")

            if BC <= 0:
                BC = B

            if NL != 0:
                ASTOT = 0.0
                for i in range(0, NL):
                    if NBS[i] == 0:
                        NBS[i] = 1
                    AS[i] = 0.0001 * AS[i] * NBS[i]
                    ASTOT += AS[i]

            if ISSTL != 0:
                self.outtxt.append(" GENERAL STEEL PLACEMENT")
                self.outtxt.append("   DEPTH      AREA")
                self.outtxt.append("    (m)     (cm**2)")
                for i in range(0, ISSTL):
                    self.outtxt.append(f"{YSS[i]:8.3f}{ASS[i]:10.4f}")
                    if NBSS[i] == 0:
                        NBSS[i] = 1
                    ASS[i] = 0.0001 * ASS[i] * NBSS[i]

        FYS1 = FYS
        ESY = FYS / YMS
        if ESH < ESY:
            ESH = ESY
        R = ESU - ESH
        YMAX = FSU - FYS
        if YSH == 0.:
            YSH = 3. * YMAX / R

        # IF (ISSTR.GT.0.) CALL STRST(FYS,YMS,YSH,ESU,ESDYN,ESY,FSU)

        C1 = (YSH - 2. * YMAX / R) / (R * R)
        C2 = 3.0 * (YMAX - 0.6667 * YSH * R) / (R * R)

        self.outtxt.append(" MATERIAL PROPERTIES -- STEEL")
        self.outtxt.append(f"     YIELD STRESS        ={FYS:10.1f} MPa")
        self.outtxt.append(f"     YOUNGS MODULUS      ={YMS:10.1f} MPa")
        self.outtxt.append("     STRAIN AT ONSET OF")
        self.outtxt.append(f"        STRAIN HARDENING ={ESH:10.6f} m/m")
        self.outtxt.append("     STRAIN HARDENING")
        self.outtxt.append(f"        MODULUS          ={YSH:10.2f} MPa")
        self.outtxt.append(f"     MAXIMUM STRAIN      ={ESU:10.6f} m/m")
        self.outtxt.append(f"     MAXIMUM STRESS      ={FSU:10.1f} MPa")
        self.outtxt.append("")
        self.outtxt.append("")

        if FYSTRP == 0:
            FYSTRP = FYS
        if XL == 0.:
            XL = 3.
        if XSTRP == 0.:
            XSTRP = 2.
        if ESUSTRP == 0.:
            ESUSTRP = ESU

        self.outtxt.append(" TRANSVERSE REINFORCEMENT")
        self.outtxt.append(f"     YIELD STRESS   ={FYSTRP:10.2f} MPa")
        self.outtxt.append(f"     AREA/SPACING   ={ASSTRP:10.4f} cm**2")
        self.outtxt.append(f"     NO OF LEGS     ={XSTRP:10.2f}")
        self.outtxt.append(f"     SPACING        ={S:10.4f} m")
        self.outtxt.append(f"     COLUMN LENGTH  ={XL:10.4f} m")
        self.outtxt.append("")
        self.outtxt.append("")

        ASSTRP = ASSTRP * 0.0001
        F = FYSTRP * ASSTRP * 1000. / S
        A1STRP = ASSTRP / XSTRP

        self.outtxt.append(" MATERIAL PROPERTIES -- CONCRETE")
        self.outtxt.append("")

        if ICSTR == 8:
            if NBAR == 0:
                α_kap91 = 0.55
                β_kap91 = 0.75
            elif NBAR == 1.0:
                α_kap91 = 1.0
                β_kap91 = 1.0
            elif NBAR >= 2.0:
                α_kap91 = 1.25
                β_kap91 = 1.0
            else:
                α_kap91 = 1.0
                β_kap91 = 1.0
                print('Check NBAR')

            kap91 = Kappos91(fc=FCJ,
                             fy=FYS,
                             bc=BC,
                             s=S,
                             ρw=PPP,
                             α=α_kap91,
                             β=β_kap91,
                             εc0=0.002)

            FCJ1 = kap91.fcc
            ECULT = kap91.εcult

            self.outtxt.append(f"    Kappos (1990) model")
            self.outtxt.append(f"")
            self.outtxt.append(f"     Cylinder strength = {FCJ:10.4f} MPa")
            self.outtxt.append(f"     Tie spacing       = {S:10.4f}   m ")
            self.outtxt.append(f"     Tie/core ratio    = {PPP:10.4f} vol/vol")
            self.outtxt.append(f"     No of interm. bars= {NBAR:10.4f}")
            self.outtxt.append(f"     Stength factor    = {kap91.k:10.4f}")
            self.outtxt.append(f"     Slope Z           = {kap91.u:10.4f}")
            self.outtxt.append(f"")
            self.outtxt.append(f"     Ultimate strain   = {ECULT:10.5f}")
            self.outtxt.append(f"")
            self.outtxt.append(f"")

            EC = np.linspace(0., kap91.εcc0, 11)
            EC = np.append(EC, [kap91.ε25c, kap91.ε25c + 0.05])
            FC = np.array([kap91.σc(_ε) for _ε in EC])

        self.outtxt.append(f"         STRAIN    STRESS")
        self.outtxt.append(f"        ( m/m )     (MPa)")
        for i, ε in enumerate(EC):
            self.outtxt.append(f"{ε:15.5f}{FC[i]:10.3f}")

        if FCJ1 == 0.0:
            FCJ1 = FCJ

        #   *************************** Unconfined concrete model **********************************
        # 220
        if ISPALL != 0:
            if ICSTRS == 1:  # User defined
                pass
            elif ICSTRS == 2:  # Kent/Park (1971)
                kentpark71 = KentPark71(fc=FCJS,
                                        bc=BC,
                                        s=SS,
                                        ρw=PPX,
                                        nsp=NSP,
                                        εc0=0.002)

                ECS = np.linspace(0., kentpark71.εc0, 11)
                if NSP == 0:
                    ECS = np.append(ECS, [kentpark71.ε20c, 0.1])
                else:
                    ECS = np.append(
                        ECS, [kentpark71.ε50u, kentpark71.ε50u + 0.00001, 0.05])
                FCS = np.array([kentpark71.σc(_ε) for _ε in ECS])

                if NSP == 1:
                    FCS[len(FCS) - 3] = 0.5 * kentpark71.fc

                self.outtxt.append(f"")
                self.outtxt.append(f"")
                self.outtxt.append(f"    Park/Kent (1971) model ")
                self.outtxt.append(f"     MAXIMUM STRESS = {FCJS:10.4f} MPa")
                self.outtxt.append(f"     TIE SPACING    = {S:10.4f} m")
                self.outtxt.append(
                    f"     TIE/CORE RATIO = {PPX:10.6f} vol/vol")
                self.outtxt.append(f"     SPALLING CODE  = {NSP}")
                self.outtxt.append(f"     Z = {kentpark71.z:10.4f}")

                self.outtxt.append(f"")
                self.outtxt.append(f"         STRAIN    STRESS")
                self.outtxt.append(f"        ( m/m )     (MPa)")
                for i, ε in enumerate(ECS):
                    self.outtxt.append(f"{ε:15.6f}{FCS[i]:10.3f}")

            elif ICSTRS == 3:  # Carreira/Chu (1985)
                pass
            else:
                print('Wrong ICSTRS value for unconfined concrete')

        #   ******************** Calculate ultimate strain and Young's modulus for concrete ****************************
        # 260
        if ECULT == 0.0:
            PPW = PPP * FYSTRP / FCJ
            if AF == 0.:
                if NBAR == 0.0:
                    AF = 0.6667
                else:
                    AF = 1.3333

            ECULT = 0.0035 + 0.025 * (1 + 0.65 * NBAR ** 0.6667) * PPW * AF

        ECMAND = 0.004 + 1.4 * PPP * FYSTRP * ESUSTRP / FCJ1

        ECBUC, bucltxt = BUCKL(AS1=AS1 if TYPES != 3 else None,
                               AS2=AS2 if TYPES != 3 else None,
                               AS=[] if TYPES != 3 else AS,
                               YS=[] if TYPES != 3 else YS,
                               NBS=[] if TYPES != 3 else NBS,
                               IBUC=[] if TYPES != 3 else IBUC,
                               A1STRP=A1STRP,
                               YSH=YSH,
                               BC=BC,
                               TC=TC,
                               S=S,
                               FSU=FSU,
                               FYS=FYS,
                               FYSTRP=FYSTRP,
                               ESH=ESH)

        # if TYPES != 3:
        #     ECBUC, bucltxt = BUCKL(AS1=AS1,
        #                            AS2=AS2,
        #                            AS=[],
        #                            YS=[],
        #                            NBS=[],
        #                            IBUC=[],
        #                            A1STRP=A1STRP,
        #                            YSH=YSH,
        #                            BC=BC,
        #                            TC=TC,
        #                            S=S,
        #                            FSU=FSU,
        #                            FYS=FYS,
        #                            FYSTRP=FYSTRP,
        #                            ESH=ESH)
        # else:
        #     ECBUC, bucltxt = BUCKL(AS1=None,
        #                            AS2=None,
        #                            AS=AS,
        #                            YS=YS,
        #                            NBS=NBS,
        #                            IBUC=IBUC,
        #                            A1STRP=A1STRP,
        #                            YSH=YSH,
        #                            BC=BC,
        #                            TC=TC,
        #                            S=S,
        #                            FSU=FSU,
        #                            FYS=FYS,
        #                            FYSTRP=FYSTRP,
        #                            ESH=ESH)

        if ECBUC < 0.004:
            ECBUC = 0.004

        self.outtxt.append(f"")
        self.outtxt.extend(bucltxt)

        ECFAIL = min(ECULT, ECMAND, ECBUC)
        if IECU == 0:
            ECULT = ECFAIL
            # ECULTconsidered = ECFAIL
        else:
            ECULT = max(ECULT, ECMAND, ECBUC)
            # ECULTconsidered = max(ECULT, ECMAND, ECBUC)

        self.outtxt.append(f"")
        self.outtxt.append(f"  No of intermediate bars per side :{NBAR}")
        self.outtxt.append(
            f"  Strain at first hoop fracture    :{ECMAND:12.6f}")
        self.outtxt.append(
            f"  Strain at buckling of long. bars :{ECBUC:12.6f}")
        self.outtxt.append(f"")
        self.outtxt.append(
            f"  Ultimate conc. strain considered :{ECULT:12.6f}")
        # self.outtxt.append(f"  Ultimate conc. strain considered :{ECULTconsidered:12.6f}")

        if ICSTR == 1:
            FCJ = max(FC)

        EEC = (FC[1] - FC[0]) / (EC[1] - EC[0])
        if EEC < 25000:
            EEC = 21500 * (FCJ / 10) ** 0.3333

        self.outtxt.append(f"")
        self.outtxt.append(f"")
        self.outtxt.append(f" YOUNGS MODULUS FOR CONCRETE={EEC:10.1f} MPa")

        RECS = YMS / EEC - 1.0
        G = 5 * math.sqrt(FCJ * 1000)

        self.outtxt.append(f" EQUILIBRIUM CALCULATED FOR THE FOLLOWING")
        self.outtxt.append(f" CONCRETE COMPRESSIVE STRAINS")
        self.outtxt.append(f"")
        self.outtxt.append(f"         M         STRAIN")
        self.outtxt.append(f"")

        # for idx, val in enumerate(STRN):
        #     self.outtxt.append(f"{idx}{val:15.6f}")

        for i in range(0, NSTRNI + 1):
            self.outtxt.append(f"{i}{STRN[i]:15.6f}")

        for i in range(NSTRNI + 1, NSTRNC + 1):
            self.outtxt.append(f"{i}{STRN[i]:15.6f}  CONFINED SECTION ONLY")

        DLAYER = 1.0 / NLAYER
        DD = 0.5 * (1.0 + DLAYER)

        if TYPEC == 1:  # Rectangular
            AG = T * B
            AII = B * T ** 3 / 12.

            AGC = TC * BC
            AIIC = BC * TC ** 3. / 12.

        elif TYPEC == 2:  # Circular
            AII = 0.0
            RR = T * T / 4.
            AG = math.pi * RR
            for i in range(0, NLAYER):
                Y[i] = T * (DD - DLAYER * i)
                A[i] = 2.0 * DLAYER * T * math.sqrt(RR - Y[i] * Y[i])
                AII = AII + A[i] * Y[i] * Y[i]

            RRC = TC * TC / 4.0
            AGC = math.pi * RRC
            AIIC = 0.0
            for i in range(0, NLAYER):
                YC[i] = TC * (DD - DLAYER * i)
                AC[i] = 2.0 * DLAYER * TC * math.sqrt(RRC - YC[i] * YC[i])
                AIIC = AIIC + AC[i] * YC[i] * YC[i]

        else:  # Arbitrary
            AG = 0.0
            AGC = 0.0
            A4 = 0.0
            A4C = 0.0
            A4S = 0.0
            A4SS = 0.0
            AST = 0.0
            AAS = 0.0
            AII = 0.0
            AIIC = 0.0
            AIIS = 0.0
            AIISS = 0.0
            ASTLC = 0.0

            DLAYER = T / float(NLAYER)
            DD = 0.5 * (1.0 + DLAYER / T)
            MM = 0

            if ISPALL != 1:
                A1 = list(np.zeros(NDATA1))

            for i in range(0, NDATA1):
                AA[i] = AA[i] * DLAYER
                A1[i] = A1[i] * DLAYER
                aa = AA[i]
                a1 = A1[i]

                for j in range(0, N1[i]):
                    MM = MM + 1
                    A[MM] = aa
                    AC[MM] = a1
                    AG = AG + aa + a1
                    AGC = AGC + aa
                    Y[MM] = T * DD - DLAYER * float(MM)
                    YC[MM] = Y[MM]
                    BB = (aa + a1) * Y[MM]
                    BB1 = aa * Y[MM]
                    AII = AII + BB * Y[MM]
                    AIIC = AIIC + BB1 * YC[MM]
                    A4C = A4C + BB1
                    A4 = A4 + BB
            A4I = A4

            for i in range(0, NL):
                if YS[i] <= 0.:
                    ASTLC = ASTLC + AS[i]
                    AAC = AAC + AS[i] * YS[i]
                AST = AST + AS[i]
                aa = AS[i] * YS[i] * RECS
                AIIS = AIIS + aa * YS[i]
                A4S = A4S + aa
            AAA = AG + AST * RECS
            ASTLI = ASTLC
            AAI = AAC
            if ISPALL != 0:
                AAAC = AGC + AST * RECS
                YBAR = (A4C + A4S) / AAAC
                AIIC = AIIC + AIIS
                AIIC = AIIC + AAAC * YBAR * YBAR
            if ISSTL != 0:
                for i in range(0, ISSTL):
                    if YSS[i] < 0:
                        ASTLI = ASTLI + ASS[i]
                        AAI = AAI + ASS[i] * YSS[i]
                    AAS = AAS + ASS[i]
                    aa = ASS[i] * YSS[i] * RECS
                    AIISS = AIISS + aa * YSS[i]
                    A4SS = A4SS + aa
                AAA = AAA + AAS * RECS
            A4 = A4 + A4S + A4SS
            YBAR = A4 / AAA
            AII = AII + AIIS + AIISS
            AII = AII + AAA * YBAR * YBAR

            if ITCONF != 0:
                AGC = 0.0
                A4 = 0.0
                AIIC = 0.0

                DLAYER = TC / float(NLAYER)
                DD = 0.5 * (1.0 + DLAYER / TC)
                MM = 0

                for i in range(0, NDATA2):
                    AAc[i] = AAc[i] * DLAYER
                    aac = AAc[i]

                    for j in range(0, N1c[i]):
                        MM += 1
                        AC[MM] = aac
                        AGC = AGC + aac
                        YC[MM] = TC * DD - DLAYER * float(MM)
                        BB = aac * YC[MM]
                        AIIC = AIIC + BB * YC[MM]
                        A4 = A4 + BB
                A4C = A4
                AAAC = AGC + AST * RECS
                AIIC = AIIC + AIIS
                A4 = A4 + A4S
                YBAR = A4 / AAAC
                AIIC = AIIC + AAAC * YBAR * YBAR

            self.outtxt.append(f"")
            self.outtxt.append(f"")
            self.outtxt.append(f" GENERAL CONCRETE SECTION GEOMETRY")
            self.outtxt.append(f"")

            if ITCONF != 1:
                if ISPALL != 1:
                    self.outtxt.append(f" LAYER          DEPTH           AREA")
                    self.outtxt.append(f"")
                    for i in range(1, NLAYER + 1):
                        self.outtxt.append(f"{i:6}{Y[i]:15.5f}{A[i]:15.5f}")
                else:
                    self.outtxt.append(
                        f"      --------CONFINED CORE--------- -------UNCONFINED COVER-------")
                    self.outtxt.append(
                        f" LAYER          DEPTH           AREA          DEPTH           AREA")
                    self.outtxt.append(
                        f"                 (m)           (m**2)          (m)           (m**2)")
                    self.outtxt.append(f"")
                    for i in range(1, NLAYER + 1):
                        self.outtxt.append(
                            f"{i:6}{Y[i]:15.5f}{A[i]:15.5f}{YC[i]:15.5f}{AC[i]:15.5f}")
            else:
                self.outtxt.append(
                    f"      -------INITIAL SECTION-------- -------CONFINED SECTION-------")
                self.outtxt.append(
                    f" LAYER          DEPTH           AREA          DEPTH           AREA")
                self.outtxt.append(f"")
                for i in range(1, NLAYER + 1):
                    self.outtxt.append(
                        f"{i:6}{Y[i]:15.5f}{A[i]:15.5f}{YC[i]:15.5f}{AC[i]:15.5f}")

        # C
        # C     SECTION PROPERTIES - STEEL
        # C
        if TYPES == 1:  # Rectangular
            NL = round(NB2 / 2 + 2)
            YS = np.zeros(NL + 1)
            AS = np.zeros(NL + 1)

            YS[0] = GT / 2
            AS[0] = NB1 * AS1 / 2

            YS[NL - 1] = -YS[0]
            AS[NL - 1] = AS[0]

            if NL != 2:
                NNL = NL - 1
                DY = float(GT / NNL)

                for i in range(1, NNL):
                    YS[i] = YS[i - 1] - DY
                    AS[i] = 2. * AS2

            AII1 = AII
            for i in range(0, NL):
                AII = AII + AS[i] * RECS * YS[i] * YS[i]

        elif TYPES == 2:  # Circular
            THETA = 2. * math.pi / NB1
            AII1 = AII
            YS = np.zeros(NB1)
            AS = np.zeros(NB1)
            NL = NB1
            for i in range(0, NL):
                YS[i] = GT * math.cos(THETA * (float(i) - 1.)) / 2.0
                AS[i] = AS1
                AII = AII + AS1 * YS[i] * YS[i] * RECS

        if TYPES == 1 or TYPES == 2:
            DAII = AII - AII1
            AIIC = AIIC + DAII
            AAS = 0.0

            if ISSTL != 0:
                for i in range(0, ISSTL):
                    AAS = AAS + ASS[i]
                    AII = AII + ASS[i] * YSS[i] * YSS[i] * RECS

            AST = NB1 * AS1 + NB2 * AS2
            AAA = AG + (AST + AAS) * RECS
            AAAC = AGC + AST * RECS

            if S > 0.:
                ASTLI = (AST + AAS) / 2.0
                ASTLC = AST / 2.0

                for i in range(0, NL):
                    if YS[i] < 0:
                        AAC = AAC + YS[i] * AS[i]

                AAI = AAC

                if ISSTL != 0:
                    for i in range(0, ISSTL):
                        if YSS[i] <= 0.0:
                            AAI = AAI + YSS[i] * ASS[i]

        RG = math.sqrt(AII / AAA)

        if TYPES == 2:
            NBOTL = NL / 2. + 1
        else:
            NBOTL = NL

        AST1 = AST

        self.outtxt.append(f"")
        self.outtxt.append(f"")
        self.outtxt.append(f" GROSS SECTION")
        self.outtxt.append(f" TRANSFORMED AREA      ={AAA:15.6f}  m**2")
        self.outtxt.append(f" MOMENT OF INERTIA     ={AII:15.6f}  m**4")
        self.outtxt.append(f" RADIUS OF GYRATION    ={RG:15.4f}  m")

        if ITCONF != 0:
            RGC = math.sqrt(AIIC / AAAC)
            self.outtxt.append(f"")
            self.outtxt.append(f"")
            self.outtxt.append(f" CONFINED SECTION")
            self.outtxt.append(f" TRANSFORMED AREA      ={AAAC:15.6f}  m**2")
            self.outtxt.append(f" MOMENT OF INERTIA     ={AIIC:15.6f}  m**4")
            self.outtxt.append(f" RADIUS OF GYRATION    ={RGC:15.4f}  m")

        DI = -AAI / ASTLI + T / 2.0
        self.outtxt.append(f"")
        self.outtxt.append(f"")
        self.outtxt.append(f"")
        self.outtxt.append(f" PARAMETERS FOR SHEAR STRENGTH EVALUATION")
        self.outtxt.append(f"    BASED ON REINFORCEMENT ON TENSILE")
        self.outtxt.append(f"    SIDE OF SECTION MID-DEPTH")
        self.outtxt.append(f"")
        self.outtxt.append(f"  INITIAL CROSS-SECTION")
        self.outtxt.append(f"    EFFECTIVE DEPTH ={DI:10.4f}  m")
        self.outtxt.append(f"    TENSILE STEEL   ={ASTLI:10.6f}  m**2")

        if ITCONF > 0:
            DC = -AAC / ASTLC + TC / 2.0
            self.outtxt.append(f"")
            self.outtxt.append(f"")
            self.outtxt.append(f"  CONFINED CROSS-SECTION")
            self.outtxt.append(f"    EFFECTIVE DEPTH ={DC:10.4f}  m")
            self.outtxt.append(f"    TENSILE STEEL   ={ASTLC:10.6f}  m**2")

        self.outtxt.append(f"")
        self.outtxt.append(f"")
        self.outtxt.append(f"")
        self.outtxt.append(f"")
        self.outtxt.append(f"*** COLUMN  INTERACTION  VALUES ***")
        self.outtxt.append(f"")
        self.outtxt.append(f" Uniaxial compression")
        self.outtxt.append(f"")
        self.outtxt.append(f"  M      CONCRETE          LOAD")
        self.outtxt.append(f"          STRAIN")
        self.outtxt.append(f"          ( m/m )         ( MN )")
        self.outtxt.append(f"")

        if ITCONF == 1:
            J = NSTRNC
        else:
            J = NSTRNI
        XXPMAX = 0.0
        PCA = np.zeros(len(STRN) + 3)
        XPA = np.zeros(len(STRN) + 3)
        PCC = np.zeros(len(STRN) + 3)
        XPC = np.zeros(len(STRN) + 3)

        for i in range(1, J + 1):
            IND = 0
            if i > NSTRNI:
                IND = 1

            XPA[i], PCA[i], XPC[i], PCC[i] = PLCENT(STRN[i], EC, FC, ECS, FCS, FYS, YMS, ESH, YSH, FSU, ESU,
                                                    C1, C2, IND, ISPALL, AG, AST, AAS, AGC, TYPEC, ITCONF,
                                                    A4I, A4C, A4S, A4SS, RECS)

            if i > 0:
                if IND != 1:
                    self.outtxt.append(
                        f"{i:3}{STRN[i]:15.5f}{XPA[i]:15.3f}   INITIAL CROSS-SECTION")
                    if abs(PCA[i]) > 0.00001:
                        self.outtxt.append(
                            '+' + ' ' * 50 + f"PL.CENTROID ={PCA[i]:10.4f}m")
                    if XPA[i] > XXPMAX:
                        XXPMAX = XPA[i]

                if ITCONF > 0:
                    self.outtxt.append(
                        f"{i:3}{STRN[i]:15.5f}{XPC[i]:15.3f}   CONFINED CROSS-SECTION")
                    if XPC[i] > XXPMAX:
                        XXPMAX = XPC[i]

        KJ = NSTRNI + 1
        XPA[KJ] = - FYS * (AST + AAS)
        E1 = XPA[KJ] * FSU / FYS
        E2 = -ESY
        E4 = -ESU

        self.outtxt.append(f"")
        self.outtxt.append(f"")

        KL = J + 1
        self.outtxt.append(
            f"{KL:3}{E2:14.5f}{XPA[KJ]:14.3f}   INITIAL CROSS-SECTION")

        if ITCONF > 0:
            JK = NSTRNC + 1
            XPC[JK] = -FYS * AST
            E3 = -FSU * AST
            self.outtxt.append(
                f"{KL:3}{E2:14.5f}{XPC[JK]:14.3f}   CONFINED CROSS-SECTION")

        KL = KL + 1
        self.outtxt.append(
            f"{KL:3}{E4:14.5f}{E1:14.3f}   INITIAL CROSS-SECTION")

        if ITCONF > 0:
            self.outtxt.append(
                f"{KL:3}{E4:14.5f}{E3:14.3f}   CONFINED CROSS-SECTION")

        self.outtxt.append("")
        self.outtxt.append("")
        self.outtxt.append("")
        self.outtxt.append(" Uniaxial Bending")
        self.outtxt.append("")
        self.outtxt.append(
            "        εc        N        M   M/My    1/r    Yield    εs       x     V     M(V)")
        self.outtxt.append(
            "      (m/m)     (MN)    (MN.m)       (rad/m)  Ductl.  (m/m)    (m)   (MN)  (MN.m)")

        XXPMIN = XPA[KJ]

        if NSTRNI >= 5:
            XPAA = XPA[5]
        else:
            XPAA = XPA[NSTRNI]

        if len(axial_loads) == 0:
            XPCALC = XPAA * default_norm_axials
            XPCALC = np.append(XPCALC, [XPA[KJ] * 0.3, XPA[KJ] * 0.6, XPA[KJ]])
        else:
            for i in range(0, NLOAD):
                XPCALC[i] = axial_loads[i]

        # goto.x9999

        K = -1

        label.x690  # **************************************************** 690
        K += 1
        # print('')
        # print('')
        # print(f'*******************************************************')
        # print(f'K = {K}    ({K + 1} in fortran)')
        # print(f'*******************************************************')
        # print('')
        XPU = XPCALC[K]
        ICONF = 0
        ERROR = max(abs(XPU / 200), 0.0045)
        ECLIM = ECULT + 0.001
        ESLIM = ESU + 0.001

        label.x700  # **************************************************** 700
        ICOUNT = 0

        label.x710  # **************************************************** 710
        ICOUNT += 1
        # print('')
        # print('---------------------------------')
        # print(f'ICOUNT = {ICOUNT}')
        # print('')
        C = 0.5 * T
        DPC = 0.0

        if ICOUNT < 4:
            goto.x740

        if ICONF == 1:
            goto.x720

        DPC = PCA[ICOUNT - 3]

        if XPU < XPA[ICOUNT - 3]:
            goto.x730

        goto.x930

        label.x720  # **************************************************** 720
        DPC = PCC[ICOUNT - 3]
        if XPU < XPC[ICOUNT - 3]:
            goto.x730
        goto.x930

        label.x730  # **************************************************** 730
        ECU = STRN[ICOUNT - 3]
        if ICOUNT > 4 and CCC[ICOUNT - 1] != 0.:
            C = CCC[ICOUNT - 1]

        label.x740  # **************************************************** 740
        KCOUNT = 0
        T1 = 0.0
        TL = T

        if ICONF == 1:
            TL = TC
        if ICOUNT == 1 or ICOUNT == 3:
            goto.x750
        if ICOUNT == 2:
            T1 = 0.5 * TL - YS[0]
        T3 = 8. * T
        goto.x760

        label.x750  # **************************************************** 750
        T1 = 0.0
        T3 = 0.5 * TL - YS[NBOTL - 1]
        if ICOUNT == 3:
            T3 = T3 * ECULT / (ESU + ECULT)
        if T3 <= C:
            C = T3 / 2.0

        label.x760  # **************************************************** 760
        KCOUNT += 1
        if KCOUNT == NITT:
            goto.x930

        if ICOUNT == 1:
            ECU = C * ESY / (TL / 2. - YS[NBOTL - 1] - C)
        elif ICOUNT == 2:
            ECU = - C * ESY / (TL / 2. - YS[0] - C)
        elif ICOUNT == 3:
            ECU = C * ESU / (TL / 2. - YS[NBOTL - 1] - C)

        # print(f'K={K:2}  ICOUNT={ICOUNT:2}   KCOUNT={KCOUNT:2}    ECU={ECU:10.6f}')

        if ECU > ECLIM:
            goto.x930

        XP = 0.0
        XM = 0.0
        ASTL = 0.0
        XX = 0.0

        if ECU < 0.0:
            goto.x840

        if TYPEC == 1:
            goto.x770
        elif TYPEC == 2:
            goto.x800
        elif TYPEC == 3:
            goto.x820

        label.x770  # **************************************************** 770
        if ICONF == 1:
            goto.x780
        XP, XM = CFRCR(C, ECU, T, B, EC, FC)
        goto.x840

        label.x780  # **************************************************** 780
        if TYPES == 1:
            goto.x790
        else:
            goto.x810

        label.x790  # **************************************************** 790
        XP, XM = CFRCR(C, ECU, TC, BC, EC, FC)
        goto.x840

        label.x800  # **************************************************** 800
        if ICONF == 1:
            goto.x810
        XP, XM = CFRCS(C, T, ECU, A, Y, EC, FC)
        goto.x840

        label.x810  # **************************************************** 810
        XP, XM = CFRCS(C, TC, ECU, AC, YC, EC, FC)
        goto.x840

        label.x820  # **************************************************** 820
        if ICONF == 1:
            goto.x830
        XP, XM = CFRCS(C, T, ECU, A, Y, EC, FC)
        # print(f'{XP}   {XM}')
        if ISPALL == 0:
            goto.x840
        XPS = 0.0
        XMS = 0.0
        XPS, XMS = CFRCS(C, T, ECU, AC, YC, ECS, FCS)
        XP = XP + XPS
        XM = XM + XMS
        goto.x840

        label.x830  # **************************************************** 830
        XP, XM = CFRCS(C, TC, ECU, AC, YC, EC, FC)

        label.x840  # **************************************************** 840
        for N in range(0, NL):
            ES[N] = (C - TL / 2. + YS[N]) * ECU / C
            FS = STRHRD(ES[N], FYS, YMS, ESH, YSH, FSU, ESU, C1, C2)
            if ES[N] < 0.0:
                goto.x850
            FCI = STRESS(ES[N], EC, FC)
            FS = FS - FCI

            label.x850  # **************************************************** 850
            XP = XP + AS[N] * FS

            label.x860  # **************************************************** 860
            XM = XM + AS[N] * FS * YS[N]

        if ISSTL == 0 or ICONF == 1:
            goto.x910

        for N in range(0, ISSTL):
            ES[N] = (C - TL / 2. + YSS[N]) * ECU / C
            FS = STRHRD(ES[N], FYS, YMS, ESH, YSH, FSU, ESU, C1, C2)
            if ES[N] < 0.:
                goto.x890
            if ISPALL == 0:
                goto.x870
            FCI = STRESS(ES[N], ECS, FCS)
            goto.x880

        label.x870  # **************************************************** 870
        FCI = STRESS(ES[N], EC, FC)

        label.x880  # **************************************************** 880
        if FCI >= 0.:
            goto.x900
        FS = FS - FCI

        label.x890  # **************************************************** 890
        XP = XP + ASS[N] * FS
        XM = XM + ASS[N] * FS * YSS[N]

        label.x900  # **************************************************** 900
        pass

        label.x910  # **************************************************** 910
        pass

        XP = -XP
        XM = -XM
        if ES[NBOTL] < -ESLIM or ES[0] > ESLIM:
            goto.x930
        if abs(XPU - XP) < ERROR:
            goto.x950
        if XP < XPU:
            goto.x920
        T3 = C
        C = (C + T1) / 2.0
        goto.x760

        label.x920  # **************************************************** 920
        T1 = C
        C = (C + T3) / 2.0
        goto.x760

        label.x930  # **************************************************** 930
        CCC[ICOUNT] = 0.0
        EES[ICOUNT] = 0.0
        ECC[ICOUNT] = 0.0
        DUCT1[ICOUNT] = 0.0
        O[ICOUNT] = 0.0
        if ICONF == 1:
            goto.x940

        XXMI[K, ICOUNT] = 0.0
        PHII[K, ICOUNT] = 0.0
        VI[ICOUNT] = 0.0
        VMI[K, ICOUNT] = 0.0

        goto.x970

        label.x940  # **************************************************** 940
        XXMC[K, ICOUNT] = 0.0
        PHIC[K, ICOUNT] = 0.0
        VC[ICOUNT] = 0.0
        VMC[K, ICOUNT] = 0.0
        goto.x1000

        label.x950  # **************************************************** 950
        if ICONF == 1:
            goto.x980

        if TYPEC != 3:
            goto.x960

        if ICOUNT >= 4:
            goto.x960

        XXP, DPC, E1, E2 = PLCENT(ECU, EC, FC, ECS, FCS, FYS, YMS, ESH, YSH, FSU, ESU, C1, C2,
                                  0, ISPALL, AG, AST, AAS, AGC, TYPEC, ITCONF, A4I, A4C, A4S, A4SS, RECS)

        print(f'{XXP} {DPC} {E1} {E2}')

        label.x960  # **************************************************** 960
        XXMI[K, ICOUNT] = XM - XP * DPC
        CCC[ICOUNT] = C
        ECC[ICOUNT] = ECU
        EES[ICOUNT] = ES[NBOTL - 1]
        PHII[K, ICOUNT] = abs(ECU / C)
        DUCT1[ICOUNT] = 0.0
        O[ICOUNT] = 0.0
        DUCT1, O = YLDDUC(PHII, PHII, XXMI, XXMI, ICOUNT, K, DUCT1, O)

        if S != 0.0:
            VI, VMI = SHEAR(VI, VMI, ICOUNT, K, AG, G, TL, AST,
                            XL, XP, F, ASTLI, DI, B, TYPEC, TYPES, ICONF)

        label.x970  # **************************************************** 970
        if ICOUNT < JJ:
            goto.x710

        DUCTI, AREA, DUCMXI = DUCTLE(
            PHII, XXMI, AREA, DUCTI, DUCMXI, K, 1, NSTRNI, NSTRNC)
        self.outtxt.append('')
        self.outtxt.append('')

        _data = []
        for i in range(1, 4):
            self.outtxt.append((f"{K + 1:2}" if i == 1 else '  ') +
                               f" {abc[i]}{ECC[i]:8.5f}{XPU:9.4f}{XXMI[K, i]:9.4f}{O[i]:5.2f}{PHII[K, i]:10.6f}" +
                               f"{DUCT1[i]:6.2f}{EES[i]:9.5f}{CCC[i]:7.3f}{VI[i]:7.3f}{VMI[K, i]:7.3f}")
            _data_row = {'K': K + 1,
                         'i': abc[i],
                         'εc': ECC[i],
                         'N': XPU,
                         'M': XXMI[K, i],
                         'M/My':O[i],
                         'φ': PHII[K, i],
                         'Duct': DUCT1[i],
                         'εs': EES[i],
                         'x': CCC[i],
                         'V': VI[i],
                         'M(V)': VMI[K, i]}
            _data.append(_data_row)

        III = 3
        IREM = 0

        for i in range(4, JJ + 1):
            if ECC[i] > 0:
                self.outtxt.append(
                    f"{i - 3:4}{ECC[i]:8.5f}{XPU:9.4f}{XXMI[K, i]:9.4f}{O[i]:5.2f}{PHII[K, i]:10.6f}" +
                    f"{DUCT1[i]:6.2f}{EES[i]:9.5f}{CCC[i]:7.3f}{VI[i]:7.3f}{VMI[K, i]:7.3f}")

                _data_row = {'K': K + 1,
                            'i': i - 3,
                            'εc': ECC[i],
                            'N': XPU,
                            'M': XXMI[K, i],
                            'M/My':O[i],
                            'φ': PHII[K, i],
                            'Duct': DUCT1[i],
                            'εs': EES[i],
                            'x': CCC[i],
                            'V': VI[i],
                            'M(V)': VMI[K, i]}
                _data.append(_data_row)
        
        self.uniaxial_bending_ini_dfs.append(pd.DataFrame(data=_data))

        label.x975  # **************************************************** 975
        if ITCONF == 0:
            goto.x1010
        ICONF = 1
        goto.x700

        label.x980  # **************************************************** 980
        if TYPEC != 3:
            goto.x990
        if ICOUNT >= 4:
            goto.x990

        E1, E2, XXP, DPC = PLCENT(ECU, EC, FC, ECS, FCS, FYS, YMS, ESH, YSH, FSU, ESU, C1, C2,
                                  0, ISPALL, AG, AST, AAS, AGC, TYPEC, ITCONF, A4I, A4C, A4S, A4SS, RECS)

        label.x990  # **************************************************** 990
        XXMC[K, ICOUNT] = XM - XP * DPC
        CCC[ICOUNT] = C
        EES[ICOUNT] = ES[NBOTL]
        ECC[ICOUNT] = ECU
        PHIC[K, ICOUNT] = abs(ECU / C)
        DUCT1[ICOUNT] = 0.0
        O[ICOUNT] = 0.0
        DUCT1, O = YLDDUC(PHIC, PHII, XXMC, XXMI, ICOUNT, K, DUCT1, O)

        if S != 0.0:
            VC, VMC = SHEAR(VC, VMC, ICOUNT, K, AGC, G, TL, AST,
                            XL, XP, F, ASTLC, DC, BC, TYPEC, TYPES, ICONF)

        label.x1000  # **************************************************** 1000
        if ICOUNT < JJJ:
            goto.x710
        DUCTC, AREA, DUCMXC = DUCTLE(
            PHIC, XXMC, AREA, DUCTC, DUCMXC, K, 2, NSTRNI, NSTRNC)

        self.outtxt.append('')
        self.outtxt.append('')
        _data = []
        for i in range(1, 4):
            self.outtxt.append((f"{K + 1:2}" if i == 1 else '  ') +
                               f" {abc[i]}{ECC[i]:8.5f}{XPU:9.4f}{XXMC[K, i]:9.4f}{O[i]:5.2f}{PHIC[K, i]:10.6f}" +
                               f"{DUCT1[i]:6.2f}{EES[i]:9.5f}{CCC[i]:7.3f}{VC[i]:7.3f}{VMC[K, i]:7.3f}")

            _data_row = {'K': K + 1,
                         'i': abc[i],
                         'εc': ECC[i],
                         'N': XPU,
                         'M': XXMC[K, i],
                         'M/My':O[i],
                         'φ': PHIC[K, i],
                         'Duct': DUCT1[i],
                         'εs': EES[i],
                         'x': CCC[i],
                         'V': VC[i],
                         'M(V)': VMC[K, i]}
            _data.append(_data_row)

        for i in range(4, JJJ + 1):
            if ECC[i] > 0:
                self.outtxt.append(f"{i - 3:4}{ECC[i]:8.5f}{XPU:9.4f}{XXMC[K, i]:9.4f}{O[i]:5.2f}{PHIC[K, i]:10.6f}" +
                                   f"{DUCT1[i]:6.2f}{EES[i]:9.5f}{CCC[i]:7.3f}{VC[i]:7.3f}{VMC[K, i]:7.3f}")
                
                _data_row = {'K': K + 1,
                        'i': i-3,
                        'εc': ECC[i],
                        'N': XPU,
                        'M': XXMC[K, i],
                        'M/My':O[i],
                        'φ': PHIC[K, i],
                        'Duct': DUCT1[i],
                        'εs': EES[i],
                        'x': CCC[i],
                        'V': VC[i],
                        'M(V)': VMC[K, i]}
                _data.append(_data_row)

        self.uniaxial_bending_conf_dfs.append(pd.DataFrame(data=_data))

        label.x1010  # **************************************************** 1010
        if K <= NLOAD - 2:
            goto.x690

        label.x9999
        pass
