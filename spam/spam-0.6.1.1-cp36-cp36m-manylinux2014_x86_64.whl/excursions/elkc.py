"""
Library of SPAM functions for computation Lipschitz-Killing Curvatures.
Copyright (C) 2020 SPAM Contributors

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy
from scipy.constants import pi

def expectedMesures(kappa, j, n, hittingSet='tail', distributionType='gauss', mu=0.0, std=1.0, correlationType='gauss', lc=1.0, nu=2.0, a=1.0):
    """
    Compute the Lipschitz-Killing Curvatures E(LKC)

    Parameters
    -----------
        kappa : float or list
            value of the threshold
        j : int
            number of the functionnal
        n : int
            spatial dimension
        hittingSet : string
            the hitting set
        distributionType : string
            type of distribution (see gaussianMinkowskiFunctionals)
        mu : float
            mean value of the distribution
        std : float
            standard deviation of the distribution
        correlationType : string
            type of correlation function
        lc : float
            correlation length
        nu : float
            parameter used for correlationType='matern'
        a : float or list of floats
            size(s) of the object
            if float, the object is considered as a cube

    Returns
    --------
        Same type as kappa
            the Gaussian Minkowski functionnal
    """

    e = 0.0 * kappa
    # compute second spetral moment
    lam2 = secondSpectralMoment(std, lc, correlationType=correlationType, nu=nu)
    # loop over i
    for i in range(n - j + 1):
        # comute LKC of the cube
        lkc = lkcCuboid(i + j, n, a)
        # compute GMF
        gmf = gaussianMinkowskiFunctionals(kappa, i, hittingSet=hittingSet, distributionType=distributionType, mu=mu, std=std)
        # compute
        fla = flag(i + j, i)
        e = e + fla * lkc * gmf * (lam2 / (2.0 * pi))**(i / 2.0)

    return e


def gaussianMinkowskiFunctionals(kappa, j, hittingSet='tail', distributionType='gauss', mu=0.0, std=1.0):
    """
    Evaluate the Gaussian Minkowski functionals j

    Parameters
    -----------
        kappa : float or list of floats
            value(s) of the threshold(s)
        j : int
            number of the functionnal
        hittingSet : string
            hitting set
        distributionType : string
            type of the underlying distribution. Implemented: ``gauss`` and ``log``
        mu : float
            mean value of the distribution
        std : float
            standard deviation of the distribution

    Returns
    --------
        mink : same type as kappa
            the Gaussian Minkowski functionnal
    """
    from scipy.special import erf

    if hittingSet == 'tail':
        sign = 1.0
    elif hittingSet == 'head':
        sign = (-1.0)**(j + 1)
    else:
        print('error in spam.excursions.elkc.gaussianMinkowskiFunctionals(): hitting set {} not implemented.'.format(hittingSet))
        return 0

    # STEP 2: change variable
    if distributionType == 'gauss':
        k = (kappa - mu) / std
    elif distributionType == 'log':
        k = (numpy.log(kappa) - mu) / std
    else:
        print('error in spam.excursions.elkc.gaussianMinkowskiFunctionals(): distribution type {} not implemented.'.format(distributionType))
        return 0

    if j == 0:
        mink = 0.5 * (1.0 - sign * erf(k / 2**0.5))
    elif j > 0:
        mink = sign * numpy.exp(-k**2.0 / 2.0) * hermitePolynomial(k, j - 1) / (std**j * (2.0 * pi)**0.5)
        # mink = - (k**3 - 3*k)*numpy.exp(-k**2.0/2.0) / (std**4*(2.0*pi)**0.5)
    else:
        print('error in spam.excursions.elkc.gaussianMinkowskiFunctionals(): j should be > 0. {} given.'.format(j))
        return 0

    return mink


def secondSpectralMoment(std, lc, correlationType='gauss', nu=2.0):
    """
    Compute the second spectral moment for a given covariance function:

    .. math::
        {\lambda}_2 = C''(h)|_{h=0}

    Parameters
    -----------
        std : float
            standard deviation
        lc : float
            correlation length
        correlationType : string
            type of correlation function
        nu : float
            parameter used for correlationType='matern'

    Returns
    --------
        float
            the second spectral moment
    """
    v = std**2.0
    if correlationType == 'gauss':
        return 2.0 * v / lc**2.0
    elif correlationType == 'matern':
        if nu <= 1:
            print('error in spam.excursions.elkc.secondSpectralMoment(): nu should be > 1. {} given.'.format(nu))
            return 0
        return (v * nu) / (lc**2.0 * (nu - 1.0))
    else:
        print('error in spam.excursions.elkc.secondSpectralMoment(): correlation type {} not implemented.'.format(correlationType))
        return 0


def flag(n, j):
    """
    Compute the flag coefficients ``[ n, j ] = ( n, j ) w_n / w_{n-j}w_j``

    Parameters
    -----------
        n : int
            first parameter of the binom
        j : int
            second parameter of the binom

    Returns
    --------
        float
            the flag coefficient [n , j]
    """
    from scipy.special import binom

    if j > n:
        print('error in spam.excursions.elkc.flag(): n should be >= j. Here n={}, j={}'.format(n, j))
        return 0
    vn = ballVolume(n)
    vj = ballVolume(j)
    vnj = ballVolume(n - j)

    return binom(n, j) * vn / (vnj * vj)


def hermitePolynomial(x, n):
    """
    Evaluate a x the probabilitic Hermite polynomial n

    Parameters
    -----------
        x : float
            point of evaluation
        n : int
            number of Hermite polynomia

    Returns
    --------
        float
            ``He_n(x)`` the value of the polynomial

    """
    from numpy.polynomial.hermite_e import hermeval

    coefs = [0] * (n + 1)
    coefs[n] = 1

    return hermeval(x, coefs)


def ballVolume(n, r=1.0):
    """
        Compute the volume of a nth dimensional ball

    Parameters
    -----------
        n : int
            spatial dimension
        r : float
            radius of the ball

    Returns
    --------
        float
            volume of the ball
    """
    from scipy.special import gamma

    return float(r)**float(n) * pi**(0.5 * n) / gamma(1.0 + 0.5 * n)


def lkcCuboid(i, n, a):
    """
    Compute the Lipschitz-Killing Curvatures of a parallelepiped

    Parameters
    -----------
        i : int
            number of the LKC. ``0 <= i <= n``
        n : int
            spatial dimension
        a : float or list of float
            size(s) of the cuboid. If float, the object is considered to be a cube.

    Returns
    --------
        float
            The Lipschitz-Killing Curvature
    """
    from scipy.special import binom

    if i > n or i < 0:
        print('error in spam.excursions.elkc.lkcCuboid(): i should be between 0 and n. Here n={}, i={}'.format(n, i))
        return 0

    # cube
    if isinstance(a, (int, float)):
        # general formula for every i and n
        lkc = binom(n, i) * a**i
        return lkc

    # cuboid
    else:
        # check if a is well defined
        if len(a) != n:
            print('error in spam.excursions.elkc.lkcCuboid(): Spatial dimension doesn\'t match length definition. len(a) = {} and n = {}'.format(len(a), n))
            return 0

        # 2D
        if n == 2:
            switcher = {
                0: 1,
                1: a[0] + a[1],
                2: a[0] * a[1],
            }
            return switcher.get(i, -1)

        # 3D
        elif n == 3:
            switcher = {
                0: 1,
                1: a[0] + a[1] + a[2],
                2: a[0] * a[1] + a[0] * a[2] + a[2] * a[1],
                3: a[0] * a[1] * a[2],
            }
            return switcher.get(i, -1)

        else:
            print('error in spam.excursions.elkc.lkcCuboid(): Spatial dimension n = {} not implemented.'.format(n))
            return 0

#
# def phi(x, s):
#     return numpy.exp(-x**2/2.0)/(s*numpy.sqrt(2.0*pi))
#
#
# def bigPhi(x, s):
#     from scipy.special import erf
#     return phi(x, s) - 0.5*x*(1.0+erf(-x/numpy.sqrt(2.0)))


# def expectedMesuresLinearThreshold(alpha, beta, j, n, hittingSet='tail', distributionType='gauss', mu=0.0, std=1.0, correlationType='gauss', lc=1.0, nu=2.0, a=1.0):
#     """
#     Compute the Lipschitz-Killing Curvatures E(LKC)
#
#     Parameters
#     -----------
#         kappa : float or list
#             value of the threshold
#         j : int
#             number of the functionnal
#         n : int
#             spatial dimension
#         hittingSet : string
#             the hitting set
#         distributionType : string
#             type of distribution (see gaussianMinkowskiFunctionals)
#         mu : float
#             mean value of the distribution
#         std : float
#             standard deviation of the distribution
#         correlationType : string
#             type of correlation function
#         lc : float
#             correlation length
#         nu : float
#             parameter used for correlationType='matern'
#         a : float or list of floats
#             size(s) of the object
#             if float, the object is considered as a cube
#
#     Returns
#     --------
#         mink : same type as kappa
#             the Gaussian Minkowski functionnal
#     """
#     # HISTORY:
#     # 2016-04-08: First version of the function
#     #
#
#     e = 0.0*alpha
#     # compute second spetral moment
#     lam2 = secondSpectralMoment(std, lc, correlationType=correlationType, nu=2.0)
#     # loop over i
#     # if prlv>5: print 'IN ELKC: n = {}, j = {}'.format( n, j )
#     # for i in range( n-j+1 ):
#     #    if prlv>5: print '\t\ti = {}'.format( i )
#     #    # comute LKC of the cube
#     #    lkc = lkcCuboid( i+j, n, a )
#     #    # compute GMF
#     #    gmf = gaussianMinkowskiFunctionalsLinearThreshold( alpha, beta, a, i, hittingSet=hittingSet, lam2=lam2 )
#
#     #    # compute
#     #    fla = flag( i+j , i )
#     #    e = e + fla*gmf*lkc*( lam2/(2.0*pi) )**(i/2.0)
#
#     e = 0.0
#     if n == 1:
#         from scipy.special import erf, erfc
#         cstA = alpha*a/(numpy.sqrt(2.0)*std)
#         cstB = beta/(numpy.sqrt(2.0)*std)
#         cstAB = cstA+cstB
#
#         # intOfMo = (( numpy.sqrt(2.0/pi) * std * ( numpy.exp(-cstAB**2.0) - numpy.exp(-cstB**2) ) + (alpha*a+beta) * erf(cstAB) - beta*erf(cstB) )/(2.0*alpha) + 0.5*a) # tail
#         intOfMo = ((numpy.sqrt(2.0/pi) * std * (-numpy.exp(-cstAB**2.0) + numpy.exp(-cstB**2)) +
#                     (alpha*a) * erfc(cstAB) - beta*erf(cstAB) + + beta*erf(cstB))/(2.0*alpha))  # head
#
#         if j == 1:
#             e = intOfMo
#         elif j == 0:
#             c = numpy.sqrt(lam2) * bigPhi(alpha/(numpy.sqrt(lam2)*std), std)
#             intOfUpCrossed = c * (erf(cstAB) - erf(cstB))/(2.0*alpha)
#
#             e = intOfMo/a + intOfUpCrossed
#         else:
#             print("ELKC not implemented for n={} and j={}-> exiting".format(n, j))
#
#     else:
#         print("ELKC not implemented for n={} -> exiting".format(n))
#
#     return e
#
#
# def gaussianMinkowskiFunctionalsLinearThreshold(alpha, beta, a, j, hittingSet='tail', distributionType='gauss', mu=0.0, std=1.0, lam2=1.0):
#     """
#     Compute the Gaussian Minkowski functionals j
#
#     Parameters
#     -----------
#         kappa : float or list
#             value of the threshold
#         j : int
#             number of the functionnal
#         hittingSet : string
#             the hitting set
#         distributionType : string
#             type of distribution (see gaussianMinkowskiFunctionals)
#             implemented: distributionType='gauss' and distributionType='log'
#         mu : float
#             mean value of the distribution
#         std : float
#             standard deviation of the distribution
#
#     Returns:
#         mink : same type as kappa
#             the Gaussian Minkowski functionnal
#     """
#     # HISTORY:
#     # 2016-04-08: First version of the function
#     #
#
#     from scipy.special import erf, erfc
#     cstA = alpha*a/(numpy.sqrt(2.0)*std)
#     cstB = beta/(numpy.sqrt(2.0)*std)
#     cstAB = cstA+cstB
#
#     if j == 0:
#         if hittingSet == 'tail':
#             mink = ((numpy.sqrt(2.0/pi) * std * (numpy.exp(-cstAB**2.0) - numpy.exp(-cstB**2)) +
#                      (alpha*a+beta) * erf(cstAB) - beta*erf(cstB))/(2.0*alpha) + 0.5*a)/a
#         elif hittingSet == 'head':
#             mink = ((numpy.sqrt(2.0/pi) * std * (-numpy.exp(-cstAB**2.0) + numpy.exp(-cstB**2)) +
#                      (alpha*a) * erfc(cstAB) - beta*erf(cstAB) + + beta*erf(cstB))/(2.0*alpha))/a
#
#     elif j == 1:
#         if hittingSet == 'tail':
#             mink = (erf(cstAB)-erf(cstB))/(2*alpha*a)
#         elif hittingSet == 'head':
#             x = alpha/(numpy.sqrt(lam2)*std)
#             mink = (erf(cstAB)-erf(cstB))/(2*alpha*a) * bigPhi(x, std)
#     else:
#         print("Error GMF not implemented", j)
#         exit()
#     return mink


