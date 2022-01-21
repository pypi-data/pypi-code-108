# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# This file is part of refidx
# License: GPLv3
# See the documentation at benvial.gitlab.io/refidx


__all__ = ["DataBase", "Material"]

"""
Get refractive index from a database
====================================

Retrieve the refractive index of a material at a given wavelength
from the refractiveindex.info_ database.
Inspired from from this repository_: github.com/cinek810/refractiveindex.info.

 .. _refractiveindex.info:
     https://refractiveindex.info/
 .. _repository:
     https://github.com/cinek810/refractiveindex.info
"""

import os
from copy import deepcopy

import numpy as np

from ._database import *


def formula(lamb, coeff, formula_number):
    if formula_number == 1:
        epsi = 0
        for i in reversed(list(range(1, np.size(coeff), 2))):
            epsi += (coeff[i] * lamb ** 2) / (lamb ** 2 - coeff[i + 1] ** 2)
        epsi += coeff[0] + 1
        n = np.sqrt(epsi)
    elif formula_number == 2:
        epsi = 0
        for i in reversed(list(range(1, np.size(coeff), 2))):
            epsi += (coeff[i] * lamb ** 2) / (lamb ** 2 - coeff[i + 1])
        epsi += coeff[0] + 1
        n = np.sqrt(epsi)
    elif formula_number == 3:
        epsi = coeff[0]
        for i in range(1, np.size(coeff), 2):
            epsi += coeff[i] * lamb ** coeff[i + 1]
        n = np.sqrt(epsi)
    elif formula_number == 4:
        coeff_ = np.zeros(17)
        for i, val in enumerate(coeff):
            coeff_[i] = val
        coeff = coeff_
        epsi = coeff[0]
        epsi += coeff[1] * lamb ** coeff[2] / (lamb ** 2 - coeff[3] ** coeff[4])
        epsi += coeff[5] * lamb ** coeff[6] / (lamb ** 2 - coeff[7] ** coeff[8])
        epsi += coeff[9] * lamb ** coeff[10]
        epsi += coeff[11] * lamb ** coeff[12]
        epsi += coeff[13] * lamb ** coeff[14]
        epsi += coeff[15] * lamb ** coeff[16]
        n = np.sqrt(epsi)
    elif formula_number == 5:
        n = coeff[0]
        for i in reversed(list(range(1, np.size(coeff), 2))):
            n += coeff[i] * lamb ** coeff[i + 1]
    elif formula_number == 6:
        n = coeff[0] + 1
        for i in reversed(list(range(1, np.size(coeff), 2))):
            n += coeff[i] / (coeff[i + 1] - lamb ** (-2))
    elif formula_number == 7:
        n = coeff[0]
        n += coeff[1] / (lamb ** 2 - 0.028)
        n += coeff[2] / (lamb ** 2 - 0.028) ** 2
        for i in range(3, np.size(coeff)):
            n += coeff[i] * lamb ** (2 * (i - 2))
    elif formula_number == 8:
        A = coeff[0]
        A += coeff[1] * lamb ** 2 / (lamb ** 2 - coeff[2])
        A += coeff[3] * lamb ** 2
        n = ((1 + 2 * A) / (1 - A)) ** 0.5
    elif formula_number == 9:
        epsi = coeff[0]
        epsi += coeff[1] / (lamb ** 2 - coeff[2])
        epsi += coeff[3] * (lamb - coeff[4]) / ((lamb - coeff[4]) ** 2 * +coeff[5])
        n = np.sqrt(epsi)
    return n


def check_bounds(lamb, dataRange):
    return np.min(lamb) >= dataRange[0] and np.max(lamb) <= dataRange[1]


def get(d, l):
    if len(l) == 1:
        return d[l[0]]
    return get(d[l[0]], l[1:])


class Material:
    """Material class"""

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f"Material " + (" ").join(self.id)

    @property
    def data(self):
        return get(database, self.id)

    @property
    def material_data(self):
        return self.data["DATA"]

    @property
    def references(self):
        return self.data["REFERENCES"]

    @property
    def type(self):
        return self.material_data["type"]

    @property
    def comments(self):
        try:
            comments = self.data["COMMENTS"]
        except:
            comments = None
        return comments

    @property
    def info(self):
        return dict(comments=self.comments, references=self.references)

    @property
    def wavelength_range(self):
        return self.material_data["wavelength_range"]

    def get_index(self, wavelength):
        """Get the complex refractive index.

        Parameters
        ----------
        wavelength : float or array of floats
            Wavelength.

        Returns
        -------
        complex or complex array
            The refractive index.

        """
        wrange = self.wavelength_range
        wavelength = np.array(wavelength)
        if not check_bounds(wavelength, wrange):
            raise ValueError(
                f"No data for this material {self.id}. Wavelength must be between {wrange[0]} and {wrange[1]} microns.",
            )

        if self.type.split()[0] == "tabulated":
            matLambda = np.array(self.material_data["wavelengths"])
            matN = np.array(self.material_data["index"])
            return np.interp(wavelength, matLambda, matN).conj()

        else:
            return formula(
                wavelength,
                self.material_data["coefficients"],
                int(self.type.split()[1]),
            )

    def print_info(self, html=False, tmp_dir=None):

        if html:
            html_data = "".join(
                [
                    "<h5>" + k.title() + "</h5>" + "<p>" + v + "</p>"
                    for k, v in self.info.items()
                    if v is not None
                ]
            )
            html_data = "<div class=matdata>" + html_data + "</div>"

            if tmp_dir is not None:
                # building the docs with sphinx-gallery
                assert os.path.exists(tmp_dir)
                with open(os.path.join(tmp_dir, "out.html"), "wt") as fh:
                    fh.write(html_data)
            else:
                try:
                    # running from a terminal or jupyter
                    from IPython.display import HTML, display

                    display(HTML(html_data))
                except ImportError:
                    print(self.info)
        else:
            print(self.info)


def recursive_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield (key, value, dictionary)
            yield from recursive_items(value)
        else:
            yield (key, value, dictionary)


database_mat = deepcopy(database)

nb_mat = 0
for key, value, dictionary in recursive_items(database_mat):
    if type(value) is dict and "DATA" in value.keys():
        dictionary[key] = Material(materials_path[nb_mat].split("/"))
        nb_mat += 1


class DataBase:
    """Material database"""

    def __init__(self):
        self.materials = database_mat

    def random(self):
        mat = self.materials
        while isinstance(mat, dict):
            mat = np.random.choice(list(mat.values()))
        return mat
