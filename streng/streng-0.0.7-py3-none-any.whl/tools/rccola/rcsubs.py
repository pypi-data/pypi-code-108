import math
import numpy as np
from goto import with_goto

def init_arrays_no_length():
    EC = []
    FC = []
    ECS = []
    FCS = []

    return EC, FC, ECS, FCS


def BUCKL(AS1, AS2, AS, YS, NBS, IBUC, A1STRP, YSH, BC, TC, S, FSU, FYS, FYSTRP, ESH):
    outtxt = []

    ECBUC = 0.004

    NALARM = 0
    ASMIN = 0.

    FBUC = 16 * FYSTRP * A1STRP

    if len(AS) == 0:
        ASMIN = AS1
        FLBUC = AS1 * FYS
        if FLBUC > FBUC:
            NALARM += 1


    else:
        ASMIN = 1000.
        for i in range(len(AS)):
            if AS[i] != 0. and NBS[i] != 0. and IBUC[i] == 0:
                ASB = AS[i] / NBS[i]
                FLBUC = ASB * FYS
                if FLBUC > FBUC:
                    NALARM += 1
                if ASB < ASMIN:
                    ASMIN = ASB

    if NALARM >= 1:
        outtxt.append(f"*** ATTENTION : ***")
        outtxt.append(f" Tie yield strength is less than 1/16th the long. bar yield strength in:")
        outtxt.append(f"   ={NALARM:6.0f} cases -> Early buckling expected")

    DMIN = 2 * math.sqrt(ASMIN / math.pi)
    SL = 4 * S / DMIN

    if S != 0. and A1STRP != 0.:
        FK = 8 * A1STRP * YSH * (BC + TC) / (BC * TC * S)
        FHARD = FSU / FYS
        SLMAX = -6 + 40 * FHARD

        if SL <= SLMAX:

            if FHARD < 1.3:
                outtxt.append(f"*** WARNING : ***")
                outtxt.append(f" Hardening capacity of steel too low (fu/fy = {FHARD:5.2f} )")

            if SL < 7.0:
                outtxt.append(f"*** WARNING : ***")
                outtxt.append(f" Slenderness of longitudinal bars too low ( A ={SL:5.2f} < 7 )")

            ALOGK = math.log(FK, 10.)
            if ALOGK > 2.5:
                outtxt.append(f"*** WARNING : ***")
                outtxt.append(f" Stiffness of transverse bars too high ( log k ={ALOGK:5.2f} > 2.5 )")

            ZHTA = 0.17 * (SLMAX / 54) ** 0.75
            HTA = math.sqrt(345 / FYS)
            XSI = 1 - math.sqrt(FHARD / 1.5)
            FAC1 = 0.75 * (ALOGK - 2.5) * (SLMAX - SL) ** (1.5 * SL ** (-ZHTA))
            FAC2 = HTA * (1 - XSI * 1.5 ** (0.2 * SL - 2))
            FAC3 = 0.029 * SL * SL - 2.67 * SL + 64
            ECBUC = ESH + 0.001 * (FAC1 + FAC2 * FAC3)

        else:
            outtxt.append(f"*** ATTENTION : ***")
            outtxt.append(f" Slenderness of longitudinal bars too high -> Early buckling expected ! ")
            outtxt.append(f"")
            outtxt.append(f"      A = {SL:6.2f} > Amax = {SLMAX:6.2f}")

    else:
        outtxt.append(f"*** ATTENTION : NO TRANSVERSE REINFORCEMENT ! ***")

    return ECBUC, outtxt

