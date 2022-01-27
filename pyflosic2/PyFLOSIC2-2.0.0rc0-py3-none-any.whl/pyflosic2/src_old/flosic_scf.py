# -----PYFLOSIC SIC CLASS----
#
# -----Authors-----
# main:
#	Lenz Fiedler (LF) (fiedler.lenz@gmail.com)
# co:
#	Sebastian Schwalbe (SS)
#	Torsten Hahn (TH)
#	Jens Kortus (JK)


# -----Imports-----
# Please note that this class imports the main SIC routine from flosic.py.
#

import time
import numpy as np
from pyscf import lib
from pyscf.lib import logger
from pyscf.scf import uhf
from pyscf.dft import rks, uks, UKS
from pyscf.dft import rks, uks, UKS
from pyscf import dft
from pyscf import scf
from pyscf.dft.uks import get_veff, energy_elec
from pyscf.scf.uhf import get_fock
from pyflosic2.src_old.flosic_os import flosic, xyz_to_nuclei_fod, ase2pyscf, get_multiplicity, dynamic_rdm, print_flo
from pyscf.dft import numint as ni
from pyscf.grad import rks as rks_grad


# -----Notes-----
# FLO-SIC class by LF. This class allows for the self-consistent usage of the FLO-SIC
# formalism in PySCF. It therefore calls the FLO-SIC routine given in flosic.py and
# uses it to update the effective potential evaluated at every SCF step. The output of the
# FLO-SIC class is twofold: the total energy value (FLO-SIC corrected) is the direct return
# value of sic_object.kernel().
# Other values can be obtained by:
#		sic_object.flo -- Will hold the FLOs.
#		sic_object.fforces -- Will hold the FOD forces. (after the get_fforces routine has
# 								been called or if calc_forces == True.
#		sic_object.homo_flosic -- Will hold the FLO-SIC HOMO value.
#		sic_object.esic -- Will hold the total energy correction.


# -----Routines----


# This routine creates the new effective potential.
# It is: veff_dft + veff_sic

def get_flosic_veff(ks, mol=None, dm=None, dm_last=0, vhf_last=0, hermi=1):
    # pyscf standard call for scf cycle 0.
    veff = uks.get_veff(ks=ks.calc_uks, mol=ks.mol, dm=dm, dm_last=dm_last, vhf_last=vhf_last, hermi=hermi)

    # Build the hamiltonian to get the KS wave functions.
    dim = np.shape(ks.calc_uks.mo_coeff)
    s1e = ks.get_ovlp(mol)
    h1e = ks.get_hcore(mol)
    hamil = ks.get_fock(h1e, s1e, vhf_last, dm)

    # Get the KSO.
    ks_new = np.zeros((2, dim[1], dim[1]), dtype=np.float64)

    try:
        if dm_last == 0:
            # First SCF cycle: do nothing.
            pass
    except BaseException:
        # Every other DFT cycle: Build the KS wavefunctions with the Hamiltonian,
        # then give them to the UKS object that is the input for flosic.
        trash, ks_new = ks.eig(hamil, s1e)
        ks_inter = np.array(ks_new)

        # Update UKS object.
        ks.calc_uks.mo_coeff = ks_inter.copy()

    # If ldax is enabled, the xc functional is set to LDA exchange only.
    if ks.ldax:
        xc_sav = ks.calc_uks.xc
        ks.calc_uks.xc = 'LDA,'

    # Call the FLOSIC routine with the UKS object.

    # This for the fixed Vsic modus.

    # If Vsic values are present and the Vsic potential should not
    # be updated use these values.
    if ks.fixed_vsic != 0.0 and ks.num_iter % ks.vsic_every != 0:
        if ks.verbose >= 4:
            print('Use fixed Vsic (cycle = %i)' % ks.num_iter)
        flo_veff = flosic(
            ks.mol,
            ks.calc_uks,
            ks.fod1,
            ks.fod2,
            datatype=np.float64,
            calc_forces=ks.calc_forces,
            debug=ks.debug,
            nuclei=ks.nuclei,
            l_ij=ks.l_ij,
            ods=ks.ods,
            fixed_vsic=ks.fixed_vsic,
            ham_sic=ks.ham_sic)

    # If no Vsic values are present or the the Vsic values should be
    # updated calcualte new Vsic values.
    if ks.fixed_vsic == 0.0 or ks.num_iter % ks.vsic_every == 0:
        if ks.verbose >= 4:
            print('Calculate new Vsic (cycle = %i)' % ks.num_iter)
        flo_veff = flosic(
            ks.mol,
            ks.calc_uks,
            ks.fod1,
            ks.fod2,
            datatype=np.float64,
            calc_forces=ks.calc_forces,
            debug=ks.debug,
            nuclei=ks.nuclei,
            l_ij=ks.l_ij,
            ods=ks.ods,
            ham_sic=ks.ham_sic)
        ks.fixed_vsic = flo_veff['fixed_vsic']

    ks.num_iter = ks.num_iter + 1

    # If ldax is enabled, the change to xc is only meant for the FLO-SIC part and
    # therefore has to be changed back.
    if ks.ldax:
        ks.calc_uks.xc = xc_sav

    # Assign the return values.
    # The total energies of DFT and FLO-SIC
    sic_etot = flo_veff['etot_sic']
    dft_etot = flo_veff['etot_dft']
    # The FLOs.
    ks.flo = flo_veff['flo']
    # The FOD forces.
    ks.fforces = flo_veff['fforces']
    # The FLO-SIC HOMO energy eigenvalue.
    ks.homo_flosic = flo_veff['homo_sic']
    ks.evalues = flo_veff['evalues']
    ks.lambda_ij = flo_veff['lambda_ij']
    # Developer modus: atomic forces (AF)
    if ks.debug:
        ks.AF = flo_veff['AF']

    try:
        # First SCF cycle: veff = veff_dft and the SIC is zero.
        if dm_last == 0:
            sic_veff = veff
            sic_etot = dft_etot
    except BaseException:
        # Every other DFT cycle: Build veff as sum of the regular veff and the SIC
        # potential.
        sic_veff = veff + flo_veff['hamil']

        # Update the density matrix.
        dm_new = dynamic_rdm(ks.flo, ks.calc_uks.mo_occ)
        dm = dm_new.copy()
        ks.mo_coeff = ks.flo

    # Give back the FLO-SIC energy correction and the corrected potential. This libtagarray
    # formalism is defined by pyscf.
    sic_back = sic_etot - dft_etot
    veff_sic = lib.tag_array(sic_veff, ecoul=veff.ecoul, exc=veff.exc, vj=veff.vj, vk=veff.vk, esic=(sic_back))

    # Return the exchange-correlation energy and the FLO-SIC energy correction.
    ks.exc = veff.exc
    ks.esic = sic_back

    return veff_sic


