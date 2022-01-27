#!/usr/bin/env python
# Copyright 2020-2022 The PyFLOSIC Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Sebastian Schwalbe <theonov13@gmail.com>
#
from pyflosic2 import Atoms, parameters

# ---------------------------
# Information of test systems
# ---------------------------
# H2O  -> sp3 hybridized, 4 lone electrons, 2 lone pairs 
#         https://www.youtube.com/watch?v=NjsIkVdhy3Q
#         oxidation number O = -2 , H = +1 , Total = 0 
# COH2 -> sp2 hybridized, 4 lone electrons, 2 lone pairs  
#         https://www.youtube.com/watch?v=BJdqjs3SxjI
#         oxidation number O = -2 , C= 0 , H = +1, Total = 0
# NH3- -> sp3 hybridized, 2 lone electrons, 1 lone pair
#         oxidation number N = -3, H = +1, Total = 0 
#         https://www.youtube.com/watch?v=NjsIkVdhy3Q
# CH4  -> sp3 hybridized, no lone electrons
#         oxidation numbers C= -4, H = +1, Total = 0 
# C6H6 -> sp2 hybridized, no lone electrons, Trigonal Planar
#         oxidation numbers C = -1 , H = +1 , Total = 0  
# Note: Sum weighted oxidation numbers = Total charge of system 

def NH3():
    """
        NH3 example
        -----------
        Check lone electrons. 
    """
    sym = ['N']*1 + ['H']*3
    p0 = [0.0,0.0,0.0]
    p1 = [0.0,-0.9377,-0.3816]
    p2 = [0.8121,0.4689,-0.3816]
    p3 = [-0.8121,0.4689,-0.3816]
    pos = [p0,p1,p2,p3]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def FeF4():
    """
        FeF4 example
        ------------
        Check metal center coordination. 
    """
    sym = ['Fe']*1+['F']*4
    p0 = [0.0,0.0,0.0]
    p1 = [1.9173,0.0,0.0]
    p2 = [0.0,-1.9173,0.0]
    p3 = [-1.9173,0.0,0.0]
    p4 = [0.0,1.9173,0.0]
    pos = [p0,p1,p2,p3,p4]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def biphenyl():
    """
        biphenyl example
    """
    sym = ['C']*12+['H']*10
    p0 = [0.7234,-0.0002,-0.0001]
    p1 = [-0.7234,0.0003,-0.0001]
    p2 = [1.4206,0.7348,0.9586]
    p3 = [-1.4206,-0.9586,0.7349]
    p4 = [1.4211,-0.735,-0.9588]
    p5 = [-1.421,0.9588,-0.735]
    p6 = [2.8155,0.7351,0.9588]
    p7 = [-2.8154,-0.9588,0.735]
    p8 = [2.8159,-0.7348,-0.9586]
    p9 = [-2.8159,0.9586,-0.7349]
    p10 = [3.5131,0.0001,0.0001]
    p11 = [-3.5132,-0.0002,0.0001]
    p12 = [0.8924,1.3132,1.713]
    p13 = [-0.8923,-1.713,1.3131]
    p14 = [0.8931,-1.3134,-1.7133]
    p15 = [-0.8931,1.7134,-1.3134]
    p16 = [3.3585,1.3074,1.7051]
    p17 = [-3.3584,-1.7054,1.3072]
    p18 = [3.3593,-1.3069,-1.7051]
    p19 = [-3.3593,1.7049,-1.307]
    p20 = [4.5992,0.0003,0.0002]
    p21 = [-4.5992,-0.0004,0.0002]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms


def Conformer3D_CID_6334():
    """
        Conformer3D_CID_6334 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3 mol01 propane 
    """
    sym = ['C']*3+['H']*8
    p0 = [0.0,-0.5689,0.0]
    p1 = [-1.2571,0.2844,0.0]
    p2 = [1.2571,0.2845,0.0]
    p3 = [0.0,-1.2183,0.8824]
    p4 = [0.0,-1.2183,-0.8824]
    p5 = [-1.2969,0.9244,0.8873]
    p6 = [-1.2967,0.9245,-0.8872]
    p7 = [-2.1475,-0.352,-0.0001]
    p8 = [2.1475,-0.352,0.0]
    p9 = [1.2968,0.9245,0.8872]
    p10 = [1.2968,0.9245,-0.8872]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)

    return atoms