@with_goto
def PLCENT(ECI, EC, FC, ECS, FCS, FYS, YMS, ESH, YSH, FSU, ESU, C1, C2, IND, ISPALL, AG, AST, AAS, AGC,
           TYPEC, ITCONF, A4I, A4C, A4S, A4SS, RECS):
    #
    #      CALCULATES PLASTIC CENTROID LOCATION (DPC) RELATIVE TO
    #      MID-DEPTH AND AXIAL LOAD (XXP) GIVEN CONCRETE STRAIN (EX)
    #

    XXP = 0.
    DPC = 0.
    XXPC = 0.
    DPCC = 0.

    FCI = - STRESS(ECI, EC, FC)
    FS = abs(STRHRD(ECI, FYS, YMS, ESH, YSH, FSU, ESU, C1, C2))

    if IND == 1:
        goto.x20
    if ISPALL == 0:
        goto.x10

    # SECTION WITH DIFFERENT CONCRETE IN COVER AND CORE
    FCJ = - STRESS(ECI, ECS, FCS)
    XXP = FCI * AGC + FCJ * (AG - AGC) + (FS - FCI) * AST + (FS - FCJ) * AAS
    DPC = (FCI * A4C + FCJ * (A4I - A4C) + (FS - FCI) * A4S / RECS + (FS - FCJ) * A4SS / RECS) / XXP
    goto.x30

    label.x10
    # INITIAL SECTION
    XXP = FCI * AG + (FS - FCI) * (AST + AAS)
    DPC = 0.0
    if TYPEC == 3:
        DPC = (FCI * A4I + (FS - FCI) * (A4S + A4SS) / RECS) / XXP

    label.x20
    # CONFINED SECTION
    if ITCONF == 0:
        goto.x30
    XXPC = FCI * AGC + AST * (FS - FCI)
    DPCC = 0.0
    if TYPEC == 3:
        DPCC = (FCI * A4C + (FS - FCI) * A4S / RECS) / XXPC

    # if IND != 1:
    #     if ISPALL != 0:
    #         # SECTION WITH DIFFERENT CONCRETE IN COVER AND CORE
    #         FCJ = - STRESS(ECI, ECS, FCS)
    #         XXP = FCI * AGC + FCJ * (AG - AGC) + (FS - FCI) * AST + (FS - FCJ) * AAS
    #         DPC = (FCI * A4C + FCJ * (A4I - A4C) + (FS - FCI) * A4S / RECS + (FS - FCJ) * A4SS / RECS) / XXP
    #     else:
    #         # INITIAL SECTION
    #         XXP = FCI * AG + (FS - FCI) * (AST + AAS)
    #         DPC = 0.0
    #         if TYPEC == 3:
    #             DPC = (FCI * A4I + (FS - FCI) * (A4S + A4SS) / RECS) / XXP
    #
    #         # print(f"XXP={XXP:10.3f}   DPC={DPC}")
    # # else:
    # if ISPALL == 0:
    #     # CONFINED SECTION
    #     if ITCONF != 0:
    #         XXPC = FCI * AGC + AST * (FS - FCI)
    #         DPCC = 0.0
    #         if TYPEC == 3:
    #             DPCC = (FCI * A4C + (FS - FCI) * A4S / RECS) / XXPC
    #         # print(f"XXPC={XXPC:10.3f}   DPCC={DPCC}")

    label.x30

    return XXP, DPC, XXPC, DPCC


def STRESS(ECI, EC, FC):
    _FCI = 0.
    if ECI <= 0.:
        _FCI = 0.
    else:
        _FCI = - np.interp(ECI, EC, FC)
    return _FCI


def STRHRD(EX, FYS, YMS, ESH, YSH, FSU, ESU, C1, C2):
    _FS = -YMS * EX
    FS1 = _FS
    if FS1 == 0.:
        FS1 = 0.000001
    SIGNS = _FS / abs(FS1)

    if abs(_FS) > FYS:
        _FS = FYS * SIGNS

    EXX = abs(EX)
    if EXX < ESU:
        if EXX > ESH:
            DS = EXX - ESH
            _FS = (FYS + (((C1 * DS) + C2) * DS + YSH) * DS) * SIGNS
    else:
        _FS = FSU * SIGNS

    return _FS


def CONC(ECU, B, EC, FC):
    COMP = 0.0
    ZZC = 0.0

    for i in range(0, len(EC)):
        if ECU >= EC[i + 1]:
            A1 = (FC[i] + FC[i + 1]) * (EC[i + 1] - EC[i])
            COMP = COMP + A1
            Z1 = ((EC[i + 1] - EC[i]) * (2.0 * FC[i] + FC[i + 1]) / (3.0 * (FC[i] + FC[i + 1]))+(ECU - EC[i + 1])) * A1
            ZZC = ZZC + Z1
        else:
            FCECU = FC[i] + (FC[i + 1] - FC[i]) * (ECU - EC[i]) / (EC[i + 1] - EC[i])
            A1 = (FC[i] + FCECU) * (ECU - EC[i])
            COMP = COMP + A1
            Z1 = ((ECU - EC[i]) * (2.0 * FC[i] + FCECU) / (3.0 * (FC[i] + FCECU))) * A1
            ZZC = ZZC + Z1
            break

    ZC = ZZC / (ECU * COMP)
    COMP = -0.5 * B * COMP / ECU

    return COMP, ZC


