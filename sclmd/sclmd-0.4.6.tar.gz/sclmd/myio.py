#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys

import numpy as np
from netCDF4 import Dataset

from sclmd.functions import mdot, nearest

'''
def cutlayers(infile, nalayer, nl, nr, outfile, ord=None):
    """
    cut down some layers for md simulation
    infile  input STRUCT.fdf file
    nalayer number of atoms per layer
    nl      nl layers from left
    nr      nr layers from left
    ord     atom lists in new order
    """
    print("reading ", infile)
    geom = MG.Geom(infile)
    xyz = geom.xyz
    snr = geom.snr
    anr = geom.anr
    pbc = geom.pbc

    if ord is not None:
        anr, xyz = reordxyz(anr, xyz, ord)

    zs = [a[2] for a in xyz]
    olen = max(zs)-min(zs)

    na = len(xyz)
    nal = nl*nalayer
    nar = nr*nalayer
    if(nal+nar >= na):
        print("Cuting too many atoms")
        sys.exit(0)

    nna = int(na-nal-nar)
    nxyz = [xyz[nal+i] for i in range(nna)]
    nsnr = [snr[nal+i] for i in range(nna)]
    nanr = [anr[nal+i] for i in range(nna)]

    nzs = [a[2] for a in nxyz]
    nlen = max(nzs)-min(nzs)

    pbc[2][2] = pbc[2][2]-(olen-nlen)

    geom.xyz = nxyz
    geom.pbc = pbc
    geom.snr = nsnr
    geom.anr = nanr
    geom.natoms = nna

    geom.writeFDF(outfile)
    geom.writeXYZ(os.path.splitext(outfile)[0]+".xyz")

    return geom
'''


def reordxyz(anr, xyz, ord):
    """
    anr list of atom numbers
    xyz old xyz
    ord atom list that needs to reord,siesta index
    """
    old = sorted(ord)
    nl = list(range(old[0]-1))+[i-1 for i in ord] + \
        list(range(old[-1], len(xyz)))
    if len(nl) != len(anr):
        print("reordxyz:length error")
        sys.exit()

    return [anr[i] for i in nl], [xyz[i] for i in nl]


def ReadEPHNCFile(filename):
    """
    Reads a NetCDF file that describes dynamical matrix, self-energies
    """
    class eph:
        pass

    file = Dataset(filename, 'r')
    print('Reading from %s' % filename)

    # General attributes
    eph.filename = filename
    eph.wl = np.array(file.variables['Wlist'])
    eph.hw = np.array(file.variables['hw'])
    eph.U = np.array(file.variables['U'])
    eph.DynMat = np.array(file.variables['DynMat'])
    eph.SigL = np.array(file.variables['ReSigL']) + \
        1j*np.array(file.variables['ImSigL'])
    eph.SigR = np.array(file.variables['ReSigR']) + \
        1j*np.array(file.variables['ImSigR'])
    eph.efric = np.array(file.variables['Friction'])
    eph.xim = np.array(file.variables['NC'])
    eph.xip = np.array(file.variables['NCP'])

    file.close()

    return eph


def ReadNewEPHNCFile(filename):
    """
    Reads a NetCDF file that describes dynamical matrix, self-energies
    """
    class eph:
        pass

    file = Dataset(filename, 'r')
    print('Reading from %s' % filename)

    # General attributes
    eph.filename = filename
    eph.wl = np.array(file.variables['Wlist'])
    eph.hw = np.array(file.variables['hw'])
    eph.U = np.array(file.variables['U'])
    eph.DynMat = np.array(file.variables['DynMat'])
    eph.SigL = np.array(file.variables['ReSigL']) + \
        1j*np.array(file.variables['ImSigL'])
    eph.SigR = np.array(file.variables['ReSigR']) + \
        1j*np.array(file.variables['ImSigR'])
    eph.efric = np.array(file.variables['Friction'])
    eph.xim = np.array(file.variables['NC'])
    eph.xip = np.array(file.variables['NCP'])
    eph.zeta1 = np.array(file.variables['zeta1'])
    eph.zeta2 = np.array(file.variables['zeta2'])
    file.close()
    return eph