def Conformer3D_CID_8252():
    """
        Conformer3D_CID_8252 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3 mol02 propene 
    """
    sym = ['C']*3+['H']*6
    p0 = [1.2818,-0.2031,0.0]
    p1 = [-0.0643,0.4402,0.0]
    p2 = [-1.2175,-0.2371,0.0]
    p3 = [1.8429,0.1063,-0.8871]
    p4 = [1.2188,-1.2959,0.0]
    p5 = [1.8429,0.1063,0.8871]
    p6 = [-0.095,1.5262,0.0]
    p7 = [-2.1647,0.2911,0.0]
    p8 = [-1.239,-1.3212,0.0]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_7845():
    """
        Conformer3D_CID_7845 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3 mol03 Buta-1,3-diene
        Notes: 
            - need to adjust eps=0.45 to eps=0.2 otherwise E_Bond wrong
            - this change does not influence 
                - f_name = 'Conformer3D_CID_6334'
                - f_name = 'Conformer3D_CID_8252'
    """
    sym = ['C']*4+['H']*6
    p0 = [-0.6022,0.3972,0.0]
    p1 = [0.6024,-0.3975,0.0]
    p2 = [-1.8315,-0.1305,0.0]
    p3 = [1.8314,0.1308,0.0]
    p4 = [-0.4975,1.4789,0.0001]
    p5 = [0.4979,-1.4792,0.0001]
    p6 = [-2.7035,0.5151,0.0]
    p7 = [-1.9975,-1.2027,0.0]
    p8 = [2.7036,-0.5143,0.0]
    p9 = [1.9969,1.203,0.0]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_6335():
    """
        Conformer3D_CID_6335 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3 mol04 propyne
        Notes: 
            - current perception does not find triple bond 
            - get_guess_bond_order(atoms) -> rc3 = rc2 - eps adjusted from 0.15 to 0.1 
            - E_Angle had a wrong else case: fixed it based on this example 
    """
    sym = ['C']*3+['H']*4
    p0 = [-1.375,0.0001,0.0]
    p1 = [0.0873,-0.0002,0.0001]
    p2 = [1.2877,0.0001,-0.0001]
    p3 = [-1.7644,0.066,1.0204]
    p4 = [-1.7641,0.851,-0.5673]
    p5 = [-1.7644,-0.9165,-0.4533]
    p6 = [2.3527,0.0003,-0.0002]
    pos = [p0,p1,p2,p3,p4,p5,p6]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_674():
    """
        Conformer3D_CID_674 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3 mol05 Dimethylamine
    """
    sym = ['N']*1+['C']*2+['H']*7
    p0 = [0.0001,-0.5504,0.0]
    p1 = [-1.2001,0.2752,0.0]
    p2 = [1.2001,0.2752,0.0]
    p3 = [0.0,-1.1423,0.8302]
    p4 = [-1.2506,0.9105,0.8903]
    p5 = [-2.0853,-0.3685,-0.0051]
    p6 = [-1.2467,0.906,-0.8936]
    p7 = [2.0853,-0.3682,-0.005]
    p8 = [1.2506,0.9106,0.8903]
    p9 = [1.2467,0.906,-0.8937]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_1146():
    """
        Conformer3D_CID_1146 example
        Automatic Molecular Structure Perception for theUniversal Force Field
        Tab. 3 mol06 Trimethylamine
    """
    sym = ['N']*1+['C']*3+['H']*9
    p0 = [0.0,0.0,0.3474]
    p1 = [-0.5373,-1.2788,-0.1158]
    p2 = [-0.8388,1.1047,-0.1158]
    p3 = [1.3762,0.1741,-0.1158]
    p4 = [-1.5537,-1.4294,0.2649]
    p5 = [0.0664,-2.1102,0.265]
    p6 = [-0.5653,-1.3456,-1.2096]
    p7 = [-1.8607,0.9976,0.2649]
    p8 = [-0.8825,1.1624,-1.2095]
    p9 = [-0.4611,2.0603,0.265]
    p10 = [1.7943,1.1125,0.265]
    p11 = [1.448,0.1832,-1.2095]
    p12 = [2.0148,-0.6309,0.2649]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms


def Conformer3D_CID_142199():
    """
        Conformer3D_CID_142199 example
        Automatic Molecular Structure Perception for theUniversal Force Field
        Tab. 3 mol07 Diazene-dimethyl
        Note:
            - we get for O -> sp 2.5  openbabel gets 3
            - I used numpy.ceil() for rounding up
    """
    sym = ['O']*2+['N']*2+['C']*2+['H']*6
    p0 = [-1.2346,-1.2528,-0.0005]
    p1 = [1.5007,-1.1487,0.0001]
    p2 = [-0.7177,-0.0885,0.0005]
    p3 = [0.701,0.0377,0.0003]
    p4 = [-1.5839,1.0914,0.0]
    p5 = [1.3344,1.3608,-0.0004]
    p6 = [-2.6278,0.7671,0.0007]
    p7 = [-1.3833,1.6736,-0.9014]
    p8 = [-1.3827,1.6748,0.9007]
    p9 = [1.0242,1.897,0.8994]
    p10 = [1.0239,1.8964,-0.9004]
    p11 = [2.4226,1.2539,-0.0006]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_6342():
    """
        Conformer3D_CID_6342 example
        Automatic Molecular Structure Perception for theUniversal Force Field
        Tab. 3 mol08 Acetonitrile
        Note:
            - used to isolate/catch some ZeroDivsionErrors in uff.py
    """
    sym = ['N']*1+['C']*2+['H']*3
    p0 = [1.2608,0.0,0.0]
    p1 = [-1.3613,0.0,0.0]
    p2 = [0.1006,0.0,0.0]
    p3 = [-1.75,-0.8301,0.5974]
    p4 = [-1.7501,-0.1022,-1.0175]
    p5 = [-1.75,0.9324,0.4202]
    pos = [p0,p1,p2,p3,p4,p5]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_14055():
    """
        Conformer3D_CID_14055 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3 mol09 Cyanoacetylene
        Notes: 
            - simple bo fails 
            - magicbonds needed 
    """
    sym = ['N']*1+['C']*3+['H']*1
    p0 = [-1.8561,0.0,0.0]
    p1 = [0.6761,-0.0003,-0.0001]
    p2 = [-0.6961,0.0001,0.0]
    p3 = [1.8761,0.0002,0.0]
    p4 = [2.9411,0.0006,0.0002]
    pos = [p0,p1,p2,p3,p4]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms


