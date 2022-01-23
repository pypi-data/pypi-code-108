import torch
import logging


class EarlyStop():
    """EarlyStop Implementation to stop model training on metrics convergence

    Parameters
    ----------
    checkpoint : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        checkpoint location
    epoch : `int <https://docs.python.org/3/library/functions.html#int>`_, optional
        epoch threshold for metrics convergence and earlystop, by default 10
    delta : `float <https://docs.python.org/3/library/functions.html#float>`_, optional
        delta/difference threshold for metrics convergence and earlystop, by default 0.001
    min : `boolean <https://docs.python.org/3/library/functions.html#bool>`_, optional
        flag to minimize/maximize metrics for convergence, by default *True*

    Attributes
    ----------
    checkpoint : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        checkpoint location
    epoch : `int <https://docs.python.org/3/library/functions.html#int>`_
        epoch threshold for metrics convergence and earlystop
    delta : `float <https://docs.python.org/3/library/functions.html#float>`_
        delta/difference threshold for metrics convergence and earlystop
    min : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        flag to minimize/maximize metrics for convergence, by default *True*
    counter : `int <https://docs.python.org/3/library/functions.html#int>`_
        metrics convergence counter
    best_score : `float <https://docs.python.org/3/library/functions.html#float>`_
        best metrics score
    early_stop : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        early_stop flag. training to stop once this flag is set

    Examples
    --------
    EarlyStop simulation using a dummy model and mock metrics and checkpoint location

    >>> class Dummy(nn.Module):
    ...    def __init__(self, n_channels, n_classes):
    ...        super(Dummy, self).__init__()
    ...        self.linear = nn.Linear(n_channels, n_classes)
    ...
    ...    def forward(self, x):
    ...        x = self.linear(x).permute(0, 3, 1, 2)
    ...        return x
    >>>
    >>> model = Dummy(1, 1)
    >>> earlystop = EarlyStop(checkpoint='/tmp/checkpoint.pt', delta=0.0001)
    >>>
    >>> last_epoch = 1
    >>> for epoch in range(1, 100):
    ...     metric = 1 + math.exp(-epoch)
    ...     earlystop(metric, model)
    ...     if earlystop.early_stop:
    ...         last_epoch = epoch
    ...         break
    >>> last_epoch
    21
    """

    def __init__(self, checkpoint, epoch=10, delta=1e-3, min=True):
        self.min = min
        self.epoch = epoch
        self.delta = delta
        self.checkpoint = checkpoint

        self.counter = 0
        self.best_score = None
        self.early_stop = False

    def __call__(self, metric, model):
        logging.debug("Enter EarlyStop __call__ routine")
        score = - metric if self.min is True else metric

        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(model)
        elif abs(score - self.best_score) <= self.delta:
            self.counter += 1
            if self.counter >= self.epoch:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(model)
            self.counter = 0
        logging.debug("Exit EarlyStop __call__ routine")

    def save_checkpoint(self, model):
        """saves model checkpoint

        Parameters
        ----------
        model : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
            training model 
        """
        logging.debug("Enter EarlyStop save_checkpoint routine")
        torch.save(model.state_dict(), self.checkpoint)
        logging.debug("Exit EarlyStop save_checkpoint routine")
