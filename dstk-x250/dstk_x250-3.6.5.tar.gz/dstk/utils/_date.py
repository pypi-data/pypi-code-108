#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes et fonctions de traitement des dates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Created on Mon Nov 23 09:54:33 2020

@author: Cyrile Delestre
"""

from typing import Optional, Union
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

import pandas as pd

def date_sup(x: Union[str, dt], format: Optional[str]=None):
    r"""\
    Fonction calculant une date max du mois précédent à partir d'une date au 
    format format_date.
    
    Parameters
    ----------
    x : Union[str, datetime.datetime]
        datetime object ou str, date
    format : Optional[str]
        format de la date pour conversion si la date est un string.
    
    Returns
    -------
    Retourne le jour max du mois précédent au format datetime si x est un 
    objet datetime ou string si x est un objet string.
    
    Examples
    --------
    >>> from datetime import datetime
    >>> from dstk.utils import date_sup
    >>> 
    >>> date_sup('2020-02-15', '%Y-%m-%d')
    '2020-01-31'
    >>> 
    >>> date_sup(datetime(2020, 2, 15))
    datetime.datetime(2020, 1, 31, 0, 0)
    
    See also
    --------
    date_inf
    """
    if isinstance(x, str):
        return (
            dt.strptime(x, format).replace(day=1) 
            - relativedelta(days=1)
        ).strftime(format)
    elif isinstance(x, dt):
        return x.replace(day=1) - relativedelta(days=1)
    else:
        raise AttributeError(
            "La date x doit être soit de type datetime ou str et non de type "
            f"{type(x)}."
        )

def date_inf(x: Union[str, dt], nb_month: int, format: Optional[str]=None):
    r"""
    Fonction calculant la date du premier jour du mois d'il y a nb_month mois 
    à partir d'une date au format format_date.

    Parameters
    ----------
    x : Union[str, datetime.datetime]
        datetime object ou str, date
    nb_month : int
        nombre de mois
    format : Optional[str]
        format de la date pour conversion si la date est un string.
    
    Returns
    -------
    Retourne le jour min du (nb_month)-ième mois précédant la date au format 
    datetime si x est un objet datetime ou string si x est un objet string.
    
    Examples
    --------
    >>> from datetime import datetime
    >>> from dstk.utils import date_inf
    >>> 
    >>> date_inf('2020-02-15', 3, '%Y-%m-%d')
    '2019-11-01'
    >>> 
    >>> date_inf(datetime(2020, 2, 15), 3)
    datetime.datetime(2019, 11, 1)
    
    See also
    --------
    date_sup
    """
    if isinstance(x, str):
        return (
            dt.strptime(x, format).replace(day=1) 
            - relativedelta(months=nb_month)
        ).strftime(format)
    elif isinstance(x, dt):
        return x.replace(day=1) - relativedelta(months=nb_month)
    else:
        raise AttributeError(
            "La date x doit être soit de type datetime ou str et non de type "
            f"{type(x)}."
        )

def convert_date_dataframe(X: pd.DataFrame,
                           column_date: str,
                           format: Optional[str]=None):
    r"""
    Fonction permettant de convertir une colonne d'une DataFrame en objet 
    datetime.

    Parameters
    ----------
    X : pd.DataFrame
        DataFrame.
    columns_date : str
        noms de la colonne à convertir.
    format : Optional[str]
        format de date.
    """
    if X.shape[0] > 0 and isinstance(X[column_date].iloc[0], str):
            X[column_date] = pd.to_datetime(
                X[column_date],
                format = format
            )
    return X
