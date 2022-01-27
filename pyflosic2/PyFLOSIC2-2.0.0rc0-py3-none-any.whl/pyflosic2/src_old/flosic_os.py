# -----Authors-----
#
#   main-authors:
#   Lenz Fiedler (LF) (fiedler.lenz@gmail.com)
#   Sebastian Schwalbe (SS)
#   Torsten Hahn (TH)
#
#   co-authors:
#   Kai Trepte (KT) (main tester)
#   Jakob Kraus (JaK) (tester)
#    Jens Kortus (JK) (supervisor)

from pyscf import gto, dft, lo
import os
import numpy as np
import glob
import shutil
from ase.data import g2_1
try:
    from ase.atoms import string2symbols
except BaseException:
    # moved in 3.17 to
    from ase.symbols import string2symbols
from ase.io import read
from ase import Atoms, Atom
from pyscf.dft import numint
from ase.io.cube import write_cube
from ase.io import write
from scipy import io
from scipy import linalg
from scipy import optimize
from ase import units
from math import pi

# -----Notes-----
#
# Main routines by Lenz Fiedler (LF). In this file, the creation of the FLOs, the
# calculation of FLO-SIC for energy and energy eigenvalues as well as the calculation of
# the forces for the FOD geometry optimization is realized. Furthermore, several
# auxiliary routines needed for Pyflosic are defined here. The full references for the
# equations implemented here can be found in Lenz Fiedlers Master Thesis. Please contact
# the authors if you want access to this thesis.
#

# -----Routines-----
#
# Get multiplicity (=spin polarization, which is the central spin variable used in PySCF)
# of the system. The approach here is to load the spin from ASE where possible and define
# exceptions where needed. Naturally, this routine only needs to be called
# if the user does not specify the spin himself.

# -----Changelog-----
# 01.10.2018    SS@CMU try to introduce atomic force correction (AF)
#         AF is calculated only in the global debug=True mode,
#        which is introduce in all src files of pyflosic
#        you need to add AF manually to the gradients/forces object
#        pyflosic_master/test/force    is the testing directory for this option
#        search tag             DEV
# 07.02.2018    SS start to port print statements to python3.0


def force_max_lij(lambda_ij):
    #
    # calculate the RMS(l_ij)
    #
    nspin = 2
    lijrms = 0
    for s in range(nspin):
        M = lambda_ij[s, :, :]
        e = (M - M.T)[np.triu_indices((M - M.T).shape[0])]
        e_tmp = 0.0
        for f in range(len(e)):
            e_tmp = e_tmp + e[f]**2.
        e_tmp = np.sqrt(e_tmp / (M.shape[0] * (M.shape[0] - 1)))
        lijrms = lijrms + e_tmp
    lijrms = lijrms / 2.
    return lijrms


def get_multiplicity(sys):

    # Read the Spin from ASE (G2-1 benchmark set).

    try:
        M = np.array((g2_1.data[sys])['magmoms']).sum()
        if M is None:
            M = 0
    except BaseException:
        'Nothing'

    # If no spin is found there try to use the self-defined database.
    # Additions can be made here.

    try:
        if sys == 'H2':
            M = 0
        if sys == 'H-':
            M = 0
        if sys == 'He':
            M = 0
        if sys == 'H2':
            M = 0
        if sys == 'H-':
            M = 0
        if sys == 'He':
            M = 0
        if sys == 'H4':
            M = 0
        if sys == 'H6':
            M = 0
        if sys == 'H8':
            M = 0
        if sys == 'H10':
            M = 0
        if sys == 'H12':
            M = 0
        if sys == 'B':
            M = 1
        if sys == 'Al':
            M = 1
        if sys == 'Ne':
            M = 0
    except BaseException:
        'Nothing'

    # If no spin is found, the spin variable will be set to None. This will cause an error
    # BEFORE the DFT calculation starts; setting the spin variable to an arbitrary value
    # would cause the DFT calculation to run properly but cause an error in the process.

    return int(M)

# Transform an ASE atoms object containing nuclei positions into the PySCF input format.


def ase2pyscf(ase_atoms):
    return [[atom.symbol, atom.position] for atom in ase_atoms]

# Split the input .xyz file into nuclei and fod position arrays.
# This function both does the splitting AND gives back an array with ghost
# atoms pyscf can work with.
# GHOST atoms allow to create a nucleus without charge at any given position, here the FOD
# positions. This is useful for e.g. debugging. The use of this functionality can be seen
# in the examples below.


def xyz_to_nuclei_fod(ase_atoms):

    # Get the number of atoms and fods.

    syssize = len(ase_atoms)

    # First the preparations for enabling the usage of GHOST atoms are done.
    # We need to determine if a FOD is included in the creation of the GHOST atoms or
    # not. If two GHOST atoms are created very close to each other (or other atoms) this
    # will result in the DFT calculation crashing. A FOD is included if it is no closer
    # then fodeps to another FOD or a nuclei.

    fodeps = 0.1
    included = []
    numbernotincluded = 0
    dist = -1.0

    # Iterate over FODs and nuclei positions.

    for i in range(0, syssize):

        # Nuclei are always included, obviously. NOTE: FODs for spin0 are given with an
        # X, the for spin1 with an He symbol.

        if ase_atoms[i].symbol != 'X' and ase_atoms[i].symbol != 'He':
            included.append(1)
        if ase_atoms[i].symbol == 'X' or ase_atoms[i].symbol == 'He':

            # For every FOD the distance to every included FOD and the nuclei is calculated
            # in order to determine whether or not it has to be included.

            distold = fodeps
            for j in range(0, i):
                dist = np.sqrt((ase_atoms[i].position[0] -
                                ase_atoms[j].position[0])**2 +
                               (ase_atoms[i].position[1] -
                                ase_atoms[j].position[1])**2 +
                               (ase_atoms[i].position[2] -
                                ase_atoms[j].position[2])**2)
                if dist < distold and included[j] == 1:
                    distold = dist

        # If the smallest distance is smaller than fodeps, the FOD will not be included.
        # Elsewise it is included.

            if distold < fodeps:
                included.append(0)
                numbernotincluded += 1
            else:
                included.append(1)

    # Now the actual splitting is done.
    # These arrays will hold nuclei and FODs (for each spin channel separately).

    nuclei = Atoms([])
    fod1 = Atoms([])
    fod2 = Atoms([])
    nrofnuclei = 0

    # tmp will be used to create the list that can be used to enable GHOST atoms.

    tmp = []

    # Determine where to split.

    for i in range(0, syssize):
        if ase_atoms[i].symbol != 'X':
            nrofnuclei = nrofnuclei + 1

        # If the first FOD is found, nuclei assigning will be done.

        if ase_atoms[i].symbol == 'X':
            break

    # Split everything.

    for i in range(0, syssize):

        # Assign the nuclei.

        if i < nrofnuclei:
            tmp.append(ase_atoms[i].symbol + ' ' + str(ase_atoms[i].position[0]) + ' ' +
                       str(ase_atoms[i].position[1]) + ' ' + str(ase_atoms[i].position[2]) + '\n')
            nuclei.append(ase_atoms[i])

        # Assing FODs for spin0.

        elif ase_atoms[i].symbol == 'X':
            fod1.append(ase_atoms[i])
            if included[i] == 1:
                tmp.append('ghost1' +
                           ' ' +
                           str(ase_atoms[i].position[0]) +
                           ' ' +
                           str(ase_atoms[i].position[1]) +
                           ' ' +
                           str(ase_atoms[i].position[2]) +
                           '\n')

        # Assign FODs for spin1.

        elif ase_atoms[i].symbol == 'He':
            fod2.append(ase_atoms[i])
            if included[i] == 1:
                tmp.append('ghost2' +
                           ' ' +
                           str(ase_atoms[i].position[0]) +
                           ' ' +
                           str(ase_atoms[i].position[1]) +
                           ' ' +
                           str(ase_atoms[i].position[2]) +
                           '\n')

    # geo holds both nuclei and GHOST atoms at FOD positions.

    geo = ''.join(tmp)

    # geo can now be used for calculation with GHOST atoms, nuclei and fod1/fod2 for
    # every other calculation.

    return geo, nuclei, fod1, fod2, included

