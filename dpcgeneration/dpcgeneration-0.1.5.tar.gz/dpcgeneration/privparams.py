'''
Created on 22 May 2017

@author: Hassan Jameel Asghar 
'''

import numpy as np
from scipy import misc
from scipy.special import comb

DEL_LIM = 2 ** (-30)
EPS_LIM = 1.0


def getdeltalim():
    return DEL_LIM


def getepslim():
    return EPS_LIM


def advcompformula(ebar, dbar, k):
    a = np.sqrt(2 * k * np.log(1 / dbar)) * ebar + k * ebar * (np.exp(ebar) - 1)  # In DP-book, page 49
    return a


def basiccompformula(ebar, k):
    a = k * ebar
    return a


def paramsadvcomp(k, pure):
    delta = getdeltalim()
    eps = getepslim()  # overall epsilon
    if pure:
        print ('pure')
        dbar = delta  # this means the k mechanisms are (eps, 0)-diff private
    else:
        dbar = delta / (k + 1)  # we set dbar and delta to be the same
    ebar = 1
    s = 0.000001  # precision level
    found = False

    while not found:
        cebar = advcompformula(ebar, dbar, k)

        if cebar < eps:
            found = True
        else:
            ebar = ebar - s

    return ebar, dbar  # this is the setting of each mechanism


def paramsbasiccomp(k, pure):
    delta = getdeltalim()
    eps = getepslim()  # overall epsilon
    if pure:
        dbar = 0  # this means the k mechanisms are (eps, 0)-diff private
    else:
        dbar = delta / k  # we set dbar and delta to be the same
    ebar = 1
    s = 0.000001  # precision level
    found = False
    while not found:
        cebar = basiccompformula(ebar, k)
        # print(cebar)
        if cebar < eps:
            found = True
        else:
            ebar = ebar - s
    return ebar, dbar  # this is the setting of each mechanism


def checkthresholdsh(eps, delta):
    thr = 2 * np.log(2 / delta) / (eps) + 1
    alp = 1
    thr = thr * alp
    print("thr:", thr)
    noise = np.random.laplace(loc=0, scale=2 / (eps))
    print("noise:", noise)
    return thr, noise


def sanitycheck(ebar, dbar, k):
    b = np.sqrt(2 * k * np.log(1 / dbar)) * ebar + k * ebar * (np.exp(ebar) - 1)
    return b


def getlapnoisebound(eps, perc, publicn):
    t = -np.log(1 - perc)
    if publicn:
        return 2 * t / eps
    else:
        return t / eps


if __name__ == '__main__':
    M = 126 # number of original attributes
    k = M + comb(M, 2)  # budget split
    # k = 15 # Budget split
    perc = 0.95  # with probability perc the answers are within
    pure = True  # whether each application of the mechanism is (eps, 0) (pure) or (eps, del) (not pure)
    publicn = False  # whether or not the population count is public or not
    print("number of budget splits:", k)
    print("confidence level for Laplace noise:", perc)
    print("")
    ebar, dbar = paramsadvcomp(k, pure)

    print("Advanced composition")
    print("====================")
    print("epsilon:", ebar)
    print("delta:", np.log2(dbar))
    lapnoise = getlapnoisebound(ebar, perc, publicn)
    print("Laplace noise bound is within:", lapnoise)
    print("")
    ebar, dbar = paramsbasiccomp(k, pure)
    print("Basic composition")
    print("=================")
    print("epsilon:", ebar)
    if dbar == 0:
        print("delta:", dbar)
    else:
        print("delta:", np.log2(dbar))

    # thr = checkthresholdsh(ebar, dbar)
    # print("Threshold is:", thr)

    lapnoise = getlapnoisebound(ebar, perc, publicn)
    print("Laplace noise bound is within:", lapnoise)
