from inspect import getmodule

from phobos import __version__ as version
from phobos.io import InputCollection, OutputCollection
from phobos.runner import Runner

from yacs.config import CfgNode as CN
from yacs import config
from polyaxon.tracking import Run

import logging
import os
import collections
import yaml
import copy
import torch

config._VALID_TYPES = config._VALID_TYPES.union({Run, torch.device})

_VALID_TYPES = config._VALID_TYPES


class Grain(CN):
    """A class derived from class CfgNode from yacs to be used for:

    - validating config yaml properties
    
    - creating a python yacs object from yaml config file

    - loading arguments for models and logging model inputs
    
    - creating input and output collections based on:
        
        - yaml properties 
    
        - combine map (optional)

    The object formed thus is a nested YACS object wherein YAML keys are converted to multilevel keys/attributes.

    Parameters
    ----------
    polyaxon_exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
        polyaxon experiment
    *args : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        a non keyworded arguments' list.
    **kwargs : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        a keyworded arguments' list.
    
    Attributes
    ----------
    polyaxon_exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
        polyaxon experiment
    
    Examples
    --------
    1. Parsing dummy metadata YAML through a Grain instance
    
    >>> grain_exp = Grain()
    >>> args = grain_exp.parse_args_from_yaml('/tmp/metadata.yaml')
    >>> args.sensor
    'sentinel2'
    
    2. Load a dummy model through Grain instance
    
    >>> class DummyNet(nn.Module):
    ... def __init__(self, foo):
    ...     super(DummyNet, self).__init__()
    ...     self.layer = foo
    ...
    ... def forward(self, x):
    ...     return x
    >>>
    >>> grain_exp = Grain()
    >>> model = grain_exp.load_model(DummyNet, foo='bar')
    >>> model.layer
    'bar'

    3. Create input and output collection instances based on YAML properties

    >>> grain_exp = Grain()
    >>> args = grain_exp.parse_args_from_yaml('examples/training/mnist_single_multihead/metadata_sat4.yaml')
    >>> 
    >>> inputs, outputs = grain_exp.get_inputs_outputs()
    >>> len(outputs.heads)
    2

    4. Create a map of loss combination methods

    >>> finloss = lambda map: map['1']
    >>> getloss = lambda map: sum(map.values())/len(map)
    >>> 
    >>> combine = {
    ...     'all': finloss,
    ...     'heads': {
    ...         '1': getloss,
    ...         '2': getloss
    ...     }
    ... }

    use combine map and YAML properties for creation of collection instances

    >>> grain_exp = Grain()
    >>> args = grain_exp.parse_args_from_yaml('examples/training/mnist_single_multihead/metadata_sat4.yaml')
    >>> 
    >>> inputs, outputs = grain_exp.get_inputs_outputs(combine) 

    These collection instances are to be consumed later by dataloader and runner

    """

    def __init__(self, polyaxon_exp = None, *args, **kwargs):
        super(Grain, self).__init__(*args, **kwargs)
        self.version = version
        self.polyaxon_exp = polyaxon_exp
    
    def parse_args_from_yaml(self, yaml_file):
        """Populates and returns a grain instance using arguments from YAML config file

        Parameters
        ----------
        yaml_file : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ 
            path to YAML config file

        Returns
        -------
        `phobos.grain.Grain <https://github.com/granularai/phobos/blob/develop/phobos/grain/grain.py>`_
            grain instance

        """
        with open(yaml_file, 'r') as fp:
            _ = yaml.safe_load(fp.read())
            _ = Grain._create_config_tree_from_dict(_, key_list=[])
            super(Grain, self).__init__(init_dict = _)
            if self.polyaxon_exp:
                map = flatten(self, sep='-')
                self.polyaxon_exp.log_inputs(**map)
        
        self.device = torch.device("cpu",0)
        if torch.cuda.is_available() and self.num_gpus > 0:
            self.device = torch.device("cuda",0)

        if Runner.local_testing():
            self.distributed = False
        elif self.distributed:
            Runner.distributed()

        return self
    
    def get_inputs_outputs(self, combine_meta=None):
        """Generates and returns input and output collection objects

        based on YAML properties and a map of loss combination methods

        Parameters
        ----------
        combine_meta : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_, optional
            map of loss combination methods, by default None

        Returns
        -------
        inputs : `phobos.io.InputCollection <https://github.com/granularai/phobos/blob/develop/phobos/io/input.py>`_
            instance containing collection of input objects
        outputs : `phobos.io.OutputCollection <https://github.com/granularai/phobos/blob/develop/phobos/io/output.py>`_
            instance containing collection of output objects

        """
        inputs = InputCollection(ymeta=self.input)
        outputs = OutputCollection(
                                ymeta=self.output,
                                cmeta=combine_meta, 
                                device=self.device,
                                )
        
        return inputs, outputs

    def load_model(self, model_cls, **kwargs):
        """Log and instantiate a model with keyword arguments

        Parameters
        ----------
        model_cls : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
            A pytorch model class to instantiate.
        **kwargs : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            all model positional arguments

        Returns
        -------
        `object <https://docs.python.org/3/reference/datamodel.html#objects-values-and-types>`_
            pytorch model object created from keyword arguments.

        """
        logging.debug("Enter load_model routine")
        if self.polyaxon_exp:
            self._log_model(model_cls, **kwargs)
        logging.debug("Exit load_model routine")
        return model_cls(**kwargs)

    def _log_model(self, model_cls, **kwargs):
        """Log model inputs

        Parameters
        ----------
        model_cls : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
            A pytorch model class.
        **kwargs : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            all model positional arguments

        """
        logging.debug("Enter _log_model routine")
        model_module = getmodule(model_cls).__name__
        model_path = os.path.relpath(getmodule(model_cls).__file__)
        model_name = model_cls.__name__

        self.polyaxon_exp.log_inputs(model_path=model_path,
                                     model_name=model_name,
                                     model_module=model_module,
                                     model_args=kwargs)
        logging.debug("Exit _log_model routine")   

    @classmethod
    def _create_config_tree_from_dict(cls, dic, key_list):
        """
        Create a configuration tree using the given dict.
        Any dict-like objects inside dict will be treated as a new CfgNode.
        Args:
            dic (dict):
            key_list (list[str]): a list of names which index this CfgNode from the root.
                Currently only used for logging purposes.
        """
        dic = copy.deepcopy(dic)
        for k, v in dic.items():
            if isinstance(v, dict):
                # Convert dict to CfgNode
                dic[k] = CN(v, key_list=key_list + [k])
            else:
                # Check for valid leaf type or nested CfgNode
                _assert_with_logging(
                    _valid_type(v, allow_cfg_node=False),
                    "Key {} with value {} is not a valid type; valid types: {}".format(
                        ".".join(key_list + [str(k)]), type(v), _VALID_TYPES
                    ),
                )
        return dic

def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v)))
    return dict(items)

def _assert_with_logging(cond, msg):
    if not cond:
        logging.debug(msg)
    assert cond, msg

def _valid_type(value, allow_cfg_node=False):
    return (type(value) in _VALID_TYPES) or (
        allow_cfg_node and isinstance(value, CN)
    )
