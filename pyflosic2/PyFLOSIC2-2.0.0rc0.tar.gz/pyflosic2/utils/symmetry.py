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
import copy 
import numpy 
from pyflosic2.systems.benzene_systems import C6H6_3RH_opt
from pyflosic2.gui.view import GUI
from pyflosic2.units.constants import atomic_masses
from pyflosic2.atoms.atoms import symbol2number
from pyflosic2.io.flosic_io import write_xyz
from pyflosic2.utils.systems_from_xyz import gen_systems_from_xyz
from pyflosic2.atoms.atoms import Atoms

__doc__ = """ Some symmetry related matrices and operations """

def E(): 
    """
        E
        -
        Identiy matrix.
    """
    return numpy.eye(3)

def I():
    """
        I
        -
        Inversion matrix. 
        E = numpy.dot(I,I) 
    """
    return numpy.eye(3)*(-1)

def Sz():
    """
       Sz
       --
       Refelection on the xy-plane. 
       z -> -z 
    """
    M = E()
    M[2,2] = -1 
    return M

def Sy():
    """
        Sy
        --
        Refelection on the xz-plane.
        y -> -y 
    """
    M = E()
    M[1,1] = -1
    return M

def Sx():
    """
        Sx
        --
        Refelection on the yz-plane.
        x -> -x
    """
    M = E()
    M[0,0] = -1
    return M

def Cnx(n):
    """
        Cnx
        ---
        Rotation around x-axis 
    """
    angle = 2*numpy.pi/n
    cosangle = numpy.cos(angle)
    sinangle = numpy.sin(angle)
    M = numpy.zeros((3,3))
    M[0,0] = 1
    M[1,1] = cosangle
    M[1,2] = -1*sinangle 
    M[2,1] = sinangle
    M[2,2] = cosangle
    return M

def Cny(n):
    """
        Cny
        ---
        Rotation around y-axis
    """
    angle = 2*numpy.pi/n
    cosangle = numpy.cos(angle)
    sinangle = numpy.sin(angle)
    M = numpy.zeros((3,3))
    M[0,0] = cosangle
    M[0,2] = sinangle
    M[1,1] = 1
    M[2,0] = -1*sinangle
    M[2,2] = cosangle
    return M


def Cnz(n):
    """
        Cnz 
        ---
        Rotation around z-axis 
    """
    angle = 2*numpy.pi/n
    cosangle = numpy.cos(angle)
    sinangle = numpy.sin(angle) 
    M = numpy.zeros((3,3))  
    M[0,0] = cosangle 
    M[0,1] = sinangle 
    M[1,0] = -1*sinangle
    M[1,1] = cosangle
    M[2,2] = 1 
    return M 

def C1x():
    """
        C1x
        ---
        Rotation around x-axis
        by 360 degrees 
    """
    return Cnx(n=1)

def C1y():
    """
        C1y
        ---
        Rotation around y-axis
        by 360 degrees
    """
    return Cny(n=1)

def C1z():
    """
        C1z
        ---
        Rotation around z-axis
        by 360 degrees
    """
    return Cnz(n=1)

def C2x():
    """
        C2x
        ---
        Rotation around x-axis
        by 180 degrees
    """
    return Cnx(n=2)

def C2y():
    """
        C2y
        ---
        Rotation around y-axis
        by 180 degrees
    """
    return Cny(n=2)

def C2z():
    """
        C2z
        ---
        Rotation around z-axis
        by 180 degrees
    """
    return Cnz(n=2)

def Snx(n):
    """
        Snx
        ---
        matrix for rotatory reflection
    """
    M = Sx().dot(Cnx(n=n))
    return M

def Sny(n):
    """
        Sny
        ---
        matrix for rotatory reflection
    """
    M = Sy().dot(Cny(n=n))
    return M

def Snz(n):
    """
        Snz
        ---
        matrix for rotatory reflection
    """
    M = Sz().dot(Cnz(n=n))
    return M  

def apply(M,p):
    """
        apply
        -----
        Apply matrix M to a point/3d coordinate.
    """
    pnew = numpy.dot(p,M)
    return pnew

def get_center_of_mass(atoms): 
    """
        get_center_of_mass
        ------------------
        Get center of mass. 

        Reference
        ---------
            - [1] https://github.com/charnley/rmsd/blob/master/rmsd/calculate_rmsd.py
    """
    M = [atomic_masses[symbol2number[s]+1] for s in atoms.symbols]
    pos = atoms.positions 
    COM = numpy.average(pos,weights=M,axis=0)
    return COM, M 

    

