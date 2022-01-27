from phobos.config import get_map, save_map
import logging

scheduler_map = get_map('scheduler')

def save_scheduler_map(dest):
    """Saves scheduler map in location ``dest`` as a json file

    This file can later be used to lookup phobos supported schedulers  

    Parameters
    ----------
    dest : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ 
        destination path

    Examples
    --------
    Save scheduler map in location ``/tmp``

    >>> save_scheduler_map('/tmp')
    
    """
    save_map(map=scheduler_map, name='scheduler', dest=dest)

def get_scheduler(key, args, optimizer):
    """Creates and returns a scheduler based on scheduler type and arguments.

    Parameters
    ----------
    key : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        type of scheduler instance
    args : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of scheduler parameters.
    optimizer : `torch.optim <https://pytorch.org/docs/stable/optim.html>`_
        optimizer instance.

    Returns
    -------
    `torch.optim.lr_scheduler <https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate>`_
        scheduler instance.

    Examples
    --------
    Create an optimizer instance using a dummy model and SGD parameters

    >>> class Dummy(nn.Module):
    ...     def __init__(self, n_channels, n_classes):
    ...         super(Dummy, self).__init__()
    ...         self.linear = nn.Linear(n_channels, n_classes)
    ...
    ...     def forward(self, x):
    ...         x = self.linear(x).permute(0, 3, 1, 2)
    ...         return x
    >>> model = Dummy(1, 1)
    >>> optim_key = 'sgd'
    >>> optim_args = {'lr': 0.1}
    >>> optimizer = get_optimizer(key=optim_key, args=optim_args, model=model)
    >>> optimizer
    SGD (
    Parameter Group 0
        dampening: 0
        lr: 0.1
        momentum: 0
        nesterov: False
        weight_decay: 0
    )

    Create a scheduler instance using optimizer instance and STEP scheduler parameters

    >>> sch_key = 'step'
    >>> sch_args = {'step_size': 30, 'gamma': 0.1}
    >>> scheduler = get_scheduler(key=sch_key, args=sch_args, optimizer=optimizer)
    >>> scheduler
    <torch.optim.lr_scheduler.StepLR object at 0x7f4597b94a60>

    This scheduler instance can be passed to runner for training.

    Click `here <phobos.scheduler.map.html>`_ to view details of schedulers supported by phobos currently.
    """
    logging.debug("Enter get_scheduler routine")
    scheduler = scheduler_map[key]
    args['optimizer'] = optimizer
    logging.debug("Exit get_scheduler routine")
    return scheduler(**args)


def set_scheduler(key, scheduler):
    """Allows: 

    * Addition of a new scheduler to scheduler map
    
    * Modification of existing scheduler definitions in scheduler map

    Parameters
    ----------
    key : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        type of scheduler instance
    scheduler : `torch.optim.lr_scheduler <https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate>`_
        scheduler class

    Examples
    --------
    Add a dummy scheduler to scheduler map

    >>> class DummyScheduler(torch.optim.lr_scheduler.StepLR):
    ...     def __init__(self, args):
    ...         super().__init__(**args)
    >>> key = 'dummy_steplr'
    >>> set_scheduler(key,DummyScheduler)

    This scheduler key can be passed to runner for training.

    Click `here <phobos.scheduler.map.html>`_ to view details of schedulers supported by phobos currently.
    """
    logging.debug("Enter set_scheduler routine")
    scheduler_map[key] = scheduler
    logging.debug("Exit set_scheduler routine")