# This routine outputs the FLOs as .cube files for later visualization. It needs an UKS
# object, the FLOs, FOD positions and nuclei positions. sys simply specifies what is
# given as the systems' name in the output files. maxcell determines the plotting area.
# The variable flo_ao can be filled with any mo_coeff-like object, thus orbitals that are
# not FLOs can be plotted as well.


def print_flo(mf, flo_ao, sys, nuclei, fod1, fod2, maxcell=6.):
    print('FLO are printed in .cube format.')

    # Get the mol object.

    mol = mf.mol

    # Get dimensions of everything (for loops).

    nfod = 2 * [0]
    tmp = np.shape(fod1.positions)
    nfod[0] = tmp[0]
    tmp = np.shape(fod2.positions)
    nfod[1] = tmp[0]

    # Build an uniform mesh.

    coords = []
    weights = []
    meshwidth = maxcell / 40

    for ix in np.arange(-maxcell, maxcell + meshwidth, meshwidth):
        for iy in np.arange(-maxcell, maxcell + meshwidth, meshwidth):
            for iz in np.arange(-maxcell, maxcell + meshwidth, meshwidth):
                coords.append((ix, iy, iz))
                weights.append(meshwidth)
    msh = np.array(coords)
    nmsh = int(msh.shape[-2])

    # Get the AO on the mesh.

    ao = numint.eval_ao(mol, msh)

    # Get the FLOs on the mesh.

    flo_tmp = ao.dot(flo_ao)
    flo = np.zeros((2, np.max(nfod), nmsh), dtype=np.float64)

    # Iterate over the spin.

    for j in range(0, 2):

        # Iterate over the KSO.

        for i in range(0, nfod[j]):

            # Iterate over the mesh.

            for k in range(0, nmsh):
                flo[j, i, k] = flo_tmp[k, j, i]

    # Get the outer bounds of the mesh.

    thrdmsh = int(nmsh**(1. / 3.)) + 1
    mshmin = [0] * 3
    mshmax = [0] * 3
    mshspac = [0] * 3
    for i in range(0, 3):
        mshmin[i] = np.min(msh[:, i])
        mshmax[i] = np.max(msh[:, i])
        mshspac[i] = (mshmax[i] - mshmin[i]) / thrdmsh

    # wfout1 is a temporary variable on the uniform mesh in the correct dimensions for the .cube file.

    wfout1 = np.zeros((thrdmsh, thrdmsh, thrdmsh), dtype=np.float64)

    # Rescale the ASE cell.

    ase_cell = nuclei.get_cell()
    rescaling = [0] * 3
    for i in range(0, 3):
        rescaling[i] = (mshmax[i] - mshmin[i])
        ase_cell[i, i] = rescaling[i]
    nuclei.set_cell(ase_cell)
    allpos = nuclei.get_positions()
    allpos = allpos / units.Bohr
    allpos = allpos + mshmax[i]
    nuclei.set_positions(allpos)

    # Fill wfout1 according to the .cube file standard.

    for j in range(0, 2):
        for i in range(0, nfod[j]):
            for k in range(0, nmsh):
                idx = int((msh[k, 0] - mshmin[0]) / mshspac[0]) - 1
                idy = int((msh[k, 1] - mshmin[1]) / mshspac[1]) - 1
                idz = int((msh[k, 2] - mshmin[2]) / mshspac[2]) - 1
                wfout1[idx, idy, idz] = flo[j, i, k]

            # Output the wfout1.

            fname1 = sys + '_FLO_state_{:d}_spin_{:d}.cube'.format(i, j + 1)
            write(fname1, nuclei, data=wfout1)

    print('FLO have been printed in .cube format.')

    return


# Build the rotation matrix in the AO formalism. Input are the KSO, the KSO at the FOD
# positions and the dimension parameters.

def get_rot(nfod, Psi_ai, nks, NSPIN, datatype=np.float64, idx_1s=[0, 0]):
    # SS: commented out, for timing 
    # print('nks')
    # print(nks)
    # print('nfod')
    # print(nfod)
    
    # Init the rotation matrix.

    R_ao = np.zeros((NSPIN, nks, nks), dtype=datatype)
    for s in range(NSPIN):
        for i in range(0, nks):
            R_ao[s, i, i] = 1.0

    # Get SUMPsi_ai (density at every point).

    SUMPsi_ai = np.zeros((NSPIN, np.max(nfod)), dtype=datatype)

    for s in range(NSPIN):
        for m in range(0, nfod[s]):
            SUMPsi_ai[s, m] = np.sqrt(np.sum((Psi_ai[s, m, :])**2))

    # Build the rotation matrices.

    for s in range(NSPIN):
        for m in range(idx_1s[s], nfod[s]):
            for i in range(idx_1s[s], nfod[s]):
                R_ao[s, m, i] = Psi_ai[s, m, i] / SUMPsi_ai[s, m]

    
    # SS: commented out, for timing 
    # print('R_ao')
    # print(R_ao)

    return R_ao

# This calculates the forces on the FLO. They have the data structure
# ((nfod[0] + nfod[1]) x 3)
# Inputs include the UKS object, FOD positions, KSO and FO, epsilon^k_kl.


