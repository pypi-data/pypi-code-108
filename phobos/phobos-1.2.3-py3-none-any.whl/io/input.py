class Input():
    """Class representing an input head of model

    Parameters
    ----------
    id : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        input head ID
    meta : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map containing input head configs

    Attributes
    ----------
    id : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        input head ID
    shape : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map representing input shape
    bands : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map containing information about input bands
    resolution : `float <https://docs.python.org/3/library/functions.html#float>`_
        input resolution
    transforms : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        config map of transforms to be applied in dataloader

    Examples
    --------
    Check InputCollection examples
    """
    def __init__(self, id, meta):
        self.id         = id
        self.shape      = meta['shape']
        self.bands      = meta['bands']
        self.sensor     = meta['sensor']
        self.resolution = meta['resolution']
        self.transforms = meta['transforms']

class InputCollection():
    """Class representing a collection of model's input heads

    Parameters
    ----------
    ymeta : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map containing all input head configurations, retrieved from YAML

    Attributes
    ----------
    heads : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map of Input instances and their head ids

    Examples
    --------
    Create an InputCollection instance from a sample config

    >>> inconfigs = {
    ...                 "heads": {
    ...                         "1": {
    ...                         "sensor": "NAIP",
    ...                         "resolution": 1,
    ...                         "shape": {
    ...                             "D": 1,
    ...                             "C": 4,
    ...                             "H": 28,
    ...                             "W": 28
    ...                         },
    ...                         "bands": {
    ...                             "Red": {
    ...                                 "min": 0,
    ...                                 "max": 1,
    ...                                 "std": 0.229,
    ...                                 "mean": 0.485
    ...                             },
    ...                             "Green": {
    ...                                 "min": 0,
    ...                                 "max": 1,
    ...                                 "std": 0.224,
    ...                                 "mean": 0.456
    ...                             },
    ...                             "Blue": {
    ...                                 "min": 0,
    ...                                 "max": 1,
    ...                                 "std": 0.225,
    ...                                 "mean": 0.406
    ...                             },
    ...                             "NIR": {
    ...                                 "min": 0,
    ...                                 "max": 1,
    ...                                 "std": 0.248,
    ...                                 "mean": 0.502
    ...                             }
    ...                         },
    ...                         "transforms": {
    ...                             "train": {
    ...                                 "normalize": None,
    ...                                 "verticalflip": {
    ...                                     "p": 0.5
    ...                                 },
    ...                                 "horizontalflip": {
    ...                                     "p": 0.5
    ...                                 }
    ...                             },
    ...                             "val": {
    ...                                 "normalize": None
    ...                             }
    ...                         }
    ...                     }
    ...                 }
    ...             } 
    >>>
    >>> inputs = InputCollection(ymeta=inconfigs)
    >>> len(inputs.heads)
    1

    This instance is later consumed by Runner
    """
    def __init__(self, ymeta):
        self.set_input_heads(ymeta)

    def set_input_heads(self, ymeta):
        """Creates Input instances for each of the heads configured in ``ymeta``

        and populates ``heads`` with a map of head IDs and corresponding Input instance

        Parameters
        ----------
        ymeta : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map containing all input head configurations, retrieved from YAML

        """
        idict = {}
        heads = ymeta['heads']
        for key in heads:
            idict[key] = Input(id=key, meta=heads[key])

        self.heads = idict  
