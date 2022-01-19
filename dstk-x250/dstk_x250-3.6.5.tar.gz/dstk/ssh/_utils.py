#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Outils associés à la gestion SSH

Created on Sun Nov 22 12:20:19 2020

@author: Cyrile Delestre
"""

import re
from os.path import isdir

from tqdm import tqdm

def download_file(url: str,
                  file_path: str,
                  chunk_size: int=2*1024*1024,
                  header_name: str='file-name',
                  verbose: bool=True):
    r"""
    Fonction permettant de télécharger la donnée à partir d'une URL.
    
    Parameters
    ----------
    url : str
        chemin URL de la donnée.
    file_path : str
        chemin en local où la donnée téléchargé sera sauvegarder.
    chunk_size : int (=2*1024*1024)
        tronçons de traitement de la donnée (pour les données trop 
        volumineuses).
    header_name : str (='file-name')
        si file_path est un répertoire, récupère le nom de la donnée 
        directement dans les informations URL (si ce dernier existe).
    verbose : bool (=True)
        affiche une barre de progression.
    
    Notes
    -----
    Cette fonction est a utiliser de pair avec la méthode get_url_staging de 
    la classe ClientSSH. Elle permet ainsi récupérer de la donnée en local 
    directement depuis le répertoire de la cellule Hadoop.
    
    .. todo:: Améliorer la barre de progression et le débit qui est incorrecte.
    
    See also
    --------
    ClientSSH, get_url_staging
    """
    import requests
    from requests.structures import CaseInsensitiveDict
    r = requests.get(url, stream=True)
    query = requests.utils.urlparse(url).query
    params = CaseInsensitiveDict(x.split('=') for x in query.split('&'))
    file_path = re.sub('\/$','',file_path)
    file_name = ''
    if isdir(file_path) and header_name in params:
        file_name = params[header_name]
    if r.status_code == 200:
        if verbose:
            size = None
            if 'content-length' in r.headers:
                size = int(r.headers.get('content-length'))
            elif 'content-length' in params:
                size = int(r.headers.get('content-length'))
            _iter = tqdm(
                iterable = r.iter_content(chunk_size),
                desc = 'Download',
                total = size if size else None,
                unit = 'B',
                unit_scale=True,
                unit_divisor=1024
            )
        else:
            _iter = r.iter_content(chunk_size)
        with open(f"{file_path}/{file_name}", 'wb') as file:
            for chunck in _iter:
                file.write(chunck)
    else:
        IOError(
            f"La requètes get a eu pour code retour : {r.status_code}."
        )