def get_fermi_forces(nspin, nfod, nks, nksocc, occup, mol, mf, fod1, fod2, Psi_ai, ks, fo,
                     s1e, T_lo, Q_lo, h_sic_input, R_ao_input, sysname, datatype, debug):

    # Initialize the forces.

    fforce = np.zeros((nspin, np.max(nfod), 3), dtype=datatype)
    fforce_output = np.zeros((nfod[0] + nfod[1], 3), dtype=datatype)

    # gradpsi_ai holds the nabla KS value at the FOD position. Dimensions:
    # (nspin x FOD index (i) x KS index (alpha) x 3.

    gradpsi_ai = np.zeros((nspin, np.max(nfod), np.max(nksocc), 3), dtype=datatype)

    # den_ai holds the density at the FOD positions, grad_ai holds nabla rho at the FOD positions.

    den_ai = np.zeros((nspin, np.max(nfod)), dtype=datatype)
    grad_ai = np.zeros((nspin, np.max(nfod), 3), dtype=datatype)

    # gradfo holds the gradients of the fermi orbitals. The dimensions are:
    # (spin x coefficients x FOD Index x components (x,y,z)

    gradfo = np.zeros((nspin, nks, np.max(nfod), 3), dtype=datatype)

    # Rgrad is the PySCF equivalent for NRLMOL's FMAT. It is only needed for debugging.
    # The dimensions are:
    # (spin x FOD index (i) x FOD index (a) x components (x,y,z) )

    Rgrad = np.zeros((nspin, np.max(nfod), np.max(nfod), 3), dtype=datatype)

    # The sum over the gradients of KSO at the positions a_i. The dimensions are:
    # (spin x coefficients x FOD Index (i) x components (x,y,z))

    sumgradpsi = np.zeros((nspin, nks, np.max(nfod), 3), dtype=datatype)

    # gradovrlp holds the derivative of the overlap matrix. The dimension are:
    # (spin x nfod (i) x nfod (j) x components (x,y,z)).
    # However, only for i=j it is unequal to zero. it might be reasonable to cut this
    # structure down later, in order to save computational space.

    gradovrlp = np.zeros((nspin, np.max(nfod), np.max(nfod), 3), dtype=datatype)

    # Delta1 and Delta3 as defined in the papers concering FOD forces.
    # They have the dimension:
    # (spin x nfod (l) x nfod (k) x nfod(m) x components (x,y,z)).

    Delta1 = np.zeros((nspin, np.max(nfod), np.max(nfod), np.max(nfod), 3), dtype=datatype)
    Delta3 = np.zeros((nspin, np.max(nfod), np.max(nfod), np.max(nfod), 3), dtype=datatype)

    # eps holds the matrix elements lambda_ij. It has the dimensions:
    # (spin x nfod (l) x nfod(k))

    eps = np.zeros((nspin, np.max(nfod), np.max(nfod)), dtype=datatype)

    # The rotation matrix, this is needed for debug purposes.

    R_fo = np.zeros((nspin, np.max(nfod), np.max(nfod)), dtype=datatype)

    # Fermi orbital overlap matrix.

    s_i_j = np.zeros((np.max(nfod), np.max(nfod)), dtype=datatype)

    # Cholesky decomposition of the atomic overlap matrix.

    sroot = np.zeros((np.max(nfod), np.max(nfod)), dtype=datatype)

    # Debugging flag. If set to false, input from NRLMOL is used to calculate everything.

    calculateinput = True

    if calculateinput:

        # Cholesky decomposition for the atomic overlap matrix.

        sroot = np.linalg.cholesky(s1e)
        for s in range(nspin):

            # Assign epsilon.

            eps[s, 0:nfod[s], 0:nfod[s]] = h_sic_input[s, 0:nfod[s], 0:nfod[s]]

        # Get the value of the gradients of the KSO at the FOD positions.

        ao1 = mol.eval_gto('GTOval_ip_sph', fod1.positions / units.Bohr, comp=3)
        gradpsi_ai_1 = [x.dot(ks) for x in ao1]
        ao2 = mol.eval_gto('GTOval_ip_sph', fod2.positions / units.Bohr, comp=3)
        gradpsi_ai_2 = [x.dot(ks) for x in ao2]

        # Rearrange the data to make it more usable.

        x_1 = gradpsi_ai_1[0]
        y_1 = gradpsi_ai_1[1]
        z_1 = gradpsi_ai_1[2]
        x_2 = gradpsi_ai_2[0]
        y_2 = gradpsi_ai_2[1]
        z_2 = gradpsi_ai_2[2]

        # Iterate over the spin.

        for j in range(0, nspin):
            l = 0

            # Iterate over the Kohn sham wf.

            for i in range(0, nks):
                if occup[j][i] != 0.0:

                    # Iterate over the fods.

                    for k in range(0, nfod[j]):
                        if j == 0:
                            gradpsi_ai[j, k, l, 0] = x_1[k][j][i]
                            gradpsi_ai[j, k, l, 1] = y_1[k][j][i]
                            gradpsi_ai[j, k, l, 2] = z_1[k][j][i]
                        if j == 1:
                            gradpsi_ai[j, k, l, 0] = x_2[k][j][i]
                            gradpsi_ai[j, k, l, 1] = y_2[k][j][i]
                            gradpsi_ai[j, k, l, 2] = z_2[k][j][i]
                    l = l + 1
                if l > nksocc[j]:
                    print('WARNING: Attempting to use not occupied KS wf for FLOSIC.')

        # Calculate the density and the gradient of the density from the KS wavefunctions.

        for s in range(nspin):
            for m in range(0, nfod[s]):
                den_ai[s, m] = np.sum((Psi_ai[s, m, :])**2)

        for s in range(nspin):
            for r in range(0, 3):
                for m in range(0, nfod[s]):
                    for a in range(0, nfod[s]):
                        grad_ai[s, m, r] = grad_ai[s, m, r] + 2. * Psi_ai[s, m, a] * gradpsi_ai[s, m, a, r]

        # sfo and sks hold the FO and KSO after the decomposed atomic overlap has been
        # included.

        sks = np.zeros((nspin, nks, nks), dtype=datatype)
        sfo = np.zeros((nspin, nks, nks), dtype=datatype)

        # Get the gradients of the Fermi orbitals. (NOTE: NOT THE FERMI LOWDIN ORBITALS!)
        # This is dF in the usual notation.

        for s in range(nspin):

            # Fill sks and sfo.

            sks[s, :, :] = np.dot(np.transpose(sroot), ks[s, :, :])
            sfo[s, :, :] = np.dot(np.transpose(sroot), fo[s, :, :])

            # bra and ket for scalar products.

            ket = np.zeros((nfod[s], 1), dtype=datatype)
            bra = np.zeros((1, nfod[s]), dtype=datatype)

            # Get dF.

            for r in range(0, 3):
                for i in range(0, nfod[s]):
                    sum1 = np.zeros((nks), dtype=datatype)
                    for a in range(0, nfod[s]):
                        sum1 = gradpsi_ai[s, i, a, r] * sks[s, :, a] + sum1
                    gradfo[s, :, i, r] = sum1[:] / np.sqrt(den_ai[s, i]) - \
                        (sfo[s, :, i] * grad_ai[s, i, r]) / (2. * den_ai[s, i])

    else:

        # Read all the input from the NRLMOL files provided.
        # The inputformat is:
        # F,eps,dF for spin 0, then for spin 1.
        # This IS ONLY FOR DEBUGGING PURPOSES!

        f = open(sysname + '_NRL.dat', 'r')
        ll = f.readlines()
        for l in range(len(ll)):
            tmp = ll[l].split()
            if l < nfod[0]:
                for i in range(nfod[0]):
                    R_fo[0, i, l] = float(tmp[i])
            if l >= nfod[0] and l < 2 * nfod[0]:
                for i in range(nfod[0]):
                    eps[0, i, l - nfod[0]] = float(tmp[i])
            if l >= 2 * nfod[0] and l < 3 * nfod[0]:
                for i in range(nfod[0]):
                    Rgrad[0, i, l - 2 * nfod[0], 0] = float(tmp[i])
            if l >= 3 * nfod[0] and l < 4 * nfod[0]:
                for i in range(nfod[0]):
                    Rgrad[0, i, l - 3 * nfod[0], 1] = float(tmp[i])
            if l >= 4 * nfod[0] and l < 5 * nfod[0]:
                for i in range(nfod[0]):
                    Rgrad[0, i, l - 4 * nfod[0], 2] = float(tmp[i])
            if l >= 5 * nfod[0] and l < 5 * nfod[0] + nfod[1]:
                for i in range(nfod[1]):
                    R_fo[1, i, l - 5 * nfod[0]] = float(tmp[i])
            if l >= 5 * nfod[0] + nfod[1] and l < 5 * nfod[0] + 2 * nfod[1]:
                for i in range(nfod[1]):
                    eps[1, i, l - (5 * nfod[0] + nfod[1])] = float(tmp[i])
            if l >= 5 * nfod[0] + 2 * nfod[1] and l < 5 * nfod[0] + 3 * nfod[1]:
                for i in range(nfod[1]):
                    Rgrad[1, i, l - (5 * nfod[0] + 2 * nfod[1]), 0] = float(tmp[i])
            if l >= 5 * nfod[0] + 3 * nfod[1] and l < 5 * nfod[0] + 4 * nfod[1]:
                for i in range(nfod[1]):
                    Rgrad[1, i, l - (5 * nfod[0] + 3 * nfod[1]), 1] = float(tmp[i])
            if l >= 5 * nfod[0] + 4 * nfod[1] and l < 5 * nfod[0] + 5 * nfod[1]:
                for i in range(nfod[1]):
                    Rgrad[1, i, l - (5 * nfod[0] + 4 * nfod[1]), 2] = float(tmp[i])

    # Calculate the forces.

    # Now the actual calculation. It is done as a loop over the spin.
    # This implementation follows the one used in NRLMOL.

    for s in range(nspin):
        if nfod[s] != 0:

            # Get the overlap matrix. Both for the NRLMOL input and the self calculated
            # input.

            s_i_j = np.zeros((nfod[s], nfod[s]), dtype=datatype)
            if not calculateinput:
                s_i_j = np.dot(np.transpose(R_fo[s, 0:nfod[s], 0:nfod[s]]), R_fo[s, 0:nfod[s], 0:nfod[s]])
            if calculateinput:
                s_i_j[0:nfod[s], 0:nfod[s]] = np.dot(np.transpose(sfo[s, :, 0:nfod[s]]), sfo[s, :, 0:nfod[s]])

            # Get the eigenvectors as done by NRLMOL.

            Q_alpha_tmp, T_alpha_tmp = linalg.eigh((s_i_j[0:nfod[s], 0:nfod[s]]))
            T_alpha = np.zeros((np.max(nfod), np.max(nfod)), dtype=datatype)
            Q_alpha = np.zeros((np.max(nfod)), dtype=datatype)

            # Resort the matrices according to NRLMOL formalism.

            for i in range(0, nfod[s]):
                for j in range(0, nfod[s]):
                    T_alpha[j, nfod[s] - 1 - i] = T_alpha_tmp[j, i]
                    Q_alpha[nfod[s] - 1 - i] = Q_alpha_tmp[i]

            T_alpha = np.transpose(T_alpha)

            # Temporary variables.

            TdST = np.zeros((np.max(nfod), np.max(nfod), np.max(nfod), 3), dtype=datatype)
            V_tmp = np.zeros((np.max(nfod)), dtype=datatype)
            M_tmp = np.zeros((np.max(nfod), np.max(nfod)), dtype=datatype)
            D1_km = np.zeros((np.max(nfod), np.max(nfod), np.max(nfod), 3), dtype=datatype)
            D1_kmd = np.zeros((np.max(nfod), np.max(nfod), np.max(nfod), 3), dtype=datatype)
            D3_km = np.zeros((np.max(nfod), np.max(nfod), np.max(nfod), 3), dtype=datatype)
            D3_kmd = np.zeros((np.max(nfod), np.max(nfod), np.max(nfod), 3), dtype=datatype)

            # Get dS.

            for r in range(0, 3):
                if not calculateinput:
                    gradovrlp[s, 0:nfod[s], 0:nfod[s], r] = np.dot(np.transpose(
                        R_fo[s, 0:nfod[s], 0:nfod[s]]), Rgrad[s, 0:nfod[s], 0:nfod[s], r])
                if calculateinput:
                    for n in range(nfod[s]):
                        for m in range(nfod[s]):
                            gradovrlp[s, n, m, r] = np.dot(np.transpose(sfo[s, :, n]), gradfo[s, :, m, r])

                # Get Matrix elements <T_j|dSdAm|T_k>.

                for m in range(nfod[s]):
                    for a in range(nfod[s]):
                        for b in range(nfod[s]):
                            for i in range(nfod[s]):
                                TdST[b, a, m, r] = TdST[b, a, m, r] + gradovrlp[s, i, m, r] * \
                                    (T_alpha[b, i] * T_alpha[a, m] + T_alpha[b, m] * T_alpha[a, i])

                # Get <phi|D1,km>

                V_tmp[0:nfod[s]] = 1. / np.sqrt(Q_alpha[0:nfod[s]])
                M_tmp = np.zeros((nfod[s], nfod[s]), dtype=datatype)
                M_tmp2 = np.zeros((nfod[s], nfod[s]), dtype=datatype)

                for m in range(nfod[s]):
                    for k in range(nfod[s]):
                        M_tmp[m, k] = np.sum(T_alpha[0:nfod[s], k] * T_alpha[0:nfod[s], m] * V_tmp[0:nfod[s]])

                M_tmp2 = np.dot(M_tmp[0:nfod[s], 0:nfod[s]], gradovrlp[s, 0:nfod[s], 0:nfod[s], r])
                for m in range(0, nfod[s]):
                    for k in range(0, nfod[s]):
                        for l in range(0, nfod[s]):
                            D1_km[l, k, m, r] = D1_km[l, k, m, r] + M_tmp[m, k] * M_tmp2[l, m]

                # Get D1_kmd (the lower case d meaning delta).

                for m in range(nfod[s]):
                    D1_kmd[0:nfod[s], 0:nfod[s], m, r] = D1_km[0:nfod[s], 0:nfod[s], m, r] - \
                        np.transpose(D1_km[0:nfod[s], 0:nfod[s], m, r])

                # Get the first part of the forces.

                for m in range(nfod[s]):
                    for k in range(nfod[s]):
                        for l in range(nfod[s]):
                            fforce[s, m, r] = fforce[s, m, r] + D1_kmd[l, k, m, r] * eps[s, l, k]

                # Get D3_km.

                for m in range(nfod[s]):
                    for k in range(nfod[s]):
                        for l in range(nfod[s]):
                            for a in range(nfod[s]):
                                for b in range(nfod[s]):
                                    tmp1 = T_alpha[b, k] * T_alpha[a, l] * np.sqrt(Q_alpha[a])
                                    tmp2 = T_alpha[a, k] * T_alpha[b, l] * np.sqrt(Q_alpha[b])
                                    tmp3 = (np.sqrt(Q_alpha[a]) + np.sqrt(Q_alpha[b])) * \
                                        np.sqrt(Q_alpha[a] * Q_alpha[b])
                                    D3_km[l, k, m, r] = D3_km[l, k, m, r] - 0.5 * \
                                        TdST[b, a, m, r] * ((tmp1 + tmp2) / tmp3)

                # Get D3_kmd (the lower case d meaning delta).

                for m in range(nfod[s]):
                    D3_kmd[0:nfod[s], 0:nfod[s], m, r] = D3_km[0:nfod[s], 0:nfod[s], m, r] - \
                        np.transpose(D3_km[0:nfod[s], 0:nfod[s], m, r])

                # Get the second part of the forces.

                for m in range(nfod[s]):
                    for k in range(nfod[s]):
                        for l in range(nfod[s]):
                            fforce[s, m, r] = fforce[s, m, r] + D3_kmd[l, k, m, r] * eps[s, l, k]

    # Output the forces.

    fforce_output[0:nfod[0], :] = fforce[0, 0:nfod[0], :]
    if nfod[1] != 0:
        fforce_output[nfod[0]:(nfod[1] + nfod[0]), :] = fforce[1, 0:nfod[1], :]
    if debug:
        write_force(fforce_output)

    return fforce_output