def get_inerita_tensor(atoms): 
    """
        get_inerita_tensor
        ------------------

        Reference
        ---------
            - [1] https://github.com/charnley/rmsd/blob/master/rmsd/calculate_rmsd.py
    """
    COM, M = get_center_of_mass(atoms)
    pos = atoms.positions - COM 
    
    # IT: inertia tensor
    IT = numpy.zeros((3,3)) 
    for i, (s,p) in enumerate(zip(atoms.symbols,pos)):
        m = M[i] 
        IT[0,0] += m*(p[1]**2 + p[2]**2) 
        IT[1,1] += m*(p[0]**2 + p[2]**2)
        IT[2,2] += m*(p[0]**2 + p[1]**2)
        tmp = m*(p[0]*p[1])
        IT[1,2] -= tmp 
        IT[2,1] -= tmp 
        tmp = m*(p[0]*p[2])
        IT[0,2] -= tmp
        IT[2,0] -= tmp
        tmp = m*(p[1]*p[2])
        IT[1,2] -= tmp
        IT[2,1] -= tmp
    return IT 

def get_principal_axis(atoms): 
    """
        get_principal_axis
        ------------------

        Reference
        ---------
            - [1] https://github.com/charnley/rmsd/blob/master/rmsd/calculate_rmsd.py

    """
    IT = get_inerita_tensor(atoms)
    e, v = numpy.linalg.eig(IT)
    idx = e.argmax() 
    axis = v[idx]
    return axis


def rodrigues_rotation(v1,v2):
    """
        rodrigues_rotation
        ------------------
        Rotate v1 on v2. 

        Reference 
        ---------
            - [1] https://github.com/charnley/rmsd/blob/master/rmsd/calculate_rmsd.py
    """
    if (v1 == v2).all():
        rot = E() 
    if (v1 == -v2).all():
        M = I() 
        M[1,1] = abs(M[1,1])
        rot = M 
    else: 
        v = numpy.cross(v1,v2) 
        s = numpy.linalg.norm(v) 
        c = numpy.vdot(v1,v2) 
        vx = numpy.array([[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]])
        rot = E() + vx + numpy.dot(vx, vx) * ((1.0 - c) / (s * s))
    return rot 


def R(theta, u):
    """
        R
        -
        Generial rotation around an arbitary axis u 
        by an angle of theta. 
    """
    c = numpy.cos(theta)
    s = numpy.sin(theta)
    return numpy.array([[c + u[0]**2 * (1-c),
                         u[0] * u[1] * (1-c) - u[2] * s, 
                         u[0] * u[2] * (1 - c) + u[1] * s],
                        [u[0] * u[1] * (1-c) + u[2] * s,
                         c + u[1]**2 * (1-c),
                         u[1] * u[2] * (1 - c) - u[0] * s],
                        [u[0] * u[2] * (1-c) - u[1] * s,
                         u[1] * u[2] * (1-c) + u[0] * s,
                         c + u[2]**2 * (1-c)]])

def apply_all(M,atoms_ref,only=None):
    """
        apply_all 
        ---------
        Apply transformation matrix M to set 
        of cartesian coordinates in atoms. 
        If only is set, M is only applied to 
        the given species. 
    """
    atoms = copy.copy(atoms_ref)
    pos = atoms.positions  
    for i,(s,p) in enumerate(zip(atoms.symbols,pos)):
        if only is None or s == only: 
            pos[i] = apply(M,p)
    atoms.positions = pos
    return atoms 


def gen_C6H6_3UH():
    """
        C6H6_3UH
        -------
        Test system. 
    """
    M = Sz()
    atoms = C6H6_3RH_opt()
    pos = atoms.positions
    for i,(s,p) in enumerate(zip(atoms.symbols,pos)):
        if s == 'He':
            pos[i] = apply(M,p)
            print(s,i,p,atoms.positions[i])
    atoms.positions = pos
    return atoms

def main():
    atoms = C6H6_3RH_opt()
    # get principal axis 
    axis = get_principal_axis(atoms)
    v1 = axis 
    # get rotation from axis to v2 
    v2 = numpy.array([1,0,0])
    # rodrigues rotation matrix 
    U = rodrigues_rotation(v1,v2)
    print(U)
    atoms = apply_all(U,atoms) 
    U = R(numpy.deg2rad(180), v2)
    atoms = apply_all(U,atoms,only='He')
    GUI(atoms)