def Conformer3D_CID_7855():
    """
        Conformer3D_CID_7855 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3 mol10 Acrylonitrile
    """
    sym = ['N']*1+['C']*3+['H']*3
    p0 = [-1.7665,-0.2148,0.0]
    p1 = [0.7119,0.5015,0.0]
    p2 = [1.7057,-0.3917,0.0]
    p3 = [-0.6511,0.105,0.0]
    p4 = [0.94,1.5621,0.0]
    p5 = [2.7387,-0.0602,0.0]
    p6 = [1.5184,-1.4606,0.0]
    pos = [p0,p1,p2,p3,p4,p5,p6]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_8254():
    """
        Conformer3D_CID_8254 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab 3. mol11 Dimethyl ether
        Notes: 
            - helps to detect spelling issue in uff.py E_phi for sp3 - sp3 case 
    """
    sym = ['O']*1+['C']*2+['H']*6
    p0 = [0.0,0.533,0.0]
    p1 = [1.175,-0.2665,0.0]
    p2 = [-1.175,-0.2665,0.0]
    p3 = [1.2129,-0.8918,0.8972]
    p4 = [2.0436,0.3974,0.0]
    p5 = [1.2129,-0.8918,-0.8972]
    p6 = [-1.2129,-0.8918,0.8973]
    p7 = [-1.2128,-0.8919,-0.8973]
    p8 = [-2.0436,0.3974,-0.0001]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_10903():
    """
        Conformer3D_CID_10903 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab 3. mol12 Methoxyethane
    """
    sym = ['O']*1+['C']*3+['H']*8
    p0 = [-0.5233,0.4709,0.0]
    p1 = [0.4954,-0.5201,0.0]
    p2 = [1.8469,0.1619,0.0]
    p3 = [-1.8191,-0.1127,0.0]
    p4 = [0.3995,-1.1496,0.8917]
    p5 = [0.3994,-1.1496,-0.8917]
    p6 = [2.6561,-0.5738,0.0]
    p7 = [1.9543,0.8051,-0.8796]
    p8 = [1.9544,0.8052,0.8796]
    p9 = [-1.9655,-0.7217,-0.8974]
    p10 = [-2.5592,0.692,0.0]
    p11 = [-1.9655,-0.7217,0.8972]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_7861():
    """
        Conformer3D_CID_7861 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab 3. mol13 Methyl vinyl ether
        Note: adjusted get_max_valence co == 2 -> max = 3 (original value) 
              else KT/SS value 
    """
    sym = ['O']*1+['C']*3+['H']*6
    p0 = [0.5506,0.5121,0.0712]
    p1 = [1.7483,-0.2328,-0.1202]
    p2 = [-0.5272,-0.2973,0.2071]
    p3 = [-1.7717,0.0179,-0.1581]
    p4 = [2.5641,0.4751,-0.2937]
    p5 = [1.6695,-0.8861,-0.9963]
    p6 = [1.9902,-0.8192,0.773]
    p7 = [-0.3097,-1.2536,0.6649]
    p8 = [-2.5852,-0.6832,-0.009]
    p9 = [-1.9956,0.9778,-0.6101]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    # openbabel mmtypes O_2 assignment different 
    mmtypes = ['O_2', 'C_3', 'C_2', 'C_2', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_']
    return atoms

def Conformer3D_CID_177():
    """
        Conformer3D_CID_177 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab 3. mol14 Acetaldehyde
    """
    sym = ['O']*1+['C']*2+['H']*4
    p0 = [1.1443,0.2412,0.0]
    p1 = [-1.2574,0.1815,0.0]
    p2 = [0.113,-0.4226,0.0]
    p3 = [-1.7938,-0.1493,0.8924]
    p4 = [-1.1865,1.2719,0.0016]
    p5 = [-1.7928,-0.1468,-0.8938]
    p6 = [0.1478,-1.5252,-0.0007]
    pos = [p0,p1,p2,p3,p4,p5,p6]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_180():
    """
        Conformer3D_CID_180 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3. mol15 Acetone
    """
    sym = ['O']*1+['C']*3+['H']*6
    p0 = [0.0003,-1.3171,-0.0002]
    p1 = [0.0,-0.0872,0.0006]
    p2 = [1.281,0.7024,-0.0002]
    p3 = [-1.2813,0.7019,-0.0002]
    p4 = [1.3279,1.3235,-0.898]
    p5 = [1.326,1.3282,0.8945]
    p6 = [2.1351,0.0196,0.0027]
    p7 = [-2.1352,0.0187,0.0027]
    p8 = [-1.3284,1.323,-0.898]
    p9 = [-1.3266,1.3278,0.8945]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_12222():
    """
        Conformer3D_CID_12222 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3. mol16 Propynal
    """
    sym = ['O']*1+['C']*3+['H']*2
    p0 = [-1.6403,0.3873,0.0]
    p1 = [-0.7691,-0.47,0.0]
    p2 = [0.6236,-0.1085,0.0001]
    p3 = [1.7859,0.1912,0.0]
    p4 = [-0.9836,-1.5502,0.0006]
    p5 = [2.8171,0.4572,-0.0002]
    pos = [p0,p1,p2,p3,p4,p5]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_7847():
    """
        Conformer3D_CID_7847 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3. mol17 Acrolein 
    """
    sym = ['O']*1+['C']*3+['H']*4
    p0 = [-1.7478,-0.1165,-0.0002]
    p1 = [0.5936,-0.4363,0.0002]
    p2 = [-0.6303,0.3856,0.0002]
    p3 = [1.7844,0.1672,-0.0002]
    p4 = [0.4972,-1.5148,0.0003]
    p5 = [-0.4849,1.4788,0.0002]
    p6 = [2.6939,-0.4243,-0.0002]
    p7 = [1.8872,1.2469,-0.0004]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_7865():
    """
        Conformer3D_CID_7865 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3. mol18 Methyl formate        
        UFF, a full periodic table force field for molecular mechanics and molecular dynamics simulations
        Fig. 6 (O-containing), C=O, C-O (ester), C-O (other)

    """
    sym = ['O']*2+['C']*2+['H']*4
    p0 = [0.6458,-0.6402,0.0]
    p1 = [-1.3384,0.5525,0.0]
    p2 = [1.3964,0.5783,0.0]
    p3 = [-0.7038,-0.4907,0.0]
    p4 = [2.4595,0.3231,-0.0001]
    p5 = [1.1749,1.1599,0.9001]
    p6 = [1.1748,1.1599,-0.9001]
    p7 = [-1.1652,-1.4902,-0.0001]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_178():
    """
        Conformer3D_CID_178 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3. mol19 Acetamide
        UFF, a full periodic table force field for molecular mechanics and molecular dynamics simulations
        Fig. 7 top, C=O, C-C, C-(1.4)-N
        Note: Openbabel set the bo for the resonant bond correct but not the type
    """
    sym = ['O']*1+['N']*1+['C']*2+['H']*5
    p0 = [0.6073,-1.1657,0.0018]
    p1 = [0.7522,1.1306,0.0015]
    p2 = [-1.4275,0.0969,0.0013]
    p3 = [0.068,-0.0618,-0.0046]
    p4 = [-1.8768,-0.6906,-0.6101]
    p5 = [-1.7917,0.014,1.0288]
    p6 = [-1.7274,1.0655,-0.4084]
    p7 = [1.7667,1.1492,0.0031]
    p8 = [0.2815,2.0298,0.0081]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_31254():
    """
        Conformer3D_CID_31254 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Tab. 3. mol20 N-Methylformamide
        UFF, a full periodic table force field for molecular mechanics and molecular dynamics simulations
        Fig. 7 bottom, C=O, C-(1.4)-N, C-N 
        Note: Openbabel set the bo for the resonant bond correct but not the type 
    """
    sym = ['O']*1+['N']*1+['C']*2+['H']*5
    p0 = [1.4062,0.5547,0.0]
    p1 = [-0.6252,-0.6033,0.0]
    p2 = [-1.527,0.525,0.0]
    p3 = [0.746,-0.4764,0.0]
    p4 = [-2.1553,0.46,0.8917]
    p5 = [-2.156,0.4593,-0.8911]
    p6 = [-0.9796,1.4706,-0.0005]
    p7 = [-1.0276,-1.5359,0.0]
    p8 = [1.2257,-1.4691,0.0]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def H2O_KT():
    """
        H2O_KT example
        Translated and rotated H2O to 
        test rotation matrix and lone electron 
        assignment.         
    """
    sym = ['O']*1+['H']*2
    p0 = [1.11093225,-6.5640966,-0.20810053]
    p1 = [1.97882381,-6.68264513,-0.59545642]
    p2 = [0.81024394,-7.45325827,-0.01754305]
    pos = [p0,p1,p2]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_7855_KT():
    """
        Conformer3D_CID_7855_KT example
    """
    sym = ['N']*1+['C']*3+['H']*3
    p0 = [2.77471903,1.65178933,0.09635351]
    p1 = [0.34235971,0.87146964,0.4572989]
    p2 = [-0.32862475,0.19362276,-0.47851526]
    p3 = [1.68070212,1.29981322,0.25644415]
    p4 = [-0.13796417,1.10717542,1.40103283]
    p5 = [-1.35092937,-0.12142973,-0.29791503]
    p6 = [0.11683744,-0.06114062,-1.43469911]
    pos = [p0,p1,p2,p3,p4,p5,p6]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_931():
    """
        Conformer3D_CID_931 example
        Naphtalene 
        Note: two aromatic rings 
    """
    sym = ['C']*10+['H']*8
    p0 = [0.0,-0.7076,0.0]
    p1 = [0.0,0.7076,0.0001]
    p2 = [1.225,-1.3944,0.0001]
    p3 = [1.225,1.3944,0.0]
    p4 = [-1.225,-1.3943,0.0]
    p5 = [-1.225,1.3943,0.0]
    p6 = [2.4327,-0.6958,0.0]
    p7 = [2.4327,0.6959,-0.0001]
    p8 = [-2.4327,-0.6958,-0.0001]
    p9 = [-2.4327,0.6958,0.0]
    p10 = [1.2489,-2.4822,0.0001]
    p11 = [1.2489,2.4821,-0.0001]
    p12 = [-1.2489,-2.4822,-0.0001]
    p13 = [-1.249,2.4821,0.0001]
    p14 = [3.3733,-1.239,-0.0001]
    p15 = [3.3732,1.2391,-0.0001]
    p16 = [-3.3733,-1.239,-0.0001]
    p17 = [-3.3732,1.239,0.0]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms


def Conformer3D_CID_638088():
    """
        Conformer3D_CID_638088 example
        Automatic Molecular Structure Perception for the Universal Force Field
        Fig 3.
        trans-stilbene 
    """
    sym = ['C']*14+['H']*12
    p0 = [1.9294,0.2286,-0.0061]
    p1 = [-1.9133,-0.231,-0.0061]
    p2 = [0.4774,0.4795,-0.0158]
    p3 = [-0.4799,-0.4781,-0.0158]
    p4 = [2.4022,-1.0031,0.417]
    p5 = [-2.4053,1.0038,0.417]
    p6 = [2.7937,1.229,-0.4205]
    p7 = [-2.7959,-1.2285,-0.4205]
    p8 = [3.7766,-1.2409,0.4258]
    p9 = [-3.7798,1.2411,0.4257]
    p10 = [4.1681,0.9911,-0.4118]
    p11 = [-4.1704,-0.9912,-0.4118]
    p12 = [4.6596,-0.2439,0.0114]
    p13 = [-4.6623,0.2436,0.0114]
    p14 = [0.2092,1.5323,-0.0414]
    p15 = [-0.2072,-1.5296,-0.0433]
    p16 = [1.7546,-1.7995,0.7694]
    p17 = [-1.7598,1.8027,0.7695]
    p18 = [2.4268,2.1959,-0.7544]
    p19 = [-2.4317,-2.1969,-0.7551]
    p20 = [4.1602,-2.2005,0.7602]
    p21 = [-4.1639,2.2006,0.76]
    p22 = [4.8558,1.7673,-0.7345]
    p23 = [-4.8578,-1.7677,-0.7345]
    p24 = [5.7298,-0.4286,0.0195]
    p25 = [-5.7326,0.428,0.0193]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms


def Conformer3D_CID_9115():
    """
        Conformer3D_CID_9115 example
        Coronene
    """
    sym = ['C']*24+['H']*12
    p0 = [-0.5083,-1.3198,0.0]
    p1 = [0.8889,-1.1001,-0.0001]
    p2 = [-1.3972,-0.2197,0.0]
    p3 = [1.3972,0.2198,-0.0001]
    p4 = [-0.8889,1.1001,0.0]
    p5 = [0.5083,1.3198,0.0]
    p6 = [-1.016,-2.6382,0.0]
    p7 = [1.7769,-2.199,0.0]
    p8 = [-2.793,-0.4393,-0.0001]
    p9 = [2.7929,0.4392,-0.0001]
    p10 = [-1.7769,2.199,0.0001]
    p11 = [1.0161,2.6383,0.0]
    p12 = [-2.4028,-2.8386,0.0]
    p13 = [1.2571,-3.5001,0.0002]
    p14 = [-0.1218,-3.7169,0.0002]
    p15 = [3.28,1.753,-0.0001]
    p16 = [-1.2569,3.5001,0.0001]
    p17 = [-3.6599,0.6615,-0.0001]
    p18 = [2.4028,2.8386,0.0001]
    p19 = [-3.1582,1.9641,0.0]
    p20 = [-3.28,-1.753,-0.0002]
    p21 = [0.1219,3.717,0.0001]
    p22 = [3.1581,-1.964,0.0]
    p23 = [3.6598,-0.6615,-0.0001]
    p24 = [-2.8165,-3.845,0.0]
    p25 = [1.9217,-4.3616,0.0004]
    p26 = [-0.49,-4.7409,0.0004]
    p27 = [2.8166,3.845,0.0002]
    p28 = [-1.9215,4.3616,0.0002]
    p29 = [-4.3508,-1.9462,-0.0002]
    p30 = [-3.8609,2.7949,0.0001]
    p31 = [4.3508,1.9461,-0.0001]
    p32 = [3.8609,-2.7948,0.0]
    p33 = [-4.7383,0.5167,-0.0001]
    p34 = [0.49,4.741,0.0002]
    p35 = [4.7382,-0.5167,-0.0001]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,p28,p29,p30,p31,p32,p33,p34,p35]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_8418():
    """
        Conformer3D_CID_8418 example
        Anthracene
    """
    sym = ['C']*14+['H']*10
    p0 = [-1.225,0.706,0.0001]
    p1 = [-1.2251,-0.7061,0.0001]
    p2 = [1.2251,0.7061,0.0002]
    p3 = [1.2251,-0.7061,0.0001]
    p4 = [0.0,1.3937,0.0001]
    p5 = [0.0,-1.3938,0.0]
    p6 = [-2.4504,1.393,-0.0001]
    p7 = [-2.4505,-1.393,0.0]
    p8 = [2.4505,1.3929,0.0]
    p9 = [2.4505,-1.3929,0.0]
    p10 = [-3.6587,0.6956,-0.0001]
    p11 = [-3.6588,-0.6955,-0.0001]
    p12 = [3.6587,0.6956,-0.0002]
    p13 = [3.6587,-0.6956,-0.0002]
    p14 = [0.0,2.4838,0.0]
    p15 = [0.0,-2.4839,-0.0001]
    p16 = [-2.4742,2.4808,-0.0001]
    p17 = [-2.4744,-2.4809,0.0]
    p18 = [2.4742,2.4808,0.0]
    p19 = [2.4743,-2.4808,0.0]
    p20 = [-4.5989,1.2394,-0.0003]
    p21 = [-4.5991,-1.2391,-0.0002]
    p22 = [4.5989,1.2393,-0.0003]
    p23 = [4.5989,-1.2393,-0.0004]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms

