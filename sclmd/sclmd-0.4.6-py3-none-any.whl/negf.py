#!/usr/bin/env python
# -*- coding: utf-8 -*

import numpy as np
from lammps import lammps


class bpt:
    # Use NEGF to calculate ballistic phonon transport
    def __init__(self, infile, maxomega, damp, dofatomofbath, dofatomfixed=[[], []], dynmatfile=None, num=1000):
        print('Class init')
        # reduced Planck constant unit in: eV*ps
        self.rpc = 6.582119569e-4
        # Boltzmann constant unit in: eV/K
        self.bc = 8.617333262e-5
        self.damp = damp  # ps
        self.maxomega = maxomega/self.rpc
        self.intnum = num
        self.dofatomfixed = dofatomfixed
        self.isbias = False
        self.dofatomofbias = []
        self.dofatomofbath = dofatomofbath
        self.dynmatfile = dynmatfile
        self.getdynmat(infile)
        # self.gettm(vector)

    def setbias(self, bias, bdamp=None, chiplus=None, chiminus=None, dofatomofbias=[]):
        # units in eV & ps^-1
        np.seterr(divide='ignore', invalid='ignore')
        self.isbias = True
        self.bias = bias/self.rpc
        self.biasgamma = bdamp
        self.chiplus = chiplus
        self.chiminus = chiminus
        self.dofatomofbias = dofatomofbias
        if len(self.biasgamma) != len(self.chiminus) or len(self.biasgamma) != len(self.chiplus) or len(self.biasgamma) != len(self.dofatomofbias):
            raise ValueError('Bias parameters not set correctly')

    def getdynmat(self, infile):
        lmp = lammps()
        #lmp = lammps(cmdargs=['-screen', 'none', '-log', 'none'])
        print('LAMMPS init')
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
        self.dynmat = (self.dynmat+self.dynmat.transpose())/2
        self.dynmat = np.delete(self.dynmat, self.dofatomfixed[0], axis=0)
        self.dynmat = np.delete(self.dynmat, self.dofatomfixed[0], axis=1)
        self.dynmat = np.delete(self.dynmat, [
                                dof-len(self.dofatomfixed[0]) for dof in self.dofatomfixed[1]], axis=0)
        self.dynmat = np.delete(self.dynmat, [
                                dof-len(self.dofatomfixed[0]) for dof in self.dofatomfixed[1]], axis=1)
        if len(self.xyz) != len(self.dynmat):
            raise ValueError(
                'System DOF test failed after atoms reduced, check again')
        ffi = []
        print('Calculate angular frequency')
        eigvals, self.eigvecs = np.linalg.eigh(self.dynmat)
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
        np.savetxt('eigvecs.dat', self.eigvecs)

    def gettm(self, vector=False):
        print('Calculate transmission')
        x = np.linspace(0, self.maxomega, self.intnum+1)
        if vector:
            function = np.vectorize(self.tm)
            self.tmnumber = np.array(
                np.column_stack((x, np.array(function(x)))))
        else:
            from tqdm import tqdm
            tm = []
            for var in tqdm(x, unit="steps", mininterval=1):
                tm.append(self.tm(var))
            self.tmnumber = np.array(np.column_stack((x, np.array(tm))))
        np.savetxt('transmission.dat', np.column_stack(
            (self.tmnumber[:, 0]*self.rpc, self.tmnumber[:, 1])))
        print('Transmission saved')

    def getps(self, T, maxomega, intnum, atomlist=None, filename=None, vector=False):
        if filename is not None:
            print('Calculate power spectrum at '+str(T)+'K of '+str(filename))
        else:
            print('Calculate power spectrum at '+str(T)+'K')
        if atomlist is None:
            # print("Power spectrum of all atoms")
            atomlist = np.array(range(0, len(self.dynmat))
                                ) + len(self.dofatomfixed[0])
        x2 = np.linspace(0, maxomega/self.rpc, intnum+1)
        if vector:
            function = np.vectorize(self.ps)
            self.psnumber = np.array(
                np.column_stack((x2, np.array(function(x2, T, atomlist)))))
        else:
            from tqdm import tqdm
            ps = []
            for var in tqdm(x2, unit="steps", mininterval=1):
                ps.append(self.ps(var, T, atomlist))
            self.psnumber = np.array(np.column_stack((x2, np.array(ps))))
        if filename is not None:
            np.savetxt('powerspectrum.'+str(filename)+'.'+str(T)+'.dat',
                       np.column_stack((self.psnumber[:, 0]*self.rpc, self.psnumber[:, 1])))
        else:
            np.savetxt('powerspectrum.'+str(T)+'.dat',
                       np.column_stack((self.psnumber[:, 0]*self.rpc, self.psnumber[:, 1])))
        print('Power spectrum saved')

    def retarselfenergy(self, omega, dofatoms):
        semat = np.zeros((self.natoms*3, self.natoms*3), dtype=np.complex_)
        for dofatom in dofatoms:
            semat[dofatom, dofatom] = -1j*omega/self.damp
        return self.cleanse(semat)

    def advanselfenergy(self, omega, dofatoms):
        return self.retarselfenergy(omega, dofatoms).conjugate().transpose()

    def retarbiasselfenergy(self, omega, dofatoms):
        if self.isbias:
            semat = np.zeros((self.natoms*3, self.natoms*3), dtype=np.complex_)
            t1, t2 = dofatoms[0], dofatoms[-1] + \
                1  # TODO Need a more elegant way
            semat[t1:t2, t1:t2] = -1j*omega * \
                self.biasgamma-self.bias*self.chiminus
            #print('Bias atom: \n', np.diag(semat))
            return self.cleanse(semat)
        else:
            return 0

    def advanbiasselfenergy(self, omega, dofatoms):
        return self.retarbiasselfenergy(omega, dofatoms).conjugate().transpose()

    def kselfenergy(self, omega, T, dofatoms):
        return -2*np.imag(self.retarselfenergy(omega, dofatoms))*self.bosedist(omega, T)

    def kbiasselfenergy(self, omega, T, dofatoms):
        # print('Calculate bias self energy')
        if self.isbias:
            semat = np.zeros((self.natoms*3, self.natoms*3), dtype=np.complex_)
            t1, t2 = dofatoms[0], dofatoms[-1] + \
                1  # TODO Need a more elegant way
            semat[t1:t2, t1:t2] = ((self.chiplus-1j*self.chiminus)*(omega+self.bias)*(2*self.bosedist(omega+self.bias, T)-2*self.bosedist(
                omega, T))+(self.chiplus+1j*self.chiminus)*(omega-self.bias)*(2*self.bosedist(omega-self.bias, T)-2*self.bosedist(omega, T)))/2
            return (1j*self.retarbiasselfenergy(omega, dofatoms))*2*self.bosedist(omega, T)+self.cleanse(semat)
        else:
            return 0

    def totalkselfenergy(self, omega, T):
        return self.kselfenergy(omega, T, self.dofatomofbath[0])+self.kselfenergy(omega, T, self.dofatomofbath[1])+self.kbiasselfenergy(omega, T, self.dofatomofbias)

    def cleanse(self, semat):
        semat = np.delete(semat, self.dofatomfixed[0], axis=0)
        semat = np.delete(semat, self.dofatomfixed[0], axis=1)
        semat = np.delete(semat, [dof-len(self.dofatomfixed[0])
                                  for dof in self.dofatomfixed[1]], axis=0)
        semat = np.delete(semat, [dof-len(self.dofatomfixed[0])
                                  for dof in self.dofatomfixed[1]], axis=1)
        if len(semat) != len(self.dynmat) or self.natoms*3 != len(self.dofatomfixed[0]) + len(self.dofatomfixed[1]) + len(semat):
            raise ValueError('System DOF test failed, check again')
        return semat

    def retargf(self, omega):
        # retarded Green function
        return np.linalg.inv((omega+1e-9j)**2*np.identity(len(self.dynmat))-self.dynmat-self.retarselfenergy(omega, self.dofatomofbath[0])-self.retarselfenergy(omega, self.dofatomofbath[1])-self.retarbiasselfenergy(omega, self.dofatomofbias))

    def advangf(self, omega):
        # advanced Green function
        return np.linalg.inv((omega+1e-9j)**2*np.identity(len(self.dynmat))-self.dynmat-self.advanselfenergy(omega, self.dofatomofbath[0])-self.advanselfenergy(omega, self.dofatomofbath[1])-self.advanbiasselfenergy(omega, self.dofatomofbias))

    def gamma(self, Pi):
        return -1j*(Pi-Pi.conjugate().transpose())

    def bosedist(self, omega, T):
        # Bose Einstein distribution
        if abs(T) < 1e-30:
            # print('T %e is too small. Set kBT min.' % T)
            return 1/(np.exp(self.rpc*omega*np.iinfo(np.int32).max)-1)
        elif abs(omega/T) < 1e-30:
            # print('omega %e is too small. Set bose einstein distribution max.' % omega)
            return np.iinfo(np.int32).max
        else:
            return 1/(np.exp(self.rpc*omega/self.bc/T)-1)

    def ps(self, omega, T, atomlist):
        dofatomse = np.array(atomlist)-len(self.dofatomfixed[0])
        if not self.isbias:
            # Power spectrum of selected atoms
            return -2*omega**2*self.bosedist(omega, T)*np.trace(np.imag(self.retargf(omega)[dofatomse][:, dofatomse]))
            #return omega**2*np.trace(np.real(np.linalg.multi_dot([self.retargf(omega), self.totalkselfenergy(omega, T), self.advangf(omega)])[dofatomse][:, dofatomse]))
        elif self.isbias:
            # Power spectrum of bias atoms
            return omega**2*np.trace(np.real(np.linalg.multi_dot([self.retargf(omega), self.totalkselfenergy(omega, T), self.advangf(omega)])[dofatomse][:, dofatomse]))
        else:
            raise ValueError('Bias is not defined')

    def tm(self, omega):
        # Transmission
        return np.real(np.trace(np.dot(np.dot(np.dot(self.retargf(omega), self.gamma(self.retarselfenergy(omega, self.dofatomofbath[0]))), self.retargf(omega).conjugate().transpose()), self.gamma(self.retarselfenergy(omega, self.dofatomofbath[1])))))
        # return np.real(np.trace(np.linalg.multi_dot([self.retargf(omega),self.gamma(self.retarselfenergy(omega, self.dofatomofbath[0])),self.retargf(omega).conjugate().transpose(),self.gamma(self.retarselfenergy(omega, self.dofatomofbath[1]))])))

    def thermalcurrent(self, T, delta):
        # def f(omega):
        #    return self.rpc*omega/2 / \
        #        np.pi*self.tm(omega)*(self.bosedist(omega, T*(1+0.5*delta)) -
        #                              self.bosedist(omega, T*(1-0.5*delta)))

        # def trape(function, maxnumber, n):
        #    function = np.vectorize(function)
        #    arr = function(np.linspace(0, maxnumber, n+1))
        #    return (float(maxnumber - 0)/n/2.)*(2*arr.sum() - arr[0] - arr[-1])

        def f(i):
            return self.rpc*self.tmnumber[i, 0]/2 / \
                np.pi*self.tmnumber[i, 1]*(self.bosedist(self.tmnumber[i, 0], T*(1+0.5*delta)) -
                                           self.bosedist(self.tmnumber[i, 0], T*(1-0.5*delta)))

        def trape(function):
            n = len(self.tmnumber[:, 0]) - 1
            if n != self.intnum:
                raise ValueError('Error in number of omega')
            function = np.vectorize(function)
            arr = function(range(n+1))
            return (float(self.tmnumber[-1, 0] - self.tmnumber[0, 0])/n/2.)*(2*arr.sum() - arr[0] - arr[-1])
        # Unit in nW
        # return trape(f, self.maxomega, self.intnum)*1.60217662*1e2
        return trape(f)*1.60217662*1e2

    def thermalconductance(self, T, delta):
        return self.thermalcurrent(T, delta)/(T*delta)

    def thermalconductivity(self, T, delta, L, A):
        # L,A units in Angstrom
        return self.thermalconductance(T, delta)*L/A*10

    def write_v_sim(self, filename="anime.ascii"):
        from sclmd.tools import get_atomname
        # TODO: Not completely accurate in box setting & eigvecs
        text = "# Generated file for v_sim 3.7\n"
        text += "%15.9f%15.9f%15.9f\n" % (
            self.boxhi[0], self.boxlo[2], self.boxhi[1])
        text += "%15.9f%15.9f%15.9f\n" % (
            self.boxlo[0], self.boxlo[1], self.boxhi[2])
        for i in range(int(len(self.els)/3)):
            text += "%15.9f%15.9f%15.9f %2s\n" % (
                self.xyz[3*i], self.xyz[3*i+1], self.xyz[3*i+2], get_atomname(self.els[3*i]))
        for i, a in enumerate(self.omegas):
            text += "#metaData: qpt=[%f;%f;%f;%f \\\n" % (0, 0, 0, a)
            for u in range(int(len(self.els)/3)):
                text += "#; %f; %f; %f; %f; %f; %f \\\n" % (
                    self.eigvecs[i, 3*u]/self.els[3*u]**0.5, self.eigvecs[i, 3*u+1]/self.els[3*u]**0.5, self.eigvecs[i, 3*u+2]/self.els[3*u]**0.5, 0, 0, 0)
            text += "# ]\n"
        vfile = open(filename, 'w')
        vfile.write(text)
        vfile.close()

    def plotresult(self, lines=180):
        from matplotlib import pyplot as plt
        plt.figure(0)
        plt.hist(self.omegas, bins=lines)
        plt.xlabel('Frequence(eV)')
        plt.ylabel('Number')
        #plt.xlim(0, self.maxomega*self.rpc)
        plt.savefig('omegas.png')
        plt.figure(1)
        plt.plot(self.tmnumber[:, 0]*self.rpc, self.tmnumber[:, 1])
        plt.xlabel('Frequence(eV)')
        plt.ylabel('Transmission')
        plt.savefig('transmission.png')


