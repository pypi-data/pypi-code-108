# -*- coding: utf-8 -*-
# pylint: disable=too-many-instance-attributes
"""Cotation.

Nage

- 4 N.
- Pap.
- Dos
- Bra.
- NL

Source: https://ffn.extranat.fr/webffn/nat_informatique.php?idact=nat

"""

import csv
import os


from .tools import Tools

# A.6.3 - Types Epreuves (raceid)

COTATION_DAMES = {
    1: '50 NL',
    2: '100 NL',
    3: '200 NL',
    4: '400 NL',
    5: '800 NL',
    6: '1500 NL',
    7: '1000 NL',
    9: '10x50 NL',
    11: '50 Dos',
    12: '100 Dos',
    13: '200 Dos',
    14: '8x100 NL',
    21: '50 Bra.',
    22: '100 Bra.',
    23: '200 Bra.',
    31: '50 Pap.',
    32: '100 Pap.',
    33: '200 Pap.',
    40: '100 4 N.',
    41: '200 4 N.',
    42: '400 4 N.',
    43: '4x100 NL',
    44: '4x200 NL',
    45: '10x100 NL',
    46: '4x100 4 N.',
    47: '4x50 NL',
    48: '4x50 4 N.',
    49: '6x50 NL',
    111: '4x50 Dos',
    121: '4x50 Bra.',
    131: '4x50 Pap.',
}

COTATION_MESSIEURS = {
    51: '50 NL',
    52: '100 NL',
    53: '200 NL',
    54: '400 NL',
    55: '800 NL',
    56: '1500 NL',
    57: '1000 NL',
    59: '10x50 NL',
    61: '50 Dos',
    62: '100 Dos',
    63: '200 Dos',
    64: '8x100 NL',
    71: '50 Bra.',
    72: '100 Bra.',
    73: '200 Bra.',
    81: '50 Pap.',
    82: '100 Pap.',
    83: '200 Pap.',
    90: '100 4 N.',
    91: '200 4 N.',
    92: '400 4 N.',
    93: '4x100 NL',
    94: '4x200 NL',
    95: '10x100 NL',
    96: '4x100 4 N.',
    97: '4x50 NL',
    98: '4x50 4 N.',
    99: '6x50 NL',
    161: '4x50 Dos',
    171: '4x50 Bra.',
    181: '4x50 Pap.',
}

COTATION_MIXTE = {
    34: '4x200 NL',
    35: '6x50 NL',
    36: '4x100 4 N.',
    37: '4x50 4 N.',
    84: '10x50 NL',
    85: '10x100 NL',
    87: '4x50 NL',
    88: '4x100 NL',
    214: '8x100 NL',
}

# 243
# 244
# 245
# 246
# 247
# 248
# 264
# 269
# 271
# 273
# 304
# 305
# 312
# 313
# 314
# 315
# 316
# 317
# 318
# 319
# 320
# 321
# 322
# 323
# 324
# 325
# 326
# 327
# 328
# 329
# 330
# 331
# 332
# 333
# 334
# 335
# 336
# 337
# 338
# 339
# 340
# 341
# 342
# 343
# 344


