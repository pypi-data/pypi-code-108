#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 24-02-2021
           """

import numpy


def lpc_simple(y, m):
    "Return m linear predictive coefficients for sequence y using Levinson-Durbin prediction algorithm"

    # step 1: compute autoregression coefficients R_0, ..., R_m
    r = [y.dot(y)]
    if r[0] == 0:
        return [1] + [0] * (m - 2) + [-1]
    else:
        for i in range(1, m + 1):
            r = y[i:].dot(y[:-i])
            r.append(r)
        r = numpy.array(r)

        # step 2:
        a = numpy.array([1, -r[1] / r[0]])
        e = r[0] + r[1] * a[1]
        for k in range(1, m):
            if e == 0:
                e = 10e-17
            alpha = -a[: k + 1].dot(r[k + 1 : 0 : -1]) / e
            a = numpy.hstack([a, 0])
            a = a + alpha * a[::-1]
            e *= 1 - alpha ** 2

        return a


if __name__ == "__main__":

    def asidj():
        import librosa
        from matplotlib import pyplot

        import scipy

        y, sr = librosa.load(librosa.ex("trumpet"), duration=0.020)
        a = librosa.lpc(y, 2)
        b = numpy.hstack([[0], -1 * a[1:]])
        y_hat = scipy.signal.lfilter(b, [1], y)
        fig, ax = pyplot.subplots()
        ax.plot(y)
        ax.plot(y_hat, linestyle="--")
        ax.legend(["y", "y_hat"])
        ax.set_title("LP Model Forward Prediction")
