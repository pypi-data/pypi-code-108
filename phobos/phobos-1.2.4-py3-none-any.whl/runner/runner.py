from typing import Tuple

from torch.distributed.distributed_c10d import group
from .scheduler import get_scheduler
from .optimizer import get_optimizer
from torch.autograd import Variable
from torch.utils.data.distributed import DistributedSampler
from phobos.loss import get_loss

from torch.utils.tensorboard import SummaryWriter
from copy import copy

import torch
import logging
import os
import torch.distributed as dist
import tqdm
import math


class Runner():
    """Runner class.

    Parameters
    ----------
    model : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
        model to train or validate.
    device : `torch.device <https://pytorch.org/docs/stable/tensor_attributes.html#torch.torch.device>`_
        device to move tensors to.
    train_loader : `torch.utils.data.DataLoader <https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader>`_
        dataloader to load training dataset.
    val_loader : `torch.utils.data.DataLoader <https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader>`_
        dataloader to load validation dataset.
    inputs : `phobos.io.InputCollection <https://github.com/granularai/phobos/blob/develop/phobos/io/input.py>`_
        object representing model's inputs
    outputs : `phobos.io.OutputCollection <https://github.com/granularai/phobos/blob/develop/phobos/io/output.py>`_
        object representing model's outputs
    optimizer : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ / `torch.optim <https://pytorch.org/docs/stable/optim.html>`_
        optimizer string / instance. Details of phobos supported optimizers `here <phobos.runner.optimizers.map.html>`_
    mode : `int <https://docs.python.org/3/library/functions.html#int>`_
        mode of model training, by default ``epoch``. runner supports ``epoch`` and ``batch`` modes
    verbose : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        flag to run model training in verbose / diagnostic mode
    scheduler : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ / `torch.optim.lr_scheduler <https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate>`_
        scheduler string / instance. Details of phobos supported schedulers `here <phobos.runner.schedulers.map.html>`_
    max_iters : `int <https://docs.python.org/3/library/functions.html#int>`_
        maximum number of iterations for model training. represents number of

        * epochs to train for ``epoch`` mode training
        * train dataset batches to process for ``batch`` mode training
    frequency : `int <https://docs.python.org/3/library/functions.html#int>`_
        train cycle frequency for ``batch`` mode training
    distributed : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        flag to represent if model is to train in distributed mode, by default ``False``
    optimizer_args : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of optimizer arguments
    scheduler_args : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of scheduler arguments
    polyaxon_exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
        polyaxon experiment.
    tensorboard_logging : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        flag to represent if results are to be logged in Tensorboard, by default ``True``

    Attributes
    ----------
    polyaxon_exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
        polyaxon experiment.
    model : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
        model to train or validate.
    device : `torch.device <https://pytorch.org/docs/stable/tensor_attributes.html#torch.torch.device>`_
        device to move tensors to.
    train_loader : `torch.utils.data.DataLoader <https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader>`_
        dataloader to load training dataset.
    val_loader : `torch.utils.data.DataLoader <https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader>`_
        dataloader to load validation dataset.
    mode : `int <https://docs.python.org/3/library/functions.html#int>`_
        mode of model training, by default ``epoch``. runner supports ``epoch`` and ``batch`` modes
    verbose : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        flag to run model training in verbose / diagnostic mode
    max_iters : `int <https://docs.python.org/3/library/functions.html#int>`_
        maximum number of iterations for model training. represents number of

        * epochs to train for ``epoch`` mode training
        * train dataset batches to process for ``batch`` mode training
    frequency : `int <https://docs.python.org/3/library/functions.html#int>`_
        train cycle frequency for ``batch`` mode training
    inputs : `phobos.io.InputCollection <https://github.com/granularai/phobos/blob/develop/phobos/io/input.py>`_
        object representing model's inputs
    outputs : `phobos.io.OutputCollection <https://github.com/granularai/phobos/blob/develop/phobos/io/output.py>`_
        object representing model's outputs
    optimizer : `torch.optim <https://pytorch.org/docs/stable/optim.html>`_
        optimizer instance
    scheduler : `torch.optim.lr_scheduler <https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate>`_
        scheduler instance
    distributed : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        flag to represent if model is to train in distributed mode, by default ``False``
    tboards : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map of Tensorboard SummaryWriters for logging

    Examples
    --------
    Parse properties configured in metadata YAML using a Grain instance

    >>> grain = Grain()
    >>> args = grain.parse_args_from_yaml('metadata.yaml')
    >>>

    Retrieve InputCollection and OutputCollection instances from Grain instance

    >>> inputs, outputs = grain.get_inputs_outputs()

    refer to Grain documentation for more details

    Create and load a dummy model 

    >>> class Dummy(nn.Module):
    ...     def __init__(self, n_channels, n_classes):
    ...         super(Dummy, self).__init__()
    ...         self.linear = nn.Linear(n_channels, n_classes)
    ... 
    ...     def forward(self, x):
    ...         x = x['inp']
    ...         x = self.linear(x).permute(0, 3, 1, 2)
    ...         x = torch.abs(x)
    ... 
    ...         map = {'out': x }
    ...         return map
    >>>
    >>> device = torch.device('cuda',args.gpu)
    >>> model = Dummy(1, 1).to(device=device)

    and dummy train and val loaders

    >>> class DummyPreloader(data.Dataset):
    ...     def __init__(self, patch_size, n_channels, n_classes, n_samples):
    ...         self.patch_size = patch_size
    ...         self.n_channels = n_channels
    ...         self.n_classes = n_classes
    ...         self.samples = n_samples
    ... 
    ...     def __getitem__(self, index):
    ...         imap = { 'inp': np.random.rand(self.patch_size, self.patch_size,
    ...                                self.n_channels) }
    ...         omap = { 'out' : np.ones((self.patch_size, self.patch_size)) }
    ... 
    ...         return imap, omap
    ... 
    ...     def __len__(self):
    ...         return self.samples
    >>>
    >>> train_set = DummyPreloader(patch_size=32,
    ...                            n_channels=1,
    ...                            n_classes=1,
    ...                            n_samples=5)
    >>> val_set = DummyPreloader(patch_size=32,
    ...                          n_channels=1,
    ...                          n_classes=16,
    ...                          n_samples=2)
    
    Use datasets map to create dataloaders

    >>> datasets = {'train': train_set, 'val': val_set }
    >>> 
    >>> loaders = getDataLoaders(
    ...     datasets=datasets,
    ...     batch_size=2,
    ...     num_workers=2,
    ...     load='full'
    ... )

    ``Note`` 
    
    keys ``inp`` and ``out`` used in model and dataset should be specified in metadata

    refer to MNIST examples for more clarity
    
    1. Create Runner instance using parsed arguments

    >>> runner = Runner(model=model,
    ...                 device=device,
    ...                 train_loader=loaders['train'],
    ...                 val_loader=loaders['val'],
    ...                 inputs=inputs,
    ...                 outputs=outputs,
    ...                 mode='epoch',
    ...                 max_iters=args.max_iters,
    ...                 optimizer=args.optimizer,
    ...                 optimizer_args=args.optimizer_args,
    ...                 scheduler=args.scheduler,
    ...                 scheduler_args=args.scheduler_args,
    ...                 )

    2. Pass ``batch`` related arguments to create Runner instance to train in ``batch`` mode: 

    >>> mode = 'batch'
    >>> frequency = 10
    >>> max_iters = 100
    >>>
    >>> runner = Runner(model=model,
    ...                 device=device,
    ...                 train_loader=loaders['train'],
    ...                 val_loader=loaders['val'],
    ...                 inputs=inputs,
    ...                 outputs=outputs,
    ...                 mode=mode,
    ...                 frequency=frequency,
    ...                 max_iters=max_iters,
    ...                 optimizer=args.optimizer,
    ...                 optimizer_args=args.optimizer_args,
    ...                 scheduler=args.scheduler,
    ...                 scheduler_args=args.scheduler_args,
    ...                 )

    these arguments can be configured in metadata YAML

    3. Set ``distributed`` flag to create Runner instance for distributed training

    >>> runner = Runner(model=model,
    ...                 device=device,
    ...                 train_loader=loaders['train'],
    ...                 val_loader=loaders['val'],
    ...                 inputs=inputs,
    ...                 outputs=outputs,
    ...                 mode='epoch',
    ...                 distributed=True,
    ...                 max_iters=args.max_iters,
    ...                 optimizer=args.optimizer,
    ...                 optimizer_args=args.optimizer_args,
    ...                 scheduler=args.scheduler,
    ...                 scheduler_args=args.scheduler_args,
    ...                 )

    4. Create optimizer and scheduler instances to be passed for Runner instance creation

    >>> optimizer = get_optimizer(key=args.optimizer, args=args.optimizer_args, model=model)
    >>> scheduler = get_scheduler(key=args.scheduler, args=args.scheduler_args, optimizer=optimizer)
    >>> runner = Runner(model=model,
    ...                 device=device,
    ...                 criterion=criterion,
    ...                 train_loader=loaders['train'],
    ...                 val_loader=loaders['val'],
    ...                 distributed=args.distributed,
    ...                 metrics=args.metrics,
    ...                 num_classes=args.num_classes,
    ...                 optimizer=optimizer,
    ...                 scheduler=scheduler,
    ...                 mode=args.mode,
    ...                 max_iters=args.max_iters
    ...                 )

    Details of optimizers and schedulers supported by phobos currently can be viewed `here <phobos.runner.optimizers.map.html>`_ and `here <phobos.runner.schedulers.map.html>`_ 
    
    Apart from this, custom optimizer (derived from :attr:`torch.optim`) and custom scheduler (derived from :attr:`torch.optim.lr_scheduler`) can also be passed for Runner instance creation.

    Runner instance created thus is used for model training and evaluation

    >>> for step, outputs in runner.trainer():
    ...     if runner.master():
    ...         print(f'step: {step}')
    ...         outputs.print()
    ... 
    ...         val_recall = outputs.headmap['out|val_metrics|recall']
    ...         if val_recall > best_val:
    ...             best_val = val_recall
    ...             cpt_path = os.path.join(args.weight_dir,
    ...                                     'checkpoint_epoch_'+ str(step) + '.pt')
    ...             state_dict = model.module.state_dict() if runner.distributed else model.state_dict()
    ...             torch.save(state_dict, cpt_path)

    """
    def __init__(self,
                model,
                device,
                train_loader,
                val_loader,
                inputs,
                outputs,
                optimizer,
                mode='epoch',
                verbose=False,
                scheduler=None,
                max_iters=0,
                frequency=0,
                distributed=False,
                optimizer_args={},
                scheduler_args={},
                polyaxon_exp=None,
                tensorboard_logging=True               
                ):
        self.polyaxon_exp = polyaxon_exp
        self.model = model
        self.device = device

        self.train_loader = train_loader
        self.val_loader = val_loader

        self.mode = mode
        self.verbose = verbose
        self.max_iters = max_iters
        self.frequency = frequency

        assert mode == 'epoch' or mode == 'batch', 'Enter the correct mode epoch/batch'                

        self.inputs = inputs
        self.outputs = outputs

        self.optimizer = self.get_runner_optimizer(optimizer, optimizer_args, model)        
        self.scheduler = self.get_runner_scheduler(scheduler, scheduler_args, self.optimizer)

        self.tboards = None

        self.distributed = distributed
        if self.distributed:
            self.set_distributed_params()

        if tensorboard_logging:
            self.tensorboard_logging = True
            if polyaxon_exp:
                tensorboard_path = os.path.join(polyaxon_exp.get_artifacts_path(), 'outputs/tensorboard')
            else:
                tensorboard_path = os.path.join(os.curdir, 'outputs/tensorboard')
            for dir_ in [tensorboard_path, os.path.join(tensorboard_path, 'train'), os.path.join(tensorboard_path, 'val')]:
                if not os.path.exists(dir_):
                    os.makedirs(dir_)
            
            tboard_train = SummaryWriter(log_dir=os.path.join(tensorboard_path, 'train'))
            tboard_val = SummaryWriter(log_dir=os.path.join(tensorboard_path, 'val'))
            
            self.tboards = {'train': tboard_train, 'val': tboard_val}

    def set_distributed_params(self):
        self.rank = dist.get_rank()
        self.world_size = dist.get_world_size()

    @staticmethod
    def distributed():
        """Initialize process group, default is nccl backend.
        """
        dist.init_process_group(backend='nccl')

    @staticmethod
    def local_testing():
        if 'POLYAXON_NO_OP' in os.environ:
            if os.environ['POLYAXON_NO_OP'] == 'true':
                return True
        else:
            return False

    def master(self):
        return (
            not self.distributed or Runner.local_testing()
            ) or (
                self.distributed and self.rank == 0
                )

    def get_runner_optimizer(self, optimizer, optimizer_args={}, model=None):
        if type(optimizer) == str:
            return get_optimizer(key=optimizer, args=optimizer_args, model=model)
        else:
            return optimizer

    def get_runner_scheduler(self, scheduler, scheduler_args={}, optimizer=None):
        if scheduler is not None:
            if type(scheduler) == str:
                return get_scheduler(key=scheduler, args=scheduler_args, optimizer=optimizer)
            else:
                return scheduler
        else:
            return None

    def tensorize_batch(self, inputs, labels):
        """Tensorize batch of input images and labels, and move them to gpu.

        Parameters
        ----------
        inputs : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map of input images batch
        labels : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map of input labels batch

        Returns
        -------
        inputs : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map of input images batch loaded in gpu
        labels : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map of input labels batch loaded in gpu
        """
        logging.debug("Enter tensorize_batch routine")

        for key in inputs:
            input = inputs[key]

            input = Variable(input)
            input = input.to(device=self.device).float()

            inputs[key] = input

        for key in labels:
            label = labels[key]

            label = Variable(label)
            label = label.to(device=self.device)

            labels[key] = label

        logging.debug("Exit tensorize_batch routine")

        return inputs, labels        

    def train_forward_backward(self, inputs, labels):
        """Performs forward propagation, loss evaluation
        and backward propagation while training model.

        Parameters
        ----------
        inputs : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map of tensorised batch of input images.
        labels : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map of tensorised batch of input labels.
        """
        # Zero the gradient
        logging.debug("Enter train_forward_backward routine")
        self.optimizer.zero_grad()

        self.model.train()

        # Get model predictions, calculate loss, backprop
        predictions = self.model(inputs)
        hlossmap = {}

        outputs = self.outputs
        for key in predictions:
            ptensor = predictions[key]
            ltensor = labels[key]

            head = outputs.heads[key]
            
            tlossmap = head.train_losses
            tmetmap = head.train_metrics

            tlosses = tlossmap(ptensor, ltensor)
            tmetrics = tmetmap(ptensor, ltensor)

            if head.combine:
                hloss = head.combine(tlosses)
            else:
                lkey = list(tlosses.keys())[0]
                hloss = tlosses[lkey]

            hlossmap[key] = hloss

        if outputs.combine:
            loss = outputs.combine(hlossmap)
        else:
            lkey = list(hlossmap.keys())[0]
            loss = hlossmap[lkey]

        loss.backward()
        self.optimizer.step()
        logging.debug("Exit train_forward_backward routine")

    def eval_forward(self, inputs, labels):
        """Performs forward propagation while evaluating model.

        Parameters
        ----------
        inputs : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map of tensorised batch of input images.
        labels : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map of tensorised batch of input labels.
        """
        # Get predictions and calculate loss
        logging.debug("Enter eval_forward routine")

        self.model.eval()

        predictions = self.model(inputs)

        hlossmap = {}

        outputs = self.outputs
        for key in predictions:
            ptensor = predictions[key]
            ltensor = labels[key]

            head = outputs.heads[key]
            
            vlossmap = head.val_losses
            vmetmap = head.val_metrics

            vlosses = vlossmap(ptensor, ltensor)
            vmetrics = vmetmap(ptensor, ltensor)

            if head.combine:
                hloss = head.combine(vlosses)
            else:
                lkey = list(vlosses.keys())[0]
                hloss = vlosses[lkey]

            hlossmap[key] = hloss

        if outputs.combine:
            loss = outputs.combine(hlossmap)
        else:
            lkey = list(hlossmap.keys())[0]
            loss = hlossmap[lkey]

        if self.scheduler:
            self.scheduler.step(loss)

        logging.debug("Exit eval_forward routine")
        
    def condRun(self, iteration):
        if iteration < self.max_iters:
            return True
        print("exiting")
        return False

    def train_epoch(self, iteration):
        """Executes a single training cycle

        Parameters
        ----------
        iteration : `int <https://docs.python.org/3/library/functions.html#int>`_
            current iteration

        Yields
        -------
        `int <https://docs.python.org/3/library/functions.html#int>`_
            next iteration
        """
        frequency = self.frequency

        while self.condRun(iteration):
            for inputs, labels in self.train_loader:
                inputs, labels = self.tensorize_batch(inputs, labels)

                self.train_forward_backward(inputs, labels)

                with torch.no_grad():
                    if self.mode == 'batch':
                        iteration += 1

                        self.outputs.compute(mode='batch', phase='train')

                        self.reduce_outputs()

                        if self.verbose:
                            print(f'step: {iteration}')
                            self.outputs.print()

                        self.log_outputs(iteration)

                        self.outputs.reset()

                        if not iteration % frequency:
                            yield iteration

            if self.mode == 'epoch':
                iteration += 1
                yield iteration

    def eval_epoch(self):
        """Executes a single validation cycle

        """
        for inputs, labels in self.val_loader:
            inputs, labels = self.tensorize_batch(inputs, labels)
            
            self.eval_forward(inputs, labels)
    
    def reduce_outputs(self):
        if self.distributed:
            outlist = [None for _ in range(self.world_size)]
            dist.all_gather_object(outlist, self.outputs, group=dist.group.WORLD)
            self.outputs.reduce(outlist, wsize=self.world_size)
            dist.barrier()

    def log_outputs(self, iteration):
        self.outputs.setHeadMap()
        
        if self.master():
            if self.polyaxon_exp:
                self.outputs.logPolyaxon(
                                        step=iteration,
                                        exp=self.polyaxon_exp)
            if self.tensorboard_logging:
                self.outputs.plotTensorboard(
                                            step=iteration,
                                            tboards=self.tboards)
        if self.distributed:
            dist.barrier()

    def trainer(self):
        """Trains model on dataset, and yields results for every cycle

        Yields
        ------
        `phobos.io.OutputCollection <https://github.com/granularai/phobos/blob/develop/phobos/io/output.py>`_
            OutputCollection instance containing cycle results
        """
        logging.debug("Enter train_model generator")

        iteration = 0

        for iteration in self.train_epoch(iteration):
            with torch.no_grad():
                self.eval_epoch()

                if self.mode == 'epoch':
                    self.outputs.compute(mode='epoch')
                elif self.mode == 'batch':
                    self.outputs.compute(mode='batch', phase='val')

                self.reduce_outputs()
                
                self.log_outputs(iteration)
                    
                if not self.distributed:
                    yield iteration, self.outputs
                elif self.rank == 0:
                    yield iteration, self.outputs

                self.outputs.reset()       

                if not self.condRun(iteration):
                    break