# Every DFT calculation in pyscf calls the energy_elec function multiple times. It
# calculates the electronic energy that is then combined with the nuclei-electron
# interaction to the total energy.

def flosic_energy_elec(mf, dm=None, h1e=None, vhf=None):
    # Get the nuclei potential.
    h1e = mf.get_hcore()

    # This is the nuclei-electron interaction.
    e_nuc = np.einsum('ij,ji', h1e, dm[0]) + np.einsum('ij,ji', h1e, dm[1])

    try:
        # Every other DFT cycle: electronic energy calculated as sum of the contributions.
        e_correction = vhf.__dict__['ecoul'] + vhf.__dict__['exc'] + vhf.__dict__['esic']
        e_sic = (e_correction, vhf.__dict__['ecoul'])

        # This part looks odd, but it is correct.
        e = (e_sic[0] + e_nuc, e_sic[1])

    except BaseException:
        # First SCF cycle: regular DFT energy.
        e = energy_elec(mf, dm=dm, h1e=h1e, vhf=vhf)

    return e

# Every DFT calculation in PySCF calls the energy_tot function multiple times. It
# calculates the total energy and is basically an interface to the electronic energy. This
# function simply makes sure that the correct FLO are handed to flosic_energy_elec. All
# the actual work is done there.


def flosic_energy_tot(mf, dm=None, h1e=None, vhf=None):
    dm = dynamic_rdm(mf.flo, mf.calc_uks.mo_occ)
    e_tot = mf.energy_elec(dm, h1e, vhf)[0] + mf.energy_nuc()
    return e_tot.real

# This is the FLO-SIC class that allows for self-consistent FLO-SIC calculations. It
# inherits a lot of functionalities from UHF/RKS/UKS classes.


