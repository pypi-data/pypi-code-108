import itertools as it
import re
import numpy as np

def c_types(atom_types):
    """
    returns all the pair types combinations.

    :param list_of_str atom_types: the types of each atom in the primitive cell in the same order as the basis vectors.
    """
    types_all = re.findall('[A-Z][^A-Z]*', atom_types)
    ptypes=list(set([s for s in types_all]))
    ptypes.sort()
    combs_types = list(it.combinations_with_replacement(ptypes, r=2))
    combs_types = [A[0]+'-'+A[1] for A in combs_types]
    return combs_types, types_all

def generate_cells_coordinates(size, primitive_cell,center):
    """ generate the cell coordinates for which we are going
    to calculate the neighbor list.

    :param array size: Number of times we are replicating the primitive cell
    :param array primitive_cell: The primitive cell
    :param array center: The position in space where the system of reference is

    """

    cell_coords = np.array(list((it.product(np.arange(size[0]),
                                            np.arange(size[1]),
                                            np.arange(size[2])))))
    cell_coords_centered = cell_coords + center
    cell_coords_centered = np.dot(cell_coords_centered, primitive_cell)

    return cell_coords_centered

def gen_Ts(Ti,Tf,nTs):
    """
    Function to generate a range of temperatures.

    :param float Ti: Initial temperature. (Try not to use the value 0. Use 0.1 instead.)
    :param float Tf: Final temperature.
    :param int nTs: Number of values. This does not include room temperature, which is included anyways.

    :retun list_of_floats: Values of temperatures between Ti and Tf, inclusive, plus room temperature.
    """
    minF_step = (Tf - Ti)/(nTs - 1.)
    Ts = np.arange(Ti, Tf+1, minF_step)
    Ts = np.r_[Ts, [298.15]]
    Ts.sort()
    return Ts

def load_doscar(filename_sufix):
    E = []
    N = []
    Ef = []
    nat = 0
    for dosfile in ['-0.10', '-0.09','-0.08','-0.07','-0.06','-0.05','-0.04','-0.03','-0.02','-0.01','-0.00','0.01','0.02','0.03','0.04','0.05','0.06','0.07','0.08','0.09','0.10']:
        countline = 0
        EN = []

        filename = filename_sufix+dosfile
        with open(filename) as infile:
                for line in infile:
                    if countline == 0:
                        nat = float(line.split()[0])
                    if countline == 5:
                        Ef.append(float(line.split()[3]))
                    if countline > 5:
                        EN.append(line.split()[0:2])

                    countline +=1
        ENAl = np.array(EN)
        E.append([float(s) for s in list(ENAl[:,0])])
        N.append([float(s)/nat for s in list(ENAl[:,1])])

    return E,N,Ef

def load_V_E(energy_dir,energy_dir_contcar, units='eV/atom'):
    with open(energy_dir_contcar,'r') as f_poscar:
        f_poscar_lines = f_poscar.readlines()
        cell_poscar = f_poscar_lines[2:5]

        cell_lst = [c.split() for c in cell_poscar]
        diag_cell = [float(c[i]) for i, c in enumerate(cell_lst)]

        try:
            nat = sum([int(li) for li in np.fromstring(f_poscar_lines[5], dtype=int, sep=' ')])
            1/nat
        except:
            nat = sum([int(li) for li in np.fromstring(f_poscar_lines[6], dtype=int, sep=' ')])
            1/nat
    with open(energy_dir + '/SUMMARY.fcc') as f_summary:
        f_summary_lines = f_summary.readlines()
        f_summary_lines = list(dict.fromkeys(f_summary_lines))
        ds = []
        E = []
        for l in f_summary_lines:
            l_lst = l.split(' ')
            ds.append(float(l_lst[0]))
            E.append(float(l_lst[3])/nat)

    V = []
    for di in ds:
        V.append(np.product(np.array(diag_cell)*(1+di))/nat)

    if units=='J/mol':
        uconvE=(0.160218e-18*6.02214e23)
        uconvV=(1e-30*6.02e23)
    elif units=='eV/atom':
        uconvE,uconvV = 1,1
    return np.array(V).T*uconvV, np.array(E).T*uconvE

def load_EM(filename_outcar_eps):
    EM = []

    with open(filename_outcar_eps) as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith(' TOTAL ELASTIC MODULI (kBar)'):
                j = i + 3
                data = lines[j:j+6]
                break

    for line in data:
        EM += [[float(x) for x in line.split()[1:]]]
    EM = np.array(EM)

    return EM

def load_cell(filename_contcar):
    with open(filename_contcar) as f:
        poscar_lines=f.readlines()
    mult = float(poscar_lines[1])
    cell = np.array([np.fromstring(line_i, dtype=float,sep=' ') for line_i in poscar_lines[2:5]])
    cell = cell*mult

    ix_nats=6
    ats_types = re.findall('[A-Z][^A-Z]*', poscar_lines[ix_nats-1].replace('  ','').replace(' ','').replace('\n',''))
    nats = np.fromstring(poscar_lines[ix_nats], dtype=int,sep=' ')

    formula_lst=[]
    for at_i, na_i in zip(ats_types,nats):
        formula_lst.append(at_i*na_i)
    formula=''.join(formula_lst)
    tots_nats=sum(nats)

    basis = np.array([np.fromstring(line_i, dtype=float,sep=' ') for line_i in poscar_lines[8:8+tots_nats]])
    # basis = np.dot(basis,cell)

    return formula, cell, basis
