#!/usr/bin/env python
# -*- coding: utf-8 -*

import numpy as np


class sig:
    # This class is used to create a selfenergy object.
    def __init__(self, infile, maxomega, atomgroup0, atomgroup1, dofatomfixed=[[], []], dynmatfile=None, num=1000, eta=0.164e-3):
        # Initializes the selfenergy object.
        # reduced Planck constant unit in: eV*ps
        self.rpc = 6.582119569e-4
        # Boltzmann constant unit in: eV/K
        # self.bc = 8.617333262e-5
        #self.infile = infile
        #self.damp = damp
        self.maxomega = maxomega/self.rpc
        self.intnum = num
        self.eta = eta/self.rpc
        self.dofatomK00 = atomgroup0
        self.dofatomK11 = atomgroup1
        self.dofatomfixed = dofatomfixed
        self.dynmatfile = dynmatfile
        self.ep = np.linspace(0, self.maxomega, self.intnum+1)
        self.getdynmat(infile)
        self.getdk()

    def getdynmat(self, infile):
        from lammps import lammps
        lmp = lammps()
        #lmp = lammps(cmdargs=['-screen', 'none', '-log', 'none'])
        lmp.commands_list(infile)
        self.natoms = lmp.get_natoms()
        box = lmp.extract_box()
        self.boxlo = np.array(box[0])
        self.boxhi = np.array(box[1])
        systype = np.array(lmp.gather_atoms("type", 0, 1))
        mass = lmp.extract_atom("mass", 2)
        self.els = []
        for type in systype:
            self.els.append([mass[type]]*3)
        self.els = np.array(self.els).flatten()
        self.xyz = lmp.gather_atoms("x", 1, 3)
        self.els = np.delete(self.els, self.dofatomfixed[0])
        self.els = np.delete(self.els, [
            dof-len(self.dofatomfixed[0]) for dof in self.dofatomfixed[1]])
        self.xyz = np.delete(self.xyz, self.dofatomfixed[0])
        self.xyz = np.delete(self.xyz, [
            dof-len(self.dofatomfixed[0]) for dof in self.dofatomfixed[1]])
        if self.dynmatfile is None:
            print('Calculate dynamical matrix')
            lmp.command('dynamical_matrix all eskm 0.000001 file dynmat.dat')
            dynmatdat = np.loadtxt('dynmat.dat')
        else:
            print('Load dynamical matrix from '+str(self.dynmatfile))
            dynmatdat = np.loadtxt(self.dynmatfile)
        lmp.close()
        self.dynmat = []
        self.omegas = []
        self.doffreeatom = 0
        dynlen = int(3*np.sqrt(len(dynmatdat)/3))
        if dynlen != self.natoms*3:
            raise ValueError(
                'System DOF test failed after load dynmat, check again')
        self.dynmat = dynmatdat.reshape((dynlen, dynlen))
        dynmatexcpfixed = np.delete(self.dynmat, self.dofatomfixed[0], axis=0)
        dynmatexcpfixed = np.delete(
            dynmatexcpfixed, self.dofatomfixed[0], axis=1)
        dynmatexcpfixed = np.delete(dynmatexcpfixed, [
            dof-len(self.dofatomfixed[0]) for dof in self.dofatomfixed[1]], axis=0)
        dynmatexcpfixed = np.delete(dynmatexcpfixed, [
            dof-len(self.dofatomfixed[0]) for dof in self.dofatomfixed[1]], axis=1)
        if len(self.xyz) != len(dynmatexcpfixed):
            raise ValueError(
                'System DOF test failed after atoms reduced, check again')
        print('Calculate angular frequency')
        eigvals, eigvecs = np.linalg.eigh(dynmatexcpfixed)
        ffi = []
        for i, val in enumerate(eigvals):
            if val > 0:
                self.omegas.append(np.sqrt(val)*self.rpc)
            else:
                ffi.append(i)
                # print('False frequency exists in system DOF %i ' %
                #      (i+len(self.dofatomfixed[0])))
                self.omegas.append(-np.sqrt(-val)*self.rpc)
        print('%i false frequencies exist in %i frequencies' %
              (len(ffi), len(self.omegas)))
        np.savetxt('falsefrequencies.dat', ffi, fmt='%d')
        np.savetxt('omegas.dat', self.omegas)
        np.savetxt('eigvecs.dat', eigvecs)

    def getdk(self):
        # Get dynamic matrix of given atoms
        self.K00 = self.dynmat[self.dofatomK00, :][:, self.dofatomK00]
        self.K11 = self.dynmat[self.dofatomK11, :][:, self.dofatomK11]
        self.K01 = self.dynmat[self.dofatomK00, :][:, self.dofatomK11]
        self.K10 = self.dynmat[self.dofatomK11, :][:, self.dofatomK00]
        if np.amax(abs(self.K01 - np.transpose(self.K10)))/np.amax(abs(self.K01)) > 1e-8:
            raise ValueError('Error: K01 and K10 are not symmetric',np.amax(abs(self.K01 - np.transpose(self.K10)))/np.amax(abs(self.K01)))
        else:
            self.K01 = (self.K01+np.transpose(self.K10))/2
            self.K10 = np.transpose(self.K01)

    def sgf(self, omega, direction):
        # Algorithm for surface Green’s function
        if direction == 'R':
            s = self.K00.astype(complex)
            e = self.K11.astype(complex)
            alpha = self.K01.astype(complex)
        elif direction == 'L':
            s = self.K11.astype(complex)
            e = self.K00.astype(complex)
            alpha = self.K10.astype(complex)
        else:
            raise ValueError('Wrong direction, should only be R or L')
        iter = 0
        while np.linalg.norm(alpha) > 1e-8:
            g = np.linalg.inv((omega+self.eta*1j)**2*np.identity(len(e))-e)
            beta = np.transpose(alpha)
            s += np.dot(np.dot(alpha, g), beta)
            e += np.dot(np.dot(alpha, g), beta) + \
                np.dot(np.dot(beta, g), alpha)
            alpha = np.dot(np.dot(alpha, g), alpha)
            iter += 1
            #print('Iteration %i' % iter, 'det(alpha)', np.linalg.norm(alpha))
            if iter >= 100:
                #print('Iteration number for surface Green’s function: %i' % iter)
                raise ValueError(
                    'Iteration number exceeded 100, please increase eta')
        return np.linalg.inv((omega+self.eta*1j)**2*np.identity(len(s))-s)

    def selfenergy(self, omega, direction):
        # self energy
        if direction == 'R':
            return np.dot(np.dot(self.K01, self.sgf(omega, direction)), self.K10)
        elif direction == 'L':
            return np.dot(np.dot(self.K10, self.sgf(omega, direction)), self.K01)
        else:
            raise ValueError('Wrong direction, should only be R or L')

    def gamma(self, Pi):
        return -1j*(Pi-Pi.conjugate().transpose())

    def retargf(self, omega):
        # retarded Green function
        return np.linalg.inv((omega+1e-8*1j)**2*np.identity(len(self.K00))-self.K00-self.selfenergy(omega, 'L')-self.selfenergy(omega, 'R'))

    def tm(self, omega):
        # Transmission
        return np.real(np.trace(np.dot(np.dot(np.dot(self.retargf(omega), self.gamma(self.selfenergy(omega, 'L'))), self.retargf(omega).conjugate().transpose()), self.gamma(self.selfenergy(omega, 'R')))))

    def getse(self, direction):
        # get a set of selfenergy of given omega
        from tqdm import tqdm
        dosx = []
        se = []
        print("Calculate selfenergy of "+str(direction)+" lead")
        for var in tqdm(self.ep, unit="steps", mininterval=1):
            selfenergysplit = self.selfenergy(var, direction)
            se.append(selfenergysplit)
            dosx.append(-np.trace(np.imag(selfenergysplit))*var/np.pi)
        self.dos = np.array(np.column_stack((self.ep, np.array(dosx))))
        np.savetxt('densityofstates_'+str(direction)+'.dat', np.column_stack(
            (self.dos[:, 0]*self.rpc, self.dos[:, 1])))
        return np.array(se)

    def gettm(self):
        # get a set of transmission of given omega
        from tqdm import tqdm
        tm = []
        print("Calculate transmission")
        for var in tqdm(self.ep, unit="steps", mininterval=1):
            tm.append(self.tm(var))
        self.tmnumber = np.array(np.column_stack((self.ep, np.array(tm))))
        np.savetxt('transmission.dat', np.column_stack(
            (self.tmnumber[:, 0]*self.rpc, self.tmnumber[:, 1])))
        # return np.array(se)

    def plotresult(self, lines=180):
        from matplotlib import pyplot as plt
        plt.figure(0)
        plt.hist(self.omegas, bins=lines)
        plt.xlabel('Frequence(eV)')
        plt.ylabel('Number')
        #plt.xlim(0, self.maxomega*self.rpc)
        plt.savefig('omegas.png')
        plt.figure(1)
        plt.plot(self.dos[:, 0]*self.rpc, self.dos[:, 1])
        plt.xlabel('Frequence(eV)')
        plt.ylabel('DOS')
        plt.gca().ticklabel_format(style='sci', scilimits=(-1, 2), axis='y')
        plt.savefig('densityofstates.png')
        plt.figure(2)
        plt.plot(self.tmnumber[:, 0]*self.rpc, self.tmnumber[:, 1])
        plt.xlabel('Frequence(eV)')
        plt.ylabel('Transmission')
        plt.savefig('transmission.png')


if __name__ == '__main__':
    import time

    #from sclmd.selfenergy import sig
    infile = [
        'atom_style full',
        'units  metal',
        #'boundary p p p',
        'read_data sig.data',
        'pair_style rebo',
        'pair_coeff *   *   CH.rebo C',
        #'min_style  cg',
        'minimize   1e-25   1e-25   5000    10000',
        'dump   1   all xyz 1   dump.xyz',
        'run    0',
    ]
    time_start = time.time()
    atomgroup0 = range(24*3, 32*3)
    atomgroup1 = range(32*3, 40*3)
    mode = sig(infile, 0.12, atomgroup0, atomgroup1,
               dofatomfixed=[[], []], dynmatfile=None, num=2000, eta=0.164e-3)
    mode.getse('L')
    mode.getse('R')
    mode.gettm()
    mode.plotresult()
    print('time cost', time.time()-time_start, 's')
