#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes Handler pour les différents type de connexion (SQLite,SQLAlchemy, 
Warp10, Artimon, etc.).

Created on Sat Apr 11 06:41:28 2020

@author: Cyrile Delestre
"""

import os
import shutil
import json
import logging
import sqlite3
from typing import List, Dict, Optional, Union
from datetime import datetime as dt

# Mapping des champs possibles d'un logging avec les type SQLite3
MAP_TYPE_HANDLER = dict(
    asctime = 'TEXT',
    created = 'REAL',
    filename = 'TEXT',
    funcName = 'TEXT',
    levelname = 'TEXT',
    levelno = 'TEXT',
    lineno = 'INTEGER',
    message = 'TEXT',
    module = 'TEXT',
    msecs = 'INTEGER',
    name = 'TEXT',
    pathname = 'TEXT',
    process = 'INTEGER',
    processName = 'TEXT',
    relativeCreated = 'REAL',
    thread = 'INTEGER',
    threadName = 'TEXT',
    engine = 'TEXT'
)


class HandlerBase(logging.Handler):
    r"""
    Classe de base permettant de créer un handler à partir d'une liste de 
    Handler.
    
    Parameters
    ----------
    format : List[str]
        liste des attributs du LogRecord qu'on souhaite récupérer et 
        stocker. Liste des attributs de LogRecord présentés à l'URL :
            https://docs.python.org/3/library/logging.html#logrecord-attributes
        asctime : str
            Timestamps de création du log interprétable 
            humainement ;
        created : float
            Timestamps de création du log ;
        filename : str
            Nom du fichier dans lequel a été appelé le logging ;
        funcName : str
            Nom de la fonction contenant l'appel du logging ;
        levelname : str
            Nom de level d'alerte ('DEBUG', 'INFO', 'WARNING', 'ERROR', 
            'CRITICAL') ;
        levelno : int
            Numérique associé au level d'alerte ;
        message : str
            Message envoyé par le logging (à définir par l'utilisateur) ;
        module : str
            Nom du module ;
        msecs : int
            Temps de création de LogRicord (en milliseconde) ;
        name : str
            Nom du logger (permet d'identifier les différents logger) ;
        pathname : str
            Chemin complet du fichier dans lequel a été appelé le logging (si 
            disponible);
        process : int
            Process ID (si disponible) ;
        processName : str
            Nom du process ID (si disponible) ;
        relativeCreated : float
            Temps en millisecondes de création de LogRecord, par rapport au 
            temps de chargement du module de logging ;
        thread : int
            Thread ID (si disponible) ;
        threadName : str
            Nom du thread ID (si disponible).
        La suite est composée des attributs de LogRecord créés
            engine : str
                Nom du moteur ('sqlite', 'sqlalchemy', Warp10, etc.).

    See also
    --------
    SQLiteHandler, SQLAlchemyHandler
    """
    def __init__(
        self,
        format: List[str]=['name', 'message']
    ) -> None:
        logging.Handler.__init__(self)
        self.format = format

    def _asctime(self, record: logging.LogRecord) -> None:
        r"""
        Méthode ajoutant au LogRecord l'attribut asctime qui est le timestamp
        (created) du log au format lisible.
        """
        record.asctime = (
            dt
            .fromtimestamp(record.created)
            .isoformat()
        )

    def _message(self, record: logging.LogRecord) -> None:
        r"""
        Méthode ajoutant au LogRecord l'attribut message qui est une copie de 
        l'attribut msg au format json encodé en UTF-8.
        """
        record.message = json.dumps(record.msg).encode('utf-8')

    def _engine(self, record: logging.LogRecord, engine: str) -> None:
        r"""
        Méthode ajoutant au LogRecord l'attribut engine.
        """
        record.engine = engine

    def _extract_format(self, record: logging.LogRecord) -> List[str]:
        r"""
        Méthode extrayant les informations du LogRecord sélectionnées par 
        l'attribut format.
        """
        rec = record.__dict__
        return list(map(lambda x: rec[x], self.format))


    def emit(self, record: logging.LogRecord) -> None:
        r"""
        Méthode d'envoi des logs à implémenter.
        """
        raise NotImplementedError(
            "Il faut implémenter la méthode emit(self, record) à la classe "
            f"{self.__name__} qui hérite de la classe HandlerBase."
        )


class SQLiteHandler(HandlerBase):
    r"""
    Classe permettant de créer un handler à partir d'une liste de Handler 
    vers une base SQLite.
    
    Parameters
    ----------
    path_sql : str
        chemin vers la base SQLite des logs.
    format : List[str]
        liste des attributs du LogRecord qu'on souhaite récupérer et stocker. 
        Liste des attributs de LogRecord présentés à l'URL :
            https://docs.python.org/3/library/logging.html#logrecord-attributes
        asctime : str
            Timestamps de création du log interprétable humainement ;
        created : float
            Timestamps de création du log ;
        filename : str
            Nom du fichier dans lequel a été appelé le logging ;
        funcName : str
            Nom de la fonction contenant l'appel du logging ;
        levelname : str
            Nom de level d'alerte ('DEBUG', 'INFO', 'WARNING', 'ERROR', 
            'CRITICAL') ;
        levelno : int
            Numérique associé au level d'alerte ;
        message : str
            Message envoyé par le logging (à définir par l'utilisateur) ;
        module : str
            Nom du module ;
        msecs : int
            Temps de création de LogRicord (en milliseconde) ;
        name : str
            Nom du logger (permet d'identifier les différents logger) ;
        pathname : str
            Chemin complet du fichier dans lequel a été appelé le logging (si 
            disponible);
        process : int
            Process ID (si disponible) ;
        processName : str
            Nom du process ID (si disponible) ;
        relativeCreated : float
            Temps en millisecondes de création de LogRecord, par rapport au 
            temps de chargement du module de logging ;
        thread : int
            Thread ID (si disponible) ;
        threadName : str
            Nom du thread ID (si disponible).
        La suite est composée des attributs de LogRecord créés
            engine : str
                Nom du moteur ('sqlite', 'sqlalchemy', etc.).
    base_name : str
        Nom de la base (par dégaut "logs").
    :**kargs_sql: arguments d'entrée au connecteur 
        SQLite3 :
            sqlite3.connect(path_sql, **kargs_sql)

    Examples
    --------
    Nous allons utiliser timer pour extraire les informations temporelles 
    d'éxécution d'une fonction.
    
    >>> import logging
    >>> from time import sleep
    >>> from dstk.metrics import SQLiteHandler, timer
    >>> 
    >>> # Création du logger
    >>> logging.basicConfig(
    >>>     level = logging.INFO,
    >>>     handlers = [
    >>>         SQLiteHandler(
    >>>             path_sql = 'metrics.log',
    >>>             format = ['asctime', 'name', 'message', 'threadName']
    >>>         )
    >>>     ]
    >>> )
    >>> logger = logging.getLogger('python.metrics.timer')
    
    >>> @timer(logger=logger, delta_time=True)
    >>> def function_test(a=1, b=1, sleep_time=0.5):
    >>>     r"Docstring de la fonction fonction_test"
    >>>     sleep(sleep_time)
    >>>     return a+b
    >>> 
    >>> function_test()
    2
    >>> function_test(2, 2)
    4
    
    Les logs sont stockés dans la base SQLite "metrics.log".
    
    >>> import sqlite3
    >>> from dstk.data import PandasSQL
    >>> 
    >>> log = PandasSQL(sqlite3.connect("metrics.log"))
    >>> 
    >>> log("SELECT asctime, name, threadName FROM logs;")
                          asctime                  name  threadName
    0  2020-04-13T13:31:06.973864  python.metrics.timer  MainThread
    1  2020-04-13T13:31:11.469728  python.metrics.timer  MainThread
    >>> 
    >>> log("SELECT message FROM logs;")
                                                 message
    0  {"name": "function_test", "dt": "0:00:00.500830"}
    1  {"name": "function_test", "dt": "0:00:00.500830"}

    See also
    --------
    SQLAlchemyHandler, timer, timer_class
    """
    def __init__(
        self,
        path_sql: str,
        format: List[str]=['name', 'message'],
        base_name: str='logs',
        **kargs_sql
    ) -> None:
        if 'msg' in format:
            raise AttributeError(
                "Ne pas utiliser l'attribut 'msg' qui est technique, mais "
                "utiliser plutôt l'attribut 'message'."
            )
        super().__init__(format = format)
        self.kargs_sql = kargs_sql
        self.path_sql = path_sql
        self.base_name = base_name
        conn = sqlite3.connect(path_sql, **kargs_sql)
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {self.base_name}("
                f"{', '.join([f'{cc} {MAP_TYPE_HANDLER[cc]}' for cc in self.format])}"
            ")"
        )
        conn.commit()
        conn.close()
        del conn

    def emit(self, record: logging.LogRecord) -> None:
        self._asctime(record)
        self._message(record)
        self._engine(record, 'sqlite')
        log_in = self._extract_format(record)
        conn = sqlite3.connect(self.path_sql, **self.kargs_sql)
        conn.execute(
            f"INSERT INTO {self.base_name}({', '.join(self.format)}) "
            f"VALUES({', '.join(len(self.format)*'?')})",
            log_in
        )
        conn.commit()
        conn.close()
        del conn


class SQLAlchemyHandler(HandlerBase):
    r"""
    Classe permettant de créer un handler à partir d'une liste de Handler 
    vers une base interfacée à SQLAlchemy.
    
    Parameters
    ----------
    path_sql : str
        URL de connexion SQLAlchemy. L'URL de connexion est définie par :
            "dialect+driver://usernam:password@host:port/database"
    format : List[str]
        liste des attributs du LogRecord qu'on souhaite récupérer et stocker. 
        Liste des attributs de LogRecord présentés à l'URL :
            https://docs.python.org/3/library/logging.html#logrecord-attributes
        asctime : str
            Timestamps de création du log interprétable humainement ;
        created : float
            Timestamps de création du log ;
        filename : str
            Nom du fichier dans lequel a été appelé le logging ;
        funcName : str
            Nom de la fonction contenant l'appel du logging ;
        levelname : str
            Nom de level d'alerte ('DEBUG', 'INFO', 'WARNING', 'ERROR', 
            'CRITICAL') ;
        levelno : int
            Numérique associé au level d'alerte ;
        message : str
            Message envoyé par le logging (à définir par l'utilisateur) ;
        module : str
            Nom du module ;
        msecs : int
            Temps de création de LogRicord (en milliseconde) ;
        name : str
            Nom du logger (permet d'identifier les différents logger) ;
        pathname : str
            Chemin complet du fichier dans lequel a été appelé le logging (si 
            disponible);
        process : int
            Process ID (si disponible) ;
        processName : str
            Nom du process ID (si disponible) ;
        relativeCreated : float
            Temps en millisecondes de création de LogRecord, par rapport au 
            temps de chargement du module de logging ;
        thread : int
            Thread ID (si disponible) ;
        threadName : str
            Nom du thread ID (si disponible).
        La suite est composée des attributs de LogRecord créés
            engine : str
                Nom du moteur ('sqlite', 'sqlalchemy', etc.).
    base_name : str
        Nom de la base (par dégaut "logs").
    **kargs_sql :
        arguments d'entrée au connecteur SQLAlchemy :
            sqlalchemy.create_engine(path_sql, **kargs_sql)

    Notes
    -----
    Cette classe nécessite SQLAlchemy, si ce package n'est pas présent dans 
    votre environnement il suffit d'ajouter le package "sqlalchemy" au fichier 
    environment.yml et de lancer le script bash bash_install_env.sh dans le 
    répertoire shell du projet.

    Examples
    --------
    Nous allons utiliser timer pour extraire les informations temporelles 
    d'éxécution d'une fonction et les stocker dans une table SQLite 
    interfacée par SQLAlchemy.
    
    >>> import logging
    >>> from time import sleep
    >>> from dstk.metrics import SQLAlchemyHandler, timer
    >>> 
    >>> # Création du logger
    >>> logging.basicConfig(
    >>>     level = logging.INFO,
    >>>     handlers = [
    >>>         SQLAlchemyHandler(
    >>>             path_sql = 'sqlite:///metrics.log',
    >>>             format = ['asctime', 'name', 'message', 'threadName']
    >>>         )
    >>>     ]
    >>> )
    >>> logger = logging.getLogger('python.metrics.timer')
    
    >>> @timer(logger=logger, delta_time=True)
    >>> def function_test(a=1, b=1, sleep_time=0.5):
    >>>     r"Docstring de la fonction fonction_test"
    >>>     sleep(sleep_time)
    >>>     return a+b
    >>> 
    >>> function_test()
    2
    >>> function_test(2, 2)
    4
    
    Les logs sont stockés dans la base SQLite "metrics.log".
    
    >>> import sqlite3
    >>> import dstk.data import PandasSQL
    >>> 
    >>> log = PandasSQL(sqlite3.connect("metrics.log"))
    >>>
    >>> log("SELECT asctime, name, threadName FROM logs;")
                          asctime                  name  threadName
    0  2020-04-13T13:31:06.973864  python.metrics.timer  MainThread
    1  2020-04-13T13:31:11.469728  python.metrics.timer  MainThread
    >>> 
    >>> log("SELECT message FROM logs;")
                                                 message
    0  {"name": "function_test", "dt": "0:00:00.500830"}
    1  {"name": "function_test", "dt": "0:00:00.500830"}

    See also
    --------
    SQLiteHandler, timer, timer_class
    """
    def __init__(
        self,
        path_sql: str,
        format: List[str]=['name', 'message'],
        base_name: str='logs',
        **kargs_sql
    ) -> None:
        try:
            global sqlalchemy
            import sqlalchemy
            from sqlalchemy.types import Integer, Float, String
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Le module SQLAlchemy n'est pas installé : l'instruction "
                "import sqlalchemy renvoit une erreur "
                "ModuleNotFoundError. Rajouter sqlalchemy dans les "
                "packages à installer dans le fichier environment.yml du "
                "projet."
            )
        if 'msg' in format:
            raise AttributeError(
                "Ne pas utiliser l'attribut 'msg' qui est technique, mais "
                "utiliser plutôt l'attribut 'message'."
            )
        super().__init__(format = format)
        self.path_sql = path_sql
        self.kargs_sql = kargs_sql
        self.base_name = base_name
        map_type = dict(
            TEXT = String(258),
            INTEGER = Integer(),
            REAL = Float()
        )
        engine = sqlalchemy.create_engine(path_sql, **kargs_sql)
        with engine.connect() as conn:
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {self.base_name}("
                    f"{', '.join([f'{cc} {map_type[MAP_TYPE_HANDLER[cc]]}' for cc in self.format])}"
                ")"
            )
        del engine

    def emit(self, record: logging.LogRecord) -> None:
        self._asctime(record)
        self._message(record)
        self._engine(record, 'sqlalchemy')
        log_in = self._extract_format(record)
        engine = sqlalchemy.create_engine(self.path_sql, **self.kargs_sql)
        with engine.connect() as conn:
            conn.execute(
                f"INSERT INTO {self.base_name}({', '.join(self.format)}) "
                f"VALUES({', '.join(len(self.format)*'?')})",
                log_in
            )
        del engine


class BaseArtimon(HandlerBase):
    r"""
    Classe de base permettant de gérer les données à envoyer dans Warp10 
    via Artimon. Cette classe n'est pas à utiliser directement, elle est 
    utiliser en tant que classe mère aux classes ArtimonAPIHandler et 
    ArtimonLocalHandler.

    Parameters
    ----------
    producer : str
        Nom du producer vers lequel les métriques seront envoyées. Il doit 
        avoir la forme <code_boite>.<nom_appli>
    hostname : Optional[str]
        nom facultatif du hostname (si non renseigné sera complété 
        automatiquement par Artimon).
    environment : Optional[str]
        nom facultatif de l'environnement (si non renseigné sera complété 
        automatiquement par Artimon).
    labels : Optional[Dict[str, Union[float, int, str]]]
        label en complément de la métrique (comme l'environnement, la version,
        etc.). Dans Artimon les labels sont références aux tags.
    format : List[str]
        liste des attributs du LogRecord qu'on souhaite récupérer et 
        stocker. Liste des attributs de LogRecord présentés à l'URL :
            https://docs.python.org/3/library/logging.html#logrecord-attributes
        asctime : str
            Timestamps de création du log interprétable humainement ;
        created : float
            Timestamps de création du log ;
        filename : str
            Nom du fichier dans lequel a été appelé le logging ;
        funcName : str
            Nom de la fonction contenant l'appel du logging ;
        levelname : str
            Nom de level d'alerte ('DEBUG', 'INFO', 'WARNING', 'ERROR', 
            'CRITICAL') ;
        levelno : int
            Numérique associé au level d'alerte ;
        message : str
            Message envoyé par le logging (à définir par l'utilisateur) ;
        module : str
            Nom du module ;
        msecs : int
            Temps de création de LogRicord (en milliseconde) ;
        name : str
            Nom du logger (permet d'identifier les différents logger) ;
        pathname : str
            Chemin complet du fichier dans lequel a été appelé le logging (si 
            disponible);
        process : int
            Process ID (si disponible) ;
        processName : str
            Nom du process ID (si disponible) ;
        relativeCreated : float
            Temps en millisecondes de création de LogRecord, par rapport au 
            temps de chargement du module de logging ;
        thread : int
            Thread ID (si disponible) ;
        threadName : str
            Nom du thread ID (si disponible).
        La suite est composée des attributs de LogRecord créés
            engine : str
                Nom du moteur ('sqlite', 'sqlalchemy', 'Warp10', etc.).

    See also
    --------
    ArtimonAPIHandler, ArtimonLocalHendleur
    """
    def __init__(
        self,
        producer: str,
        hostname: Optional[str]=None,
        environment: Optional[str]=None,
        labels: Optional[Dict[str, Union[float, int, str]]]=None,
        format: List[str]=['name', 'msg'],
    ) -> None:
        super().__init__(format = format)
        self.producer = producer
        self.hostname = hostname
        self.environment = environment
        self.labels = labels

    def parser(self, record: logging.LogRecord) -> str:
        name = record.name
        format = self.format
        if 'created' in self.format:
            format.remove('created')
        if 'name' in self.format:
            format.remove('name')
        if 'msg' in self.format:
            format.remove('msg')
        tags = {kk: record.__dict__[kk] for kk in format}
        if self.hostname:
            tags['hostname'] = self.hostname
        if self.environment:
            tags['environment'] = self.environnement
        if self.labels:
            for kk in self.labels:
                tags[kk] = self.labels[kk]
        message = [
            dict(
                i=dict(p=self.producer),
                m=dict(n=name, t=tags),
                v=record.msg,
                c=dict(t=int(round(record.created*1000)))
            )
        ]
        return json.dumps(message)

class ArtimonAPIHandler(BaseArtimon):
    r"""
    Classe permettant de créer un handler designné pour Artimon le parser 
    Warp10 du SI Arkéa. Elle utilise le protocal POST pour envoyer la donnée 
    dans Warp10.
    
    Parameters
    ----------
    producer : str
        nom du producer Artimon/Warp10.
    host : str
        host de l'API Artimon (par défaut '127.0.0.1').
    port : str
        port de l'API Artimon (par défaut '9023').
    hostname : Optional[str]
        nom facultatif du hostname (si non renseigné sera complété 
        automatiquement par Artimon).
    environment : Optional[str]
        nom facultatif de l'environnement (si non renseigné sera complété 
        automatiquement par Artimon).
    labels : Optional[Dict[str, Union[float, int, str]]]
        label en complément de la métrique (comme l'environnement, la version,
        etc.). Dans Artimon les labels sont références aux tags.
    format : List[str]
        liste des attributs du LogRecord qu'on souhaite récupérer et stocker. 
        Liste des attributs de LogRecord présentés à l'URL :
            https://docs.python.org/3/library/logging.html#logrecord-attributes
        asctime : str
            Timestamps de création du log interprétable humainement ;
        created : float
            Timestamps de création du log ;
        filename : str
            Nom du fichier dans lequel a été appelé le logging ;
        funcName : str
            Nom de la fonction contenant l'appel du logging ;
        levelname : str
            Nom de level d'alerte ('DEBUG', 'INFO', 'WARNING', 'ERROR', 
            'CRITICAL') ;
        levelno : int
            Numérique associé au level d'alerte ;
        message : str
            Message envoyé par le logging (à définir par l'utilisateur) ;
        module : str
            Nom du module ;
        msecs : int
            Temps de création de LogRicord (en milliseconde) ;
        name : str
            Nom du logger (permet d'identifier les différents logger) ;
        pathname : str
            Chemin complet du fichier dans lequel a été appelé le logging (si 
            disponible);
        process : int
            Process ID (si disponible) ;
        processName : str
            Nom du process ID (si disponible) ;
        relativeCreated : float
            Temps en millisecondes de création de LogRecord, par rapport au 
            temps de chargement du module de logging ;
        thread : int
            Thread ID (si disponible) ;
        threadName : str
            Nom du thread ID (si disponible).
        La suite est composée des attributs de LogRecord créés
            engine : str
                Nom du moteur ('sqlite', 'sqlalchemy', 'Warp10', etc.).

    Notes
    -----
    Avec cette classe il n'est pas possible d'utiliser le format "message", 
    il est important de ce référer à "msg" pour le message. De même il n'est 
    pas nécessaire de mettre "msg" dans l'argument format car le contenu du 
    message sera utilisé automatiquement comme argument de la série.
    
    Examples
    --------
    Envoi d'un timer mesurant de temps d'exécution d'une fonction et de sans 
    sortie.
    
    >>> import logging
    >>> from time import sleep
    >>> import numpy as np
    >>> from dstk.metrics import ArtimonAPIHandler, timer, sniffer
    >>> 
    >>> # Création du logger
    >>> logging.basicConfig(
    >>>     level = logging.INFO,
    >>>     handlers = [
    >>>         ArtimonAPIHandler(
    >>>             producer = 'NAME.producer',
    >>>             format = ['asctime', 'threadName']
    >>>         )
    >>>     ]
    >>> )
    >>> logger_timer = logging.getLogger('metrics.python.timer')
    >>> logger_sniffer = logging.getLogger('metrics.python.sniffer')
    
    >>> @timer(logger=logger_timer, delta_time=True)
    >>> @sniffer(logger=logger_sniffer)
    >>> def function_test(a=1, b=1, sleep_time=0.5):
    >>>     r"Docstring de la fonction fonction_test"
    >>>     sleep(sleep_time)
    >>>     return a+b
    
    >>> res = [
    >>>     function_test(a=ii, sleep_time=5*np.random.rand())
    >>>     for ii in range(10)
    >>> ]
    >>> res
    [1, 3, 4, 5, 6, 7, 8, 9, 10]
    
    Les données seront envoyés directement vers Warp10.
    
    See also
    --------
    ArtimonLocalHandler
    """
    def __init__(
        self,
        producer: str,
        host: str='127.0.0.1',
        port: str='9023',
        hostname: Optional[str]=None,
        environment: Optional[str]=None,
        labels: Optional[Dict[str, Union[float, int, str]]]=None,
        format: List[str]=['name', 'msg']
    ) -> None:
        try:
            global requests
            import requests
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Le module requests n'est pas installé : l'instruction "
                "import requests renvoit une erreur "
                "ModuleNotFoundError. Rajouter requests dans les "
                "packages à installer dans le fichier environment.yml du "
                "projet."
            )
        if 'message' in format:
            raise AttributeError(
                "Ne pas utiliser l'attribut 'message' qui est technique, mais "
                "utiliser plutôt l'attribut 'msg'."
            )
        super().__init__(
            format=format,
            producer=producer,
            hostname=hostname,
            environment=environment,
            labels=labels
        )
        self.host = host
        self.port = port
        self.url = f"http://{self.host}:{self.port}/metrics"

    def emit(self, record: logging.LogRecord) -> None:
        self._asctime(record)
        self._engine(record, 'artimon')
        response = requests.post(
            self.url,
            data = self.parser(record)
        )
        if response.status_code != 200:
            stat = int(response.status_code/100)
            if stat == 4 or stat == 5:
                raise IOError(
                    "Le retour du puch vers Warp10 à renvoyer une erreur. L'API "
                    f"a renvoyer le code {response.status_code}. "
                    f"Message d'erreur :\n{response.text}"
                )
            else:
                Warning(
                    "Le retour du puch vers Warp10 n'est pas 200 mais "
                    f"{response.status_code}. Message de retour :\n"
                    f"{response.text}"
                )

class ArtimonLocalHandler(BaseArtimon):
    r"""
    Classe permettant de créer un handler designné pour Artimon le parser 
    Warp10 du SI Arkéa. Elle utilise le collecteur Artimon qui doit être 
    installé en local. Le collecteur Artimon va cherche les fichiers 
    finissant par l'extention .artimon dans le répertoire par défaut 
    '/var/run/artimonV2'.
    
    Parameters
    ----------
    producer : str
        nom du producer Artimon/Warp10.
    path : str
        répertoire du dépot des métriques pour le collecteur Artimon (par 
        défaut '/var/run/artimonV2).
    hostname : Optional[str]
        nom facultatif du hostname (si non renseigné sera complété 
        automatiquement par Artimon).
    environment : Optional[str]
        nom facultatif de l'environnement (si non renseigné sera complété 
        automatiquement par Artimon).
    labels : Optional[Dict[str, Union[float, int, str]]]
        label en complément de la métrique (comme l'environnement, la version,
        etc.). Dans Artimon les labels sont références aux tags.
    time_life : int (**deprecated**)
        nombre de jour d'activité du fichier récoltant les métriques. Le
        collecteur Artimon supprime automatiquement les fichiers qui ont 7 
        jours d'inactivité (par défaut 1 jours).
    format : List[str]
        liste des attributs du LogRecord qu'on souhaite récupérer et stocker. 
        Liste des attributs de LogRecord présentés à l'URL :
            https://docs.python.org/3/library/logging.html#logrecord-attributes
        asctime : str
            Timestamps de création du log interprétable humainement ;
        created : float
            Timestamps de création du log ;
        filename : str
            Nom du fichier dans lequel a été appelé le logging ;
        funcName : str
            Nom de la fonction contenant l'appel du logging ;
        levelname : str
            Nom de level d'alerte ('DEBUG', 'INFO', 'WARNING', 'ERROR', 
            'CRITICAL') ;
        levelno : int
            Numérique associé au level d'alerte ;
        message : str
            Message envoyé par le logging (à définir par l'utilisateur) ;
        module : str
            Nom du module ;
        msecs : int
            Temps de création de LogRicord (en milliseconde) ;
        name : str
            Nom du logger (permet d'identifier les différents logger) ;
        pathname : str
            Chemin complet du fichier dans lequel a été appelé le logging (si 
            disponible);
        process : int
            Process ID (si disponible) ;
        processName : str
            Nom du process ID (si disponible) ;
        relativeCreated : float
            Temps en millisecondes de création de LogRecord, par rapport au 
            temps de chargement du module de logging ;
        thread : int
            Thread ID (si disponible) ;
        threadName : str
            Nom du thread ID (si disponible).
        La suite est composée des attributs de LogRecord créés
            engine : str
                Nom du moteur ('sqlite', 'sqlalchemy', 'Warp10', etc.).

    Notes
    -----
    Avec cette classe il n'est pas possible d'utiliser le format "message", 
    il est important de ce référer à "msg" pour le message. De même il n'est 
    pas nécessaire de mettre "msg" dans l'argument format car le contenu du 
    message sera utilisé automatiquement comme argument de la série.

    L'argument time_life n'est plus pris en compte et sera supprimé dans les 
    versions futures.

    Examples
    --------
    Envoi d'un timer mesurant de temps d'exécution d'une fonction et de sans 
    sortie.
    
    >>> import logging
    >>> from time import sleep
    >>> import numpy as np
    >>> from dstk.metrics import ArtimonLocalHandler, timer, sniffer
    >>> 
    >>> # Création du logger
    >>> logging.basicConfig(
    >>>     level = logging.INFO,
    >>>     handlers = [
    >>>         ArtimonLocalHandler(
    >>>             producer = 'NAME.producer',
    >>>             format = ['asctime', 'threadName']
    >>>         )
    >>>     ]
    >>> )
    >>> logger_timer = logging.getLogger('metrics.python.timer')
    >>> logger_sniffer = logging.getLogger('metrics.python.sniffer')
    
    >>> @timer(logger=logger_timer, delta_time=True)
    >>> @sniffer(logger=logger_sniffer)
    >>> def function_test(a=1, b=1, sleep_time=0.5):
    >>>     r"Docstring de la fonction fonction_test"
    >>>     sleep(sleep_time)
    >>>     return a+b
    
    >>> res = [
    >>>     function_test(a=ii, sleep_time=5*np.random.rand())
    >>>     for ii in range(10)
    >>> ]
    >>> res
    [1, 3, 4, 5, 6, 7, 8, 9, 10]
    
    Les données seront envoyés directement vers le fichier 
    date_du_jour.artimon dans le répertoire '/var/run/artimonV2'. C'est le 
    collecteur Artimon qui ce chargera de l'envoie vers Warp10.
    
    See also
    --------
    ArtimonAPIHandler
    """
    def __init__(
        self,
        producer: str,
        path: str='/var/run/artimonV2',
        hostname: Optional[str]=None,
        environment: Optional[str]=None,
        labels: Optional[Dict[str, Union[float, int, str]]]=None,
        format: List[str]=['name', 'msg']
    ) -> None:
        if 'message' in format:
            raise AttributeError(
                "Ne pas utiliser l'attribut 'message' qui est technique, mais "
                "utiliser plutôt l'attribut 'msg'."
            )
        super().__init__(
            format=format,
            producer=producer,
            hostname=hostname,
            environment=environment,
            labels=labels
        )
        self.path = path
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Le répertoire {path} n'existe pas."
            )

    def emit(self, record: logging.LogRecord) -> None:
        self._asctime(record)
        self._engine(record, 'artimon')
        file_name = (
            f"{self.path}{os.sep}{record.name.replace('.', '_')}_"
            f"{dt.now().strftime('%Y%m%d_%H:%M:%S:%f')}"
        )
        with open(f"{file_name}.tmp", 'w') as file:
            file.write(self.parser(record)+'\n')
        shutil.move(f"{file_name}.tmp", f"{file_name}.artimon")


class Warp10Handler(HandlerBase):
    r"""
    Classe de base permettant de créer un handler à partir d'une liste de 
    Handler vers une base interfacée à Warp10.
    """
    def __init__(
        self,
        token: str,
        host: str='127.0.0.1',
        port: str='8080',
        field_value: str='value',
        format: List[str]=['name', 'msg'],
        api_version: str='v0'
    ) -> None:
        try:
            global requests
            import requests
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Le module requests n'est pas installé : l'instruction "
                "import requests renvoit une erreur "
                "ModuleNotFoundError. Rajouter requests dans les "
                "packages à installer dans le fichier environment.yml du "
                "projet."
            )
        if 'message' in format:
            raise AttributeError(
                "Ne pas utiliser l'attribut 'message' qui est technique, mais "
                "utiliser plutôt l'attribut 'msg'."
            )
        if not isinstance(field_value, dict):
            raise AttributeError(
                "field_value doit être un dictionnaire avec comme clef le "
                "nom du logger et comme valeur le nom du champ ou la liste "
                "si plusieur champs."
            )
        super().__init__(format = format)
        self.headers = {
         'X-Warp10-Token': token
        }
        self.host = host
        self.port = port
        self.field_value = field_value
        self.api_version = api_version
        self.url = (
            f"http://{self.host}:{self.port}/api/{self.api_version}/update"
        )

    def emit(self, record: logging.LogRecord) -> None:
        self._asctime(record)
        self._engine(record, 'warp10')
        gts = GTS(record, self.field_value, self.format)
        response = requests.post(
            self.url,
            headers = self.headers,
            data = gts.commit()
        )
        if response.status_code != 200:
            raise IOError(
                "Le retour du puch vers Warp10 à renvoyer une erreur. L'API "
                f"a renvoyer le code {response.status_code}."
            )


class GTS:
    r"""
    Classe modélisant un objet GTS (Geo Time Series) Warp10.
    """
    def __init__(
        self,
        record: logging.LogRecord,
        dict_value: list,
        format: List[str]
    ) -> None:
        self.msg = record.msg.copy()
        field_value = dict_value[record.name]
        if isinstance(field_value, str):
            field_value = [field_value]
        if not all([ii in self.msg for ii in field_value]):
            raise IOError(
                "Le ou l'un des champs de field_value n'est ou ne sont pas "
                "présent(s) dans les données du message envoyées par le "
                f"logger qui sont :\n{', '.join(self.msg.keys())}."
            )
        self.format = format
        self.ts = f"{str(record.created).replace('.', '')[:16]:0<16}"
        self.name = record.name
        self.value = [self.msg.pop(ii) for ii in field_value]
        if 'created' in self.format:
            self.format.remove('created')
        if 'name' in self.format:
            self.format.remove('name')
        if 'msg' in self.format:
            self.format.remove('msg')
        log_att = record.__dict__
        self.log_att = list(map(lambda x: log_att[x], self.format))

    def commit(self) -> str:
        query = (
            f"{self.ts}// {self.name}"
            f"{{{','.join([f'{kk}={vv}' for kk, vv in zip(self.format, self.log_att)])}}}"
            f"{{{','.join([f'{kk}={vv}' for kk, vv in self.msg.items()])}}} "
        )
        if len(self.value) == 1:
            value = (
                f"'{self.value[0]}'"
                if isinstance(self.value[0], str) else
                f"{self.value[0]}"
            )
        else:
            value = (
                f"""[ {' '.join([(f"'{ii}'" if isinstance(ii, str) else f'{ii}') 
                for ii in self.value])} ]"""
            )
        return query+value