def CFRCS(C, T, ECU, A, Y, EC, FC):
    NLAYER = len(A) - 1
    XI = float(NLAYER) * C / T + 0.5
    I = int(XI)
    if I > NLAYER:
        I = NLAYER
    T1 = ECU / C
    T2 = (C - 0.5 * T) * T1

    XP = 0.0
    XM = 0.0
    for n in range(1, I+1):
        ECI = T2 + Y[n] * T1
        FCI = STRESS(ECI, EC, FC)
        T3 = A[n] * FCI
        XP = XP + T3
        XM = XM + T3 * Y[n]

    return XP, XM


def CFRCR(C, ECU, T, B, EC, FC):
    if C <= T:
        COMP, ZC = CONC(ECU, B, EC, FC)
    else:
        COMP, ZC = FLANGE(ECU, C, T, B, EC, FC)
    XP = C * COMP
    XM = XP * (T / 2. - ZC * C)

    # print(f'XP = {XP}     XM = {XM}')
    return XP, XM


@with_goto
def FLANGE(ECU, C, TT, BB, EC, FC):

    # print('FLANGE')
    COMPF = 0.0
    ZCF = 0.0
    COMP = 0.0
    ZZC = 0.0

    FCECU = - STRESS(ECU, EC, FC)

    for i in range(0, len(EC)):
        if COMP != 0.0:
            goto.x20
        ZZ = (ECU - EC[i]) * C / ECU
        if ZZ > TT:
            continue
        ECBOT = ECU * (1. - TT / C)
        FCBOT = np.interp(ECBOT, EC, FC)

        if EC[i] < ECU:
            goto.x10
        COMP = (FCBOT + FCECU) * (ECU - ECBOT)
        ZZC = ((ECU - ECBOT) * (2. * FCBOT + FCECU) / (3. * (FCBOT + FCECU))) * COMP
        break

        label.x10
        COMP = (FCBOT + FC[i]) * (EC[i] - ECBOT)
        ZZC = ((EC[i] - ECBOT) * (2. * FCBOT + FC[i]) / (3. * (FCBOT + FC[i])) + (ECU - EC[i])) * COMP

        label.x20
        if ECU < EC[i+1]:
            goto.x30
        A1 = (FC[i] + FC[i + 1]) * (EC[i + 1] - EC[i])
        COMP = COMP + A1
        Z1 = ((EC[i + 1] - EC[i]) * (2. * FC[i] + FC[i + 1]) / (3. * (FC[i] + FC[i + 1])) + (ECU - EC[i + 1])) * A1
        ZZC = ZZC + Z1
        goto.x40

        label.x30
        A1 = (FC[i] + FCECU) * (ECU - EC[i])
        COMP = COMP + A1
        Z1 = ((ECU - EC[i]) * (2. * FC[i] + FCECU) / (3. * (FC[i] + FCECU))) * A1
        ZZC = ZZC + Z1
        break

        label.x40
        continue

    label.x50
    ZCF = ZZC / (ECU * COMP)
    COMPF = -BB * COMP / (2.0 * ECU)

    return COMPF, ZCF

@with_goto
def YLDDUC(PHII, PHI2, XXMI, XXM2, ICOUNT, K, DUCT1, O):
    DUC = 0.0
    OO = 0.0
    if ICOUNT == 1:
        goto.x60
    if PHI2[K, 1] == 0.:
        goto.x10
    DUCT1[ICOUNT] = PHII[K, ICOUNT]/PHI2[K, 1]
    O[ICOUNT] = XXMI[K, ICOUNT] / XXM2[K, 1]

    label.x10
    if PHI2[K, 2] == 0.0:
        goto.x20
    DUC = PHII[K, ICOUNT] / PHI2[K, 2]
    OO = XXMI[K, ICOUNT] / XXM2[K, 2]

    label.x20
    if DUCT1[ICOUNT] > DUC:
        goto.x30
    DUCT1[ICOUNT] = DUC
    O[ICOUNT] = OO

    label.x30
    if ICOUNT != 2:
        goto.x60
    DUC = 0.0
    OO = 0.0
    if PHI2[K, 1] == 0.0:
        goto.x40
    DUCT1[1] = PHII[K, 1] / PHI2[K, 1]
    O[1] = XXMI[K, 1] / XXM2[K, 1]

    label.x40
    if PHI2[K, 2] == 0.0:
        goto.x50
    DUC = PHII[K, 1] / PHI2[K, 2]
    OO = XXMI[K, 1] / XXM2[K, 2]

    label.x50
    if DUCT1[1] > DUC:
        goto.x60
    DUCT1[1] = DUC
    O[1] = OO

    label.x60

    return DUCT1, O