if __name__ == '__main__':
    '''
    Units
    Time: ps
    Frequence: eV
    Temperture: K
    Heat Current: nW
    '''
    import time
    import numpy as np
    from matplotlib import pyplot as plt
    infile = ['atom_style full',
              'units metal',
              'boundary f p p',
              'read_data structure.data',
              'pair_style rebo',
              'pair_coeff * * CH.rebo C H',
              ]
    time_start = time.time()
    atomfixed = [range(0*3, (19+1)*3), range(181*3, (200+1)*3)]
    atomofbath = [range(20*3, (69+1)*3), range(131*3, (180+1)*3)]
    mybpt = bpt(infile, 0.25, 0.1, atomofbath, atomfixed)
    mybpt.gettm()
    mybpt.plotresult()
    # T_H/C = T*(1±delta/2)
    T = [100, 200, 300, 400, 500, 600, 700,
         800, 900, 1000]
    delta = 0.1
    thermalconductance = []
    for temp in T:
        thermalconductance.append(
            [temp, mybpt.thermalconductance(temp, delta)])
    mybpt.getps(300, 0.5, 1000)
    #mybpt.setbias(0.6, bdamp=None, chiplus=None, chiminus=None, dofatomofbias=[])
    #mybpt.getps(300, 0.5, 1000, dofatomofbias=[], filename='biascenter')
