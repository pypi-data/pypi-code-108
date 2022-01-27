#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys

import numpy as np

import sclmd.units as U


class myfft:
    def __init__(self, dt, n):
        self.dt = dt
        self.N = n
        self.dw = 2*np.pi/dt/n

    def Fourier1D(self, a):
        """ 
        1D Fourier transform from t to w using our definition:
        f(w) = int f(t) e^Iwt dt
        In discrete form, it's
        f(j) = dt sum_{i=0}^{N-1} f(i) e^(I 2pi i j/N).
        N is length of the data. 
        domega/2/pi = 1/N/dt
        This corresponds to the inverse FFT in numpy:
            numpy.fft.ifft(a)*2*pi/domega
        """
        if(len(a) != self.N):
            print("MyFFT.Fourier1D: array length error!")
            sys.exit(0)
        else:
            nor = 2.*np.pi/self.dw
            b = np.fft.ifft(a)
            return nor*b

    def iFourier1D(self, a):
        """ 
        1D Fourier transform from w to t using our definition:
        f(t) = int f(w) e^-Iwt dw/2/pi
        In discrete form, it's
        f(i) = dw/2/pi sum_{j=0}^{N-1} f(j) e^(-I 2pi i j/N).
        N is length of the data. 
        domega/2/pi = 1/N/dt
        This corresponds to the FFT in numpy:
            numpy.fft.fft(a)*domega/2/pi
        """
        if(len(a) != self.N):
            print("MyFFT.iFourier1D: array length error!")
            sys.exit(0)
        else:
            nor = self.dw/2/np.pi
            b = np.fft.fft(a)
            return nor*b


np.seterr(over="ignore")


def coth(x):
    """
    hyperbolic cotangent function
    """
    if x == 0.0:
        print("coth:coth(0) is infinity")
        sys.exit(0)
    else:
        return np.cosh(x)/np.sinh(x)


def xcoth(x):
    """
    x*coth(x)
    """
    if x == 0.0:
        return 1.0
    else:
        return x*np.cosh(x)/np.sinh(x)


def bose(w, T):
    """
    bose distribution
    """
    #small = 10e-20
    if T == 0.0:
        if w == 0.0:
            return 1/(np.exp(1.0/U.kb)-1)
        elif w < 0.0:
            return -1.0
        else:
            return 0.0
    else:
        if w == 0.0:
            # return 1/small
            # have problems for finite temperature for bias calculation
            # return 0 seems solves it
            return 0.0
        else:
            return 1.0/(np.exp(w/U.kb/T)-1.0)


def fermi(ep, mu, T):
    """
    fermi distribution
    """
    if T == 0.0:
        if(ep < mu):
            return 1.0
        elif(ep > mu):
            return 0.0
        else:
            return 0.5
    else:
        return 1/(np.exp((ep-mu)/U.kb/T)+1)


def flinterp(x, xs, ys):
    """
    do a linear interpolation of (xs,ys), return the interpolated value at x.
    """
    id = nearest(x, xs)

    # boundaries
    if id == len(xs)-1:
        return ys[-1]
    if id == 0:
        return ys[0]

    # linear interpolation
    dd = xs[id]-x
    if dd < 0:
        return ys[id]+dd/(xs[id]-xs[id-1])*(ys[id]-ys[id-1])
    else:
        return ys[id]+dd/(xs[id]-xs[id+1])*(ys[id]-ys[id+1])


def nearest(b, bs):
    """
    return the index of the element in bs wich is the nearest to b.
    """
    bsn = np.array(bs)
    bst = abs(bsn-b)
    return(list(bst).index(min(bst)))


def rpadleft(bs, b):
    if len(bs) > 1:
        return np.concatenate((np.array([b]), np.array(bs)[:-1]), axis=0)
    elif len(bs) == 1:
        return np.array([b])
    else:
        print("len(bs) is less than 1")
        sys.exit()


def mdot(* args):
    return np.linalg.multi_dot([im for im in args])

def mm(* args):
    # mm with arbitrary number of arguments
    tmp=args[0].copy()
    for mat in args[1:]:
        tmp=np.dot(tmp,mat)
    return tmp

def chkShape(a):
    """
    check if a is a n by n matrix, if yes return n
    """
    aa = np.array(a)
    ash = np.shape(aa)
    if(ash[0] == ash[1]):
        return ash[0]
    else:
        print("The matrix should be a n by n matrix")
        sys.exit(0)


def symmetrize(a):
    aa = np.array(a)
    return 0.5*(aa+np.transpose(aa))


def antisymmetrize(a):
    aa = np.array(a)
    return 0.5*(aa-np.transpose(aa))


def dagger(a):
    aa = np.array(a)
    ash = np.shape(aa)
    if(ash[0] != ash[1]):
        print("Not sqaure matrix")
        sys.exit(0)
    return np.transpose(np.conjugate(aa))


def hermitianize(a):
    aa = np.array(a)
    return 0.5*(aa+dagger(aa))


def powerspecq(qs, dt, nmd):
    """
    qs      list of trajectories, shape(nmd,nph)
    dt      time step of MD simulation
    nmd     number of MD steps
    """
    qst = np.transpose(np.array(qs))
    nmd2 = qst.shape[1]
    if nmd != nmd2:
        print("power: qs shape error!")
        sys.exit()
    dw = 2.*np.pi/dt/nmd

    qsw = np.array([myfft(dt, nmd).Fourier1D(a) for a in qst])
    qsw = np.real(np.transpose(qsw*np.conjugate(qsw)))
    return np.array([[i*dw, (dw*i)**2*np.sum(qsw[i])/dt/nmd] for i in range(nmd)])


def powerspecp(ps, dt, nmd):
    """
    ps      list of trajectories, shape(nmd,nph)
    dt      time step of MD simulation
    nmd     number of MD steps
    """
    pst = np.transpose(np.array(ps))
    nmd2 = pst.shape[1]
    if nmd != nmd2:
        print("power: ps shape error!")
        sys.exit()
    dw = 2.*np.pi/dt/nmd

    psw = np.array([myfft(dt, nmd).Fourier1D(a) for a in pst])
    psw = np.real(np.transpose(psw*np.conjugate(psw)))
    return np.array([[i*dw, np.sum(psw[i])/dt/nmd] for i in range(nmd)])
