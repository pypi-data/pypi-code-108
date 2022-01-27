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
from pyscf import dft, lib
from pyscf.dft import numint
from pyflosic2.units import units
from pyflosic2.time.timeit import tictoc
import functools
# This is currently needed, as we evaluate the potential from the UKS routines, even in the restricted case.
# This come from the fact that doing it with the corresponding RKS routines lead to significant problems.
from pyscf.dft.uks import get_veff

""" Construction of Fermi-Loewdin orbitals (FLOs) mode=restricted"""

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
    # Restricted calculation
    if p.nspin == 1:
        for i in range(0, p.nks):
            if int(p.occup[i]) != int(0):
                # Only one spin-Index -> only nksocc[0]
                nksocc[0] += 1
    else:
        p.log.write('You should not use unrestricted input (spin=2) in a restricted routine (in rflo.py)!')
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
    # fod1 should be carried by p
    #
    # Restricted calculation
    if p.nspin == 1:
        # Working array initialization
        ao1 = numint.eval_ao(mf.mol, p.fod1.positions / units.Bohr)
        psi_ai_1 = ao1.dot(mf.mo_coeff)
        psi_ai_work = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nksocc)), dtype=p.datatype)
        #
        l = 0
        # Iterate over the occupied Kohn-Sham wf.
        for i in range(0, p.nks):
            if int(p.occup[i]) != int(0):
                # Iterate over the FODs.
                for k in range(0, p.nfod[0]):
                    # The dimension of psi_ai_work and psi_ai_1 are the same in the restricted case.
                    psi_ai_work[k, i] = psi_ai_1[k, i]
                l = l + 1
            if l > p.nksocc[0]:
                p.log.write('WARNING: Attempting to use unoccupied KS wf for FLOSIC.')
    else:
        p.log.write('You should not use unrestricted input (spin=2) in a restricted routine (in rflo.py)!')
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
    # Restricted calculation
    if p.nspin == 1:
        # Init the rotation matrix.
        R_ao = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        for i in range(0, p.nks):
            R_ao[i, i] = 1.0
        # Get SUMPsi_ai (density at every point).   point = fod
        SUMPsi_ai = numpy.zeros((numpy.max(p.nfod)), dtype=p.datatype)
        for m in range(0, p.nfod[0]):
            SUMPsi_ai[m] = numpy.sqrt(numpy.sum((p.PSI_ai[m, :])**2))
        # Build the rotation matrices.
        for m in range(0, p.nfod[0]):
            for i in range(0, p.nfod[0]):
                R_ao[m, i] = p.PSI_ai[m, i] / SUMPsi_ai[m]
    else:
        p.log.write('You should not use unrestricted input (spin=2) in a restricted routine (in rflo.py)!')
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
    # Restricted calculation
    if p.nspin == 1:
        fo = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        # Apply the rotation to the occupied orbitals.
        for i in range(0, p.nfod[0]):
            for j in range(0, p.nfod[0]):
                fo[:, i] = fo[:, i] + p.R_ao[i, j] * mf.mo_coeff[:, j]
        # Copy the unoccupied orbitals.
        for i in range(p.nfod[0], p.nks):
            fo[:, i] = mf.mo_coeff[:, i].copy()
    else:
        p.log.write('You should not use unrestricted input (spin=2) in a restricted routine (in rflo.py)!')
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
    # Restricted calculation
    if p.nspin == 1:
        flo = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        # sfo is needed in order to determine the overlap matrix.
        sfo = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        # Initialize everything for the Lowdin orthonormalization.
        T_lo = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
        Q_lo = numpy.zeros((numpy.max(p.nfod)), dtype=p.datatype)
        if p.nfod[0] != 0:
            # Initialize the overlap of the FOs.
            ovrlp_fo = numpy.zeros((p.nfod[0], p.nfod[0]), dtype=p.datatype)
            # Get the overlap.
            # The atomic overlap is directly included in sfo.
            sroot = numpy.linalg.cholesky(p.s1e)
            sfo[:, :] = numpy.dot(numpy.transpose(sroot), p.fo[:, :])
            ovrlp_fo[0:p.nfod[0], 0:p.nfod[0]] = numpy.dot(numpy.transpose(sfo[:, 0:p.nfod[0]]), sfo[:, 0:p.nfod[0]])
            # This is a Lowdin symmetric orthonormalization.
            q_fo, v_fo = scipy.linalg.eigh(ovrlp_fo)
            T_lo[0:p.nfod[0], 0:p.nfod[0]] = v_fo
            Q_lo[0:p.nfod[0]] = q_fo
            one_div_d = (1.0 / numpy.sqrt(q_fo)) * numpy.eye(p.nfod[0])
            vinv_fo = (numpy.transpose(v_fo))
            tra1 = numpy.dot(v_fo, one_div_d)
            trafo = numpy.dot(tra1, vinv_fo)
            for j in range(0, p.nfod[0]):
                for i in range(0, p.nfod[0]):
                    flo[:, j] = trafo[i, j] * p.fo[:, i] + flo[:, j]
            # For the unoccupied orbitals copy the FOs (and therefore the KSO).
            for i in range(p.nfod[0], p.nks):
                flo[:, i] = p.fo[:, i].copy()
    else:
        p.log.write('You should not use unrestricted input (spin=2) in a restricted routine (in rflo.py)!')
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
    # Restricted calculation
    if p.nspin == 1:
        if p.verbose >= 4:
            p.log.write('make_rdm1: restricted, nspin = {}'.format(p.nspin))
        mo_a = mo_coeff
        dm = numpy.dot(mo_a * mo_occ, mo_a.T.conj())
    else:
        p.log.write('You should not use unrestricted input (spin=2) in a restricted routine (in rflo.py)!')
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
    # Restricted calculation
    if p.nspin == 1:
        # The variables vsics and onedm save the contributions of the orbitals themselves.
        vsics = numpy.zeros((numpy.max(p.nfod), p.nks, p.nks), dtype=p.datatype)
        onedm = numpy.zeros((numpy.max(p.nfod), p.nks, p.nks), dtype=p.datatype)
        # Get the SIC for every orbital.
        for j in range(0, p.nfod[0]):
            # Build the occupancy array in order to get one electron densities.
            occup_work = numpy.zeros_like(p.occup)
            for i in range(0, p.nks):
                if i == j:
                    occup_work[i] = 2.
            # Build the one electron densities.
            dm_work_flo = make_rdm1(p.flo, occup_work, p)
            onedm[j] = dm_work_flo
            # Diagnostic output, if needed. This checks the one electron matrices.
            if p.verbose >= 5:
                p.log.write('One-FOD-Density-Matrix')
                p.log.write(str(dm_work_flo))
            # Currently: using UKS to evaluate effective potential, and thus Coulomb and EXC
            veff_work_flo = get_veff(mf, mol=p.mol, dm=numpy.array(
                [dm_work_flo / 2.0, dm_work_flo * 0.0]))  # Using UKS with density from RKS
            # Mutliply E_C and E_XC with 2, as it is currently evaluated for 1-electron density
            ecoul_work_flo = veff_work_flo.__dict__['ecoul'] * 2.0
            exc_work_flo = veff_work_flo.__dict__['exc'] * 2.0
            # Save the SIC potential.
            # take the one for the 'first' spin channel ONLY. This is in analogy to
            # what happens in the unrestricted case
            vsics[j] = veff_work_flo[0]
            # Increment the SIC energy.
            exc_sic_flo = exc_sic_flo + exc_work_flo
            ecoul_sic_flo = ecoul_sic_flo + ecoul_work_flo

            # Check number of electrons.
            if p.verbose >= 4:
                nelec_work_flo, dumm1, dumm2 = dft.numint.nr_vxc(mf.mol, mf.grids, mf.xc, dm_work_flo, spin=0)
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
        p.log.write('You should not use unrestricted input (spin=2) in a restricted routine (in rflo.py)!')
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
    # Restricted calculation
    if p.nspin == 1:
        # First, initialize all variables.
        h_sic = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        h_sic_virtual = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        # h_ks = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        v_virtual = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        sumpfs = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        lambda_ij = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
        # Bra and Ket are useful for doing scalar products using matrix multiplication.
        ket = numpy.zeros((p.nks, 1), dtype=p.datatype)
        bra = numpy.zeros((1, p.nks), dtype=p.datatype)
        # DFT values
        dm_ks = mf.make_rdm1()
        h1e = mf.get_hcore(mf.mol)
        # Using UKS routines to evaluate potential, E_C, E_XC
        vhf = get_veff(mf, mol=p.mol, dm=numpy.array([dm_ks / 2.0, dm_ks / 2.0]))
        ecoul_tmp = vhf.__dict__['ecoul'] * 2.0
        exc_tmp = vhf.__dict__['exc'] * 2.0
        vj_tmp = vhf.__dict__['vj']
        vk_tmp = None  # maybe None
        vhf = lib.tag_array((vhf[0] + vhf[1]) / 2.0, ecoul=ecoul_tmp, exc=exc_tmp, vj=vj_tmp, vk=vk_tmp)
        # vhf[0] and vhf[1] should be the same in the restricted case. So
        # (vhf[0]+vhf[1])/2.0 -> average, and use that inthe next steps
        hamil = mf.get_fock(h1e, p.s1e, vhf, dm_ks)
        # v_virtual is the projector of the virtual subspace, that might be needed
        # depending on which unified hamiltonian approximation is used.
        if p.nfod[0] != 0:
            for i in range(p.nfod[0], p.nks):
                bra[0, :] = numpy.transpose(p.flo[:, i])
                ket[:, 0] = (p.flo[:, i])
                v_virtual = v_virtual + numpy.dot(ket, bra)
        # Get the KS eigenvalues for comparison.
        eval_ks, trash = mf.eig(hamil, p.s1e)
        # Calculate the Cholesky decomposition of the atomic overlap and apply it to the
        # FLO. With this, things like the overlap matrix can be calculated more easily.
        # sflo = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        # sroot = numpy.linalg.cholesky(p.s1e)
        # sflo = numpy.dot(numpy.transpose(sroot), p.flo[:, :])
        # Get epsilon^k_kl, here named lambda to avoid confusion. (This is needed for the
        # forces.)
        for j in range(p.nfod[0]):
            for i in range(p.nfod[0]):
                bra[0, :] = numpy.transpose(p.flo[:, i])
                ket[:, 0] = (p.flo[:, j])
                right = numpy.dot(p.vsics[j], ket)
                lambda_ij[i, j] = -numpy.dot(bra, right)
                if p.verbose >= 5:
                    p.log.write('lambda_ij')
                    p.log.write(str(lambda_ij[i, j]))
        # Do the energy eigenvalue correction and the SIC Hamiltonian.
        sumpfs[:, :] = 0.0
        if p.nfod[0] != 0:
            for i in range(0, p.nfod[0]):
                # Using onedm[i] = onedm[i]/2.0 , in analogy to using UKS routines to evaluate potential
                # HOO
                ps = numpy.dot(p.onedm[i] / 2.0, p.s1e)
                pf = numpy.dot(p.onedm[i] / 2.0, p.vsics[i])
                fps = numpy.dot(p.vsics[i], ps)
                spf = numpy.dot(p.s1e, pf)
                h_sic = h_sic + fps + spf
                # HOOOV
                pfp = numpy.dot(pf, p.onedm[i] / 2.0)
                fp = numpy.dot(p.vsics[i], p.onedm[i] / 2.0)
                vfp = numpy.dot(v_virtual, fp)
                pfv = numpy.dot(pf, v_virtual)
                sumpf = pfp + vfp + pfv
                sumpfs = numpy.dot(sumpf, p.s1e) + sumpfs
                # Get the SIC Hamiltonian.
                h_sic = -0.5 * h_sic
                h_sic_virtual = -numpy.dot(p.s1e, sumpfs)
                # h_ks = eval_ks * numpy.eye(p.nks, p.nks)
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
        p.log.write('You should not use unrestricted input (spin=2) in a restricted routine (in rflo.py)!')
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
    # Restricted calculation
    if p.nspin == 1:
        # Initialize the forces.
        fforce = numpy.zeros((numpy.max(p.nfod), 3), dtype=p.datatype)
        fforce_output = numpy.zeros((p.nfod[0], 3), dtype=p.datatype)
        # gradpsi_ai holds the nabla KS value at the FOD position. Dimensions:
        # (FOD index (i) x KS index (alpha) x 3.
        gradpsi_ai = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nksocc), 3), dtype=p.datatype)
        # den_ai holds the density at the FOD positions, grad_ai holds nabla rho at the FOD positions.
        den_ai = numpy.zeros((numpy.max(p.nfod)), dtype=p.datatype)
        grad_ai = numpy.zeros((numpy.max(p.nfod), 3), dtype=p.datatype)
        # gradfo holds the gradients of the fermi orbitals. The dimensions are:
        # (coefficients x FOD Index x components (x,y,z)
        gradfo = numpy.zeros((p.nks, numpy.max(p.nfod), 3), dtype=p.datatype)
        # The sum over the gradients of KSO at the positions a_i. The dimensions are:
        # (coefficients x FOD Index (i) x components (x,y,z))
        # sumgradpsi = numpy.zeros((p.nks, numpy.max(p.nfod), 3), dtype=p.datatype)
        # gradovrlp holds the derivative of the overlap matrix. The dimension are:
        # (nfod (i) x nfod (j) x components (x,y,z)).
        # However, only for i=j it is unequal to zero. it might be reasonable to cut this
        # structure down later, in order to save computational space.
        gradovrlp = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod), 3), dtype=p.datatype)
        # Delta1 and Delta3 as defined in the papers concering FOD forces.
        # They have the dimension:
        # (nfod (l) x nfod (k) x nfod(m) x components (x,y,z)).
        # Delta1 = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod), numpy.max(p.nfod), 3), dtype=p.datatype)
        # Delta3 = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod), numpy.max(p.nfod), 3), dtype=p.datatype)
        # eps holds the matrix elements lambda_ij. It has the dimensions:
        # (nfod (l) x nfod(k))
        eps = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
        # Fermi orbital overlap matrix.
        s_i_j = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
        # Cholesky decomposition of the atomic overlap matrix.
        sroot = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
        # Cholesky decomposition for the atomic overlap matrix.
        sroot = numpy.linalg.cholesky(p.s1e)
        # Assign epsilon.
        eps[0:p.nfod[0], 0:p.nfod[0]] = p.lambda_ij[0:p.nfod[0], 0:p.nfod[0]]
        # Get the value of the gradients of the KSO at the FOD positions.
        ao1 = mf.mol.eval_gto('GTOval_ip_sph', p.fod1.positions / units.Bohr, comp=3)
        gradpsi_ai_1 = [x.dot(mf.mo_coeff) for x in ao1]
        # Rearrange the data to make it more usable.
        x_1 = gradpsi_ai_1[0]
        y_1 = gradpsi_ai_1[1]
        z_1 = gradpsi_ai_1[2]
        # No iteration over spin
        l = 0
        # Iterate over the Kohn sham wf.
        for i in range(0, p.nks):
            if p.occup[i] != 0.0:
                # Iterate over the fods.
                for k in range(0, p.nfod[0]):
                    gradpsi_ai[k, l, 0] = x_1[k][i]
                    gradpsi_ai[k, l, 1] = y_1[k][i]
                    gradpsi_ai[k, l, 2] = z_1[k][i]
                l = l + 1
            if l > p.nksocc[0]:
                p.log.write('WARNING: Attempting to use not occupied KS wf for FLOSIC.')
        # Calculate the density and the gradient of the density from the KS wavefunctions.
        for m in range(0, p.nfod[0]):
            den_ai[m] = numpy.sum((p.PSI_ai[m, :])**2)
        for r in range(0, 3):
            for m in range(0, p.nfod[0]):
                for a in range(0, p.nfod[0]):
                    grad_ai[m, r] = grad_ai[m, r] + 2. * p.PSI_ai[m, a] * gradpsi_ai[m, a, r]
        # sfo and sks hold the FO and KSO after the decomposed atomic overlap has been
        # included.
        sks = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        sfo = numpy.zeros((p.nks, p.nks), dtype=p.datatype)
        # Get the gradients of the Fermi orbitals. (NOTE: NOT THE FERMI LOWDIN ORBITALS!)
        # This is dF in the usual notation.
        # Fill sks and sfo.
        sks[:, :] = numpy.dot(numpy.transpose(sroot), mf.mo_coeff[:, :])
        sfo[:, :] = numpy.dot(numpy.transpose(sroot), p.fo[:, :])
        # bra and ket for scalar products.
        # ket = numpy.zeros((p.nfod[0], 1), dtype=p.datatype)
        # bra = numpy.zeros((1, p.nfod[0]), dtype=p.datatype)
        # Get dF.
        for r in range(0, 3):
            for i in range(0, p.nfod[0]):
                sum1 = numpy.zeros((p.nks), dtype=p.datatype)
                for a in range(0, p.nfod[0]):
                    sum1 = gradpsi_ai[i, a, r] * sks[:, a] + sum1
                gradfo[:, i, r] = sum1[:] / numpy.sqrt(den_ai[i]) - (sfo[:, i] * grad_ai[i, r]) / (2. * den_ai[i])
        # Calculate the forces.
        # Now the actual calculation. It is done as a loop over the spin.
        # This implementation follows the one used in NRLMOL.
        if p.nfod[0] != 0:
            # Get the overlap matrix. Both for the NRLMOL input and the self calculated
            # input.
            s_i_j = numpy.zeros((p.nfod[0], p.nfod[0]), dtype=p.datatype)
            s_i_j[0:p.nfod[0], 0:p.nfod[0]] = numpy.dot(numpy.transpose(sfo[:, 0:p.nfod[0]]), sfo[:, 0:p.nfod[0]])
            # Get the eigenvectors as done by NRLMOL.
            Q_alpha_tmp, T_alpha_tmp = scipy.linalg.eigh((s_i_j[0:p.nfod[0], 0:p.nfod[0]]))
            T_alpha = numpy.zeros((numpy.max(p.nfod), numpy.max(p.nfod)), dtype=p.datatype)
            Q_alpha = numpy.zeros((numpy.max(p.nfod)), dtype=p.datatype)
            # Resort the matrices according to NRLMOL formalism.
            for i in range(0, p.nfod[0]):
                for j in range(0, p.nfod[0]):
                    T_alpha[j, p.nfod[0] - 1 - i] = T_alpha_tmp[j, i]
                    Q_alpha[p.nfod[0] - 1 - i] = Q_alpha_tmp[i]
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
                for n in range(p.nfod[0]):
                    for m in range(p.nfod[0]):
                        gradovrlp[n, m, r] = numpy.dot(numpy.transpose(sfo[:, n]), gradfo[:, m, r])
                # Get Matrix elements <T_j|dSdAm|T_k>.
                for m in range(p.nfod[0]):
                    for a in range(p.nfod[0]):
                        for b in range(p.nfod[0]):
                            for i in range(p.nfod[0]):
                                TdST[b, a, m, r] = TdST[b, a, m, r] + gradovrlp[i, m, r] * \
                                    (T_alpha[b, i] * T_alpha[a, m] + T_alpha[b, m] * T_alpha[a, i])
                # Get <phi|D1,km>
                V_tmp[0:p.nfod[0]] = 1. / numpy.sqrt(Q_alpha[0:p.nfod[0]])
                M_tmp = numpy.zeros((p.nfod[0], p.nfod[0]), dtype=p.datatype)
                M_tmp2 = numpy.zeros((p.nfod[0], p.nfod[0]), dtype=p.datatype)
                for m in range(p.nfod[0]):
                    for k in range(p.nfod[0]):
                        M_tmp[m, k] = numpy.sum(T_alpha[0:p.nfod[0], k] * T_alpha[0:p.nfod[0], m] * V_tmp[0:p.nfod[0]])
                M_tmp2 = numpy.dot(M_tmp[0:p.nfod[0], 0:p.nfod[0]], gradovrlp[0:p.nfod[0], 0:p.nfod[0], r])
                for m in range(0, p.nfod[0]):
                    for k in range(0, p.nfod[0]):
                        for l in range(0, p.nfod[0]):
                            D1_km[l, k, m, r] = D1_km[l, k, m, r] + M_tmp[m, k] * M_tmp2[l, m]
                # Get D1_kmd (the lower case d meaning delta).
                for m in range(p.nfod[0]):
                    D1_kmd[0:p.nfod[0], 0:p.nfod[0], m, r] = D1_km[0:p.nfod[0], 0:p.nfod[0], m, r] - \
                        numpy.transpose(D1_km[0:p.nfod[0], 0:p.nfod[0], m, r])
                # Get the first part of the forces.
                for m in range(p.nfod[0]):
                    for k in range(p.nfod[0]):
                        for l in range(p.nfod[0]):
                            fforce[m, r] = fforce[m, r] + D1_kmd[l, k, m, r] * eps[l, k]
                # Get D3_km.
                for m in range(p.nfod[0]):
                    for k in range(p.nfod[0]):
                        for l in range(p.nfod[0]):
                            for a in range(p.nfod[0]):
                                for b in range(p.nfod[0]):
                                    tmp1 = T_alpha[b, k] * T_alpha[a, l] * numpy.sqrt(Q_alpha[a])
                                    tmp2 = T_alpha[a, k] * T_alpha[b, l] * numpy.sqrt(Q_alpha[b])
                                    tmp3 = (numpy.sqrt(Q_alpha[a]) + numpy.sqrt(Q_alpha[b])
                                            ) * numpy.sqrt(Q_alpha[a] * Q_alpha[b])
                                    D3_km[l, k, m, r] = D3_km[l, k, m, r] - 0.5 * \
                                        TdST[b, a, m, r] * ((tmp1 + tmp2) / tmp3)
                # Get D3_kmd (the lower case d meaning delta).
                for m in range(p.nfod[0]):
                    D3_kmd[0:p.nfod[0], 0:p.nfod[0], m, r] = D3_km[0:p.nfod[0], 0:p.nfod[0], m, r] - \
                        numpy.transpose(D3_km[0:p.nfod[0], 0:p.nfod[0], m, r])
                # Get the second part of the forces.
                for m in range(p.nfod[0]):
                    for k in range(p.nfod[0]):
                        for l in range(p.nfod[0]):
                            fforce[m, r] = fforce[m, r] + D3_kmd[l, k, m, r] * eps[l, k]
        # Output the forces.
        fforce_output[0:p.nfod[0], :] = fforce[0:p.nfod[0], :]
        # SS sign?
        fforce_output = -1 * fforce_output
    else:
        p.log.write('You should not use unrestricted input (spin=2) in a restricted routine (in rflo.py)!')
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


class RFLO():
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
        self.p.nfod = [nfod1]
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
    from pyflosic2.test.knight_valley.rflo.test_rflo import test_rflo

    test_rflo()