def WriteEPHNCfile(filename, wl, hw, U, DynMat, SigL, SigR, Friction, NC, NCP, zeta1, zeta2):
    """
    Write a NetCDF file contains information for harmonic analysis
    """
    fn = Dataset(filename, 'w')
    print('Writing to %s' % filename)
    dhw = len(hw)
    dwl = len(wl)
    dsl = len(SigL[0])
    dsr = len(SigR[0])

    fn.createDimension('NPh', len(hw))
    fn.createDimension('NWl', len(wl))
    fn.createDimension('Nsl', len(SigL[0]))
    fn.createDimension('Nsr', len(SigR[0]))
    Write2NetCDFFile(fn, wl, 'Wlist', ('NWl',), units='eV')
    Write2NetCDFFile(fn, hw, 'hw', ('NPh',), units='eV')
    Write2NetCDFFile(fn, U, 'U', ('NPh', 'NPh',), units='None')
    Write2NetCDFFile(fn, DynMat, 'DynMat', ('NPh', 'NPh',), units='eV**2')
    Write2NetCDFFile(fn, SigL.real, 'ReSigL',
                     ('NWl', 'Nsl', 'Nsl',), units='eV**2')
    Write2NetCDFFile(fn, SigL.imag, 'ImSigL',
                     ('NWl', 'Nsl', 'Nsl',), units='eV**2')
    Write2NetCDFFile(fn, SigR.real, 'ReSigR',
                     ('NWl', 'Nsl', 'Nsl',), units='eV**2')
    Write2NetCDFFile(fn, SigR.imag, 'ImSigR',
                     ('NWl', 'Nsl', 'Nsl',), units='eV**2')
    Write2NetCDFFile(fn, Friction, 'Friction', ('NPh', 'NPh',), units='eV**2')
    Write2NetCDFFile(fn, NC, 'NC', ('NPh', 'NPh',), units='eV**2')
    Write2NetCDFFile(fn, NCP, 'NCP', ('NPh', 'NPh',), units='eV**2')
    Write2NetCDFFile(fn, zeta1, 'zeta1', ('NPh', 'NPh',), units='eV**2')
    Write2NetCDFFile(fn, zeta2, 'zeta2', ('NPh', 'NPh',), units='eV**2')
    print('Finished writing.')
    fn.close()


def Write2NetCDFFile(file, var, varLabel, dimensions, units=None, description=None):
    print('Write2NetCDFFile:', varLabel, dimensions)
    tmp = file.createVariable(varLabel, 'd', dimensions)
    tmp[:] = var
    if units:
        tmp.units = units
    if description:
        tmp.description = description


def ReadNetCDFVar(file, var):
    print("ReadNetCDFFile: reading " + var)
    f = Dataset(file, 'r')
    vv = np.array(f.variables[var])
    f.close()
    return vv


def ReadMDNCFile(filename):
    """
    Reads a NetCDF file 
    """
    class mdmath:
        pass

    file = Dataset(filename, 'r')
    print('Reading from %s' % filename)

    # General attributes
    mdmath.filename = filename
    mdmath.cell = np.array(file.variables['UnitCell'])
    mdmath.xyz = np.array(file.variables['XYZ'])
    mdmath.dynatom = np.array(file.variables['DynamicAtoms'])
    mdmath.atomlist = np.array(file.variables['AtomList'])

    file.close()

    return mdmath


def ReadDynmat(filename, order=None):
    """
    [20220121]Updated version, new version of Inelastica saves U in diff. way
    Reads the NetCDF file output from PHrun, Dev*.nc
    return the dynamical matrix in real space

    order:  new order of atoms in siesta index
    """
    file = Dataset(filename)
    print('Reading from %s' % filename)

    hw = np.array(file.variables['hw'][:])
    fullU = np.array(file.variables['U'][:])
    DynamicAtoms = np.array(file.variables['DynamicAtoms'][:])
    nlen = len(fullU)
    file.close()

    idF = DynamicAtoms[0]-1
    idL = DynamicAtoms[-1]

    U = np.zeros([nlen, nlen], np.float)
    for ii in range(len(fullU)):
        U[ii] = fullU[ii][idF:idL].flatten()

    # reorder
    if order is not None:
        n3 = 3*len(order)
        if n3 != len(hw):
            print("ReadDynmat: length of order error!")
            sys.exit()
        idx = ord2idx(order)
        nU = 0.0*U
        for i in range(len(idx)):
            nU[:, i] = U[:, idx[i]]
    else:
        nU = U

    dyn = mdot(nU.T, np.diag(hw**2), nU)
    dyn = 0.5*(dyn+dyn.T)
    return dyn, nU, hw


