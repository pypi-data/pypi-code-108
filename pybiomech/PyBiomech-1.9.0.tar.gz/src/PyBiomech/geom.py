# -*- coding: utf-8 -*-


import numpy as np


def vec2R(line):
    z = line.copy()
    z = z / np.linalg.norm(z)
    x = np.cross(z, (1, 0, 0))
    x = x / np.linalg.norm(x)
    y = np.cross(z, x)
    y = y / np.linalg.norm(y)
    R = np.array((x, y, z)).T
    return R


def pointsFromCircle(radius, step):
    v = np.arange(-radius, +radius+step, step)
    X, Y = np.meshgrid(v, v)
    D = np.sqrt(X**2 + Y**2)
    idx = D < radius
    x, y = X[idx], Y[idx]
    P = np.hstack( (x[:,np.newaxis], y[:,np.newaxis], np.zeros((x.shape[0],1))) )
    return P


def pointsFromCircumference(radius, angleStep):
    angles = np.arange(0., 360., angleStep)
    anglesr = np.deg2rad(angles)
    x, y = radius*np.cos(anglesr), radius*np.sin(anglesr)
    P = np.hstack( (x[:,np.newaxis], y[:,np.newaxis], np.zeros((x.shape[0],1))) )
    return P


def circlePointsOnRotatedPlane(line, point, aperture, step):
    # https://stackoverflow.com/questions/3461869/plot-a-plane-based-on-a-normal-vector-and-a-point-in-matlab-or-matplotlib
    R = vec2R(line)
    Ps = pointsFromCircle(aperture, step)
    Ps2 = np.dot(Ps, R.T) + point[np.newaxis,:]
    return Ps2


def circumferencePointsOnRotatedPlane(line, point, aperture, angleStep):
    R = vec2R(line)
    Ps = pointsFromCircumference(aperture, angleStep)
    Ps2 = np.dot(Ps, R.T) + point[np.newaxis,:]
    return Ps2