def Conformer3D_CID_31423():
    """
        Conformer3D_CID_31423 example
        Pyrene
    """
    sym = ['C']*16+['H']*10
    p0 = [-0.7085,0.0,0.0]
    p1 = [0.7085,0.0,0.0]
    p2 = [-1.4154,1.225,0.0]
    p3 = [1.4154,1.2251,0.0]
    p4 = [-1.4154,-1.2251,0.0]
    p5 = [1.4154,-1.225,0.0]
    p6 = [-0.6982,2.429,0.0]
    p7 = [0.6981,2.429,0.0]
    p8 = [-0.6981,-2.429,0.0]
    p9 = [0.6982,-2.429,0.0]
    p10 = [-2.8178,1.2083,0.0]
    p11 = [2.8178,1.2084,-0.0001]
    p12 = [-2.8178,-1.2084,0.0]
    p13 = [2.8178,-1.2083,0.0]
    p14 = [-3.5126,0.0,0.0]
    p15 = [3.5126,0.0,0.0]
    p16 = [-1.2205,3.3836,0.0]
    p17 = [1.2203,3.3836,0.0]
    p18 = [-1.2203,-3.3836,0.0]
    p19 = [1.2205,-3.3836,0.0]
    p20 = [-3.3829,2.138,0.0001]
    p21 = [3.3827,2.1382,-0.0001]
    p22 = [-3.3827,-2.1382,-0.0001]
    p23 = [3.3828,-2.138,0.0001]
    p24 = [-4.5989,0.0,0.0]
    p25 = [4.5989,0.0001,0.0]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin)
    return atoms