# -------------------------------------------------------------
# Old version
# -------------------------------------------------------------
# def ReadDynmat(filename, order=None):
#    """
#    Reads the NetCDF file output from PHrun, Dev*.nc
#    return the dynamical matrix in real space
#
#    order:  new order of atoms in siesta index
#    """
#    file = Dataset(filename, 'r')
#    print('Reading from %s' % filename)
#
#    hw = np.array(file.variables['hw'][:])
#    U = np.array(file.variables['U'][:])
#    file.close()
#
#    # reorder
#    if order is not None:
#        n3 = 3*len(order)
#        if n3 != len(hw):
#            print("ReadDynmat: length of order error!")
#            sys.exit()
#        idx = ord2idx(order)
#        nU = 0.0*U
#        for i in range(len(idx)):
#            nU[:, i] = U[:, idx[i]]
#    else:
#        nU = U
#
#    dyn = mdot(nU.T, np.diag(hw**2), nU)
#    dyn = 0.5*(dyn+dyn.T)
#    return dyn, nU, hw


def ord2idx(order):
    n3 = 3*len(order)
    idx = np.zeros(n3, np.int)
    for i in range(len(order)):
        for j in range(3):
            idx[3*i+j] = 3*(order[i]-1)+j
    return idx


def ReadSig(filename):
    """
    Reads a NetCDF file that describes dynamical matrix, self-energies
    """
    file = Dataset(filename, 'r')
    print('Reading from %s' % filename)

    class eph:
        pass
    # General attributes
    eph.wl = np.array(file.variables['Wlist'])
    eph.SigL = np.array(file.variables['ReSigL']) + \
        1j*np.array(file.variables['ImSigL'])
    eph.SigR = np.array(file.variables['ReSigR']) + \
        1j*np.array(file.variables['ImSigR'])

    return eph


def ReadwbLambda(filename, order=None):
    """
    Reads a NetCDF file that describes dynamical matrix, self-energies
    """
    file = Dataset(filename, 'r')
    print('Reading from %s' % filename)

    #mus = np.array(file.variables['muLR'])
    # Bias is always zero for wideband calculation.
    bias = 0.0
    # General attributes
    eta = np.array(file.variables['eta'])
    xim = np.array(file.variables['xim'])
    xip = np.array(file.variables['xip'])
    zeta1 = np.array(file.variables['zeta1'])
    zeta2 = np.array(file.variables['zeta2'])

    return bias, eta, xim, xip, zeta1, zeta2


def ReadLambda(filename, w0, order=None):
    """
    Reads a NetCDF file that describes dynamical matrix, self-energies
    """
    file = Dataset(filename, 'r')
    print('Reading from %s' % filename)

    # General attributes
    wl = np.array(file.variables['wl'])
    mus = np.array(file.variables['muLR'])
    bias = mus[0]-mus[1]
    print("applied bias in Lambda.nc:", bias)
    id = nearest(w0, wl)
    print("using energy point:", wl[id])

    w00 = wl[id]

    eta0 = np.array(file.variables['ImPir2'][id])
    eta = -(eta0+np.transpose(eta0))/2/w00
    zeta2 = -(eta0-np.transpose(eta0))/2/w00/bias
    xim0 = np.array(file.variables['RePir2'][id])
    xim = -(xim0-np.transpose(xim0))/2/bias
    zeta1 = (xim0+np.transpose(xim0))/2/bias

    xip = np.array(file.variables['ReLamLR'][id])
    xip = -np.pi*(xip+np.transpose(xip))/2/w00

    return bias, eta, xim, xip, zeta1, zeta2