# This outputs the forces in the same format as NRMOL.


def write_force(frc, name='fforce.dat'):
    f = open(name, 'w')
    for fi in range(len(frc)):
        f.write('%0.14f %0.14f %0.14f \n' % (frc[fi][0], frc[fi][1], frc[fi][2]))
    f.close()

# Flosic routine for AO formalism. Needs an mole object, a calculator and the FOD
# positions. Everything else is optional. For the output, see the dictionary initialized
# below.


def flosic(
        mol,
        mf,
        fod1,
        fod2,
        sysname=None,
        datatype=np.float64,
        print_dm_one=False,
        print_dm_all=False,
        debug=False,
        calc_forces=True,
        nuclei=None,
        l_ij=None,
        ods=None,
        idx_1s=[
            0,
            0],
    fixed_vsic=None,
        ham_sic='HOO'):

    # Get the atomic overlap and set the number of spins to two.

    s1e = mf.get_ovlp(mol)
    nspin = 2

    # Get the KSO.

    ks = np.array(mf.mo_coeff)

    # Build the KSO density matrix.

    dm_ks = mf.make_rdm1()

    # Get the dimensions.

    nks_work = np.shape(ks)
    nks = nks_work[1]

    # Get the occupation of the KSO.

    occup = np.array(mf.mo_occ).copy()
    nksocc = nspin * [0]
    for j in range(nspin):
        for i in range(0, nks):
            if occup[j][i] != 0.0:
                nksocc[j] += 1
    
    # SS: commented out, for timing 
    #print('occup')
    #print(occup)
    #print('nksocc')
    #print(nksocc)

    # Get the Kohn-Sham orbitals at FOD positions.
    # psi_ai_spin has the dimension (Number of FODS x spin x Number of KS wf)
    # Obviously, we have to rearrange that, so that only the spin that is actually needed
    # for the descriptor is taken into account.
    # IMPORTANT! Units have to be in Bohr!

    ao1 = numint.eval_ao(mol, fod1.positions / units.Bohr)
    psi_ai_1 = ao1.dot(ks)
    # SS: commented out, for timing 
    #print('psi_ai_1')
    #print(psi_ai_1)
    ao2 = numint.eval_ao(mol, fod2.positions / units.Bohr)
    psi_ai_2 = ao2.dot(ks)
    # SS: commented out for timing 
    #print('psi_ai_2')
    #print(psi_ai_2)

    nfod = nspin * [0]

    # Get the FOD dimensions.

    nfod[0] = int(psi_ai_1.shape[-3])
    nfod[1] = int(psi_ai_2.shape[-3])

    # Some diagnostic output.

    if debug:
        print('FLOSIC input: DONE.')
        print(
            'Parameters: \n{:d} FODs for spin 0 \n{:d} FODs for spin 1 \n{:d} KS wavefunctions in total \n{:d} occupied KS orbitals for spin1 \n{:d} occupied KS orbitals for spin2'.format(
                nfod[0],
                nfod[1],
                nks,
                nksocc[0],
                nksocc[1]))

    # Get psi_ai_work, which then gets passed to the rotation matrix building routine.

    psi_ai_work = np.zeros((nspin, np.max(nfod), np.max(nksocc)), dtype=datatype)

    # Iterate over the spin.

    for j in range(nspin):
        l = 0

        # Iterate over the Kohn sham wf.

        for i in range(0, nks):
            if occup[j][i] != 0.0:

                # Iterate over the FODs.

                for k in range(0, nfod[j]):
                    if j == 0:
                        psi_ai_work[j, k, l] = psi_ai_1[k, j, i]
                    if j == 1:
                        psi_ai_work[j, k, l] = psi_ai_2[k, j, i]
                l = l + 1
            if l > nksocc[j]:
                print('WARNING: Attempting to use not occupied KS wf for FLOSIC.')

    # SS: commented out, for timing 
    #print('psi_ai_work')
    #print(psi_ai_work)

    # Get the rotation matrix.

    R_ao = get_rot(nfod, psi_ai_work, nks, nspin, datatype=datatype, idx_1s=idx_1s)
    if idx_1s[0] != 0:
        print(R_ao)
    # Apply rotation matrix to the KSO.
    # fo will hold the FOs. sfo is needed in order to determine the overlap matrix.

    fo = np.zeros((nspin, nks, nks), dtype=datatype)
    sfo = np.zeros((nspin, nks, nks), dtype=datatype)

    for s in range(nspin):

        # Apply the rotation to the occupied orbitals.

        for i in range(idx_1s[s], nfod[s]):
            for j in range(idx_1s[s], nfod[s]):
                fo[s, :, i] = fo[s, :, i] + R_ao[s, i, j] * ks[s, :, j]

        # Copy the unoccupied orbitals.

        for i in range(nfod[s], nks):
            fo[s, :, i] = ks[s, :, i].copy()

        if idx_1s[s] != 0:
            fo[s, :, 0] = ks[s, :, 0].copy()

    if debug:
        print('KS have been transformed into FO.')
        print(fo)
    # Now we need to orthonormalize the FOs, in order to get the FLOs.

    flo = np.zeros((nspin, nks, nks), dtype=datatype)

    # Initialize everything for the Lowdin orthonormalization.

    T_lo = np.zeros((nspin, np.max(nfod), np.max(nfod)), dtype=datatype)
    Q_lo = np.zeros((nspin, np.max(nfod)), dtype=datatype)

    for s in range(0, nspin):
        if nfod[s] != 0:

            # Initialize the overlap of the FOs.

            ovrlp_fo = np.zeros((nfod[s], nfod[s]), dtype=datatype)

            # Get the overlap.
            # The atomic overlap is directly included in sfo.

            sroot = np.linalg.cholesky(s1e)
            sfo[s, :, :] = np.dot(np.transpose(sroot), fo[s, :, :])
            ovrlp_fo[0:nfod[s], 0:nfod[s]] = np.dot(np.transpose(sfo[s, :, 0:nfod[s]]), sfo[s, :, 0:nfod[s]])

            # This is a Lowdin symmetric orthonormalization.

            q_fo, v_fo = linalg.eigh(ovrlp_fo)
            T_lo[s, 0:nfod[s], 0:nfod[s]] = v_fo
            Q_lo[s, 0:nfod[s]] = q_fo
            one_div_d = (1.0 / np.sqrt(q_fo)) * np.eye(nfod[s])
            vinv_fo = (np.transpose(v_fo))
            tra1 = np.dot(v_fo, one_div_d)
            trafo = np.dot(tra1, vinv_fo)
            for j in range(0, nfod[s]):
                for i in range(0, nfod[s]):
                    flo[s, :, j] = trafo[i, j] * fo[s, :, i] + flo[s, :, j]

            # For the unoccupied orbitals copy the FOs (and therefore the KSO).

            for i in range(nfod[s], nks):
                flo[s, :, i] = fo[s, :, i].copy()

            # if idx_1s[s] != 0:
                #        flo[s,:,0] = ks[s,:,0].copy()

    if debug:
        print('FO have been transformed into FLO.')
        print(flo)

    # Now we want to calculate the SIC. Therefore, variables summing the SIC contribution
    # of the orbitals are initialized.

    exc_sic_flo = 0.0
    ecoul_sic_flo = 0.0
    nelec_sic_flo = 0.0

    # Get the KS total energy. This is needed to calculate e_sic as difference between
    # e_tot(flosic) - e_tot(dft)

    etot_ks = mf.e_tot

    # The variables vsics and onedm save the contributions of the orbitals themselves.

    vsics = np.zeros((nspin, np.max(nfod), nks, nks), dtype=datatype)
    onedm = np.zeros((nspin, np.max(nfod), nks, nks), dtype=datatype)

    # Save for fixed vsic

    all_veff_work_flo_up = []
    all_veff_work_flo_dn = []
    all_veff_work_flo = []

    all_exc_work_flo_up = []
    all_exc_work_flo_dn = []
    all_exc_work_flo = []
    all_ecoul_work_flo_up = []
    all_ecoul_work_flo_dn = []
    all_ecoul_work_flo = []

    if fixed_vsic is not None:
        all_veff_work_flo = fixed_vsic[0]
        all_exc_work_flo = fixed_vsic[1]
        all_ecoul_work_flo = fixed_vsic[2]

    # Bra and Ket are useful for doing scalar products using matrix multiplication.

    ket = np.zeros((nks, 1), dtype=datatype)
    bra = np.zeros((1, nks), dtype=datatype)

    for s in range(0, nspin):

        # Get the SIC for every orbital.

        for j in range(0, nfod[s]):

            # Build the occupancy array in order to get one electron densities.

            occup_work = np.array(mf.mo_occ).copy()
            for i in range(0, nks):
                if i == j:
                    occup_work[0][i] = 0.
                    occup_work[1][i] = 0.
                    occup_work[s][i] = 1.
                else:
                    occup_work[0][i] = 0.
                    occup_work[1][i] = 0.

            # Build the one electron densities.

            dm_work_flo = dynamic_rdm(flo, occup_work)
            onedm[s, j] = dm_work_flo[s]

            # Diagnostic output, if needed. This checks the one electron matrices.

            if debug:
                print('One-FOD-Density-Matrix')
                print(dm_work_flo)

            if fixed_vsic is None:
                # Get the SIC potential and energy for FLO.

                veff_work_flo = mf.get_veff(mol=mol, dm=dm_work_flo)
                if s == 0:
                    all_veff_work_flo_up.append(veff_work_flo[s])
                if s == 1:
                    all_veff_work_flo_dn.append(veff_work_flo[s])

                # Save the SIC potential.

                vsics[s, j] = veff_work_flo[s]

                # Get the SIC energy parts for every FLO.

            if fixed_vsic is not None:

                # print s
                # print j
                veff_work_flo = all_veff_work_flo[s][j]
                # print type(veff_work_flo)
                # print veff_work_flo.__dict__
                vsics[s, j] = veff_work_flo

            if ods is None:
                if fixed_vsic is None:
                    exc_work_flo = veff_work_flo.__dict__['exc']
                    if s == 0:
                        all_exc_work_flo_up.append(exc_work_flo)
                    if s == 1:
                        all_exc_work_flo_dn.append(exc_work_flo)
                if fixed_vsic is not None:
                    exc_work_flo = all_exc_work_flo[s][j]
            if ods:
                rhoi = dft.numint.get_rho(mf._numint, mol, dm_work_flo[s], mf.grids)
                rhot = dft.numint.get_rho(mf._numint, mol, dm_ks, mf.grids)
                print('rhot', rhot.sum())
                print('rhoi', rhoi.sum())
                print('rho_i.sum()/rhot.sum()', rhoi.sum() / rhot.sum())
                Xi = (rhoi.sum() / rhot.sum())**(0.04)
                exc_i = veff_work_flo.__dict__['exc']
                print('Xi', Xi)
                exc_work_flo = Xi * exc_i

                #full_grid_coords = mf.grids.coords
                #full_grid_weights = mf.grids.weights
                #full_fxc = mf.xc
                #exc_lo = 0.0
                # print mf.grids.coords.shape[0]
                # for MP_i in range(full_grid_coords.shape[0]):
                #    mf.grids.coords = full_grid_coords
                #    mf.grids.weights = full_grid_weights
                #    mf.xc = full_fxc
                #    print mf.grids.coords.shape
                #    print mf.grids.weights.shape
                #    #MP_i =  np.array([[mf.grids.coords[MP_i,0],mf.grids.coords[MP_i,1],mf.grids.coords[MP_i,2]]])
                #    #print MP_i.shape
                #    #print MP_i[0,:]
                #           # select the Meshpoint and Weight
                #           mf.grids.coords = np.array([[mf.grids.coords[MP_i,0],mf.grids.coords[MP_i,1],mf.grids.coords[MP_i,2]]])
                #           mf.grids.weights = np.array([mf.grids.weights[MP_i]])
                #           # calculate that Xi for that MP_i
                #           rho_i= dft.numint.get_rho(mf._numint,mol,dm_work_flo,mf.grids)
                #           rho_t = dft.numint.get_rho(mf._numint,mol,dm_ks,mf.grids)
                #           lampda = 0.2
                #           Xi = (rho_i/rho_t)**lampda
                #           # set up a MP_i dependet fxc
                #           mf.xc = '%0.5f*%s,%0.5f*%s' % (Xi,full_fxc.split(',')[0],Xi,full_fxc.split(',')[1])
                #           # calculate exc only for that MP_i
                #           veff_work_flo = mf.get_veff(mol=mol,dm=dm_work_flo)
                #           exc_work_flo = veff_work_flo.__dict__['exc']
                #           # sum over all MP_i
                #    exc_lo = exc_lo + exc_work_flo
                #exc_work_flo = exc_lo
                #mf.grids.coords = full_grid_coords
                #mf.grids.weights = full_grid_weights
                #mf.xc = full_fxc
            if fixed_vsic is None:
                ecoul_work_flo = veff_work_flo.__dict__['ecoul']
                if s == 0:
                    all_ecoul_work_flo_up.append(ecoul_work_flo)
                if s == 1:
                    all_ecoul_work_flo_dn.append(ecoul_work_flo)
            if fixed_vsic is not None:
                ecoul_work_flo = all_ecoul_work_flo[s][j]
            # Increment the SIC energy.

            exc_sic_flo = exc_sic_flo + exc_work_flo
            ecoul_sic_flo = ecoul_sic_flo + ecoul_work_flo

            # Diagnostic output, if needed. This checks once again if electrons have been 'lost'.

            if debug:
                nelec_work_flo, dumm1, dumm2 = dft.numint.nr_vxc(mol, mf.grids, mf.xc, dm_work_flo, spin=1)
                nelec_sic_flo = nelec_sic_flo + nelec_work_flo

    # Save values for fixed_vsic

    all_veff_work_flo = [all_veff_work_flo_up, all_veff_work_flo_dn]
    all_exc_work_flo = [all_exc_work_flo_up, all_exc_work_flo_dn]
    all_ecoul_work_flo = [all_ecoul_work_flo_up, all_ecoul_work_flo_dn]

    # Print the density matrix if wished.

    if debug:
        dm_flo = dynamic_rdm(flo, occup)
        print('Complete-FOD-Density-Matrix')
        print(dm_flo)

    # Now that we got all the contributions, build the SIC energy.

    esic_flo = ecoul_sic_flo + exc_sic_flo
    # SS: commented out, timing 
    #print('ESIC {}'.format(esic_flo))
    etot_sic_flo = etot_ks - esic_flo
    # SS: commented out, timing 
    # print('Etot {}'.format(etot_sic_flo))

    # Next step is the energy eigenvalue correction / SIC Hamiltonian.
    # First, initialize all variables.

    h_sic = np.zeros((nspin, nks, nks), dtype=datatype)
    h_sic_virtual = np.zeros((nspin, nks, nks), dtype=datatype)
    h_ks = np.zeros((nspin, nks, nks), dtype=datatype)
    v_virtual = np.zeros((nspin, nks, nks), dtype=datatype)
    sumpfs = np.zeros((nks, nks), dtype=datatype)
    lambda_ij = np.zeros((nspin, np.max(nfod), np.max(nfod)), dtype=datatype)

    # We also need the DFT hamiltonian.

    dm_ks = mf.make_rdm1()
    h1e = mf.get_hcore(mol)
    vhf = mf.get_veff(mol, dm_ks)
    hamil = mf.get_fock(h1e, s1e, vhf, dm_ks)

    # v_virtual is the projector of the virtual subspace, that might be needed
    # depending on which unified hamiltonian approximation is used.

    for s in range(0, nspin):
        if nfod[s] != 0:
            for i in range(nfod[s], nks):
                bra[0, :] = np.transpose(flo[s, :, i])
                ket[:, 0] = (flo[s, :, i])
                v_virtual[s] = v_virtual[s] + np.dot(ket, bra)

    # Get the KS eigenvalues for comparison.

    eval_ks, trash = mf.eig(hamil, s1e)

    # Calculate the Cholesky decomposition of the atomic overlap and apply it to the
    # FLO. With this, things like the overlap matrix can be calculated more easily.

    sflo = np.zeros((nspin, nks, nks), dtype=datatype)
    sroot = np.linalg.cholesky(s1e)
    for s in range(nspin):
        sflo[s] = np.dot(np.transpose(sroot), flo[s, :, :])

    # Get epsilon^k_kl, here named lambda to avoid confusion. (This is needed for the
    # forces.)
    # SS: commented out, for timing 
    #print('vsics: {}'.format(vsics))
    for s in range(nspin):
        for j in range(nfod[s]):
            for i in range(nfod[s]):
                bra[0, :] = np.transpose(flo[s, :, i])
                ket[:, 0] = (flo[s, :, j])
                right = np.dot(vsics[s, j], ket)
                lambda_ij[s, i, j] = -np.dot(bra, right)

    # Test lampda_ij as well input for the AF correction
    cst = np.zeros((nspin, np.max(nfod), np.max(nfod)), dtype=datatype)

    if l_ij:
        kappa_ij = np.zeros((nspin, np.max(nfod), np.max(nfod)), dtype=datatype)
        for s in range(nspin):
            for j in range(nfod[s]):
                for i in range(nfod[s]):
                    bra[0, :] = np.transpose(flo[s, :, i])
                    # print '<bra,bra>'
                    # print np.dot(bra,sflo[s,:,i])
                    ket[:, 0] = (flo[s, :, j])
                    # print '<ket|ket>'
                    # print np.dot(np.transpose(ket),ket)
                    delta = vsics[s, i] - vsics[s, j]
                    #delta = np.dot(np.transpose(sroot),vsics[s,i]-vsics[s,j])
                    right = np.dot(delta, ket)
                    right1 = np.dot(vsics[s, i], ket)
                    #right1 = np.dot(np.transpose(sroot),right1)
                    right2 = np.dot(vsics[s, j], (flo[s, :, i]))
                    #right2 = np.dot(np.transpose(sroot),right2)
                    kappa_ij[s, i, j] = 1 * (np.dot(bra, right))
                    #lambda_ij[s,i,j] = np.dot(bra,right1) - np.dot(np.transpose(flo[s,:,j]),right2)
                    # test
                    cst[s, i, j] = np.dot(bra, ket)
        for s in range(nspin):
            for i in range(nfod[s]):
                for j in range(nfod[s]):
                    bra[0, :] = np.transpose(flo[s, :, i])
                    # print '<bra,bra>'
                    # print np.dot(bra,sflo[s,:,i])
                    ket[:, 0] = (flo[s, :, j])
                    # print '<ket|ket>'
                    # print np.dot(np.transpose(ket),ket)
                    delta = vsics[s, i] - vsics[s, j]
                    #delta = np.dot(np.transpose(sroot),vsics[s,i]-vsics[s,j])
                    right = np.dot(delta, ket)
                    right1 = np.dot(vsics[s, i], ket)
                    #right1 = np.dot(np.transpose(sroot),right1)
                    right2 = np.dot(vsics[s, j], (flo[s, :, i]))
                    #right2 = np.dot(np.transpose(sroot),right2)
                    kappa_ij[s, i, j] = lambda_ij[s, i, j] - 1 * (np.dot(bra, right))
                    #lambda_ij[s,i,j] = np.dot(bra,right1) - np.dot(np.transpose(flo[s,:,j]),right2)
                    # test
                    cst[s, i, j] = np.dot(bra, ket)

    if l_ij:
        for s in range(nspin):
            # printing the lampda_ij matrix for both spin channels
            print('kappa_ij spin%0.1f' % s)
            print(kappa_ij[s, :, :])
            # print 'RMS lambda_ij'
            #M = lambda_ij[s,:,:]
            #print (M-M.T)[np.triu_indices((M-M.T).shape[0])].sum()
            print('RMS lambda_ij')
        print(force_max_lij(kappa_ij))

    # DEV
    # (SS)    Debuging atomic force correction
    #    AF = Force1 + Force2
    #    AF = -2 \sum_{i=1}^{N}\sum_{s,t}^{N_bas} c_s^{i}c_t^{i} < df_s/dR_nu| H_SIC | f_t> +
    #         +2 \sum_{i,j}^{M}\lampda_{ij}\sum_{s,t}^{N_bas} c_s^{i}c_t^{j} < df_s/dR_nu| f_t>
    #     we assuming that we have Force one while updating the hamiltonian in SCF modus
    #    therefore we only try to implement the Force2 term
    hans = 5
    if hans == 4:
        gradpsi_nuclei = np.zeros((nspin, np.max(nfod), len(nuclei), 3), dtype=datatype)
        #gradpsi_nuclei = np.zeros((nspin,np.max(nfod),np.max(nksocc),3), dtype=datatype)
        for s in range(nspin):
            # printing the lampda_ij matrix for both spin channels
            print('lambda_ij')
            print(lambda_ij[s, :, :])

        #nuc = nuclei.positions/units.Bohr
        # for nu in range(len(nuc)):

        # get the gradient of the basis functions at the nuclei positions
        # all positions at some time
        # the next lines are similiar to the FOD generation while changing fod1 to nuclei
        print('Nuclei positions [Bohr]')
        print(nuclei.positions / units.Bohr)
        nuclei1 = mol.eval_gto('GTOval_ip_sph', nuclei.positions / units.Bohr, comp=3)
        gradpsi_nuclei1 = [x.dot(flo) for x in nuclei1]
        nuclei2 = mol.eval_gto('GTOval_ip_sph', nuclei.positions / units.Bohr, comp=3)
        gradpsi_nuclei2 = [x.dot(flo) for x in nuclei2]

        print('Grad nuclei1')
        print(np.shape(gradpsi_nuclei1))

        # Rearrange the data to make it more usable.

        x_1 = gradpsi_nuclei1[0]
        y_1 = gradpsi_nuclei1[1]
        z_1 = gradpsi_nuclei1[2]
        x_2 = gradpsi_nuclei2[0]
        y_2 = gradpsi_nuclei2[1]
        z_2 = gradpsi_nuclei2[2]

        # Iterate over the spin.
        for j in range(0, nspin):
            l = 0

            # Iterate over the Kohn sham wf.

            for i in range(0, nfod[j]):
                if occup[j][i] != 0.0:

                    # Iterate over the fods.

                    for k in range(0, nfod[j]):
                        if j == 0:
                            gradpsi_nuclei[j, k, l, 0] = x_1[k][j][i]
                            gradpsi_nuclei[j, k, l, 1] = y_1[k][j][i]
                            gradpsi_nuclei[j, k, l, 2] = z_1[k][j][i]
                        if j == 1:
                            gradpsi_nuclei[j, k, l, 0] = x_2[k][j][i]
                            gradpsi_nuclei[j, k, l, 1] = y_2[k][j][i]
                            gradpsi_nuclei[j, k, l, 2] = z_2[k][j][i]
                    l = l + 1
        # Variables neeed later
        sroot = np.zeros((np.max(nfod), np.max(nfod)), dtype=datatype)
        sroot = np.linalg.cholesky(s1e)
        sks = np.zeros((nspin, nks, nks), dtype=datatype)
        # Components of the AF correction
        AFx = np.zeros((nspin, len(nuclei)), dtype=datatype)
        AFy = np.zeros((nspin, len(nuclei)), dtype=datatype)
        AFz = np.zeros((nspin, len(nuclei)), dtype=datatype)
        for s in range(nspin):
            # This is for debugging reasons we need a different sign for the force
            if int(s) == int(0):
                print('SPIN UP')
                pre = 1.
            if int(s) != int(0):
                print('SPIN DOWN')
                pre = -1.

            # Fill sks
            sks[s, :, :] = np.dot(np.transpose(sroot), ks[s, :, :])

            # Get AF force correction .
            for i in range(0, nfod[s]):
                sumx = np.zeros((nfod[s]), dtype=datatype)
                sumy = np.zeros((nfod[s]), dtype=datatype)
                sumz = np.zeros((nfod[s]), dtype=datatype)
                for a in range(0, nfod[s]):
                    # we need a correction for each cartesian coordinate (x,y,z)
                    # gradient of the basis function x basisfunction summed over grid
                    #sumx = (gradpsi_nuclei[s,:,a,0]*sks[s,:,a]).sum() + sumx
                    #sumy = (gradpsi_nuclei[s,:,a,1]*sks[s,:,a]).sum() + sumy
                    #sumz = (gradpsi_nuclei[s,:,a,2]*sks[s,:,a]).sum() + sumz
                    sumx = (gradpsi_nuclei[s, :, a, 0] * flo[s, :, i]).sum() + sumx
                    sumy = (gradpsi_nuclei[s, :, a, 1] * flo[s, :, i]).sum() + sumy
                    sumz = (gradpsi_nuclei[s, :, a, 2] * flo[s, :, i]).sum() + sumz
                    flo[s, :, i]
                # the prefactor of the lampda matrix
                af1 = 2. * lambda_ij[s, :, :].sum()
                # the prefactor of the coeffcients
                af2 = cst[s, :, :].sum()
                afx = af1 * af2 * sumx
                afy = af1 * af2 * sumy
                afz = af1 * af2 * sumz
                # For now we using only on spin channel
                # I introduced a spin scanling factor of sqrt(2)
                ss = 1.  # 2.*np.sqrt(2.)
                AFx[s, i] = ss * pre * afx.sum()
                AFy[s, i] = ss * pre * afy.sum()
                AFz[s, i] = ss * pre * afz.sum()

        print('Atomic force correction')
        AF = []
        print('AF_dx')
        print(AFx)
        print('AF_dy')
        print(AFy)
        print('AF_dz')
        print(AFz)
        for i in range(0, len(nuclei)):
            if i == 0:
                AF.append([AFx[0, 0] - AFx[1, 0], AFy[0, 0] - AFy[1, 0], AFz[0, 0] - AFz[1, 0]])
                print('%i %0.5f %0.5f %0.5f' % (i, AFx[0, 0] - AFx[1, 0], AFy[0, 0] - AFy[1, 0], AFz[0, 0] - AFz[1, 0]))
            if i == 1:
                AF.append([abs(AFx[0, 0]) + abs(AFx[1, 0]), abs(AFy[0, 0]) +
                          abs(AFy[1, 0]), abs(AFz[0, 0]) + abs(AFz[1, 0])])
                print('%i %0.5f %0.5f %0.5f' %
                      (i, abs(AFx[0, 0]) +
                       abs(AFx[1, 0]), abs(AFy[0, 0]) +
                          abs(AFy[1, 0]), abs(AFz[0, 0]) +
                          abs(AFz[1, 0])))

        # the AF variable will be returned to other functions
        # if debug= True option is chosen
        print(AF)

    # Do the energy eigenvalue correction and the SIC Hamiltonian.

    for s in range(nspin):
        sumpfs[:, :] = 0.0
        if nfod[s] != 0:
            for i in range(0, nfod[s]):

                # Assuming that virtual coefficients are zero.

                ps = np.dot(onedm[s, i], s1e)
                pf = np.dot(onedm[s, i], vsics[s, i])
                fps = np.dot(vsics[s, i], ps)
                spf = np.dot(s1e, pf)
                h_sic[s] = h_sic[s] + fps + spf

                # Assuming they are not.
                # NOTE: They almost always are in our formalism. I'm not deleting this
                # code because it might come in handy at some other point, but it is more
                # or less not needed.

                pfp = np.dot(pf, onedm[s, i])
                fp = np.dot(vsics[s, i], onedm[s, i])
                vfp = np.dot(v_virtual[s], fp)
                pfv = np.dot(pf, v_virtual[s])
                sumpf = pfp + vfp + pfv
                sumpfs = np.dot(sumpf, s1e) + sumpfs

            # Get the SIC Hamiltonian.

            h_sic[s] = -0.5 * h_sic[s]
            h_sic_virtual[s] = -np.dot(s1e, sumpfs)
            h_ks[s] = eval_ks[s] * np.eye(nks, nks)

    # Get the SIC eigenvalues.

    eval_flo, trash = mf.eig(hamil + h_sic, s1e)
    # SS: commented out, for timing 
    # print('HOO: {}'.format(eval_flo))

    # Again, the next line is only for cases where the virtual coefficient are not zero, which they should be here.

    eval_flo_2, trash = mf.eig(hamil + h_sic_virtual, s1e)
    # SS: commented out, for timing
    #print('HOOOV: {}'.format(eval_flo_2))
    if ham_sic == 'HOOOV':
        eval_flo = eval_flo_2

    for s in range(nspin):

        # Output the HOMO energy eigenvalue if needed.
        # Get the HOMO for DFT and FLO-SIC. Note: there might be two spin channels but
        # only one HOMO. Therefore we have to make sure the correct one is outputted.

        if nfod[s] != 0:
            if s == 0:
                HOMO_ks = 1. * eval_ks[s][nfod[s] - 1]
                HOMO_flo = 1 * eval_flo[s][nfod[s] - 1]
            if s == 1 and HOMO_ks < 1. * eval_ks[s][nfod[s] - 1]:
                HOMO_ks = 1. * eval_ks[s][nfod[s] - 1]
                HOMO_flo = 1 * eval_flo[s][nfod[s] - 1]

    # Print the HOMO values if wished.

    if debug:
        print('DFT, FLO-SIC HOMO value in Hartree', HOMO_ks, HOMO_flo)
        print('DFT, FLO-SIC HOMO value in eV', HOMO_ks * units.Hartree, HOMO_flo * units.Hartree)

    # Next step is to calculate the forces. This is done by the following routine.

    fforce_output = np.zeros((nfod[0] + nfod[1], 3), dtype=datatype)
    if calc_forces:
        fforce_output = get_fermi_forces(
            nspin,
            nfod,
            nks,
            nksocc,
            occup,
            mol,
            mf,
            fod1,
            fod2,
            psi_ai_work,
            ks,
            fo,
            s1e,
            T_lo,
            Q_lo,
            lambda_ij,
            R_ao,
            sysname,
            datatype,
            debug)

    # Output the results on the screen if wished. Output is also given in form of the
    # output dictionary.

    if debug:
        print('\n')
        print('-----Number-Of-----')
        print('Electrons in both spin channels: %0.5f %0.5f' % (nelec_sic_flo[0], nelec_sic_flo[1]))
        print('Number of FODs in both spin channels: %0.5f %0.5f' % (nfod[0], nfod[1]))
        print('The numbers in the two lines above should be identical.')
        print('If they are not, something went terribly wrong.')
        print('\n')
        print('-----Total Energy-----')
        print('Total Energy (DFT, FLO-SIC):  %0.5f %0.5f' % (etot_ks, etot_sic_flo))

    # Fill the output dictionary.
    if ham_sic == 'HOO':
        h_sic_ks_base = h_sic  # h_sic_virtual #h_sic
    if ham_sic == 'HOOOV':
        h_sic_ks_base = h_sic_virtual
    return_dict = {}
    # The DFT total energy.
    return_dict['etot_dft'] = etot_ks
    # The FLO-SIC total energy.
    return_dict['etot_sic'] = etot_sic_flo
    # The DFT HOMO value.
    return_dict['homo_dft'] = HOMO_ks
    # The FLO-SIC HOMO value.
    return_dict['homo_sic'] = HOMO_flo
    # The SIC Hamiltonian.
    return_dict['hamil'] = h_sic_ks_base
    # The FOD forces.
    return_dict['fforces'] = fforce_output
    # The FLOs.
    return_dict['flo'] = flo
    # The dipole momemt.
    return_dict['dipole'] = mf.dip_moment(verbose=0)
    # The FLO-SIC evalues.
    return_dict['evalues'] = eval_flo
    # The lambda_ij
    return_dict['lambda_ij'] = lambda_ij
    # The VSICs
    return_dict['fixed_vsic'] = [all_veff_work_flo, all_exc_work_flo, all_ecoul_work_flo]
    if hans == 3:
        # Test AF
        return_dict['AF'] = AF

    # Done with FLO-SIC!

    return return_dict