class FLOSIC(uhf.UHF):
    '''FLOSIC
    See pyscf/dft/rks.py RKS class for the usage of the attributes
    Rewritten UKS class. '''  # This part is directly taken from the RKS class.

    def __init__(self, mol, xc, fod1, fod2, ldax=False, grid_level=3, calc_forces=False, debug=False,
                 nuclei=None, l_ij=None, ods=None, fixed_vsic=None, num_iter=0, ham_sic='HOO', vsic_every=1):
        uhf.UHF.__init__(self, mol)
        rks._dft_common_init_(self)

        # Give the input variables to the SIC object.
        self.mol = mol  # Molecular geometry.
        self.xc = xc  # Exchange-correlation functional
        self.fod1 = fod1  # FOD geometry for first spin channel.
        self.fod2 = fod2  # FOD geometry for second spin channel.
        self.nuclei = nuclei
        self.ldax = ldax  # If True, LDA exchange is used for FLO-SIC (debugging mainly).
        self.is_first = True  # Used to determine which SCF cycle we are in.
        self.grid_level = grid_level  # Grid level.
        self.grids.level = grid_level
        # Determines whether or not FOD forces are calculated in every step. Default: False.
        self.calc_forces = calc_forces
        self.debug = debug  # enable debugging output
        self.l_ij = l_ij  # Lagrangian multiplier output
        self.lambda_ij = []  # Lagrangian multiplier matrix
        self.ods = ods  # orbital density scalcing

        # creation of an internal UKS object for handling FLO-SIC calculations.
        mol.verbose = 0
        calc_uks = UKS(mol)
        calc_uks.xc = self.xc
        calc_uks.max_cycle = 1
        calc_uks.grids.level = grid_level
        calc_uks.kernel()
        self.calc_uks = calc_uks

        # Parameters to coordinate FLO-SIC output.
        dim = np.shape(self.calc_uks.mo_coeff)  # Dimensions of FLO-SIC.
        dim1 = np.shape(fod1)
        dim2 = np.shape(fod2)
        self.flo = np.zeros((2, dim[1], dim[1]), dtype=np.float64)  # Will hold the FLOs.
        self.fforces = np.zeros((dim1[0] + dim2[0], 3), dtype=np.float64)  # Will hold the FOD forces.
        if fixed_vsic is None:
            self.fixed_vsic = None
        if fixed_vsic is not None:
            self.fixed_vsic = fixed_vsic
        self.homo_flosic = 0.0  # Will hold the FLO-SIC HOMO value.
        self.esic = 0.0  # Will hold the total energy correction.
        self.exc = 0.0  # Will hold the FLO-SIC exchange-correlation energy.
        self.evalues = 0.0  # Will hold the FLO-SIC evalues.
        self.AF = 0.0
        self.num_iter = num_iter  # Number of iteration
        self.vsic_every = vsic_every  # Calculate the vsic after e.g 50 cycles
        self.ham_sic = ham_sic  # SIC hamiltonian
        # This is needed that the PySCF mother class get familiar with all new variables.
        self._keys = self._keys.union(['grid_level',
                                       'fod1',
                                       'homo_flosic',
                                       'exc',
                                       'evalues',
                                       'calc_uks',
                                       'esic',
                                       'flo',
                                       'fforces',
                                       'fod2',
                                       'ldax',
                                       'calc_forces',
                                       'is_first',
                                       'debug',
                                       'nuclei',
                                       'AF',
                                       'l_ij',
                                       'ods',
                                       'lambda_ij',
                                       'num_iter',
                                       'vsic_every',
                                       'fixed_vsic',
                                       'ham_sic'])

    # Flags that might be helpful for debugging.
    def dump_flags(self):
        uhf.UHF.dump_flags(self)
        logger.info(self, 'XC functionals = %s', self.xc)
        logger.info(self, 'small_rho_cutoff = %g', self.small_rho_cutoff)
        self.grids.dump_flags()

    # This routine can be called by a SIC object any time AFTER a SCF cycle has been
    # completed. It calculates and outputs the forces.
    def get_fforces(self):
        flo_veff = flosic(self.mol, self.calc_uks, self.fod1, self.fod2, datatype=np.float64, calc_forces=True)
        self.fforces = flo_veff['fforces']
        return flo_veff['fforces']

    # Set a new potential calculator.
    get_veff = get_flosic_veff
    vhf = get_flosic_veff

    # set a new energy calculator.
    energy_elec = flosic_energy_elec
    energy_tot = flosic_energy_tot
    define_xc_ = rks.define_xc_

# New class that allows for the spin to change during the FLO-SIC calculation.
# Based on the float_occ_ routine for UHF from PySCF. It is in principle a copy of
# float_occ_ with the correct treament of the FOD geometry added.


