#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Surcharge de certaines classes de transformations Scikit-Learn pour 
s'adapter au mieux aux DataFrame.

Created on Mon Nov 23 12:19:02 2020

@author: Cyrile Delestre
"""

from warnings import warn
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import (OneHotEncoder, KBinsDiscretizer,
                                   RobustScaler, QuantileTransformer)

from dstk.utils import check_dataframe

class OneHotEncoderPandas(OneHotEncoder):
    r"""
    One Hot-Encoder Scikit-Learn appliqué à une DataFrame.
    Pour plus détaille voir la doc :
    https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html
    
    Parameters
    ----------
    subset : list
        liste de colonnes à transformer
    drop_columns : bool
        Si on préserve ou supprimer les colonnes originales
    sep : str
        séparateur entre le nom de la colonne et la classe
    
    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> from dstk.features import OneHotEncoderPandas
    >>> 
    >>> test = pd.DataFrame(
    >>>     np.random.choice(['a', 'b', 'c', 'd'], size=10),
    >>>     columns=['tirage']
    >>> )
    >>> ohe = OneHotEncoderPandas(subset=['tirage'], drop_columns=False)
    >>> ohe.fit_transform(test)
      tirage  tirage__a  tirage__b  tirage__c  tirage__d
    0      b        0.0        1.0        0.0        0.0
    1      b        0.0        1.0        0.0        0.0
    2      d        0.0        0.0        0.0        1.0
    3      d        0.0        0.0        0.0        1.0
    4      c        0.0        0.0        1.0        0.0
    5      d        0.0        0.0        0.0        1.0
    6      c        0.0        0.0        1.0        0.0
    7      b        0.0        1.0        0.0        0.0
    8      a        1.0        0.0        0.0        0.0
    9      d        0.0        0.0        0.0        1.0
    
    Notes
    -----
    Les entrées du OneHotEncoder sont suseptible de dépendre de la version de 
    Scikit-Learn.
    """
    def __init__(self,
                 subset: list,
                 drop_columns: bool=True,
                 sep: str='__',
                 categories: str='auto',
                 drop: Optional[str]=None,
                 sparse: bool=False,
                 dtype: type=np.float64,
                 handle_unknown: str='error'):
        if not isinstance(subset, list):
            raise AttributeError(
                f"subset doit être une liste et non de type : {type(subset)}."
            )
        self.subset = subset
        self.drop_columns = drop_columns
        self.sep = sep
        if sparse:
            warn(
                "La version Pandas de OneHotEncoder ne peut pas fonctionner "
                "avec les matrices sparce. L'arguement sparse True est "
                "emplacé par False."
            )
            sparse = False
        super().__init__(
            categories=categories,
            drop=drop,
            sparse=sparse,
            dtype=dtype,
            handle_unknown=handle_unknown
        )

    def fit(self, X: pd.DataFrame, y: None=None):
        r"""\
        Méthode générique scikit-learn pour l'apprentissage.

        Parameters
        ----------
        X : pd.DataFrame
            Observations
        y : None
            pour être ISO avec Scikit-Learn
        """
        check_dataframe(X, columns_name=self.subset);
        super().fit(X[self.subset].values, y=None)
        return self

    def transform(self, X: pd.DataFrame):
        r"""\
        Méthode générique scikit-learn pour la transformation.

        Parameters
        ----------
        X : pd.DataFrame
            Observations
        """
        X = check_dataframe(X, columns_name=self.subset, copy=True)
        transfo = pd.DataFrame(
            super().transform(X[self.subset]),
            columns=[
                f"{self.subset[ii]}{self.sep}{cc}"
                    for ii, cat in enumerate(self.categories_)
                        for cc in cat
            ]
        )
        if self.drop_columns:
            X = X.drop(columns=self.subset)
        return pd.concat(
            [X.reset_index(drop=True), transfo.reset_index(drop=True)],
            axis=1
        )

class KBinsDiscretizerPandas(KBinsDiscretizer):
    r"""
    Discrétiseur KBinsDiscretizer appliqué à une DataFrame.
    Pour plus détaille voir la doc :
    https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.KBinsDiscretizer.html#sklearn.preprocessing.KBinsDiscretizer

    Parameters
    ----------
    subset : list
        liste de colonnes à transformer
    drop : bool
        Supression ou conservation des colonnes originales (seulement pour 
        encode onehot ou onehot-dense).
    sep : str
        séparateur entre le nom de la colonne et la classe (seulement pour 
        encode onehot ou onehot-dense).
    
    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> from dstk.features import KBinsDiscretizerPandas
    >>> 
    >>> test = pd.DataFrame(
    >>>     np.random.rand(10, 2)*99,
    >>>     columns=['age_1', 'age_2']
    >>> )
    >>> kdb = KBinsDiscretizerPandas(
    >>>     subset=['age_1', 'age_2'],
    >>>     drop=False,
    >>>     encode='onehot-dense',
    >>>     n_bins=2,
    >>>     strategy='kmeans'
    >>> )
    >>> kbd.fit_transform(test)
           age_1      age_2  age_1__0  age_1__1  age_2__0  age_2__1
    0   4.699553  14.819436       1.0       0.0       1.0       0.0
    1  81.369349  75.722283       0.0       1.0       0.0       1.0
    2  78.331536  62.132574       0.0       1.0       0.0       1.0
    3  70.266323  20.734727       0.0       1.0       1.0       0.0
    4  97.121698  66.319727       0.0       1.0       0.0       1.0
    5  56.710455  23.110782       0.0       1.0       1.0       0.0
    6  15.223127  77.464874       1.0       0.0       0.0       1.0
    7  62.688611  22.735150       0.0       1.0       1.0       0.0
    8  10.280744  56.422985       1.0       0.0       0.0       1.0
    9  58.044423  78.144402       0.0       1.0       0.0       1.0
    
    Notes
    -----
    Les entrées du OneHotEncoder sont suseptible de dépendre de la version de 
    Scikit-Learn.
    """
    def __init__(self,
                 subset: list,
                 drop: bool=True,
                 sep: str='__',
                 n_bins: int=5,
                 encode: str='onehot-dense',
                 strategy: str='quantile'):
        if not isinstance(subset, list):
            raise AttributeError(
                f"subset doit être une liste et non de type : {type(subset)}."
            )
        self.subset = subset
        self.drop = drop
        self.sep = sep
        if encode == 'onehot':
            warn(
                "La version Pandas de KNinsDiscretizer ne peut pas "
                "fonctionner avec les matrices sparce. L'arguement encode "
                "'onehot' est remplacé par 'onehot-dense'."
            )
            encode = 'onehot-dense'
        super().__init__(
            n_bins=n_bins,
            encode=encode,
            strategy=strategy
        )

    def fit(self, X: pd.DataFrame, y: None=None):
        r"""
        Méthode générique scikit-learn pour l'apprentissage.

        Parameters
        ----------
        X : pd.DataFrame
            Observations
        y : None
            pour être ISO avec Scikit-Learn
        """
        check_dataframe(X, columns_name=self.subset);
        super().fit(X[self.subset].values, y=None)
        return self

    def transform(self, X: pd.DataFrame):
        r"""
        Méthode générique scikit-learn pour la transformation.

        Parameters
        ----------
        X : pd.DataFrame
            Observations
        """
        X = check_dataframe(X, columns_name=self.subset, copy=True)
        if self.encode == 'ordinal':
            X[self.subset] = super().transform(X[self.subset])
        else:
            transfo = pd.DataFrame(
            super().transform(X[self.subset]),
            columns=[
                    f"{self.subset[ii]}{self.sep}{cc}"
                        for ii, cat in enumerate(self.n_bins_)
                            for cc in range(cat)
                ]
            )
            if self.drop:
                X = X.drop(columns=self.subset)
            X = pd.concat(
                [X.reset_index(drop=True), transfo.reset_index(drop=True)],
                axis=1
            )
        return X

class RobustScalerPandas(RobustScaler):
    r"""
    RobustScaler appliqué à une DataFrame.
    Pour plus détaille voir la doc :
    https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html

    Parameters
    ----------
    subset : list
        liste des colonnes à transformer
    
    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> from dstk.features import RobustScalerPandas
    >>> 
    >>> test = pd.DataFrame(
    >>>     np.random.randn(10,3)*99+50,
    >>>     columns=['val_1', 'val_2', 'val_3']
    >>> )
    >>> RobustScalerPandas(subset=['val_1', 'val_3']).fit_transform(test)
          val_1       val_2     val_3
    0  1.928098  -86.849620 -0.809872
    1  0.655437   75.359294 -0.069656
    2 -0.734671  128.554065  0.069656
    3  0.316941  -72.130564 -0.619062
    4 -0.360382  -91.138696 -1.058226
    5  2.583596    5.003472  0.339982
    6  0.611535  134.733492  1.357780
    7 -0.837148  156.824472  0.150562
    8 -0.316941  231.724600  0.266921
    9 -0.341011  -37.310851 -1.107859
    
    Notes
    -----
    Les entrées du OneHotEncoder sont suseptible de dépendre de la version de 
    Scikit-Learn.
    """
    def __init__(self,
                 subset: list,
                 with_centering: bool=True,
                 with_scaling: bool=True,
                 quantile_range: tuple=(25.0, 75.0),
                 copy: bool=False):
        self.subset = subset
        super().__init__(
            with_centering=with_centering,
            with_scaling=with_scaling,
            quantile_range=quantile_range,
            copy=copy
        )

    def fit(self, X: pd.DataFrame, y: None=None):
        r"""
        Méthode générique scikit-learn pour l'apprentissage.

        Parameters
        ----------
        X : pd.DataFrame
            Observations
        y : None
            pour être ISO avec Scikit-Learn
        """
        check_dataframe(X, columns_name=self.subset);
        super().fit(X[self.subset].values, y=None)
        return self

    def transform(self, X: pd.DataFrame):
        r"""
        Méthode générique scikit-learn pour la transformation.

        Parameters
        ----------
        X : pd.DataFrame
            Observations
        """
        X = check_dataframe(X, columns_name=self.subset, copy=True)
        X[self.subset] = super().transform(X[self.subset])
        return X

class QuantileTransformerPandas(QuantileTransformer):
    r"""
    QuantileTransformer appliqué à une DataFrame.
    Pour plus de détaille voir la doc :
    https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.QuantileTransformer.html#sklearn.preprocessing.QuantileTransformer

    Parameters
    ----------
    subset : list
        liste des colonnes à transformer
    
    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> from dstk.features import RobustScalerPandas
    >>> 
    >>> test = pd.DataFrame(
    >>>     np.random.randn(10,3)*99+50,
    >>>     columns=['val_1', 'val_2', 'val_3']
    >>> )
    >>> QuantileTransformerPandas(
    >>>     subset=['val_1', 'val_3'],
    >>>     n_quantiles=10
    >>> ).fit_transform(test)
          val_1       val_2     val_3
    0  0.888889  -86.849620  0.222222
    1  0.777778   75.359294  0.444444
    2  0.111111  128.554065  0.555556
    3  0.555556  -72.130564  0.333333
    4  0.222222  -91.138696  0.111111
    5  1.000000    5.003472  0.888889
    6  0.666667  134.733492  1.000000
    7  0.000000  156.824472  0.666667
    8  0.444444  231.724600  0.777778
    9  0.333333  -37.310851  0.000000
    
    Notes
    -----
    Les entrées du OneHotEncoder sont suseptible de dépendre de la version de 
    Scikit-Learn.
    """
    def __init__(self,
                 subset: list,
                 n_quantiles: int=1000,
                 output_distribution: str='uniform',
                 ignore_implicit_zeros: bool=False,
                 subsample: int=100000,
                 random_state: Optional[int]=None,
                 copy: bool=False):
        self.subset = subset
        super().__init__(
            n_quantiles=n_quantiles,
            output_distribution=output_distribution,
            ignore_implicit_zeros=ignore_implicit_zeros,
            subsample=subsample,
            random_state=random_state,
            copy=copy
        )

    def fit(self, X: pd.DataFrame, y: None=None):
        r"""
        Méthode générique scikit-learn pour l'apprentissage.

        Parameters
        ----------
        X : pd.DataFrame
            Observations
        y : None
            pour être ISO avec Scikit-Learn
        """
        check_dataframe(X, columns_name=self.subset);
        super().fit(X[self.subset].values, y=None)
        return self

    def transform(self, X: pd.DataFrame):
        r"""
        Méthode générique scikit-learn pour la transformation.

        Parameters
        ----------
        X : pd.DataFrame
            Observations
        """
        X = check_dataframe(X, columns_name=self.subset, copy=True)
        X[self.subset] = super().transform(X[self.subset])
        return X