def C6H6_3UH():
    """
        C6H6_3UH 
    """
    sym = ['C']*6+['H']*6+['X']*21+['He']*21
    p0 = [-1.213075171851934,-0.688402107972801,-2.246649826e-06]
    p1 = [-1.202775171851934,0.706397892027199,9.7753350174e-05]
    p2 = [-0.010275171851934,-1.394802107972801,-2.246649826e-06]
    p3 = [0.010424828148066,1.394797892027199,-0.000102246649826]
    p4 = [1.202824828148066,-0.706302107972801,-2.246649826e-06]
    p5 = [1.213124828148066,0.688397892027199,-2.246649826e-06]
    p6 = [-2.157675171851934,-1.224402107972801,-2.246649826e-06]
    p7 = [-2.139275171851934,1.256397892027199,9.7753350174e-05]
    p8 = [-0.018375171851934,-2.480902107972801,-0.000102246649826]
    p9 = [0.018424828148066,2.480797892027199,-2.246649826e-06]
    p10 = [2.139424828148066,-1.256302107972801,9.7753350174e-05]
    p11 = [2.157724828148066,1.224497892027199,-2.246649826e-06]
    p12 = [0.002660674526672,1.397720676544042,-0.071755879618913]
    p13 = [0.504154572464288,0.852493786596533,1.169228711401114]
    p14 = [0.608916318235767,1.035694468869223,0.307492984277537]
    p15 = [-0.5839905197191,1.029596349239557,0.093677375914613]
    p16 = [0.043187340946915,2.229243105882647,-0.015419567228607]
    p17 = [1.219435948923908,0.68319666679102,-0.071899855017928]
    p18 = [1.183240484397023,-0.008846331187293,0.096129705198001]
    p19 = [1.925179755701892,1.125124386158666,-0.01370700375086]
    p20 = [1.209240214904593,-0.701067664096829,-0.071915619296053]
    p21 = [0.593271213585312,-1.045200881078445,0.30766567945778]
    p22 = [0.49460355225531,-0.863317900136449,1.169963213975415]
    p23 = [1.908332742679417,-1.152276591856516,-0.011443482276232]
    p24 = [-0.018067531987729,-1.397588715821983,-0.071671579383703]
    p25 = [-0.599584543124414,-1.020845691128458,0.092091567432029]
    p26 = [0.012100964302093,-2.22832570542381,-0.012090249421508]
    p27 = [-1.211609320566986,-0.696705836640849,-0.071657157959282]
    p28 = [-1.202246679195933,0.009358974016951,0.307648198163848]
    p29 = [-1.001256766441855,0.009497614188003,1.169028791051101]
    p30 = [-1.95090609538213,-1.075420401211826,-0.009375143580005]
    p31 = [-1.201275817581239,0.714618242329418,-0.07178102974525]
    p32 = [-1.935635475087094,1.102964175934473,-0.007781671100341]
    p33 = [0.002660329490229,1.397720328860712,0.071751723537528]
    p34 = [1.219435710440631,0.683196464883806,0.071894648259001]
    p35 = [0.608917073662677,1.03569471997428,-0.307495462186553]
    p36 = [0.504160186360118,0.852494355438279,-1.169229366750987]
    p37 = [1.20923998905938,-0.70106722382095,0.071911537671115]
    p38 = [1.183241379147613,-0.008846138801961,-0.096132457932447]
    p39 = [-0.018067566770217,-1.397588424150014,0.071666393131649]
    p40 = [0.494600952600159,-0.863323048632698,-1.169963965356026]
    p41 = [0.593270982716285,-1.045201665640412,-0.307668196981417]
    p42 = [-1.211608850585104,-0.696705990688875,0.071652993609109]
    p43 = [-0.599584824559412,-1.020846558101814,-0.09209447622449]
    p44 = [-1.201275497305572,0.714618145611972,0.071775844001198]
    p45 = [-1.001259676203412,0.009502138324912,-1.169029728583262]
    p46 = [-1.202247215465959,0.009359500120156,-0.307650586399672]
    p47 = [-0.583991132379269,1.029597050626926,-0.093680184239565]
    p48 = [0.04318651021166,2.229242166330305,0.015415262028056]
    p49 = [1.925179268173196,1.125123296380495,0.013702299548755]
    p50 = [1.90833238652658,-1.152275445257688,0.011439078674885]
    p51 = [0.012100239969456,-2.228324733830784,0.012085631817474]
    p52 = [-1.950904911242003,-1.075420726340601,0.009370927708031]
    p53 = [-1.935634305460524,1.102964356419488,0.007777055972759]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,p28,p29,p30,p31,p32,p33,p34,p35,p36,p37,p38,p39,p40,p41,p42,p43,p44,p45,p46,p47,p48,p49,p50,p51,p52,p53]
    charge = 0
    spin = 0
    atoms = Atoms(sym,pos,charge=charge,spin=spin,elec_symbols=['X','He'])
    return atoms

def test():
    atoms = gen_C6H6_3UH()
    GUI(atoms)
    write_xyz(atoms) 
    gen_systems_from_xyz('atoms.xyz', charge=0, spin=0)
    atoms = C6H6_3UH()
    GUI(atoms)

if __name__ == '__main__': 
    #main()
    test()