# This routine is borrowed from the pyscf code. It allows a reduced density matrix to be
# build using FOs or FLOs. It takes an mo_coeff-like array and mo_occ as an arbitrary
# occupation array as input.

def dynamic_rdm(mo_coeff, mo_occ):

    #    Taken from PySCF UKS class.

    spin_work = np.shape(mo_coeff)
    if spin_work[0] == 2:
        mo_a = mo_coeff[0]
        mo_b = mo_coeff[1]
        dm_a = np.dot(mo_a * mo_occ[0], mo_a.T.conj())
        dm_b = np.dot(mo_b * mo_occ[1], mo_b.T.conj())
        return np.array((dm_a, dm_b))
    else:
        mo_a = mo_coeff
        dm_a = np.dot(mo_a * mo_occ, mo_a.T.conj())
        return np.array((dm_a))

# Direct interface to the FLO-SIC routine for one-shot mode.


def calculate_flosic(ase_atoms=None, fname=None, spin=None, charge=0, debug=False, xc='LDA,PW',
                     basis='6-311++Gss', ghost=False, verbose=0, max_cycle=300, conv_tol=1e-5, grid=3):

    # Initiliaze the calculation.
    # Choose a datatype.

    dt = [np.complex128, np.float64][1]

    # Get the geometry configuration.

    if ase_atoms is None:
        if fname is not None:
            try:
                ase_atoms = read(fname + '.xyz')
            except BaseException:
                return None, None
        else:
            print('No input found. Ending the calculation.')
            return None, None
    else:
        if fname is None:
            fname = 'Unknown_System'

    # xyz_to_nuclei_fod gives both an array for the init of pyscf
    # as well as an array containing all the fods and core positions.
    # Core and fods are given back as ase atoms objects.

    pyscf_atoms, nuclei, fod1, fod2, included = xyz_to_nuclei_fod(ase_atoms)

    # Get the spin configuration.

    if spin is None:
        spin = get_multiplicity(fname)

    # Set the basis.

    b = basis

    # Optional symmetry parameter. In this case: linear molecules.

    issymmetric = False
    if issymmetric:
        mol.symmetry = 'D2h'

    # Initiliaze the mol object.

    if ghost:
        mol = gto.M(
            atom=pyscf_atoms, basis={
                'default': b, 'GHOST1': gto.basis.load(
                    'sto3g', 'H'), 'GHOST2': gto.basis.load(
                    'sto3g', 'H')}, spin=spin, symmetry=issymmetric, charge=charge)
    elif not ghost:
        mol = gto.M(atom=ase2pyscf(nuclei), basis={'default': b}, spin=spin, symmetry=issymmetric, charge=charge)
    if debug:
        print('Molecular Geometry: ', mol.atom)
        print('Spin Configuration: ', spin)

    # Initiliaze the DFT calculator.

    mf = dft.UKS(mol)
    mf.verbose = verbose
    mf.max_cycle = max_cycle
    mf.conv_tol = conv_tol

    if debug:
        mf.verbose = 4

    # Grid level, default is 3.

    mf.grids.level = grid

    # Choose an xc functional.

    mf.xc = xc
    print('DFT calculator initilization: DONE.')
    print('Functional used:', mf.xc)

    # Do the calculation.
    # This is a one shot calculation.

    print('FLOSIC calculation entered in the one-shot mode.')

    # Ground state calculation.

    mf.kernel()
    print('Ground state calculation: DONE.')

    # Call the flosic routine.

    flosic_values = flosic(mol, mf, fod1, fod2, fname, datatype=dt, debug=debug, nuclei=nuclei)
    print('FLOSIC: DONE.')

    # FLO-SIC is done, output the values.

    return flosic_values


# This is the main script that allows for a fast test to be done.
# The only required input is a system name that one wants to calculate.

if __name__ == "__main__":
    from ase.atoms import Atoms
    from ase.io import read
    import os
    #f_xyz = os.path.dirname(os.path.realpath(__file__))+'/../examples/basic_calculations/H2.xyz'
    #f_xyz = os.path.dirname(os.path.realpath(__file__))+'/../test/CH4.xyz'
    #ase_atoms = read(f_xyz)
    ase_atoms = Atoms('HHXHe', [[0, 0, 0.3707], [0, 0, -0.3707], [0, 0, 0], [0, 0, 0]])
    flosic_values = calculate_flosic(ase_atoms, 'H2', debug=True, basis='STO3G', xc='LDA,PW')
    print(flosic_values['fforces'])