@with_goto
def DUCTLE(PHI, XXM, AREA, DUCT, DUCMAX, K, N, NSTRNI, NSTRNC):
    PHIYMY_K = 0.0
    L = 4
    if N == 2:
        L = 4 + NSTRNI
    J = NSTRNI + 3
    if N == 2:
        J = NSTRNC + 3
        goto.x10

    A = PHI[K, 1]
    B = PHI[K, 2]

    if A == 0.:
        A = 100000.
    if B == 0.:
        B = 100000.

    PHIYMY_K = XXM[K, 1] * PHI[K, 1]
    PM = XXM[K, 2] * PHI[K, 2]

    if A > B:
        PHIYMY_K = PM

    label.x10
    PHIMAX = 0.0
    XMMAX = 0.0
    A = 0.0
    B = 0.0
    C = 0.0

    label.x20
    for I in range(1, 4):
        AREA[I] = 0.0
        DUCT[K, I] = 0.0

    for I in range(L, J):
        if XXM[K, I] == 0.0:
            goto.x40
        if PHI[K, I] > PHIMAX:
            PHIMAX = PHI[K, I]
        if abs(XXM[K, I]) > abs(XMMAX):
            XMMAX = XXM[K, I]
        D = PHI[K, I] - B
        A = A + 0.5 * D * (XXM[K, I] + C)
        B = PHI[K, I]
        C = XXM[K, I]
        AREA[I] = A
        if PHIYMY_K == 0.0:
            goto.x50
        DUCT[K, I] = A / PHIYMY_K + 0.5
        if DUCT[K, I] > DUCMAX:
            DUCMAX = DUCT[K, I]
        continue

        label.x40
        AREA[I] = 0.0

        label.x50
        DUCT[K, I] = 0.0

    AA = 0.0
    BB = 0.0
    CC = 0.0

    if N != 2:
        AA = A
        BB = B
        CC = C

    return DUCT, AREA, DUCMAX


@with_goto
def SHEAR(V, VM, I, K, AG, G, TL, AST, XL, XP, F, ASTL, D, BW, TYPEC, TYPES, ICONF):
    if I == 1 or V[I-1] == 0.0:
        goto.x10
    V[I] = V[I-1]
    VM[K, I] = VM[K, I-1]
    goto.x90

    label.x10
    if XP < 0.0:
        goto.x50

    if ICONF == 1:
        goto.x20
    if TYPEC == 2:
        goto.x30

    goto.x40

    label.x20
    if TYPES==2:
        goto.x30
    goto.x40

    label.x30
    A = AG * (G + 5000. * TL * AST / (XL * AG))
    C = 40.0 * XP
    E = TL * F
    AE = A + E
    V[I] = (AE + math.sqrt(AE * AE + 4.0 * A * C)) / 2.0
    goto.x80

    label.x40
    A = 2500. * ASTL * D
    B = XL / 2.0
    C = XP * (4.0 * TL - D) * 125.0
    E = BW * D * (G + F / BW)
    CABE = C + A + B * E
    V[I] = (CABE + math.sqrt(CABE * CABE - 4.0 * B * C * E)) / (2.0 * B)
    VMAX = BW * D * (F / BW + 1.842 * G * math.sqrt(1. + 0.29 * XP / AG))
    if V[I] > VMAX:
        V[I] = VMAX
    goto.x80

    label.x50
    A = 0.29 * XP / AG
    A = 1.0 + A
    if A < 0.0:
        A = 0.0
    A = 2.0 * A * G / 1.9
    AV = BW * D
    if TYPEC == 2:
        goto.x60
    if TYPES == 2 and ICONF == 1:
        goto.x60
    goto.x70

    label.x60
    R = TL / 2.0
    X = 2.0 * math.sqrt(2. * R * D - D * D)
    B = 2.0 * math.sqrt(X / (2. * R))
    if D > R:
        B = 2 * math.pi - B
    B = B * R
    AV = (B * R - X * (R - D)) / 2.0

    label.x70
    V[I] = A * AV + F * D

    label.x80
    VM[K, I] = V[I] * XL / 2000.
    V[I] = V[I] * 0.001

    label.x90
    return V, VM