class Cotation():
    """CLASS : Cotation."""

    def __init__(self):
        """Constructor."""
        fpath = os.path.dirname(os.path.abspath(__file__))
        self.__csvpath__ = os.path.join(fpath, 'data')
        self.__cotation_csvfile__ = 'ffnex_table_cotation.csv'
        self.__coeff_csvfile__ = 'ffnex_coefficients_rajeunissement.csv'
        self.__coeffmixte_csvfile__ = 'ffnex_coefficients_rajeunissement_relais_mixtes.csv'
        self.__data__ = None
        self.__coeff__ = None
        self.__coeffmixte__ = None
        self.__cotation_dames_invert__ = {v: k for k, v in COTATION_DAMES.items()}
        self.__cotation_messieurs_invert__ = {v: k for k, v in COTATION_MESSIEURS.items()}
        self.__cotation_mixte_invert__ = {v: k for k, v in COTATION_MIXTE.items()}

    @property
    def data(self):
        """Get data."""
        if self.__data__ is None:
            self.__read_cotation__()

        return self.__data__

    @property
    def coeff(self):
        """Get coeff."""
        if self.__coeff__ is None:
            self.__read_coeff__()

        return self.__coeff__

    @property
    def coeffmixte(self):
        """Get coeff mixte."""
        if self.__coeffmixte__ is None:
            self.__read_coeffmixte__()

        return self.__coeffmixte__

    def __read_cotation__(self):
        """Read cotation file."""
        result = {}
        filename = os.path.join(self.__csvpath__, self.__cotation_csvfile__)

        with open(filename, encoding="utf-8") as csvfile:

            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                # EPREUVE_ID;TEMPS;POINTS;
                key = row['EPREUVE_ID']
                if key not in result:
                    result[key] = []

                result[key].append({'temps': float(row['TEMPS']), 'point': int(row['POINTS'])})

        self.__data__ = result

    def __read_coeff__(self):
        """Read coeff file."""
        result = {'F': {}, 'M': {}}
        filename = os.path.join(self.__csvpath__, self.__coeff_csvfile__)

        with open(filename, encoding="utf-8") as csvfile:

            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                # CATEGORIE;EPREUVE;COEFFICIENT;
                # C1 : 25 - 29 ans;50 Nage Libre Dames;1.147;

                # epreuve / sexe
                epreuve = row['EPREUVE']
                if 'Dames' in epreuve:
                    sexe = 'F'
                else:
                    sexe = 'M'
                epreuve = Tools.convertnage(epreuve)

                # age
                index = row['CATEGORIE'].find(':')
                age = row['CATEGORIE'][:index - 1]

                if epreuve not in result[sexe]:
                    result[sexe][epreuve] = {}

                result[sexe][epreuve][age] = float(row['COEFFICIENT'])

        self.__coeff__ = result

    def __read_coeffmixte__(self):
        """Read coeff mixte file."""
        result = {}
        filename = os.path.join(self.__csvpath__, self.__coeffmixte_csvfile__)

        with open(filename, encoding="utf-8") as csvfile:

            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                # CATEGORIE;EPREUVE;COEFFICIENT;
                # C1 : 25 - 29 ans;50 Nage Libre Dames;1.147;

                # epreuve
                epreuve = Tools.convertnage(row['EPREUVE'])

                # age
                index = row['CATEGORIE'].find(':')
                age = row['CATEGORIE'][:index - 1]

                if epreuve not in result:
                    result[epreuve] = {}

                result[epreuve][age] = float(row['COEFFICIENT'])

        self.__coeffmixte__ = result

    def __get_epreuve_code__(self, sexe, nage):
        """Get Epreuve code."""
        result = 0
        data = None
        sexe = sexe.upper()

        if sexe == 'F':
            data = self.__cotation_dames_invert__
        elif sexe == 'M':
            data = self.__cotation_messieurs_invert__
        elif sexe == 'MIXTE':
            data = self.__cotation_mixte_invert__

        if data is not None:
            if nage in data.keys():
                result = data[nage]

        return result

    def __get_temps_ajuste__(self, sexe, category_age, nage, temps):
        """Get temps ajuste."""
        result = 1

        if sexe in ['F', 'M']:
            if category_age in self.coeff[sexe][nage]:
                result = self.coeff[sexe][nage][category_age]
        elif sexe == 'MIXTE':
            if category_age in self.coeffmixte[nage]:
                result = self.coeffmixte[nage][category_age]

        # print(f'Temps: {temps} / coeff: {result}')

        # calcul
        t_ent, t_dec = divmod(temps, 1)
        tmp = (t_dec + t_ent * 0.60) / result
        t_ent, t_dec = divmod(tmp, 0.6)

        return round(t_ent + t_dec, 4)

    def get_cotation(self, sexe, category_age, nage, temps, coeff_enable=True):  # pylint: disable=too-many-arguments
        """Get cotation."""
        result = 0
        temps = float(temps)

        idnage = self.__get_epreuve_code__(sexe=sexe, nage=nage)
        if coeff_enable:
            temps = self.__get_temps_ajuste__(sexe=sexe, category_age=category_age, nage=nage, temps=temps)

        # print(f'idnage: {idnage} / Temps: {temps}')

        if idnage > 0:
            tabtps = self.data[str(idnage)]
            for item in tabtps:
                if item['temps'] >= temps:
                    result = item['point']
                    break

        return result

    def get_cotation_nageur(self, nageur, nage, temps, coeff_enable=True):
        """Get cotation."""
        return self.get_cotation(sexe=nageur.sexe, category_age=nageur.category_age, nage=nage, temps=temps, coeff_enable=coeff_enable)
