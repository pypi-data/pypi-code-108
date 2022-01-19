#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe de rolling sur une fenêtre
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Created on Sat Mar 27 10:17:24 2021

@author: Cyrile Delestre
"""

from typing import List, Union, Any
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class RollingWindow:
    r"""
    Classe permettant de faire un rolling sur un itérateur qui peut être 
    une DataFrame Pandas, un array Numpy ou un liste.

    Parameters
    ----------
    data : Union[List[Any], np.ndarray, pd.DataFrame]
        Itérable où sera appliquer le rolling.
    window : int
        Taille de la fenêtre du rolling. Elle doit être au minimum de taille 
        2 et maximum la taille de data.
    poisition : str (='right')
        Position du centrage de la fenêtre, elle peut être "right", "center" 
        ou "left".

    Notes
    -----
    La classe convertie les types de la DataFrame d'origine aux type étandu 
    de Pandas 1.0. La classe n'est pas compatible avec une version de 
    Pandas inférieur. Une copy de la sous DataFrame est faite en sortie 
    d'ésoladirisant ainsi le retour du rolling avec la DataFrame d'origine.

    Examples
    --------
    >>> import pandas as pd
    >>> from dstk.utils import RollingWindow
    >>> 
    >>> df = pd.DataFrame({'a': ['a', 'b', 'c', 'd'], 'b': [1,2,3,4]})
    >>> roll = RollingWindow(test,3, position='right')
    >>> roll[0]
          a     b
    0  <NA>  <NA>
    1  <NA>  <NA>
    2     a     1
    >>> roll[1]
          a     b
    0  <NA>  <NA>
    1     a     1
    2     b     2
    >>> len(roll)
    4
    >>> roll[4]
    IndexError: Index out of band, l'index doit être compris entre 0 et 3.
    """
    data: Union[List[Any], np.ndarray, pd.DataFrame]
    window: int
    position: str = 'right'

    def __post_init__(self):
        if not isinstance(self.data, (list, np.ndarray, pd.DataFrame)):
            raise AttributeError(
                "data doit être un array-like (list, NumPy array ou "
                f"DataFrame) et non de type {type(self.data)}."
            )
        if self.position not in ['left', 'right', 'center']:
            raise AttributeError(
                "La position de la fenêtre doit être 'left', 'center' ou "
                f"'right' et non '{self.position}'."
            )
        if self.window > len(self.data):
            raise AttributeError(
                "La taille de la fenêtre ne peut pas être supérieur à la "
                "taille de la donnée."
            )
        if isinstance(self.data, pd.DataFrame):
            self.pandas = True
            self.data = self.data.convert_dtypes()
        else: self.pandas = False

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        if idx > self.__len__()-1:
            raise IndexError(
                "Index out of band, l'index doit être compris entre 0 et "
                f"{self.__len__()-1}."
            )
        if self.position == 'right':
            if idx < self.window-1:
                return self._out_of_lower_band(idx, 1)
            else:
                return (
                    self.data[idx-self.window+1:idx+1].copy()
                    if not self.pandas else
                    (
                        self.data
                        .iloc[idx-self.window+1:idx+1]
                        .copy()
                    )
                )
        elif self.position == 'left':
            if idx > len(self.data)-self.window:
                return self._out_of_upper_band(idx, 0)
            else:
                return (
                    self.data[idx:idx+self.window].copy()
                    if not self.pandas else
                    (
                        self.data
                        .iloc[idx:idx+self.window]
                        .copy()
                    )
                )
        else:
            middle_win = (self.window-1)//2
            right_res = self.window-middle_win
            if idx < middle_win:
                return self._out_of_lower_band(idx, self.window//2+1)
            elif idx > len(self.data)-right_res:
                return self._out_of_upper_band(idx, (self.window-1)//2)
            else:
                return (
                    self.data[idx-middle_win:idx+right_res].copy()
                    if not self.pandas else
                    (
                        self.data
                        .iloc[idx-middle_win:idx+right_res]
                        .copy()
                    )
                )

    def _out_of_lower_band(self, idx: int, offset: int):
        if self.pandas:
            roll = pd.DataFrame(
                columns=self.data.columns,
                index=(
                    [pd.NA]*(self.window-idx-offset)
                    +list(self.data.iloc[0:idx+offset].index)
                )
            )
            roll.iloc[self.window-idx-offset:self.window] = (
                self.data.iloc[0:idx+offset]
            )
            roll = roll.astype(self.data.dtypes.to_dict())
            return roll
        elif isinstance(self.data, np.ndarray):
            roll = np.empty((self.window, self.data.shape[1]))
            roll.fill(np.nan)
            roll[self.window-idx-offset:self.window] = (
                self.data[0:idx+offset]
            )
            return roll
        else:
            return self.data[0:idx+offset].copy()

    def _out_of_upper_band(self, idx: int, offset: int):
        if self.pandas:
            roll = pd.DataFrame(
                columns=self.data.columns,
                index=(
                    list(self.data.iloc[idx-offset:].index)
                    +[pd.NA]*(self.window-len(self.data)+idx-offset)
                )
            )
            roll.iloc[0:len(self.data)-idx+offset] = (
                self.data.iloc[idx-offset:]
            )
            roll = roll.astype(self.data.dtypes.to_dict())
            return roll
        elif isinstance(self.data, np.ndarray):
            roll = np.empty((self.window, self.data.shape[1]))
            roll.fill(np.nan)
            roll[0:len(self.data)-idx+offset] = self.data[idx-offset:]
            return roll
        else:
            return self.data[idx-offset:].copy()
