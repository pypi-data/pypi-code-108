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
import numpy
import scipy
from pyscf import dft
from pyscf.dft import numint
from pyflosic2.units import units
from pyflosic2.time.timeit import tictoc, history
import functools

""" Construction of Fermi-Loewdin orbitals (FLOs) mode=unrestricted"""

def get_nksocc(mf, p):
    """
        Get nksocc
        ----------

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        nksocc : Number of occupied orbitals
    """
    nksocc = p.nspin * [0]
    # Unrestricted calculation
    if p.nspin == 2:
        for j in range(p.nspin):
            for i in range(0, p.nks):
                if int(p.occup[j][i]) != int(0):
                    nksocc[j] += 1
    else:
        p.log.write('You should not use restricted input (spin=1) in an unrestricted routine (in uflo.py)!')
        # Add abort statement ?
    return nksocc


def get_PSI_ai(mf, p):
    """
        Get PSI_ai
        ----------

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        psi_ai_work : psi evaluated a FODi (ai)

    """
    # mol can be carried by both mf and p
    # fod1/fod2 should be carried by p
    #
    # Unrestricted calculation
    if p.nspin == 2:
        # Working array initialization
        ao1 = numint.eval_ao(mf.mol, p.fod1.positions / units.Bohr)
        psi_ai_1 = ao1.dot(mf.mo_coeff)
        ao2 = numint.eval_ao(mf.mol, p.fod2.positions / units.Bohr)
        psi_ai_2 = ao2.dot(mf.mo_coeff)
        psi_ai_work = numpy.zeros((p.nspin, numpy.max(p.nfod), numpy.max(p.nksocc)), dtype=p.datatype)
        # Iterate over the spin.
        for j in range(p.nspin):
            l = 0
            # Iterate over the Kohn sham wf.
            for i in range(0, p.nks):
                if int(p.occup[j][i]) != int(0):
                    # Iterate over the FODs.
                    for k in range(0, p.nfod[j]):
                        if j == 0:
                            psi_ai_work[j, k, l] = psi_ai_1[k, j, i]
                        if j == 1:
                            psi_ai_work[j, k, l] = psi_ai_2[k, j, i]
                    l = l + 1
                if l > p.nksocc[j]:
                    p.log.write('WARNING: Attempting to use unoccupied KS wf for FLOSIC.')
    else:
        p.log.write('You should not use restricted input (spin=1) in an unrestricted routine (in uflo.py)!')
        # Add abort statement ?

    if p.verbose >= 4:
        p.log.write('psi_ai_work')
        p.log.write(str(psi_ai_work))
    return psi_ai_work


def get_R(mf, p):
    """
        Get R
        -----
        Get the rotation matrix.

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        R_ao : rotation matrix
    """
    # old: (nfod,Psi_ai,nks,NSPIN,datatype=np.float64,idx_1s=[0,0]):
    # Unrestricted calculation
    if p.nspin == 2:
        # Init the rotation matrix.
        R_ao = numpy.zeros((p.nspin, p.nks, p.nks), dtype=p.datatype)
        for s in range(p.nspin):
            for i in range(0, p.nks):
                R_ao[s, i, i] = 1.0
        # Get SUMPsi_ai (density at every point).
        SUMPsi_ai = numpy.zeros((p.nspin, numpy.max(p.nfod)), dtype=p.datatype)
        for s in range(p.nspin):
            for m in range(0, p.nfod[s]):
                SUMPsi_ai[s, m] = numpy.sqrt(numpy.sum((p.PSI_ai[s, m, :])**2))
        # Build the rotation matrices.
        for s in range(p.nspin):
            for m in range(0, p.nfod[s]):
                for i in range(0, p.nfod[s]):
                    # print(p.PSI_ai[s,m,i])
                    R_ao[s, m, i] = p.PSI_ai[s, m, i] / SUMPsi_ai[s, m]
    else:
        p.log.write('You should not use restricted input (spin=1) in an unrestricted routine (in uflo.py)!')
        # Add abort statement ?

    if p.verbose >= 4:
        p.log.write('Build rotation matrix R_ao')
    return R_ao


def get_FO(mf, p):
    """
        Get Fermi orbitals (FO)
        -----------------------
        Apply rotation matrix to the KSO.

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        fo : Fermi orbitals (FOs)
    """
    # Unrestricted calculation
    if p.nspin == 2:
        fo = numpy.zeros((p.nspin, p.nks, p.nks), dtype=p.datatype)
        for s in range(p.nspin):
            # Apply the rotation to the occupied orbitals.
            for i in range(0, p.nfod[s]):
                for j in range(0, p.nfod[s]):
                    fo[s, :, i] = fo[s, :, i] + p.R_ao[s, i, j] * mf.mo_coeff[s, :, j]
            # Copy the unoccupied orbitals.
            for i in range(p.nfod[s], p.nks):
                fo[s, :, i] = mf.mo_coeff[s, :, i].copy()
    else:
        p.log.write('You should not use restricted input (spin=1) in an unrestricted routine (in uflo.py)!')
        # Add abort statement ?

    if p.verbose >= 4:
        p.log.write('KS have been transformed into FO.')
    return fo


