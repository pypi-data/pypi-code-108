#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes pour simplifier l'exploitation des bases SQL par Pandas.

Created on Mon Nov 23 09:23:52 2020

@author: Cyrile Delestre
"""

import sqlite3
from dataclasses import dataclass, field
from typing import Dict, Any, Union
from warnings import warn

import pandas as pd

@dataclass
class PandasSQL:
    r"""
    Classe de manipulation Pandas pour attaquer une base SQL. Gère toutes 
    les connexions aux bases de données compatibles avec la méthode Pandas
    pandas.read_sql_query :
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_sql_query.html

    Parameters
    ----------
    conn : sqlite3.Connection
        connecteur vers une base SQL.

    Notes
    -----
    Attention si vous utilisez la méthode close() le connecteur sera perdu. 
    Il fraudra alors réinstancier la classe PandasSQL avec un nouveau 
    connecteur.

    Attention cette classe n'est pas Picklelisable, car les connecteurs sont 
    des objets non binarisables. Dans ce cas utiliser PandasSQLite ou 
    PandasSQLAlchemy avec un context manager avec le mot clef "with".

    Examples
    --------
    >>> import sqlite3
    >>> from dstk.data import PandasSQL

    Si on considère une base SLQLite3 "base.db" dans le répertoire data du 
    projet et que cette base possède une table "base_name".

    >>> df = PandasSQL(sqlite3.connect("data/base.db"))
    >>> df("SELECT * FROM base_name;")
       field_name_1  field_name_2
    0             d             1
    1             e             2
    2             f             3

    >>> gen = df.gen_data("SELECT * FROM base_name;")
    >>> type(gen)
    >>> generator
    >>> next(gen)
    ('d', 1)

    >>> df.close()
    >>> df("SELECT * FROM base_name;")
    AttributeError: L'instance PandasSQL n'a pas de connecteur. 
    Ceci est peut-être du au fait que vous avez fermé la connexion avec la 
    méthode close.

    La classe PandasSQL n'est pas binarisable, elle est donc inutilisable 
    dans un context multi-processing (voir PandasSQLite ou PandasSQLAlchemy).

    >>> import pickle
    >>> df = PandasSQL(sqlite3.connect("data/base.db"))
    >>> pickle.dumps(df)
    TypeError: can't pickle sqlite3.Connection objects

    See also
    --------
    PandasSQLite, PandasSQLAlchemy
    """
    conn: sqlite3.Connection

    def __call__(self, cmd: str, **sql_ope):
        r"""
        Le call est un alise de read_data
        """
        return self.read_data(cmd=cmd, **sql_ope)

    def _conn_test(self):
        r"""
        Méthode privée de test de connexion.
        """
        if not hasattr(self, 'conn'):
            raise AttributeError(
                "L'instance PandasSQL n'a pas de connecteur. Ceci est "
                "peut-être du au fait que vous avez fermé la connexion "
                "avec la méthode close."
            )

    def read_data(self, cmd: str, **sql_opt):
        r"""
        Permet de lire les données à partir de la commande SQL cmd.

        Parameters
        ----------
        cmd : str
            commande SQL
        **sql_opt :
            arguments de pandas.read_sql_query

        Returns
        -------
        :df: DataFrame Pandas
        """
        self._conn_test()
        return pd.read_sql_query(cmd, self.conn, **sql_opt)
    
    def gen_data(self, cmd: str):
        r"""
        Générateur de la commande SQL. Attention en fonction du connecteur 
        cette méthode peut ne pas fonctionner. Il faudra alors la surcharger.

        Parameters
        ----------
        cmd : str
            commande SQL

        Returns
        -------
        :data: générateur
        """
        self._conn_test()
        cur = self.conn.cursor()
        cur.execute(cmd)
        gen = (data for data in cur.fetchall())
        cur.close()
        return gen

    def close(self):
        r"""
        Permet de fermer le connecteur SQL. Attention en fonction du 
        connecteur cette méthode peut ne pas fonctionner. Il faudra alors la 
        surcharger.
        """
        self._conn_test()
        self.conn.commit()
        self.conn.close()
        # del important sinon objet non Picklelisable
        del self.conn
    

class PandasSQLite(PandasSQL):
    r"""
    Classe de manipulation Pandas pour attaquer une base SQL. Utilise le 
    moteur SQLite3 de Python. Elle n'est compatible que SQLite mais ne 
    nécessite pas d'installation de package supplémentaire.

    Parameters
    ----------
    path_sql : Union[str, sqlite3.Connection]
        chemin vers une base SQLite3 (utilisation recommendé).
        Peut être également un connecteur SQLite3.
    kargs_sql : 
        arguments d'entrée au connecteur SQLite3 :
            sqlite3.connect(path_sql, **kargs_sql)

    Notes
    -----
    Contrairement à PandasSQL cette classe est binarisable car ne fait pas 
    d'effet de bord sur les connecteurs. Il faut l'utiliser dans un contexte 
    manager avec le mot clef "with".

    Attention si vous utilisez un connecteur SQLite3 a la place de d'un 
    chemin vers la base, l'objet n'est plus binarisable !

    Examples
    --------
    >>> from dstk.data import PandasSQLite

    Si on considère une base SLQLite3 "base.db" dans le répertoire data du 
    projet.

    >>> df = PandasSQLite("data/base.db")
    >>> 
    >>> with df:
    >>>     info = df.info_database()
    >>> info
    {'base_name': {'field_name_1': 'INTEGER'}, {'field_name_2': 'TEXT'}}

    >>> with df:
    >>>     out = df("SELECT * FROM base_name;")
    >>> out
       field_name_1  field_name_2
    0            31       janvier
    1            29       février
    2            31          mars

    >>> with df:
    >>>     gen = df.gen_data("SELECT * FROM base_name;")
    >>> type(gen)
    generator
    >>> next(gen)
    (31, 'janvier')

    Cette classe est bien binarisable.

    >>> import pickle
    >>> pickle.dumps(df)
    b'...'

    See also
    --------
    PandasSQL, PandasSQLAlchemy
    """ 
    def __init__(self, path_sql: Union[str, sqlite3.Connection], **kargs_sql):
        if isinstance(path_sql, sqlite3.Connection):
            self.conn = path_sql
            self.path_sql = path_sql
            warn(
                "Attention ! Vous utilisez comme arguement path_sql un "
                "connecteur SQLite3. Ce n'est pas l'utilisation recommendé. "
                "Vous ne pourrez par exemple pas paralléliser un process "
                "avec cette instanciation de PandasSQLite !"
            )
        else:
            self.path_sql = path_sql
        self.kargs_sql = kargs_sql
    
    def __enter__(self):
        r"""\
        Contexte de PandasSQL.
        """
        if not isinstance(self.path_sql, sqlite3.Connection):
            self.conn = sqlite3.connect(self.path_sql, **self.kargs_sql)
        return self

    def __exit__(self, error_type, error_value, error_traceback):
        r"""\
        Sortie du contexte.
        """
        if not isinstance(self.path_sql, sqlite3.Connection):
            self.close()

    def get_cursor(self):
        r"""\
        Renvoit un cursor si la connexion avec la base est établie.
        """
        self._conn_test()
        return self.conn.cursor()

    def info_database(self):
        r"""\
        Retourne sous un dictionnaire les informations de la base.
        
        Returns
        -------
        out : dict
            dict au format {table_name: {field_name: field_type}}
        """
        self._conn_test()
        cur = self.conn.cursor()
        info = {
            tt[0]: {
                ii[1]: ii[2] 
                for ii in cur.execute(
                    f"PRAGMA TABLE_INFO({tt[0]});"
                ).fetchall()
            }
            for tt in cur.execute(
                "SELECT name FROM sqlite_master WHERE type=='table';"
            ).fetchall()
        }
        cur.close()
        return info

class PandasSQLAlchemy(PandasSQL):
    r"""
    Classe de manipulation Pandas pour attaquer une base SQL. Utilise le 
    moteur SQLAlchemy. L'avantage de cette librairie est d'être compatible 
    avec beaucoup de bases de données.

    Parameters
    ----------
    path_sql : str
        URL de connexion SQLAlchemy. L'URL de connexion est définit par :
            "dialect+driver://usernam:password@host:port/database"
    kargs_sql : Dict[str, Any]
        arguments d'entrée au connecteur SQLAlchemy :
            sqlalchemy.create_engine(path_sql, **kargs_sql)

    Notes
    -----
    Contrairement à PandasSQL cette classe est binarisable car ne fait pas 
    d'effet de bord sur les connecteurs. Il faut l'utiliser dans un contexte 
    manager avec le mot clef "with".

    Cette classe nécessite SQLAlchemy, si ce package n'est pas présent dans 
    votre environnement il suffit d'ajouter le package "sqlalchemy" au fichier 
    environment.yml et de lancer le script bash bash_install_env.sh dans le 
    répertoire shell du projet.

    Examples
    --------
    >>> from dstk.data import PandasSQLAlchemy

    Si on considère une base SLQLite3 "base.db" dans le répertoire data du 
    projet.

    >>> df = PandasSQLAlchemy("sqlite:///data/base.db")
    >>> 
    >>> with df:
    >>>     info = df.info_database()
    >>> info
    {'base_name': {'field_name_1': 'TEXT'}, {'field_name_2': 'TEXT'}}

    >>> with df:
    >>>     out = df("SELECT * FROM base_name;")
    >>> out
       field_name_1  field_name_2
    0          riri        picsou
    1          fifi        donald
    2        loulou        mickey

    >>> with df:
    >>>     gen = df.gen_data("SELECT * FROM base_name;")
    >>> type(gen)
    generator
    >>> next(gen)
    ('riri', 'picsou')

    Cette classe est bien binarisable.

    >>> import pickle
    >>> pickle.dumps(df)
    b'...'

    See also
    --------
    PandasSQL, PandasSQLite
    """ 
    path_sql: str
    kargs_sql: Dict[str, Any] = field(default_factory=dict)
    
    def __init__(self, path_sql: str, **kargs_sql):
        try:
            global sqlalchemy
            import sqlalchemy
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Le module SQLAlchemy n'est pas installé : l'instruction "
                "import sqlalchemy renvoit une erreur "
                "ModuleNotFoundError. Rajouter sqlalchemy dans les "
                "packages à installer dans le fichier environment.yml du "
                "projet."
            )
        self.path_sql = path_sql
        self.kargs_sql = kargs_sql

    def __enter__(self):
        r"""
        Contexte de PandasSQL.
        """
        self.engine =  sqlalchemy.create_engine(
            self.path_sql,
            **self.kargs_sql
        )
        self.conn = self.engine.connect()
        return self

    def __exit__(self, error_type, error_value, error_traceback):
        r"""
        Sortie du contexte.
        """
        self.close()

    def get_engine(self):
        r"""
        Méthode qui permet de récupérer l'engine SQLAlchemy. Attention il 
        faut que la connection se fasse explicitement dans la classe 
        (path_sql non None et engine = 'sqlalchemy'.
        """
        if hasattr(self, 'engine'):
            return self.engine
        raise AttributeError(
            "Il n'y a pas d'engine SQLAlchemy dans cette instance de "
            "PandasSQLAlchemy."
        )

    def info_database(self):
        r"""
        Retourne sous un dictionnaire les informations de la base.
        
        Returns
        -------
        out : dict
            dict au format {table_name: {field_name: field_type}}
        """
        self._conn_test()
        import sqlalchemy
        metadata = sqlalchemy.MetaData()
        metadata.reflect(bind = self.engine)
        info = {
            tt: {
                ii.name: str(ii.type) 
                for ii in ff.columns
            }
            for tt, ff in metadata.tables.items()
        }
        return info

    def gen_data(self, cmd: str):
        r"""
        Générateur de la commande SQL.

        Parameters
        ----------
        cmd : str
            commande SQL

        Returns
        -------
        data : generator
            générateur sur la data en sortie de la commande appliqué sur la 
            base.
        """
        self._conn_test()
        res = self.conn.execute(cmd)
        return (data for data in res.fetchall())

    def close(self):
        r"""\
        Permet de fermer le connecteur SQL.
        """
        self._conn_test()
        self.conn.close()
        self.engine.dispose()
        # del important sinon objet non Picklelisable
        del self.engine, self.conn