def sic_occ_(mf):
    # This part is directly taken from PySCF.
    from pyscf.scf import uhf
    assert(isinstance(mf, uhf.UHF))

    def get_occ(mo_energy, mo_coeff=None):
        # Spin configuration is only changed ONCE at the beginning. Elsewise, SCAN will behave very inconsistently.
        if mf.is_first:
            mol = mf.mol
            ee = np.sort(np.hstack(mo_energy))
            n_a = np.count_nonzero(mo_energy[0] < (ee[mol.nelectron - 1] + 1e-1))
            n_b = mol.nelectron - n_a
            if mf.nelec is None:
                nelec = mf.mol.nelec
            else:
                nelec = mf.nelec
            if n_a != nelec[0]:
                logger.info(mf, 'change num. alpha/beta electrons '
                                ' %d / %d -> %d / %d',
                                nelec[0], nelec[1], n_a, n_b)

            # If the spin configuration has changed, the FOD configuration needs to do as
            # well.
            # First, initialize needed parameters.
            dim = np.shape(mf.calc_uks.mo_coeff)
            occ = np.zeros((2, dim[1]), dtype=np.float64)
            dim1 = np.shape(mf.fod1)
            dim2 = np.shape(mf.fod2)

            # Calculate new and old spin polarization.
            difforig = dim1[0] - dim2[0]
            diffnew = n_a - n_b
            diff = diffnew - difforig

            # If something has changed, update the FODs.
            if dim1[0] != n_a and dim2[0] != n_b:
                print('Electronic configuration has been changed, changing FOD geometry.')

                # Update the FODs.
                if diff > 0:
                    counter = diff / 2
                    for i in range(0, int(counter)):
                        mf.fod1.append(mf.fod2[i])
                    del mf.fod2[0:int(counter)]

                if diff < 0:
                    counter = abs(diff) / 2
                    for i in range(0, int(counter)):
                        mf.fod2.append(mf.fod1[i])
                    del mf.fod1[0:int(counter)]

            # Update the occupation of the internal UKS object as well
            for i in range(0, n_a):
                occ[0, i] = 1.0
            for i in range(0, n_b):
                occ[1, i] = 1.0
            mf.calc_uks.mo_occ = occ.copy()

            # Taken from the UHF routine.
            mf.nelec = (n_a, n_b)

            # As discussed above, only for the FIRST SCF iteration the spin configuration is
            # variable.
            mf.is_first = False
        return uhf.UHF.get_occ(mf, mo_energy, mo_coeff)
    mf.get_occ = get_occ
    return mf


dynamic_sz_ = sic_occ = sic_occ_

# This routine is supposed to replace float_occ_ to enable a more direct manipulation of
# the parameters for the variable spin calculation. This is especially important for
# calculations with the SCAN functional; if this is not done correctly they might crash
# due to very small energy differences for different spin configurations. The routine is
# in principle a copy of float_occ_ restricting it to only vary the spin for the first SCF
# iteration.
# NOTE: To use this function, one has to add m2.is_first = True to the calculator before
# doing m2.kernel()


def dft_occ_(mf):
    # This part is directly taken from PySCF.
    from pyscf.scf import uhf
    assert(isinstance(mf, uhf.UHF))

    def get_occ(mo_energy, mo_coeff=None):
        # Spin configuration is only changed ONCE at the beginning. Elsewise, SCAN will behave very inconsistently.
        if mf.is_first:
            mol = mf.mol
            ee = np.sort(np.hstack(mo_energy))
            n_a = np.count_nonzero(mo_energy[0] < (ee[mol.nelectron - 1] + 1e-1))
            n_b = mol.nelectron - n_a
            if mf.nelec is None:
                nelec = mf.mol.nelec
            else:
                nelec = mf.nelec
            if n_a != nelec[0]:
                logger.info(mf, 'change num. alpha/beta electrons '
                                ' %d / %d -> %d / %d',
                                nelec[0], nelec[1], n_a, n_b)
            mf.nelec = (n_a, n_b)

            # As discussed above, only for the FIRST SCF iteration the spin configuration is
            # variable.
            mf.is_first = False

        return uhf.UHF.get_occ(mf, mo_energy, mo_coeff)
    mf.get_occ = get_occ
    return mf


dynamic_sz_ = dft_occ = dft_occ_


if __name__ == '__main__':
    # Test example for the FLOSIC class.
    # This simple example shows of all of the features of the SIC class.
    from ase.io import read
    import sys
    import numpy as np
    from pyscf import gto
    import os

    # Path to the xyz file
    f_xyz = os.path.dirname(os.path.realpath(__file__)) + '/../examples/basic_calculations/H2.xyz'

    # Read the input file.
    ase_atoms = read(f_xyz)

    # Split the input file.
    pyscf_atoms, nuclei, fod1, fod2, included = xyz_to_nuclei_fod(ase_atoms)

    # Get the spin and charge.
    charge = 0
    spin = 0

    # Uncomment the basis set you want to use.
    b = 'cc-pvqz'

    # The ghost option enables ghost atoms at the FOD positions. Mostly obsolete.

    # Build the mol object.
    mol = gto.M(atom=ase2pyscf(nuclei), basis={'default': b}, spin=spin, charge=charge)

    # Adjust verbosity as desired.
    mol.verbose = 4

    # Calculation parameters.
    max_cycle = 1200
    grid_level = 7
    conv_tol = 1e-7
    xc = 'LDA,PW'

    # Build the SIC calculator.
    m = FLOSIC(mol, xc=xc, fod1=fod1, fod2=fod2, grid_level=grid_level)
    m.max_cycle = max_cycle
    m.conv_tol = conv_tol

    # Do the calculation.
    e_calc = m.kernel()
    print('Pyflosic total energy: ', e_calc)
