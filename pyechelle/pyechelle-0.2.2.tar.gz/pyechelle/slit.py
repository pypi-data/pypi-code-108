import math
import random

from numba import njit, float64
from numba.types import UniTuple


@njit(UniTuple(float64, 2)(float64, float64))
def simple_slit(xx, yy):
    return xx, yy


@njit(UniTuple(float64, 2)(float64, float64))
def round_slit(xx, yy):
    r = math.sqrt(xx) / 2.
    phi = yy * math.pi * 2
    return r * math.cos(phi) + 0.5, r * math.sin(phi) + 0.5


@njit(UniTuple(float64, 2)(float64, float64))
def octagonal_slit(r1, r2):
    phi = 0.
    s1 = math.sqrt(r1)
    phi_segment = 2. * math.pi / 8

    b = [1., 0.]
    c = [math.cos(phi_segment), math.sin(phi_segment)]
    x = b[0] * (1.0 - r2) * s1 + c[0] * r2 * s1
    y = b[1] * (1.0 - r2) * s1 + c[1] * r2 * s1

    segments = random.randint(0, 7)
    arg_values = phi_segment * segments + phi
    cos_values = math.cos(arg_values)
    sin_values = math.sin(arg_values)
    x_new = x * cos_values - y * sin_values
    y_new = x * sin_values + y * cos_values
    return x_new / 2. + 0.5, y_new / 2. + 0.5


@njit(UniTuple(float64, 2)(float64, float64))
def hexagonal_slit(r1, r2):
    phi = 0.
    s1 = math.sqrt(r1)
    phi_segment = 2. * math.pi / 6

    b = [1., 0.]
    c = [math.cos(phi_segment), math.sin(phi_segment)]
    x = b[0] * (1.0 - r2) * s1 + c[0] * r2 * s1
    y = b[1] * (1.0 - r2) * s1 + c[1] * r2 * s1

    segments = random.randint(0, 5)
    arg_values = phi_segment * segments + phi
    cos_values = math.cos(arg_values)
    sin_values = math.sin(arg_values)
    xnew = x * cos_values - y * sin_values
    ynew = x * sin_values + y * cos_values
    return xnew / 2. + 0.5, ynew / 2. + 0.5