ref_openbabel = {'H2O' : {'E_Angle': 6.991159153957004e-05,
                          'E_Bond': 4.9464243003785375,
                          'E_OOP': 0.0,
                          'E_Torsion': 0.0,
                          'E_tot': 4.946494211970077,
                          'E_vdW': 0.0,
                          'mmtypes' : ['O_3', 'H_', 'H_']},
                'H2O_KT': {'E_Angle': 6.990895347193351e-05,
                           'E_Bond': 4.946423683898072,
                           'E_OOP': 0.0,
                           'E_Torsion': 0.0,
                           'E_tot': 4.946493592851544,
                           'E_vdW': 0.0,
                           'mmtypes': ['O_3', 'H_', 'H_']},
                'CH4' : {'E_Angle': 4.3039381651564857e-07,
                         'E_Bond': 2.158972256420181,
                         'E_OOP': 0.0,
                         'E_Torsion': 0.0,
                         'E_tot': 2.1589726868139976,
                         'E_vdW': 0.0,
                         'mmtypes' : ['C_3', 'H_', 'H_', 'H_', 'H_']},
                'COH2': {'E_Angle': 0.020214229249171545,
                         'E_Bond': 26.444785312225616,
                         'E_OOP': 0.0,
                         'E_Torsion': 0.0,
                         'E_tot': 26.464999541474786,
                         'E_vdW': 0.0,
                         'mmtypes': ['O_2', 'C_2', 'H_', 'H_']},
                'C6H6': {'E_Angle': 0.12130338259682961,
                          'E_Bond': 3.0191169439793537,
                          'E_OOP': 2.1079788888665796e-06,
                          'E_Torsion': 0.00017243230257741606,
                          'E_tot': 44.64239866113353,
                          'E_vdW': 41.50180379427588,
                          'mmtypes': ['C_R','C_R','C_R','C_R','C_R','C_R','H_','H_','H_','H_','H_','H_']},
                 'Conformer3D_CID_6334' : {'E_Angle': 2.174232222652353,
                                           'E_Bond': 2.4273563431729066,
                                           'E_OOP': 0.0,
                                           'E_Torsion': 0.1347703333864017,
                                           'E_tot': 7.689389069000933,
                                           'E_vdW': 2.9530301697892716,
                                           'mmtypes' : ['C_3', 'C_3', 'C_3', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_8252' : {'E_Angle': 4.026246451038748,
                                           'E_Bond': 1.1123255605520865,
                                           'E_OOP': 0.0,
                                           'E_Torsion': 0.00852059920436809,
                                           'E_tot': 7.64365738432907,
                                           'E_vdW': 2.4965647735338674,
                                           'mmtypes': ['C_3', 'C_2', 'C_2', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_7845' : {'E_Angle': 5.027888485276356,
                                           'E_Bond': 1.0685077925833193,
                                           'E_OOP': 1.986518874653065e-07,
                                           'E_Torsion': 9.915601828213208e-06,
                                           'E_tot': 11.29298820986676,
                                           'E_vdW': 5.196581817753369,
                                           'mmtypes': ['C_2', 'C_2', 'C_2', 'C_2', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_6335' : {'E_Angle': 0.7352432449154617,
                                           'E_Bond': 1.1042646843470456,
                                           'E_OOP': 0.0,
                                           'E_Torsion': 0.0,
                                           'E_tot': 0.7118387409571882,
                                           'E_vdW': -1.127669188305319,
                                           'mmtypes': ['C_3', 'C_1', 'C_1', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_674'  : {'E_Angle': 6.245940573231682,
                                           'E_Bond': 3.290513492463346,
                                           'E_OOP': 10.329949448391869,
                                           'E_Torsion': 0.026827015471103822,
                                           'E_tot': 28.24039569437523,
                                           'E_vdW': 8.347165164817229,
                                           'mmtypes' : ['N_3', 'C_3', 'C_3', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_1146' : {'E_Angle': 11.683934520620262,
                                           'E_Bond': 3.134164013993492,
                                           'E_OOP': 9.725253465358751,
                                           'E_Torsion': 0.11873643149005843,
                                           'E_tot': 44.130535180574924,
                                           'E_vdW': 19.468446749112363,
                                           'mmtypes' : ['N_3', 'C_3', 'C_3', 'C_3', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_142199' : {'E_Angle': 245.50170608134755,
                                             'E_Bond': 45.6264517438789,
                                             'E_OOP': 2.289436757932428e-05,
                                             'E_Torsion': 28.29847086663093,
                                             'E_tot': 333.03920173244177,
                                             'E_vdW': 13.612550146216787,
                                             'mmtypes' : ['O_3', 'O_3', 'N_3', 'N_3', 'C_3', 'C_3', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_6342' :  {'E_Angle': 0.7036859885838535,
                                            'E_Bond': 1.0196347527458984,
                                            'E_OOP': 0.0,
                                            'E_Torsion': 0.0,
                                            'E_tot': 1.0448316167481901,
                                            'E_vdW': -0.6784891245815617,
                                            'mmtypes' : ['N_1', 'C_3', 'C_1', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_14055' : {'E_Angle': 0.00016907350374276793,
                                            'E_Bond': 3.047922868663565,
                                            'E_OOP': 0.0,
                                            'E_Torsion': 0.0,
                                            'E_tot': 2.4123040280268864,
                                            'E_vdW': -0.6357879141404212,
                                            'mmtypes' : ['N_1', 'C_1', 'C_1', 'C_1', 'H_']},
                 'Conformer3D_CID_7855'  : {'E_Angle': 1.2359123624506336,
                                             'E_Bond': 0.7485971187627263,
                                             'E_OOP': 0.0,
                                             'E_Torsion': 0.0,
                                             'E_tot': 3.1247897753046,
                                             'E_vdW': 1.14028029409124,
                                             'mmtypes' : ['N_1', 'C_2', 'C_2', 'C_1', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_8254'  : {'E_Angle': 10.324079738052124,
                                            'E_Bond': 5.364048463429649,
                                            'E_OOP': 0.0,
                                            'E_Torsion': 25.300094120158263,
                                            'E_tot': 50.96488631509783,
                                            'E_vdW': 9.976663993457791,
                                            'mmtypes' : ['O_3', 'C_3', 'C_3', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_10903' : {'E_Angle': 10.73311062355622,
                                            'E_Bond': 5.805819557394422,
                                            'E_OOP': 0.0,
                                            'E_Torsion': 25.642341625979228,
                                            'E_tot': 53.56526398977961,
                                            'E_vdW': 11.383992182849738,
                                            'mmtypes' : ['O_3', 'C_3', 'C_3', 'C_3', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_7861'  : {'E_Angle': 19.02403805970977,
                                            'E_Bond': 7.876721655358854,
                                            'E_OOP': 0.020436032686126104,
                                            'E_Torsion': 22.190500433372016,
                                            'E_tot': 64.13853920089933,
                                            'E_vdW': 15.026843019772558,
                                            'mmtypes' : ['O_2', 'C_3', 'C_2', 'C_2', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_177'   : {'E_Angle': 3.512596909341777,
                                            'E_Bond': 1.985461467547289,
                                            'E_OOP': 3.937646022506902e-05,
                                            'E_Torsion': 0.0007860398863547317,
                                            'E_tot': 6.456343239834634,
                                            'E_vdW': 0.9574594465989893,
                                            'mmtypes' : ['O_2', 'C_3', 'C_2', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_180'  :  {'E_Angle': 2.326529384255209,
                                            'E_Bond': 3.370465496024238,
                                            'E_OOP': 0.0003092456527495946,
                                            'E_Torsion': 0.029308463029759323,
                                            'E_tot': 9.200407848544653,
                                            'E_vdW': 3.4737952595826966,
                                            'mmtypes' : ['O_2', 'C_2', 'C_3', 'C_3', 'H_', 'H_', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_12222' : {'E_Angle': 2.5736865761029875,
                                           'E_Bond': 0.5928085957608717,
                                           'E_OOP': 3.876960129763241e-05,
                                           'E_Torsion': 0.0,
                                           'E_tot': 2.3293419138828773,
                                           'E_vdW': -0.83719202758228,
                                           'mmtypes' : ['O_2', 'C_2', 'C_1', 'C_1', 'H_', 'H_']},
                 'Conformer3D_CID_7847'  : {'E_Angle': 3.1157300420071192,
                                            'E_Bond': 0.8683528961780178,
                                            'E_OOP': 1.2747575410159228e-05,
                                            'E_Torsion': 5.302145738001483e-05,
                                            'E_tot': 9.232262864988055,
                                            'E_vdW': 5.248114157770128,
                                            'mmtypes' : ['O_2', 'C_2', 'C_2', 'C_2', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_7865'  : {'E_Angle': 32.262878911631695,
                                            'E_Bond': 10.611991683357829,
                                            'E_OOP': 7.506965745029958e-07,
                                            'E_Torsion': 0.036217489744121534,
                                            'E_tot': 54.18324682764665,
                                            'E_vdW': 11.27215799221643,
                                            'mmtypes' : ['O_2', 'O_2', 'C_3', 'C_2', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_178'   : {'E_Angle': 13.946884612811324,
                                            'E_Bond': 4.901905139029269,
                                            'E_OOP': 0.01971527438535843,
                                            'E_Torsion': 22.3445536933493,
                                            'E_tot': 49.80932767760773,
                                            'E_vdW': 8.596268958032484,
                                            'mmtypes': ['O_2', 'N_2', 'C_3', 'C_2', 'H_', 'H_', 'H_', 'H_', 'H_']},
                 'Conformer3D_CID_31254' : {'E_Angle': 29.93634712641768,
                                            'E_Bond': 4.928736119660642,
                                            'E_OOP': 0.0,
                                            'E_Torsion': 0.031165003091171248,
                                            'E_tot': 42.562414976414104,
                                            'E_vdW': 7.6661667272446135,
                                            'mmtypes' : ['O_2', 'N_2', 'C_3', 'C_2', 'H_', 'H_', 'H_', 'H_', 'H_']},
                'Conformer3D_CID_7855_KT': {'E_Angle': 1.235912457990007,
                             'E_Bond': 0.7485968440844849,
                             'E_OOP': 0.0,
                             'E_Torsion': 4.706538139262027e-11,
                             'E_tot': 3.1247895344924785,
                             'E_vdW': 1.1402802323709214,
                             'mmtypes': ['N_1',
                                         'C_2',
                                         'C_2',
                                         'C_1',
                                         'H_',
                                         'H_',
                                         'H_']},
                'Conformer3D_CID_931': {'E_Angle': 1.8816913535864475,
                         'E_Bond': 10.341722493511424,
                         'E_OOP': 2.539483385997077e-06,
                         'E_Torsion': 8.10940921420576e-05,
                         'E_tot': 92.1445370715043,
                         'E_vdW': 79.9210395908309,
                         'mmtypes': ['C_R',
                                     'C_R',
                                     'C_R',
                                     'C_R',
                                     'C_R',
                                     'C_R',
                                     'C_R',
                                     'C_R',
                                     'C_R',
                                     'C_R',
                                     'H_',
                                     'H_',
                                     'H_',
                                     'H_',
                                     'H_',
                                     'H_',
                                     'H_',
                                     'H_']},
                'Conformer3D_CID_638088': {'E_Angle': 15.352862463107726,
                            'E_Bond': 6.935073097515105,
                            'E_OOP': 0.018863698483669592,
                            'E_Torsion': 38.740248747912815,
                            'E_tot': 175.39369707651338,
                            'E_vdW': 114.34664906949406,
                            'mmtypes': ['C_R',
                                        'C_R',
                                        'C_2',
                                        'C_2',
                                        'C_R',
                                        'C_R',
                                        'C_R',
                                        'C_R',
                                        'C_R',
                                        'C_R',
                                        'C_R',
                                        'C_R',
                                        'C_R',
                                        'C_R',
                                        'H_',
                                        'H_',
                                        'H_',
                                        'H_',
                                        'H_',
                                        'H_',
                                        'H_',
                                        'H_',
                                        'H_',
                                        'H_',
                                        'H_',
                                        'H_']},
                'Conformer3D_CID_9115': {'E_Angle': 5.756054243786933,
                          'E_Bond': 42.526431551116595,
                          'E_OOP': 3.1311475036654088e-06,
                          'E_Torsion': 0.00025142090607077844,
                          'E_tot': 295.0647143877344,
                          'E_vdW': 246.78197404077727,
                          'mmtypes': ['C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_']},
                'Conformer3D_CID_8418': {'E_Angle': 3.552229859367222,
                          'E_Bond': 17.439780749711343,
                          'E_OOP': 2.4526597476837606e-06,
                          'E_Torsion': 0.00010668356242433906,
                          'E_tot': 140.15157813600092,
                          'E_vdW': 119.15945839070018,
                          'mmtypes': ['C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'C_R',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_',
                                      'H_']},
                'Conformer3D_CID_31423': {'E_Angle': 3.831629866896717,
                           'E_Bond': 23.677063159000383,
                           'E_OOP': 7.029173446176706e-07,
                           'E_Torsion': 2.7199094116234654e-05,
                           'E_tot': 175.6875475619001,
                           'E_vdW': 148.17882663399152,
                           'mmtypes': ['C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'C_R',
                                       'H_',
                                       'H_',
                                       'H_',
                                       'H_',
                                       'H_',
                                       'H_',
                                       'H_',
                                       'H_',
                                       'H_',
                                       'H_']}
                }