def getThresholdFromVolume(targetVolume, initialThreshold, hittingSet='tail', distributionType='gauss', mu=0.0, std=1.0, correlationType='gauss', nu=2.0, a=1.0):
    import scipy.optimize

    def minFunc(t):
        vol = expectedMesures(t, 3, 3, hittingSet=hittingSet, distributionType=distributionType, mu=mu, std=std, correlationType=correlationType, nu=nu, a=a)
        # print("t = {}, vol = {}, diff = {}".format(t, vol, vol-targetVolume))
        return numpy.square(vol - targetVolume)

    res = scipy.optimize.minimize(minFunc, initialThreshold, method='BFGS')
    return res.x[0]


def getCorrelationLengthFormArea(targetArea, initialLength, threshold, hittingSet='tail', distributionType='gauss', mu=0.0, std=1.0, correlationType='gauss', nu=2.0, a=1.0):
    import scipy.optimize

    def minFunc(l):
        ar = 2.0 * expectedMesures(threshold, 2, 3, hittingSet=hittingSet, distributionType=distributionType, mu=mu, std=std, lc=l, correlationType=correlationType, nu=nu, a=a)
        # print("l = {}, ar = {}, diff = {}".format(l, ar, ar-targetArea))
        return numpy.square(ar - targetArea)

    res = scipy.optimize.minimize(minFunc, initialLength, method='BFGS')
    return res.x[0]