def get_FLO(mf, p):
    """
        Get Fermi-Lowedin orbitals (FLOs)
        --------------------------------
        We need to orthonormalize the FOs in order to get the FLOs.


        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        flo : Fermi-Lowedin orbitals (FLOs)
    """
    # Unrestricted calculation
    if p.nspin == 2:
        flo = numpy.zeros((p.nspin, p.nks, p.nks), dtype=p.datatype)
        # sfo is needed in order to determine the overlap matrix.
        sfo = numpy.zeros((p.nspin, p.nks, p.nks), dtype=p.datatype)
        # Initialize everything for the Lowdin orthonormalization.
        T_lo = numpy.zeros((p.nspin, numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
        Q_lo = numpy.zeros((p.nspin, numpy.max(p.nfod)), dtype=p.datatype)
        for s in range(0, p.nspin):
            if p.nfod[s] != 0:
                # Initialize the overlap of the FOs.
                ovrlp_fo = numpy.zeros((p.nfod[s], p.nfod[s]), dtype=p.datatype)
                # Get the overlap.
                # The atomic overlap is directly included in sfo.
                sroot = numpy.linalg.cholesky(p.s1e)
                sfo[s, :, :] = numpy.dot(numpy.transpose(sroot), p.fo[s, :, :])
                ovrlp_fo[0:p.nfod[s], 0:p.nfod[s]] = numpy.dot(
                    numpy.transpose(sfo[s, :, 0:p.nfod[s]]), sfo[s, :, 0:p.nfod[s]])
                # This is a Lowdin symmetric orthonormalization.
                q_fo, v_fo = scipy.linalg.eigh(ovrlp_fo)
                T_lo[s, 0:p.nfod[s], 0:p.nfod[s]] = v_fo
                Q_lo[s, 0:p.nfod[s]] = q_fo
                one_div_d = (1.0 / numpy.sqrt(q_fo)) * numpy.eye(p.nfod[s])
                vinv_fo = (numpy.transpose(v_fo))
                tra1 = numpy.dot(v_fo, one_div_d)
                trafo = numpy.dot(tra1, vinv_fo)
                for j in range(0, p.nfod[s]):
                    for i in range(0, p.nfod[s]):
                        flo[s, :, j] = trafo[i, j] * p.fo[s, :, i] + flo[s, :, j]
                # For the unoccupied orbitals copy the FOs (and therefore the KSO).
                for i in range(p.nfod[s], p.nks):
                    flo[s, :, i] = p.fo[s, :, i].copy()
    else:
        p.log.write('You should not use restricted input (spin=1) in an unrestricted routine (in uflo.py)!')
        # Add abort statement ?

    if p.verbose >= 4:
        p.log.write('FO have been transformed into FLO.')
    return flo


def make_rdm1(mo_coeff, mo_occ, p):
    """
        Make reduced density matrix
        ---------------------------
        Taken and adjusted from the PySCF UKS class.

        Input
        -----
        mo_coeff : mf.mo_coeff (PySCF)
        mo_occ   : mf.mo_occ (PySCF)
        p        : Parameters()

        Output
        ------
        dm      : density matrix (dm)
    """
    # spin_work = numpy.shape(mo_coeff)
    # Unrestricted calculation
    if p.nspin == 2:
        if p.verbose >= 4:
            p.log.write('make_rdm1: unrestricted, nspin = {}'.format(p.nspin))
        mo_a = mo_coeff[0]
        mo_b = mo_coeff[1]
        dm_a = numpy.dot(mo_a * mo_occ[0], mo_a.T.conj())
        dm_b = numpy.dot(mo_b * mo_occ[1], mo_b.T.conj())
        dm = numpy.array((dm_a, dm_b))
    else:
        p.log.write('You should not use restricted input (spin=1) in an unrestricted routine (in uflo.py)!')
        # Add abort statement ?
    return dm


def get_ESIC(mf, p):
    """
        Get ESIC
        --------
        Calculate the self-interaction correction energy (ESIC)

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        esic_flo : ESIC
        etot_sic_flo : total energy including ESIC
        onedm: one body density matricies
        vsics: SIC potentials

    """
    # Calculate SIC. Therefore, variables summing the SIC contribution
    # of the orbitals are initialized.
    exc_sic_flo = 0.0
    ecoul_sic_flo = 0.0
    nelec_sic_flo = 0.0
    # Get the KS total energy. This is needed to calculate e_sic as difference between
    # e_tot(flosic) - e_tot(dft)
    etot_ks = mf.e_tot
    # Unrestricted calculation
    if p.nspin == 2:
        # The variables vsics and onedm save the contributions of the orbitals themselves.
        vsics = numpy.zeros((p.nspin, numpy.max(p.nfod), p.nks, p.nks), dtype=p.datatype)
        onedm = numpy.zeros((p.nspin, numpy.max(p.nfod), p.nks, p.nks), dtype=p.datatype)
        for s in range(0, p.nspin):
            # Get the SIC for every orbital.
            for j in range(0, p.nfod[s]):
                # Build the occupancy array in order to get one electron densities.
                occup_work = numpy.zeros_like(p.occup)
                for i in range(0, p.nks):
                    if i == j:
                        occup_work[s][i] = 1.
                # Build the one electron densities.
                dm_work_flo = make_rdm1(p.flo, occup_work, p)
                onedm[s, j] = dm_work_flo[s]
                # Diagnostic output, if needed. This checks the one electron matrices.
                if p.verbose >= 5:
                    p.log.write('One-FOD-Density-Matrix')
                    p.log.write(str(dm_work_flo))
                # Get the SIC potential and energy for FLO.
                veff_work_flo = mf.get_veff(mol=mf.mol, dm=dm_work_flo)
                ecoul_work_flo = veff_work_flo.__dict__['ecoul']
                exc_work_flo = veff_work_flo.__dict__['exc']
                # Save the SIC potential.
                vsics[s, j] = veff_work_flo[s]
                # Increment the SIC energy.
                exc_sic_flo = exc_sic_flo + exc_work_flo
                ecoul_sic_flo = ecoul_sic_flo + ecoul_work_flo
                # Check number of electrons.
                if p.verbose >= 4:
                    nelec_work_flo, dumm1, dumm2 = dft.numint.nr_vxc(mf.mol, mf.grids, mf.xc, dm_work_flo, spin=1)
                    nelec_sic_flo = nelec_sic_flo + nelec_work_flo
                    p.log.write('Nelec : {}'.format(nelec_sic_flo))
        dm_flo = make_rdm1(p.flo, p.occup, p)
        if p.verbose >= 5:
            p.log.write('Complete-FOD-Density-Matrix')
            p.log.write(str(dm_flo))
        # Now that we got all the contributions, build the SIC energy.
        esic_flo = ecoul_sic_flo + exc_sic_flo
        etot_sic_flo = etot_ks - esic_flo
        if p.verbose >= 4:
            p.log.write('ESIC   {}'.format(esic_flo))
            p.log.write('E_coul {}'.format(ecoul_sic_flo))
            p.log.write('E_XC   {}'.format(exc_sic_flo))
            p.log.write('Etot   {}'.format(etot_sic_flo))
    else:
        p.log.write('You should not use restricted input (spin=1) in an unrestricted routine (in uflo.py)!')
        # Add abort statement ?
    return esic_flo, etot_sic_flo, onedm, vsics


def get_HSIC(mf, p):
    """
        Get HSIC
        -------
        Get the SIC Hamiltonian.

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        hsic : SIC Hamiltonian
        eval_flo : Eigenvalues FLOs
        lambda_ij: input for the FOD forces
    """
    # Next step is the energy eigenvalue correction / SIC Hamiltonian.
    # Unrestricted calculation
    if p.nspin == 2:
        # First, initialize all variables.
        h_sic = numpy.zeros((p.nspin, p.nks, p.nks), dtype=p.datatype)
        h_sic_virtual = numpy.zeros((p.nspin, p.nks, p.nks), dtype=p.datatype)
        h_ks = numpy.zeros((p.nspin, p.nks, p.nks), dtype=p.datatype)
        v_virtual = numpy.zeros((p.nspin, p.nks, p.nks), dtype=p.datatype)
        sumpfs = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        lambda_ij = numpy.zeros((p.nspin, numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
        # Bra and Ket are useful for doing scalar products using matrix multiplication.
        ket = numpy.zeros((p.nks, 1), dtype=p.datatype)
        bra = numpy.zeros((1, p.nks), dtype=p.datatype)
        # DFT values
        dm_ks = mf.make_rdm1()
        h1e = mf.get_hcore(mf.mol)
        vhf = mf.get_veff(mf.mol, dm_ks)
        hamil = mf.get_fock(h1e, p.s1e, vhf, dm_ks)
        # v_virtual is the projector of the virtual subspace, that might be needed
        # depending on which unified hamiltonian approximation is used.
        for s in range(0, p.nspin):
            if p.nfod[s] != 0:
                for i in range(p.nfod[s], p.nks):
                    bra[0, :] = numpy.transpose(p.flo[s, :, i])
                    ket[:, 0] = (p.flo[s, :, i])
                    v_virtual[s] = v_virtual[s] + numpy.dot(ket, bra)
        # Get the KS eigenvalues for comparison.
        eval_ks, trash = mf.eig(hamil, p.s1e)
        # Calculate the Cholesky decomposition of the atomic overlap and apply it to the
        # FLO. With this, things like the overlap matrix can be calculated more easily.
        sflo = numpy.zeros((p.nspin, p.nks, p.nks), dtype=p.datatype)
        sroot = numpy.linalg.cholesky(p.s1e)
        for s in range(p.nspin):
            sflo[s] = numpy.dot(numpy.transpose(sroot), p.flo[s, :, :])
        # Get epsilon^k_kl, here named lambda to avoid confusion. (This is needed for the
        # forces.)
        for s in range(p.nspin):
            for j in range(p.nfod[s]):
                for i in range(p.nfod[s]):
                    bra[0, :] = numpy.transpose(p.flo[s, :, i])
                    ket[:, 0] = (p.flo[s, :, j])
                    right = numpy.dot(p.vsics[s, j], ket)
                    lambda_ij[s, i, j] = -numpy.dot(bra, right)
                    if p.verbose >= 5:
                        p.log.write('lambda_ij')
                        p.log.write(str(lambda_ij[s, i, j]))
        # Do the energy eigenvalue correction and the SIC Hamiltonian.
        for s in range(p.nspin):
            sumpfs[:, :] = 0.0
            if p.nfod[s] != 0:
                for i in range(0, p.nfod[s]):
                    # HOO
                    ps = numpy.dot(p.onedm[s, i], p.s1e)
                    pf = numpy.dot(p.onedm[s, i], p.vsics[s, i])
                    fps = numpy.dot(p.vsics[s, i], ps)
                    spf = numpy.dot(p.s1e, pf)
                    h_sic[s] = h_sic[s] + fps + spf
                    # HOOOV
                    pfp = numpy.dot(pf, p.onedm[s, i])
                    fp = numpy.dot(p.vsics[s, i], p.onedm[s, i])
                    vfp = numpy.dot(v_virtual[s], fp)
                    pfv = numpy.dot(pf, v_virtual[s])
                    sumpf = pfp + vfp + pfv
                    sumpfs = numpy.dot(sumpf, p.s1e) + sumpfs
                    # Get the SIC Hamiltonian.
                    h_sic[s] = -0.5 * h_sic[s]
                    h_sic_virtual[s] = -numpy.dot(p.s1e, sumpfs)
                    h_ks[s] = eval_ks[s] * numpy.eye(p.nks, p.nks)
        # Get the SIC eigenvalues.
        if p.ham_sic == 'HOO':
            eval_flo, trash = mf.eig(hamil + h_sic, p.s1e)
            hsic = h_sic
            if p.verbose >= 5:
                p.log.write('HOO: {}'.format(eval_flo))
        if p.ham_sic == 'HOOOV':
            eval_flo, trash = mf.eig(hamil + h_sic_virtual, p.s1e)
            hsic = h_sic_virtual
            if p.verbose >= 5:
                p.log.write('HOOOV: {}'.format(eval_flo))
    else:
        p.log.write('You should not use restricted input (spin=1) in an unrestricted routine (in uflo.py)!')
        # Add abort statement ?
    return hsic, eval_flo, lambda_ij


def get_FOD_FORCES(mf, p):
    """
        Get FOD forces
        --------------
        Calculate the FOD forces.
        Note: This is the orginal LF implementation.

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        fforce_output : FOD forces
    """
    # Unrestricted calculation
    if p.nspin == 2:
        # Initialize the forces.
        fforce = numpy.zeros((p.nspin, numpy.max(p.nfod), 3), dtype=p.datatype)
        fforce_output = numpy.zeros((p.nfod[0] + p.nfod[1], 3), dtype=p.datatype)
        # gradpsi_ai holds the nabla KS value at the FOD position. Dimensions:
        # (nspin x FOD index (i) x KS index (alpha) x 3.
        gradpsi_ai = numpy.zeros((p.nspin, numpy.max(p.nfod), numpy.max(p.nksocc), 3), dtype=p.datatype)
        # den_ai holds the density at the FOD positions, grad_ai holds nabla rho at the FOD positions.
        den_ai = numpy.zeros((p.nspin, numpy.max(p.nfod)), dtype=p.datatype)
        grad_ai = numpy.zeros((p.nspin, numpy.max(p.nfod), 3), dtype=p.datatype)
        # gradfo holds the gradients of the fermi orbitals. The dimensions are:
        # (spin x coefficients x FOD Index x components (x,y,z)
        gradfo = numpy.zeros((p.nspin, p.nks, numpy.max(p.nfod), 3), dtype=p.datatype)
        # The sum over the gradients of KSO at the positions a_i. The dimensions are:
        # (spin x coefficients x FOD Index (i) x components (x,y,z))
        # sumgradpsi = numpy.zeros((p.nspin, p.nks, numpy.max(p.nfod), 3), dtype=p.datatype)
        # gradovrlp holds the derivative of the overlap matrix. The dimension are:
        # (spin x nfod (i) x nfod (j) x components (x,y,z)).
        # However, only for i=j it is unequal to zero. it might be reasonable to cut this
        # structure down later, in order to save computational space.
        gradovrlp = numpy.zeros((p.nspin, numpy.max(p.nfod), numpy.max(p.nfod), 3), dtype=p.datatype)
        # Delta1 and Delta3 as defined in the papers concering FOD forces.
        # They have the dimension:
        # (spin x nfod (l) x nfod (k) x nfod(m) x components (x,y,z)).
        # Delta1 = numpy.zeros((p.nspin, numpy.max(p.nfod), numpy.max(p.nfod), numpy.max(p.nfod), 3), dtype=p.datatype)
        # Delta3 = numpy.zeros((p.nspin, numpy.max(p.nfod), numpy.max(p.nfod), numpy.max(p.nfod), 3), dtype=p.datatype)
        # eps holds the matrix elements lambda_ij. It has the dimensions:
        # (spin x nfod (l) x nfod(k))
        eps = numpy.zeros((p.nspin, numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
        # Fermi orbital overlap matrix.
        s_i_j = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
        # Cholesky decomposition of the atomic overlap matrix.
        sroot = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
        # Cholesky decomposition for the atomic overlap matrix.
        sroot = numpy.linalg.cholesky(p.s1e)
        for s in range(p.nspin):
            # Assign epsilon.
            eps[s, 0:p.nfod[s], 0:p.nfod[s]] = p.lambda_ij[s, 0:p.nfod[s], 0:p.nfod[s]]
        # Get the value of the gradients of the KSO at the FOD positions.
        ao1 = mf.mol.eval_gto('GTOval_ip_sph', p.fod1.positions / units.Bohr, comp=3)
        gradpsi_ai_1 = [x.dot(mf.mo_coeff) for x in ao1]
        ao2 = mf.mol.eval_gto('GTOval_ip_sph', p.fod2.positions / units.Bohr, comp=3)
        gradpsi_ai_2 = [x.dot(mf.mo_coeff) for x in ao2]
        # Rearrange the data to make it more usable.
        x_1 = gradpsi_ai_1[0]
        y_1 = gradpsi_ai_1[1]
        z_1 = gradpsi_ai_1[2]
        x_2 = gradpsi_ai_2[0]
        y_2 = gradpsi_ai_2[1]
        z_2 = gradpsi_ai_2[2]
        # Iterate over the spin.
        for j in range(0, p.nspin):
            l = 0
            # Iterate over the Kohn sham wf.
            for i in range(0, p.nks):
                if p.occup[j][i] != 0.0:
                    # Iterate over the fods.
                    for k in range(0, p.nfod[j]):
                        if j == 0:
                            gradpsi_ai[j, k, l, 0] = x_1[k][j][i]
                            gradpsi_ai[j, k, l, 1] = y_1[k][j][i]
                            gradpsi_ai[j, k, l, 2] = z_1[k][j][i]
                        if j == 1:
                            gradpsi_ai[j, k, l, 0] = x_2[k][j][i]
                            gradpsi_ai[j, k, l, 1] = y_2[k][j][i]
                            gradpsi_ai[j, k, l, 2] = z_2[k][j][i]
                    l = l + 1
                if l > p.nksocc[j]:
                    p.log.write('WARNING: Attempting to use not occupied KS wf for FLOSIC.')
        # Calculate the density and the gradient of the density from the KS wavefunctions.
        for s in range(p.nspin):
            for m in range(0, p.nfod[s]):
                den_ai[s, m] = numpy.sum((p.PSI_ai[s, m, :])**2)
        for s in range(p.nspin):
            for r in range(0, 3):
                for m in range(0, p.nfod[s]):
                    for a in range(0, p.nfod[s]):
                        grad_ai[s, m, r] = grad_ai[s, m, r] + 2. * p.PSI_ai[s, m, a] * gradpsi_ai[s, m, a, r]
        # sfo and sks hold the FO and KSO after the decomposed atomic overlap has been
        # included.
        sks = numpy.zeros((p.nspin, p.nks, p.nks), dtype=p.datatype)
        sfo = numpy.zeros((p.nspin, p.nks, p.nks), dtype=p.datatype)
        # Get the gradients of the Fermi orbitals. (NOTE: NOT THE FERMI LOWDIN ORBITALS!)
        # This is dF in the usual notation.
        for s in range(p.nspin):
            # Fill sks and sfo.
            sks[s, :, :] = numpy.dot(numpy.transpose(sroot), mf.mo_coeff[s, :, :])
            sfo[s, :, :] = numpy.dot(numpy.transpose(sroot), p.fo[s, :, :])
            # bra and ket for scalar products.
            # ket = numpy.zeros((p.nfod[s], 1), dtype=p.datatype)
            # bra = numpy.zeros((1, p.nfod[s]), dtype=p.datatype)
            # Get dF.
            for r in range(0, 3):
                for i in range(0, p.nfod[s]):
                    sum1 = numpy.zeros((p.nks), dtype=p.datatype)
                    for a in range(0, p.nfod[s]):
                        sum1 = gradpsi_ai[s, i, a, r] * sks[s, :, a] + sum1
                    gradfo[s, :, i, r] = sum1[:] / numpy.sqrt(den_ai[s, i]) - \
                        (sfo[s, :, i] * grad_ai[s, i, r]) / (2. * den_ai[s, i])
        # Calculate the forces.
        # Now the actual calculation. It is done as a loop over the spin.
        # This implementation follows the one used in NRLMOL.
        for s in range(p.nspin):
            if p.nfod[s] != 0:
                # Get the overlap matrix. Both for the NRLMOL input and the self calculated
                # input.
                s_i_j = numpy.zeros((p.nfod[s], p.nfod[s]), dtype=p.datatype)
                s_i_j[0:p.nfod[s], 0:p.nfod[s]] = numpy.dot(
                    numpy.transpose(sfo[s, :, 0:p.nfod[s]]), sfo[s, :, 0:p.nfod[s]])
                # Get the eigenvectors as done by NRLMOL.
                Q_alpha_tmp, T_alpha_tmp = scipy.linalg.eigh((s_i_j[0:p.nfod[s], 0:p.nfod[s]]))
                T_alpha = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
                Q_alpha = numpy.zeros((numpy.max(p.nfod)), dtype=p.datatype)
                # Resort the matrices according to NRLMOL formalism.
                for i in range(0, p.nfod[s]):
                    for j in range(0, p.nfod[s]):
                        T_alpha[j, p.nfod[s] - 1 - i] = T_alpha_tmp[j, i]
                        Q_alpha[p.nfod[s] - 1 - i] = Q_alpha_tmp[i]
                T_alpha = numpy.transpose(T_alpha)
                # Temporary variables.
                TdST = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod), numpy.max(p.nfod), 3), dtype=p.datatype)
                V_tmp = numpy.zeros((numpy.max(p.nfod)), dtype=p.datatype)
                M_tmp = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
                D1_km = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod), numpy.max(p.nfod), 3), dtype=p.datatype)
                D1_kmd = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod), numpy.max(p.nfod), 3), dtype=p.datatype)
                D3_km = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod), numpy.max(p.nfod), 3), dtype=p.datatype)
                D3_kmd = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod), numpy.max(p.nfod), 3), dtype=p.datatype)
                # Get dS.
                for r in range(0, 3):
                    for n in range(p.nfod[s]):
                        for m in range(p.nfod[s]):
                            gradovrlp[s, n, m, r] = numpy.dot(numpy.transpose(sfo[s, :, n]), gradfo[s, :, m, r])
                    # Get Matrix elements <T_j|dSdAm|T_k>.
                    for m in range(p.nfod[s]):
                        for a in range(p.nfod[s]):
                            for b in range(p.nfod[s]):
                                for i in range(p.nfod[s]):
                                    TdST[b, a, m, r] = TdST[b, a, m, r] + gradovrlp[s, i, m, r] * \
                                        (T_alpha[b, i] * T_alpha[a, m] + T_alpha[b, m] * T_alpha[a, i])
                    # Get <phi|D1,km>
                    V_tmp[0:p.nfod[s]] = 1. / numpy.sqrt(Q_alpha[0:p.nfod[s]])
                    M_tmp = numpy.zeros((p.nfod[s], p.nfod[s]), dtype=p.datatype)
                    M_tmp2 = numpy.zeros((p.nfod[s], p.nfod[s]), dtype=p.datatype)
                    for m in range(p.nfod[s]):
                        for k in range(p.nfod[s]):
                            M_tmp[m, k] = numpy.sum(T_alpha[0:p.nfod[s], k] *
                                                    T_alpha[0:p.nfod[s], m] * V_tmp[0:p.nfod[s]])
                    M_tmp2 = numpy.dot(M_tmp[0:p.nfod[s], 0:p.nfod[s]], gradovrlp[s, 0:p.nfod[s], 0:p.nfod[s], r])
                    for m in range(0, p.nfod[s]):
                        for k in range(0, p.nfod[s]):
                            for l in range(0, p.nfod[s]):
                                D1_km[l, k, m, r] = D1_km[l, k, m, r] + M_tmp[m, k] * M_tmp2[l, m]
                    # Get D1_kmd (the lower case d meaning delta).
                    for m in range(p.nfod[s]):
                        D1_kmd[0:p.nfod[s], 0:p.nfod[s], m, r] = D1_km[0:p.nfod[s], 0:p.nfod[s], m, r] - \
                            numpy.transpose(D1_km[0:p.nfod[s], 0:p.nfod[s], m, r])
                    # Get the first part of the forces.
                    for m in range(p.nfod[s]):
                        for k in range(p.nfod[s]):
                            for l in range(p.nfod[s]):
                                fforce[s, m, r] = fforce[s, m, r] + D1_kmd[l, k, m, r] * eps[s, l, k]
                    # Get D3_km.
                    for m in range(p.nfod[s]):
                        for k in range(p.nfod[s]):
                            for l in range(p.nfod[s]):
                                for a in range(p.nfod[s]):
                                    for b in range(p.nfod[s]):
                                        tmp1 = T_alpha[b, k] * T_alpha[a, l] * numpy.sqrt(Q_alpha[a])
                                        tmp2 = T_alpha[a, k] * T_alpha[b, l] * numpy.sqrt(Q_alpha[b])
                                        tmp3 = (numpy.sqrt(Q_alpha[a]) + numpy.sqrt(Q_alpha[b])
                                                ) * numpy.sqrt(Q_alpha[a] * Q_alpha[b])
                                        D3_km[l, k, m, r] = D3_km[l, k, m, r] - 0.5 * \
                                            TdST[b, a, m, r] * ((tmp1 + tmp2) / tmp3)
                    # Get D3_kmd (the lower case d meaning delta).
                    for m in range(p.nfod[s]):
                        D3_kmd[0:p.nfod[s], 0:p.nfod[s], m, r] = D3_km[0:p.nfod[s], 0:p.nfod[s], m, r] - \
                            numpy.transpose(D3_km[0:p.nfod[s], 0:p.nfod[s], m, r])
                    # Get the second part of the forces.
                    for m in range(p.nfod[s]):
                        for k in range(p.nfod[s]):
                            for l in range(p.nfod[s]):
                                fforce[s, m, r] = fforce[s, m, r] + D3_kmd[l, k, m, r] * eps[s, l, k]
        # Output the forces.
        fforce_output[0:p.nfod[0], :] = fforce[0, 0:p.nfod[0], :]
        if p.nfod[1] != 0:
            fforce_output[p.nfod[0]:(p.nfod[1] + p.nfod[0]), :] = fforce[1, 0:p.nfod[1], :]
        # SS sign?
        fforce_output = -1 * fforce_output
    else:
        p.log.write('You should not use restricted input (spin=1) in an unrestricted routine (in uflo.py)!')
        # Add abort statement ?
    return fforce_output


