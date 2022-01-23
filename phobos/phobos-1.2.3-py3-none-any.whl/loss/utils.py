import logging
import inspect
import torch
import torch.nn as nn

from phobos.config import get_map, save_map

from .dice import DiceLoss
from .dice_spline import DiceSplineLoss
from .focal import FocalLoss
from .jaccard import JaccardLoss
from .binary_jaccard import BCEJaccardLoss
from .spline import SplineLoss
from .tversky import TverskyLoss
from .mse import MSELoss
from .mae import MAELoss
from .nll import NLL_Loss
from .ml_dice import MLDiceLoss

loss_cmap = {
    'diceloss': DiceLoss,
    'mldiceloss': MLDiceLoss,
    'focalloss': FocalLoss,
    'jaccardloss': JaccardLoss,
    'tverskyloss': TverskyLoss,
    'splineloss': SplineLoss,
    'dicesplineloss': DiceSplineLoss,
    'bcejaccardloss': BCEJaccardLoss,
    'mseloss': MSELoss,
    'maeloss': MAELoss,
    'nllloss': NLL_Loss
}

loss_map = get_map('loss')
loss_map.update(loss_cmap)

def save_loss_map(dest):
    """Saves loss map in location ``dest`` as a json file

    This file can later be used to lookup phobos supported losses  

    Parameters
    ----------
    dest : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ 
        destination path

    Examples
    --------
    Save loss map in location ``/tmp``

    >>> save_loss_map('/tmp')
    
    """
    save_map(map=loss_map, name='loss', dest=dest)

def get_loss(lconfig, cconfig):
    """Creates and returns a LossCollection instance based on loss config and common config maps. 

    This method is consumed in the OutputCollection creation pipeline.

    Parameters
    ----------
    lconfig : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        loss config map
    cconfig : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        common config map

    Returns
    -------
    `phobos.loss.LossCollection <https://github.com/granularai/phobos/blob/develop/phobos/loss/utils.py>`_
        LossCollection instance

    Examples
    --------
    Create a LossCollection object from loss and common config maps

    >>> lconfig = {
    ...     'tverskyloss': {
    ...         'alpha': 1,
    ...         'beta': 0.5
    ...     },
    ...     'diceloss': None
    ... }
    >>>    
    >>> cconfig = {}
    >>>
    >>> lmap = get_loss(lconfig, cconfig)
    >>> lmap
    LossCollection(
    (tverskyloss): TverskyLoss()
    (diceloss): DiceLoss()
    )
    
    """
    losslist = []
    for lkey in lconfig:
        linst = None

        if lkey in loss_map:
            lclass = loss_map[lkey]
            largs = lconfig[lkey]

            argslist = inspect.getfullargspec(lclass.__init__).args
            for ckey in cconfig:
                if ckey in argslist:
                    largs[ckey] = cconfig[ckey]

            if largs is None:
                linst = lclass()
            else:

                linst = lclass(**largs)

        losslist.append(linst)

    return LossCollection(losslist)

def set_loss(loss_str, loss):
    """Allows: 

    * Addition of a new loss to loss map
    
    * Modification of existing loss definitions in loss map

    Parameters
    ----------
    loss_str : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        string representing loss class
    loss : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
        loss class

    Examples
    --------
    Add an entry for a dummy loss to loss map:

    >>> class DummyLoss(DiceLoss):
    ...    def __init__(self):
    ...        super().__init__()
    ...    
    >>> lstr = 'dummyloss'
    >>> set_loss(lstr, DummyLoss)

    Add entry and config for this loss to loss config map

    >>> lconfig = {
    ...     'tverskyloss': {
    ...         'alpha': 1,
    ...         'beta': 0.5
    ...     },
    ...     'diceloss': None,
    ...     'dummyloss': None
    ... }  
    >>> cconfig = {}
    
    Create a LossCollection instance using loss and common configs

    >>> losses = get_loss(lconfig,cconfig)
    >>> losses
    LossCollection(
    (tverskyloss): TverskyLoss()
    (diceloss): DiceLoss()
    (dummyloss): DummyLoss()
    )

    This instance can later be used in training/validation cycles 

    Click `here <phobos.loss.map.html>`_ to view details of losses supported by phobos currently. 
    """
    logging.debug("Enter set_loss routine")

    loss_map[loss_str] = loss

    logging.debug("Exit set_loss routine")

class LossCollection(nn.ModuleDict):
    """Class representing a collection of losses

    Parameters
    ----------
    losslist : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list of losses in collection

    Attributes
    ----------
    state : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        state dictionary for individual losses

    Examples
    --------
    Given a map of loss configs

    >>> lconfig = {
    ...     'tverskyloss': {
    ...         'alpha': 1,
    ...         'beta': 0.5
    ...     },
    ...     'diceloss': None
    ... } 

    Create a list of loss objects

    >>> losslist = []
    >>> for key in lconfig:
    ...     largs = lconfig[key]
    ... 
    ...     if key in loss_map:
    ...         lclass = loss_map[key]
    ...         if largs is None:
    ...             linst = lclass()
    ...         else:
    ...             linst = lclass(**largs)
    ... 
    ...     losslist.append(linst)
    ... 

    Use this list to create a LossCollection instance

    >>> losses = LossCollection(losslist)
    >>> losses
    LossCollection(
    (tverskyloss): TverskyLoss()
    (diceloss): DiceLoss()
    )

    Compute individual loss for every train/val pass

    >>> pred = torch.rand(size=(2,1,32,32))
    >>> targ = torch.randint(0,2,size=(2,32,32))
    >>> 
    >>> lmap = losses(pred,targ)
    >>> lmap
    {'tverskyloss': tensor(0.6058), 'diceloss': tensor(0.5070)}

    Combine loss combinations after a cycle

    >>> means = losses.compute()

    Log compute results and reset loss states after cycle completion

    >>> losses.reset()

    """
    def __init__(self, losslist):
        super().__init__()
        self.state = {}
        
        self.add_losses(losslist)

    def add_losses(self, losslist):
        """Add loss instances in loss list to LossCollection

        Parameters
        ----------
        losslist : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
            loss list

        Raises
        ------
        ValueError
            LossCollection should not have redundant entries
        """
        for loss in losslist:
            lkey = loss.__class__.__name__
            if lkey in self:
                raise ValueError(f"Loss config had two losses both named {lkey}")
            self[lkey.lower()] = loss
            self.state[lkey.lower()] = []

    def forward(self, predicted, target):
        """Performs loss computation for predicted and ground truth tensors

        Parameters
        ----------
        predicted : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            predicted tensor
        target : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            ground truth tensor

        Returns
        -------
        `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map containing loss computation results
        """
        losses = {}
        for lkey, loss in self.items():
            lval = loss(predicted, target)

            losses[lkey] = lval
            self.state[lkey].append(lval)

        return losses

    def compute(self):
        """Combines loss computation results after a train/val cycle

        Returns
        -------
        `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map summarising overall loss after the cycle
        """
        return { lkey: torch.mean(torch.tensor(self.state[lkey])) for lkey in self.state }

    def reset(self):
        """Resets loss states 
        
        """
        for lkey in self.state:
            self.state[lkey] = []