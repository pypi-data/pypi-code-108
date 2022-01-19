#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes de supervision ou de visualisation utilisant TensorBoard

Created on Sun Mar 22 11:59:21 2020

@author: Cyrile Delestre
"""

try:
    from torch.utils.tensorboard import SummaryWriter
except ModuleNotFoundError:
    raise ModuleNotFoundError(
            "Le module TensorBoard n'est pas installé : l'instruction "
            "torch.utils.tensorboard renvoit une erreur ModuleNotFoundError. "
            "Visitez la page du projet PyTorch pour savoir comment "
            "installer le package TorchVision qui comprend TensorBoard à "
            "destination de PyTorch. Ou installez directement TensorBoard "
            "via pip ou conda."
        )

from dataclasses import dataclass, field
from typing import Dict, Optional, Union, List, Tuple, Any

from numpy import ndarray, array, vectorize
from pandas import DataFrame
from torch import Tensor, zeros, from_numpy

from dstk.utils import shape_list

@dataclass
class Writer:
    r"""
    Classe d'instensiation TensorBoard qui permet d'écrire des données dans 
    TensorBoard en créant un logging TensorBoard.
    
    Parameters
    ----------
    :log_dir: Path directory où les fichiers de communication du programme 
        vers TensorBoard seront storé. Par défaut 
        chemin_courant/RUN/current_datetime_hostname qui change avec chaque 
        run.
    :comment: Ajoute un suffix au log_dir. Si log_dir est non None cet 
        argument ne sera pas pris en compte.
    :purge_step: Si le logging crache à l'étape T+X et redémarre à l'étape 
        T, tout événement qui ont un gloabl_step plus grand ou égual à X 
        seront purgé et caché dans TensorBoard.
    :max_queue: Taille de la queue d'évenement à stocker avec de pousser (add)
        vers le disque dur.
    :flush_secs: Temps de refraichissement ver les logs sur le disque dure.
    :filename_suffix: Suffix ajouter à tous les événements dans le répertoire
        log_dir.
    """
    log_dir: Optional[str]=None
    comment: str=''
    purge_step: Optional[int]=None
    max_queue: int=10
    flush_secs: int=120
    filename_suffix: str=''
    
    def get_writer(self):
        r"""
        Renvoit un logging TensorBoard.
        """
        return SummaryWriter(
            log_dir = self.log_dir,
            comment = self.comment,
            purge_step = self.purge_step,
            max_queue = self.max_queue,
            flush_secs = self.flush_secs,
            filename_suffix = self.filename_suffix
        )

@dataclass
class EmbeddingProjector:
    r"""
    Classe permettant de calculer dans TensorBoard en temps réel des 
    projecteurs dans des espaces embedded d'observations.
    
    Parameters
    ----------
    X : Union[ndarray, DataFrame, Tensor, List, Tuple]
        array like contenant les observations.
    y : Optional[Union[List,List[List], ndarray]]
        array like des labels associé à chaques observations.
    images : Optional[Union[Tensor, ndarray, List[Union[Tensor, ndarray]]]]
        images peut être de plusieur type :
            - Numpy Array ou Tensor de dimensions (N, C, H, W) avec N les 
                observation, C les channels de couleurs, H la taille et W la 
                largeur ;
            - List d'array ou de Tensor de dimension (C, H, W) ;
            - List d'array ou de Tensor de dimension (H, W).
    tag : str
        nom dans TensorBoard de l'embedding.
    kargs_writer : Dict[str, Any]
        dictionnaire d'argument pour le logging TensorBoard (voir la classe 
        Writer)
    """
    X: Union[ndarray, DataFrame, Tensor, List, Tuple]
    y: Optional[Union[List,List[List], ndarray]]=None
    image: Optional[Union[Tensor, ndarray, List[Union[Tensor, ndarray]]]]=None
    tag: str='default'
    kargs_writer: Dict[str, Any]=field(default_factory=dict)

    def __post_init__(self):
        self.writer = Writer(**self.kargs_writer).get_writer()

    def set_image(self,
                  image: Optional[Union[Tensor,
                                        ndarray,
                                        List[Union[Tensor, ndarray]]]]):
        r"""
        Permet de charger un set d'image associé aux observations.
        
        Parameters
        ----------
        image : Optional[Union[Tensor, ndarray, List[Union[Tensor, ndarray]]]]
            images peut être de plusieur type :
                - Numpy Array ou Tensor de dimensions (N, C, H, W) avec N les 
                    observation, C les channels de couleurs, H la taille et W 
                    la largeur ;
                - List d'array ou de Tensor de dimension (C, H, W) ;
                - List d'array ou de Tensor de dimension (H, W).
        """
        self.image = image
        return self

    def transform_image(self):
        r"""
        Tensorforme les images au bon format à savoir Tensor PyTorch de 
        dimensions (N, C, H, W).
        """
        image = None
        if self.image is not None:
            if isinstance(self.image, list):
                if isinstance(self.image[0], ndarray):
                    if len(self.image[0].shape) == 2:
                        dtype = from_numpy(self.image[0]).dtype
                        image = zeros(
                            (len(self.image), 1, *self.image[0].shape),
                            dtype = dtype
                        )
                        for ii, img in enumerate(self.image):
                            image[ii, 0, :, :] = from_numpy(img)
                    elif len(self.image[0].shape) == 3:
                        dtype = from_numpy(self.image[0]).dtype
                        image = zeros(
                            (len(self.image), *self.image[0].shape),
                            dtype = dtype
                        )
                        for ii, img in enumerate(self.image):
                            image[ii, :, :, :] = from_numpy(img)
                    else:
                        raise AttributeError(
                            "La dimension de l'image n'est pas comprise, "
                            "elle devrait soit être de 2 pour (H, W) ou de "
                            "3 pour (C, H, W). Mais elle est de "
                            f"{len(self.image[0].shape)}."
                        )
                elif isinstance(self.image[0], Tensor):
                    if len(self.image[0].shape) == 2:
                        image = zeros(
                            (len(self.image), 1, *self.image[0].shape),
                            dtype = self.image[0].dtype
                        )
                        for ii, img in enumerate(self.image):
                            image[ii, 0, :, :] = img
                    elif len(self.image[0].shape) == 3:
                        image = zeros(
                            (len(self.image), *self.image[0].shape),
                            dtype = self.image[0].dtype
                        )
                        for ii, img in enumerate(self.image):
                            image[ii, :, :, :] = img
                    else:
                        raise AttributeError(
                            "La dimension de l'image n'est pas comprise, "
                            "elle devrait soit être de 2 pour (H, W) ou de "
                            "3 pour (C, H, W). Mais elle est de "
                            f"{len(self.image[0].shape)}."
                        )
            if isinstance(self.image, ndarray):
                if len(self.image.shape) == 4:
                    image = from_numpy(self.image)
                else:
                    raise AttributeError(
                        "La dimension de la variable image n'est pas bonne, "
                        f"elle est de {len(self.image.shape)} alors qu'elle "
                        "devrait être de 4 avec (N, C, H, W)."
                    )
            if isinstance(self.image, Tensor):
                if len(self.image.shape) != 4:
                    raise AttributeError(
                        "La dimension de la variable image n'est pas bonne, "
                        f"elle est de {len(self.image.shape)} alors qu'elle "
                        "devrait être de 4 avec (N, C, H, W)."
                    )
        self.image = image
        return self

    def transform_X(self):
        r"""
        Transforme au format adéquate les observations.
        """
        if isinstance(self.X, DataFrame):
            self.X = self.X.values
        elif isinstance(self.X, list) and isinstance(self.X[0], list):
            self.X = array(self.X)
        elif not (isinstance(self.X, ndarray) or isinstance(self.X, Tensor)):
            raise AttributeError(
                f"L'attribue X est de type {type(self.X)}, alors qu'il "
                "devrait être soit du style Numpy Array, DataFrame ou "
                "liste de liste."
            )
        return self

    def transform_y(self):
        r"""
        Transforme en list de string les labels.
        """
        numpy_str = vectorize(
            pyfunc = lambda x: str(x),
            doc='Convert to str.',
            otypes=[str]
        )
        if isinstance(self.y, ndarray):
            self.y = numpy_str(self.y).ravel().tolist()
        elif isinstance(self.y, list):
            len_shape = len(shape_list(self.y))
            if len_shape == 2:
                self.y = [str(y[0]) for y in self.y]
            elif len_shape == 1:
                self.y = [str(y) for y in self.y]
            else:
                raise AttributeError(
                    "Si y est une liste elle doit être de dimension 1 ou 2 "
                    f"et non de dimension {len_shape}."
                )
        else:
            raise AttributeError(
                "y doit être de type Numpy Array ou liste de liste ou liste."
            )
        return self

    def push(self, global_step: Optional[int]=None, tag: Optional[str]=None):
        r"""
        Méthode permettant de pousser le projecteur dans TensorBard.
        
        Parameters
        ----------
        global_step : Optional[int]
            itération globale enregistrée
        tag : Optional[str]
            nom de l'embedding
        """
        if tag is None:
            tag = self.tag
        self.transform_X().transform_y().transform_image()
        self.writer.add_embedding(
            mat=self.X,
            metadata=self.y,
            label_img=self.image,
            global_step=global_step,
            tag=tag
        )