def get_fmax(mf, p):
    """
        Get fmax
        --------
        Calculate maximum force criterion (fmax).

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        fmax : maximum force criterion (fmax)
    """
    ff = p.fforces
    fmax = numpy.sqrt((ff**2).sum(axis=1).max())
    if p.verbose >= 4:
        p.log.write('fmax = {} [Ha/Bohr]'.format(fmax))
    return fmax


class UFLO():
    """
        FLO class
        ---------
        Construct FLOs from given density matrix and molecular coefficients.
        Main function to be used is the kernel function. 
    """

    def __init__(self, mf, p):
        """
            Initialize class
            ----------------

            Input
            -----
            mf : mf(), PySCF object
                 - carries all PySCF natural variables
            p  : Parameters(), Parameters object/instance
                 - carries all PyFLOSIC variables
        """
        self.mf = mf
        self.p = p
        # Starting values
        # Get s1e
        self.p.s1e = mf.get_ovlp(mf.mol)
        # RorU[ndim]
        # determine if we run a restricted or unrestricted calculation
        RorU = {1: 'restricted', 2: 'unrestricted'}
        # Get nspin
        nspin = self.mf.mo_occ.ndim
        self.p.nspin = nspin
        self.p.nks = (numpy.array(self.mf.mo_coeff).shape)[1]
        # ks = numpy.array(mf.mo_coeff)
        # nks_work = numpy.shape(ks)
        # nks = nks_work[1]
        nfod1 = len(p.fod1.get_chemical_symbols())
        nfod2 = len(p.fod2.get_chemical_symbols())
        self.p.nfod = [nfod1, nfod2]
        # Get the occupation of the KSO.
        occup = numpy.array(mf.mo_occ).copy()
        self.p.occup = occup
        self.p.nksocc = get_nksocc(mf=self.mf, p=self.p)
        # Default values.
        self.e_tot = 0
        self.esic = 0
        if p.verbose >= 4:
            self.p.log.write(RorU[nspin])
            self.p.log.write('nks : {}'.format(self.p.nks))
            self.p.log.write('nfod : {}'.format(self.p.nfod))
            self.p.log.write('occup : {}'.format(self.p.occup))
            self.p.log.write('nksocc : {}'.format(self.p.nksocc))
        # May not good to have it here.
        # Because UFLO is used at various places.
        # self.p.show()

    def get_PSI_ai(self):
        """
            Construct: PSI_ai
            ----------------
        """
        self.p.PSI_ai = get_PSI_ai(self.mf, self.p)

    def get_R(self):
        """
            Construct: the rotation matrix R
            -------------------------------
        """
        self.p.R_ao = get_R(self.mf, self.p)

    def get_FO(self):
        """
            Construct: the FO (KS->FO)
            ------------------------
        """
        if self.p.verbose >= 4:
            self.p.log.write('get_FO: inside flo.py')
            self.p.log.write(str(self.p.R_ao))
        self.p.fo = get_FO(self.mf, self.p)

    def get_FLO(self):
        """
            Construct: the FLO (FO->FLO)
            --------------------------
        """
        self.p.flo = get_FLO(self.mf, self.p)

    def get_ESIC(self):
        """
            Calculate: ESIC
            ---------------
            Calculate ESIC, Etot, one-body DMs, and one-body potentials.
        """
        self.p.esic, self.p.e_tot, self.p.onedm, self.p.vsics = get_ESIC(self.mf, self.p)

    def get_HSIC(self):
        """
            Build: SIC Hamiltonian
            ----------------------
        """
        self.p.hsic, self.p.eval, self.p.lambda_ij = get_HSIC(self.mf, self.p)

    def kernel(self):
        """
            FLO kernel function
            -------------------
            Run FLO-SIC for a given density matrix (DM).
        """
        @tictoc(self.p)
        @functools.wraps(self.kernel)
        def wrapper(self):
            """
                Wrapper
                -------
                Needed to log the output from tictoc.
            """
            self.get_PSI_ai()
            self.PSI_ai = self.p.PSI_ai
            if self.p.verbose >= 5:
                self.p.log.write(str(self.p.PSI_ai))
            self.get_R()
            self.R = self.p.R_ao
            if self.p.verbose >= 5:
                self.p.log.write(str(self.p.R_ao))
            self.get_FO()
            self.fo = self.p.fo
            if self.p.verbose >= 5:
                self.p.log.write(str(self.p.fo))
            self.get_FLO()
            self.flo = self.p.flo
            if self.p.verbose >= 5:
                self.p.log.write(str(self.p.flo))
            self.get_ESIC()
            self.esic = self.p.esic
            self.e_tot = self.p.e_tot
            if self.p.verbose >= 5:
                self.p.log.write(str(self.p.esic))
                self.p.log.write(str(self.p.e_tot))
                self.p.log.write(str(self.p.vsics))
            self.get_HSIC()
            self.eval = self.p.eval
            self.hsic = self.p.hsic
            if self.p.verbose >= 5:
                self.p.log.write(str(self.p.hsic))
                self.p.log.write(str(self.p.eval))
            return self.e_tot
        return wrapper(self)

    def get_FOD_FORCES(self):
        """
            Get FOD forces
            --------------
        """
        self.p.fforces = get_FOD_FORCES(self.mf, self.p)
        if self.p.verbose >= 4:
            self.p.log.write(str(self.p.fforces))
        return self.p.fforces

    def get_fmax(self):
        """
            Get fmax for FOD forces
            -----------------------
        """
        fmax = get_fmax(mf=self.mf, p=self.p)
        return fmax

    def make_rdm1(self):
        """
            Make reduced density matrix
            ---------------------------
        """
        if self.flo.any() is None:
            self.kernel()
        # if self.p.occup.any() == None:
        self.mo_occ = self.p.occup
        dm = make_rdm1(self.flo, self.mo_occ, self.p)
        return dm


if __name__ == "__main__":
    from pyflosic2.test.knight_valley.uflo.test_uflo import test_uflo

    test_uflo()
