#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes et fonctions liées à la gestion de bases SQL.

Created on Mon Nov 23 08:42:43 2020

@author: Cyrile Delestre
"""

import sqlite3
from typing import Union

import pandas as pd
import numpy as np
from tqdm import tqdm
from joblib import Parallel, delayed

def csv2sql(path_csv_or_df: Union[str, pd.DataFrame],
            path_sql: str,
            table_name: str,
            n_jobs: int=1,
            if_exists: str='append',
            **csv_opt):
    r"""
    Fonction permettant de convertir un fichier CSV en base SQLite3.
    La méthode permet de ne pas charger le CSV en RAM si ce dernier est 
    trop gros.
    
    Parameters
    ----------
    path_csv : Union[str, pd.DataFrame]
        chemin du csv ou DataFrame
    path_sql : str
        chemin de la base sql
    table_name : str
        nom de la table sql
    n_jobs : int
        nombre de jobs (gain si gros chunck), par défaut 1
    if_exists : str
        comportement si l'indice existe déjà dans la table sql. Peut être : 
        'fail', 'replace', 'append', par défaut 'append'
    **csv_opt :
        arguments de pandas.read_csv
    
    Examples
    --------
    Transfert d'un CSV trop gros pour être mis en RAM vers une base SQLite3.
    
    >>> from dstk.data import csv2sql
    >>> 
    >>> csv2sql(
    >>>     path_csv_or_df="data/mon_gros_csv.csv",
    >>>     path_sql="data/ma_table_sql.db",
    >>>     table_name="nom_de_ma_table",
    >>>     n_jobs=4,       # Nombre de jobs en parallèle
    >>>     chunksize=1000  # taille du chunker (1000 par 1000 ligne)
    >>> );
    
    Attention, dans notre cas ce sera 4 lignes qui seront stockées en RAM : 
    n_jobs*chunksize
    """
    if isinstance(path_csv_or_df, str):
        data = pd.read_csv(path_csv_or_df, **csv_opt)
    elif isinstance(path_csv_or_df, pd.DataFrame):
        data = path_csv_or_df
    else:
        raise AttributeError(
            "path_csv_or_df doit être soit un str ou une DataFrame, mais pas "
            f"{type(path_csv_or_df)}."
        )

    if "chunksize" in csv_opt.keys() and csv_opt["chunksize"] is not None:
        if isinstance(path_csv_or_df, str):
            with open(path_csv_or_df) as file:
                total = sum(1 for line in file)
        else:
            total = data.shape[0]

        @delayed
        def inser_sql(dd:pd.DataFrame):
            with sqlite3.connect(path_sql) as conn:
                dd.to_sql(
                    table_name,
                    conn,
                    if_exists = 'append',
                    index = False
                )

        with Parallel(n_jobs=n_jobs, backend='loky') as par:
            par(
                inser_sql(dd) for dd in tqdm(
                    data,
                    desc = "csv2sql",
                    total = int(np.ceil(total/csv_opt["chunksize"])),
                    miniters = 0.5
                )
            )
    else:
        with sqlite3.connect(path_sql) as conn:
            data.to_sql(
                table_name,
                conn,
                if_exists = if_exists,
                index = False
            )

def index_sql(path_sql: str,
              table_name: str,
              list_keys: list,
              index_name: str='idx',
              unique: bool=False):
    r"""
    Fonction créant un index pour une base SQLite. Créer un index peremet 
    d'accélérer grandement les filtres sur une base, car l'index est mise 
    en RAM.
    
    Parameters
    ----------
    path_sql : str
        chemin de la base sql
    table_name : str
        nom de la table sql
    list_keys: list
        list contenant les colonnes pour la génération de l'index
    index_name : str
        nom de l'index, par défaut 'idx'
    unique : bool
        si l'index est unique ou non, par défaut false
    
    Examples
    --------
    Je possède une base base.db et je sais que je vais de manière très 
    fréquente un filtrage sur la colonne A et B du type :
    
    >>> from dstk.data import PandasSQLite
    >>> 
    >>> arg1, arg2 = '...', '...'
    >>> with PandasSQLite("data/base.db") as db:
    >>>     data = db(
    >>>         "SELECT * FROM toto "
    >>>         f"WHERE A='{arg1}' AND B='{arg2}';"
    >>>     )
    
    Cette commande ira beaucoup plus vite si au préalable en aillant fait :
    
    >>> from dstk.data import index_sql
    >>> 
    >>> index_sql(
    >>>     path_sql="data/base.db",
    >>>     table_name="toto",
    >>>     list_keys=['A', 'B']
    >>> );
    
    Notes
    -----
    Commande à n'exécuter qu'une seule fois. Si plusieurs index sont créés 
    les noms 'index_name' douvent être uniques.
    """
    with sqlite3.connect(path_sql) as conn:
        cmd = (f"CREATE {'UNIQUE INDEX' if unique else 'INDEX'} {index_name} "
               f"ON {table_name}({', '.join(list_keys)});")
        cursor = conn.cursor()
        cursor.execute(cmd)
        conn.commit()
