#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe pour client SSH.

Created on Sat Apr 11 06:41:28 2020

@author: Cyrile Delestre
"""

import logging
from os.path import dirname
from typing import List, Dict, Optional
from functools import reduce
from subprocess import run as sp_run

class ClientSSH:
    r"""
    Classe de connextion SSH permettant d'envoyer, exécuter et récupérer des 
    données sur un serveur distant (typiquement les bastions). La classe a 
    pour optique de faciliter le lancement de scipts Pig directement d'une 
    machine locale.
    
    Parameters
    ----------
    hostname : Optional[str]
        nom du hostname du serveur distant. Si cette valeur n'est pas 
        renseigné alors un promp pour demander le serveur souvrira dans 
        le terminal.
    username : Optional[str]
        nom de l'utilisateur pour identification. Si cette valeur n'est pas 
        renseigné alors uin prompt pour demander l'identifiant de 
        l'utilisateur souvrira dans le terminal.
    ssh_key : Optional[str]
        chemin vers la clef SSH privé. Si non reseigné un prompt s'ouvrira 
        pour demande le mot de passe associé au username.
    timeout : int
        timeout des commande SSH. ATTENTION : Une commande Pig peut être long. 
        Si pendant l'exécution le timeout est atteint et qu'il y a d'autre 
        instruction dans le script il y aura une erreur Python. Mais la 
        procédure Pig continura en fond sur la cellule Hadoop, sauf si le 
        terminal avec la session Python ce ferme.
    verbose : bool
        affiche le retour de la commande SSH.
    
    Notes
    -----
    La procédure standars pour lancer un scipt Pig est :
        
        1 : Envoyer le Pig sur un des bastions
        
        2 : Envoyer les données nécéssaire pour l'exécution du Pig sur 
        Bastion
        
        3 : Envoyer les données sur HDFS
        
        4 : Exécuter le scipt Pig
        
        5 : Récupérer les résultat sous Bastion
        
        6 : Les renvoyer en local
        
        7 : Supprimer les données de Bastion
        
    ou une alternative à l'étape 6 et 7 :
        
        5 bis : Envoyer sur staging
        
        6 bis : Récupérer les données directement depuis HDFS via le 
        staging
    
    Il existe dans la classe des procédures aggregant certaines de ces étapes.
    
    Si aucun ssh_key n'est renseigné alors un mot de passe sera demandé. Dans 
    un terminal bash ce mot de passe sera masqué, mais ce ne sera pas le cas 
    dans un terminal iPython (incompatible avec le masquage des inputs).
    
    Examples
    --------
    L'exemple suiviant consiste à mettre l'ensemble des fichiers jar et 
    script sur un serveur distant afin de permettre l'exécusion d'un script 
    pig. La commande pig serait équivalente à :
    ::
        pig -useHCatalog -f script.pig -p param_1="param_1" -p param_2=42 -p param_3="param_3"
    >>> from dstk.ssh import ClientSSH
    >>> 
    >>> # conf_ssh dictionnaire contenant les paramètres de connexions SSH
    >>> ssh = ClientSSH(**conf_ssh, verbose=False, timeout=10800)
    >>> 
    >>> # SCP d'un fichier vers un serveur distant
    >>> ssh.cp(local_path_file, server_path_file)
    >>> 
    >>> # SCP de plusieur script Pig vers un serveur distant
    >>> for script in all_script_path:
    >>>     ssh.cp(f"{local_path_script}{script}", server_path_file)
    >>> 
    >>> # SCP d'un repertoir local ver un serveur distant
    >>> ssh.cp(local_path_folder, server_path_folder, recursive=True)
    >>> 
    >>> # Upload sur la cellule Hadoop d'un fichier nécessaire à l'exécution 
    >>> # d'un script Pig
    >>> ssh.hadoop_put(f"{server_path}/data_input.csv")
    >>> 
    >>> # Exécution d'un script Pig qui utilise HCatalog pour une table Hive
    >>> ssh.pig(
    >>>     f"{server_path}/script.pig",
    >>>     params=dict(
    >>>         param_1='param_1',
    >>>         param_2=42,
    >>>         param_3='param_3'
    >>>     ),
    >>>     opt=['useHCatalog']
    >>> )
    >>> 
    >>> # Déconnexion au serveur
    >>> ssh.logout()
    
    See also
    --------
    download_file
    """
    def __init__(self,
                 hostname: Optional[str]=None,
                 username: Optional[str]=None,
                 ssh_key: Optional[str]=None,
                 timeout: int=30,
                 verbose: bool=False):
        try:
            global getpass
            import getpass
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Le module getpass n'est pas installé : l'instruction "
                "import getpass renvoit une erreur "
                "ModuleNotFoundError. Rajouter getpass dans les "
                "packages à installer dans le fichier environment.yml du "
                "projet."
            )
        try:
            global pxssh
            from pexpect import pxssh
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Le module pexpect n'est pas installé : l'instruction "
                "from pexpect import pxssh renvoit une erreur "
                "ModuleNotFoundError. Rajouter pexpect dans les "
                "packages à installer dans le fichier environment.yml du "
                "projet."
            )
        self.hostname = input('hostname: ') if hostname is None else hostname
        self.username = input('username: ') if username is None else username
        self.ssh_key = ssh_key
        self.timeout = timeout
        self.verbose = verbose
        self._connexion()

    def _connexion(self):
        try:
            self.conn = pxssh.pxssh(timeout=self.timeout)
            if self.ssh_key is None:
                password = getpass.getpass('password: ')
                self.conn.login(
                    server = self.hostname,
                    username = self.username,
                    password = password
                )
            else:
                self.conn.login(
                    server = self.hostname,
                    username = self.username,
                    ssh_key = self.ssh_key
                )
        except pxssh.ExceptionPxssh as e:
            print("La connexion pxssh a échouer.")
            print(e)

    def test_connexion(self):
        r"""
        Méthode permettant de tester la connexion SSH. Retourne la commande 
        'uptime'. Si la connexion est correctement établie retourne sur le 
        terminal le uptime du serveur, sinon retourne une erreur.
        """
        self.exe_cmd('uptime', True)
        return self

    def exe_cmd(self, cmd: str, verbose: Optional[bool]=None):
        r"""
        Méthode d'éxécution d'une commande sur le serveur distant.
        
        Parameters
        ----------
        cmd : str
            cammande (shell, bach, etc.) à exécuter.
        verbose : Optional[bool]
            affiche le retour de la commande. Si None utilise le paramétrage 
            par défaut de la classe ClientSSH.
        
        Examples
        --------
        La commande suivant retourne les fichiers contenue dans le repertoire 
        courant :
        >>> from dstk.ssh import ClientSSH
        >>> 
        >>> # conf_ssh dictionnaire contenant les paramètres de connexions SSH
        >>> ssh = ClientSSH(**conf_ssh, verbose=False, timeout=10800)
        >>> ssh.exe_cmd('ls', verbose=True)
        """
        verbose = verbose if verbose is not None else self.verbose
        self.conn.sendline(cmd)
        self.conn.prompt()
        if verbose:
            print(self.before())
        return self

    def before(self):
        r"""
        Permet de rendre interprétable dans Python les retours des prompts 
        ce produisant avec le timeout.
        """
        return self.conn.before.decode('utf-8').replace('\r\n', '\n')

    def after(self):
        r"""
        Permet de rendre interprétable dans Python les retours des prompts 
        ce produisant après le timeout.
        """
        return self.conn.after.decode('utf-8').replace('\r\n', '\n')

    def check_cmd(self):
        r"""
        Permet de récupérer le sortie d'une commande.
        """
        self.conn.sendline("echo $?")
        self.conn.prompt()
        return self.before().split('\n')[1]

    def pig(self,
            path_script: str,
            params: Dict[str, str]=dict(),
            opt: List[str]=[]):
        r"""
        Méthode d'exécution d'un script Pig.
        
        Parameters
        ----------
        path_scipt : str
            chemin sur le serveur distant du scipt Pig à exécuter
        params : Dict[str, str]
            dictionnaire de l'ensemble des paramètres à envoyer au srcipt Pig.
        opt : List[str]
            list d'option Pig.
        
        Examples
        --------
        L'exemple suivant est equivalent à lancer manuellement sur le serveur 
        distant la commande :
        ::
            pig -useHCatalog -f script.pig -p param_1="param_1" -p param_2=42 -p param_3="param_3"
        
        >>> from dstk.ssh import ClientSSH
        >>> 
        >>> # conf_ssh dictionnaire contenant les paramètres de connexions SSH
        >>> ssh = ClientSSH(**conf_ssh, verbose=False, timeout=10800)
        >>> ssh.pig(
        >>>     "script.pig",
        >>>     params=dict(
        >>>         param_1='param_1',
        >>>         param_2=42,
        >>>         param_3='param_3',
        >>>     ),
        >>>     opt=['useHCatalog']
        >>> )
        """
        query = "pig"
        if len(opt) > 0:
            for op in opt:
                query += f" -{op}"
        query += f" -f {path_script}"
        if len(params) > 0:
            for kk, vv in params.items():
                query += f' -p {kk}=\"{vv}\"'
        self.exe_cmd(query)
        return self

    def hadoop_put(self,
                   path_file_server: str,
                   path_file_hadoop: Optional[str]=None,
                   verbose: Optional[bool]=None,
                   if_exist: bool=True):
        r"""
        Permet de mettre un fichier du serveur distant vers la cellule 
        Hadoop.
        
        Parameters
        ----------
        path_file_server : str
            chemin du fichier sur le serveur distant.
        path_file_hadoop : Optional[str]
            chemin de destination sur la cellule Hadoop.
        verbose : Optional[bool]
            affiche le retour de commandes.
        if_exist : bool
            créé le répertoire sur la cellule Hadoop sur ce dernier n'éxiste 
            pas.
        """
        if path_file_hadoop is None:
            path_file_hadoop = "./"
        if if_exist:
            # Check si le réperoire existe
            path_hadoop = '/'.join(path_file_hadoop.split('/')[:-1])+'/'
            exist = (
                self.exe_cmd(f"hadoop fs -ls {path_hadoop}", False)
                .check_cmd()
            )
            if exist != '0':
                logging.warning(
                    f"Le répertoire {path_hadoop} sur la cellule Hadoop "
                    "n'existe pas. Création de cette dernière."
                )
                self.exe_cmd(f"hadoop fs -mkdir {path_hadoop}", False)
            # Check si le fichier existe
            file_name = path_file_hadoop.split('/')[-1]
            if file_name == '':
                file_name = path_file_server.split('/')[-1]
            exist = (
                self.exe_cmd(f"hadoop fs -ls {path_hadoop}{file_name}", False)
                .check_cmd()
            )
            if exist == '0':
                logging.warning(
                    f"Le fichier {file_name} existe déjà. "
                    "Suppression de ce dernier."
                )
                self.exe_cmd(f"hadoop fs -rmr {path_hadoop}{file_name}", False)
        query = f"hadoop fs -put {path_file_server} {path_file_hadoop}"
        self.exe_cmd(query, verbose)
        return self

    def hadoop_getmerge(self,
                        path_file_hadoop: str,
                        path_file_server: Optional[str]=None,
                        check_is_directory: bool=False,
                        verbose: Optional[bool]=None):
        r"""
        Permet de faire un getmerge de la cellule Hadoop vers un répertoire 
        du serveur distant.
        
        Parameters
        ----------
        path_file_hadoop : str
            chemin vers le répertoire Hadoop où sont stockés tous les segments 
            d'un même fichier. Fonctionne également si le chemin pointe vers 
            un simple fichier.
        path_file_server : Optional[str]
            chemin vers le fichier du serveur distant vers le quel seront 
            fusionné tous les sergments.
        check_is_directory : bool
            check si le chemin entré est un répertoire ou un fichier (par 
            défaut False). Pour une exécution plus rapide sans passer par ce 
            test finir le path_file_or_folder_hadoop par "/*" si on pointe 
            vers un répertoire évitant ainsi ce test.
        verbose : Optional[bool]
            affiche le retour de commandes.
        
        Notes
        -----
        Il est déconseillé généralement de passer par cette méthode de 
        récupération de donnée si le fichier en trop volumineux pouvant 
        saturer très rapidement l'espace disque du serveur distant. Pour les 
        gros fichier il est conseiller de stocker sur le répertoire staging 
        de la cellule et de passer par get_url_staging qui permet de créer 
        le chemin URL du fichier et d'utiliser 
        :func:`~dstk.ssh._utils.download_file`. Celà permet de passer de 
        Hadoop vers un machine local sans passer par le serveur distant.
        
        See also
        --------
        get_url_staging, :class:`~dstk.ssh._utils.download_file`
        """
        siz_file = 0
        if check_is_directory:
            query = f"hadoop fs -ls {path_file_hadoop}/"
            self.exe_cmd(query, False)
            siz_file = int(
                list(
                    filter(
                        lambda x: len(x) > 0,
                        self.before().split('\n')[1].split(' ')
                    )
                )[4]
            )
        query = f"hadoop fs -getmerge {path_file_hadoop}"
        if siz_file > 0 and check_is_directory:
            query += "/*"
        query = (
            query if path_file_server is None
            else query + f" {path_file_server}"
        )
        self.exe_cmd(query, verbose)
        return self

    def get_url_staging(self,
                        path_staging: str,
                        file_name: Optional[str]=None,
                        content_length: bool=True):
        r"""
        Méthode permettant de récuper l'URL d'un fichier (ou repertoire si 
        le fichier est segmenté) sur le staging de la cellule Hadoop.
        
        Parameters
        ----------
        path_staging : str
            chemin vers le répertoire du staging.
        file_name : Optional[str]
            nom du fichier que l'on souhaite récupérer (attention si None 
            descend l'ensemble de répertoire).
        content_length : bool
            Permet d'intégrer la taille du fichier dans l'URL permettant 
            d'avoir une bare de progression du téléchargement de la donnée 
            via :class:`~dstk.ssh._utils.download_file`.
        
        Notes
        -----
        Cette méthode est à utiliser avec le fonction 
        :func:`~dstk.ssh._utils.download_file` qui, a partir de l'URL généré, 
        télécharger la donnée depuis la cellule Hadoop directement vers 
        l'ordinateur local.
        
        See also
        --------
        :class:`~dstk.ssh._utils.download_file`
        """
        if not path_staging.startswith("/hdfs/staging/out/"):
            path = f"/hdfs/staging/out/{path_staging}"
        else:
            path = path_staging
        info = self.exe_cmd(f"hadoop fs -ls {path}").before()
        if self.check_cmd() != '0':
            raise IOError(f"Fichier {path} inexistant.")
        url = (
            "http://hadoop-manny-staging.s.arkea.com:8080/hadoop-staging/get"
            + path
        )
        if file_name is not None or content_length:
            url += "?"
        if file_name is not None:
            url += f"file-name={file_name}"
        if content_length:
            info = list(
                map(
                    lambda x: list(
                        filter(
                            lambda y: len(y) > 0,
                            x.split(' ')
                        )
                    ),
                    filter(
                        lambda x: len(x) > 0,
                        info.split("\n")
                    )
                )
            )
            length = reduce(lambda x,y: int(y[4])+x, info[1:], 0)
            if file_name is not None:
                url += "&"
            url += f"content-length={length}"
        return url

    def cp(self,
           file_path_local: str,
           file_path_server: Optional[str]=None,
           recursive: bool=False,
           if_exist: bool=True,
           verbose: Optional[bool]=None):
        r"""
        Méthode SCP (Secure CoPy) d'une machine local vers un serveur distant.
        
        Parameters
        ----------
        file_path_local : str
            chemin vers un fichier ou un répertoire local.
        file_path_server : Optional[str]
            chemin vers un répertoire sur le serveur distant.
        recursive : bool
            si file_path_local pointe vers un répertoire, permet de copié 
            récursivement les fichiers et répertoires contenu dans le 
            répertoire vers le serveur distant.
        if_exist : bool
            permet de tester si le répertoire sur le serveur distant existe, 
            s'il n'éxiste pas le crée.
        verbose : Optional[bool]
            affiche le retour de commandes.
        """
        verbose = verbose if verbose is not None else self.verbose
        option = "rp" if recursive else "p"
        if file_path_server is None:
            path_server = "./"
        else:
            path_server = file_path_server
        if if_exist:
            dir_server = dirname(file_path_server)
            exist = self.exe_cmd(f"ls {dir_server}").check_cmd()
            if exist == '2':
                logging.warning(
                    f"Le répertoire {dir_server} n'existe pas. "
                    "Création de ce dernier."
                )
                self.exe_cmd(f"mkdir {dir_server}")
        if isinstance(file_path_local, list):
            dquote = '"'
            file_path_local = f"{dquote}{' '.join(['a', 'b'])}{dquote}"
            path_server = dirname(file_path_server)
        query = [
            "scp",
            f"-{option}",
            file_path_local,
            f"{self.username}@{self.hostname}:{path_server}"
        ]
        output = sp_run(query)
        if verbose:
            print(output.stdout)
        return self

    def logout(self):
        r"""
        Déconnexion du client SSH.
        """
        self.conn.logout()
