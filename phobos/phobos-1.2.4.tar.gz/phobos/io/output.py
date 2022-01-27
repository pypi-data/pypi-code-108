from phobos.loss import get_loss
from phobos.metrics import get_metric

class Output():
    """Class representing an output head of model

    Parameters
    ----------
    id : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        output head ID
    meta : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map containing output head configs
    device : `torch.device <https://pytorch.org/docs/stable/tensor_attributes.html#torch.torch.device>`_
        model device
    combine : `func <https://docs.python.org/3/tutorial/classes.html#method-objects>`_
        method to combine losses computed for output head 

    Attributes
    ----------
    id : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        output head ID
    means : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map containing crunched statistics after a batch/epoch cycle
    logits : `boolean <https://docs.python.org/3/library/functions.html#bool>`_, optional
        flag representing type of input expected by MetricCollection instance, by default ``False``
    
        * ``True``  : logits based inputs
        * ``False`` : non logits based inputs

    combine : `func <https://docs.python.org/3/tutorial/classes.html#method-objects>`_
        method to combine losses computed for output head
    num_classes : `int <https://docs.python.org/3/library/functions.html#int>`_
        number of classes in output
    train_losses : `phobos.loss.LossCollection <https://github.com/granularai/phobos/blob/develop/phobos/loss/utils.py>`_
        object representing collection of training losses at output head
    train_metrics : `phobos.metrics.MetricCollection <https://github.com/granularai/phobos/blob/develop/phobos/metrics/metrics.py>`_
        object representing collection of training metrics at output head
    val_losses : `phobos.loss.LossCollection <https://github.com/granularai/phobos/blob/develop/phobos/loss/utils.py>`_
        object representing collection of validation losses at output head
    val_metrics : `phobos.metrics.MetricCollection <https://github.com/granularai/phobos/blob/develop/phobos/metrics/metrics.py>`_
        object representing collection of validation metrics at output head
    lossmap : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map of final losses after combination

    Examples
    --------
    Check OutputCollection examples
    """
    def __init__(self, id, meta, device, combine=None):
        self.id = id
        self.means = {}
        self.logits = meta['logits']
        self.combine = combine
        self.num_classes = meta['num_classes']
        
        self.train_losses  = get_loss(
                                lconfig=meta['loss'],
                                cconfig=self.getCommonParams()
                                )
        self.train_metrics = get_metric(
                                mconfig=meta['metrics'],
                                cconfig=self.getCommonParams(),
                                device=device,
                                logits=self.logits
                                )       
        self.val_losses    = get_loss(
                                lconfig=meta['loss'],
                                cconfig=self.getCommonParams()
                                )
        self.val_metrics   = get_metric(
                                mconfig=meta['metrics'],
                                cconfig=self.getCommonParams(),
                                device=device,
                                logits=self.logits
                                )

        self.lossmap = None

    def compute(self, mode, phase):
        """Combines losses' and metrics' computation results for output head after a train/val cycle

        Parameters
        ----------
        mode : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
            training mode. phobos supports following modes currently

            * ``epoch`` : epoch-wise model training
            * ``batch`` : batch-wise model training
        phase : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
            phase of a training cycle. by default ``train``. can take following values

            * ``train`` : training phase
            * ``val``   : validation phase
        """
        if mode == 'epoch':
            params = [self.train_metrics, self.train_losses, self.val_metrics, self.val_losses]
            keys   = ['train_metrics', 'train_loss', 'val_metrics', 'val_loss']
        elif mode == 'batch':
            if phase == 'train':
                params = [self.train_metrics, self.train_losses]
                keys = ['train_metrics', 'train_loss']
            elif phase == 'val':
                params = [self.val_metrics, self.val_losses]
                keys = ['val_metrics', 'val_loss']

        for i in range(len(params)):
            pmeans = params[i].compute()
            self.means[keys[i]] = { k: float(v) for k, v in pmeans.items() }

        if mode == 'epoch':
            if self.combine:
                trnloss = self.combine(self.means['train_loss'])
                valloss = self.combine(self.means['val_loss'])
            else:
                losskey = list(self.means['train_loss'].keys())[0]

                trnloss = self.means['train_loss'][losskey]
                valloss = self.means['val_loss'][losskey]

            self.lossmap = {'train_loss': trnloss, 'val_loss': valloss}
        elif mode == 'batch':
            if phase == 'train':
                if self.combine:
                    trnloss = self.combine(self.means['train_loss'])
                else:
                    losskey = list(self.means['train_loss'].keys())[0]
                    trnloss = self.means['train_loss'][losskey]

                self.lossmap = {'train_loss': trnloss}
            elif phase == 'val':
                if self.combine:
                    valloss = self.combine(self.means['val_loss'])
                else:
                    losskey = list(self.means['val_loss'].keys())[0]
                    valloss = self.means['val_loss'][losskey]

                self.lossmap = {'val_loss': valloss}                

    def reduce(self, outputlist, wsize):
        """Reduces metrics and losses from similar output heads in multiple nodes during distributed model training

        Parameters
        ----------
        outputlist : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
            list of similar output head instances in multiple nodes
        wsize : `int <https://docs.python.org/3/library/functions.html#int>`_
            node pool's world size
        """
        for mkey in self.means:
            if 'metric' not in mkey:
                for pkey in self.means[mkey]:
                    psum = 0 
                    for output in outputlist:
                        psum += output.means[mkey][pkey]

                    self.means[mkey][pkey] = psum/wsize

        for lkey in self.lossmap:
            losses = [outputs.lossmap[lkey] for outputs in outputlist]
            
            lsum = sum(losses)
            self.lossmap[lkey] = lsum/wsize

    def reset(self):
        """Resets metrics and loss states for output head

        """
        params = [self.train_metrics, self.train_losses, self.val_metrics, self.val_losses]
        for param in params:
            param.reset()

        self.means = {}
        self.lossmap = {}

    def getCommonParams(self):
        """Creates and returns a map of common parameters for all metrics and losses for output head

        Returns
        -------
        `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map of common parameters
        """
        cparams = {
            'id': self.id,
            'combine': self.combine,
            'num_classes': self.num_classes
        }
        return cparams

    def print(self):
        """Prints current statistics for output head

        """
        for mkey in self.means:
            print(f'\t{mkey}:')
            for pkey, pmean in self.means[mkey].items():
                print(f'\t\t{pkey}: {pmean}')

        for lkey in self.lossmap:
            print(f'\t{lkey} : {self.lossmap[lkey]}')


class OutputCollection():
    """Class representing a collection of model's output heads

    Parameters
    ----------
    ymeta : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map containing all output head configurations, retrieved from YAML
    device : `torch.device <https://pytorch.org/docs/stable/tensor_attributes.html#torch.torch.device>`_
        model device
    cmeta : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map containing references to loss combination logic for all output heads and for overall losses

    Attributes
    ----------
    lossmap : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map of final losses after combination
    combine : `func <https://docs.python.org/3/tutorial/classes.html#method-objects>`_
        method to combine losses computed for all output heads
    device : `torch.device <https://pytorch.org/docs/stable/tensor_attributes.html#torch.torch.device>`_
        model device
    heads : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map of Output instances and their head ids
    headmap : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map with overall model output statistics

    Examples
    --------
    Use a sample config

    >>> out_params = {
    ...             'heads': {
    ...                 '1': {
    ...                     'logits': True,
    ...                     'num_classes': 10,
    ...                     'metrics': {
    ...                         'precision': {
    ...                             'average': 'macro'
    ...                         },
    ...                         'recall': {
    ...                             'average': 'macro'
    ...                         }
    ...                     },
    ...                     'loss': {
    ...                         'crossentropyloss': None
    ...                     }
    ...                 },
    ...                 '2': {
    ...                     'logits': True,
    ...                     'num_classes': 10,
    ...                     'metrics': {
    ...                         'precision': {
    ...                             'average': 'macro'
    ...                         },
    ...                         'recall': {
    ...                             'average': 'macro'
    ...                             }
    ...                         },
    ...                     'loss': {
    ...                         'crossentropyloss': None
    ...                     }
    ...                 }
    ...             }
    ...         }

    a map containing references to logic combining losses within 
    
    individual output heads, as well as combining all output head losses

    ``Note`` 
    
    * In case individual heads have a single loss or model has a single output head, respective entry can be left blank

    * For training a single loss single head model, this argument can be skipped

    >>> comb = lambda x: sum(list(x.values()))/len(x)
    >>>
    >>> combine = {
    ...     'all': comb,
    ...     'heads': {
    ...         '1': comb,
    ...         '2': None
    ...     }
    ... }

    and model's device to create an OutputCollection instance

    >>> device = torch.device("cpu",0)
    >>> outputs = OutputCollection(ymeta=out_params,cmeta=combine, device=device)
    >>>

    Combine output statistics (metrics and losses) at the end of a train/val cycle

    >>> outputs.compute(mode='epoch')

    At master node in case of distributed training,
    
    combine results in OutputCollection instances from worker nodes

    >>> wsize = 32
    >>> outlist = [None for _ in range(wsize)]
    >>> dist.all_gather_object(outlist, outputs, group=dist.group.WORLD)
    >>> outputs.reduce(outlist, wsize)
    >>>

    print final results of a cycle

    >>> outputs.print()

    summarise results of cycle 

    >>> outputs.setHeadMap()

    use a map of tensorboard writers to log cycle's results to tensorboard

    >>> twriter = SummaryWriter(log_dir='/tmp')
    >>> vwriter = SummaryWriter(log_dir='/tmp')
    >>> map = {'train': twriter, 'val': vwriter}
    >>> cycle = 10
    >>>
    >>> outputs.plotTensorBoard(map, cycle)
    >>>

    use a polyaxon experiment to log cycle's results to polyaxon

    >>> outputs.logPolyaxon(cycle, exp)

    reset results to cycle after computation, printing and logging

    >>> outputs.reset()

    """
    def __init__(self, ymeta, device, cmeta=None):
        self.lossmap = {}

        if cmeta:
            self.combine = cmeta['all']
        else:
            self.combine = None
        self.device = device

        self.setOutputHeads(ymeta, cmeta)

    def setOutputHeads(self, ymeta, cmeta):
        """Creates Output instances for each of the heads configured in ``ymeta``

        and populates ``heads`` with a map of head IDs and corresponding Output instance

        Parameters
        ----------
        ymeta : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map containing all output head configurations, retrieved from YAML
        cmeta : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map containing references to loss combination logic for all output heads and for overall losses
        """
        if cmeta and cmeta['heads']:
            odict = {}
            yheads, cheads = ymeta['heads'], cmeta['heads']

            for key in yheads:
                if cheads[key]:
                    odict[key] = Output(id=key,
                                        meta=yheads[key],
                                        device=self.device,
                                        combine=cheads[key])
                else:
                    odict[key] = Output(id=key,
                                        meta=yheads[key],
                                        device=self.device
                                        )                    
        else:
            odict = {}
            yheads = ymeta['heads']

            for key in yheads:
                odict[key] = Output(id=key,
                                    meta=yheads[key],
                                    device= self.device
                                    )

        self.heads = odict

    def setHeadMap(self):
        """Internally summarises results of a cycle

        """
        map = {}
        for id, output in self.heads.items():
            for mkey in output.means:
                for pkey, pmean in output.means[mkey].items():
                    key = f'{id}|{mkey}|{pkey}'
                    map[key] = pmean

            for lkey in output.lossmap:
                key = f'{id}|{lkey}'
                map[key] = output.lossmap[lkey]

        for key in self.lossmap:
            map[key] = self.lossmap[key]

        self.headmap = map

    def compute(self, mode, phase='train'):
        """Combines  model's output statistics(metrics and losses) for a train/val cycle

        Parameters
        ----------
        mode : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
            training mode. phobos supports following modes currently

            * ``epoch`` : epoch-wise model training
            * ``batch`` : batch-wise model training
        phase : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
            phase of a training cycle. by default ``train``. can take following values

            * ``train`` : training phase
            * ``val``   : validation phase
        """
        for id, output in self.heads.items():
            output.compute(mode=mode, phase=phase)

        if mode == 'epoch':
            trnlossmap = {output.id: output.lossmap['train_loss'] for output in self.heads.values()}
            vallossmap = {output.id: output.lossmap['val_loss'] for output in self.heads.values()}

            if self.combine:
                trnloss = self.combine(trnlossmap)
                valloss = self.combine(vallossmap)
            else:
                losskey = list(trnlossmap)[0]

                trnloss = trnlossmap[losskey]
                valloss = vallossmap[losskey]            

            self.lossmap = {'train_loss': trnloss, 'val_loss': valloss}
        elif mode == 'batch':
            if phase == 'train':
                trnlossmap = {output.id: output.lossmap['train_loss'] for output in self.heads.values()}

                if self.combine:
                    trnloss = self.combine(trnlossmap)
                else:
                    losskey = list(trnlossmap)[0]
                    trnloss = trnlossmap[losskey]

                self.lossmap = {'train_loss': trnloss}
            elif phase == 'val':
                vallossmap = {output.id: output.lossmap['val_loss'] for output in self.heads.values()}

                if self.combine:
                    valloss = self.combine(vallossmap)
                else:
                    losskey = list(vallossmap)[0]
                    valloss = vallossmap[losskey]
                
                self.lossmap = {'val_loss': valloss}

    def reduce(self, outputslist, wsize):
        """Reduces results in OutputCollection instances from worker nodes during distributed model training

        Parameters
        ----------
        outputslist : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
            list of output collections from worker nodes
        wsize : `int <https://docs.python.org/3/library/functions.html#int>`_
            node pool's world size
        """
        for id, output in self.heads.items():
            outputlist = [outputs.heads[id] for outputs in outputslist]
            output.reduce(outputlist, wsize)

        for lkey in self.lossmap:
            losses = [outputs.lossmap[lkey] for outputs in outputlist]

            lsum = sum(losses)
            self.lossmap[lkey] = lsum/wsize

    def reset(self):
        """Resets final results of a cycle

        """
        for id, output in self.heads.items():
            output.reset()

        self.lossmap = {}
        self.headmap = {}

    def print(self):
        """Prints final results of a cycle

        """
        for id, output in self.heads.items():
            print(f'{id}:')
            output.print()

        for lkey in self.lossmap:
            print(f'{lkey}: {self.lossmap[lkey]}')

    def plotTensorboard(self, tboards, step):
        """Logs results of a cycle to Tensorboard

        Parameters
        ----------
        tboards : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            map of tensorboard writers
        step : `int <https://docs.python.org/3/library/functions.html#int>`_
            current step/iteration number
        """
        for key in self.headmap:
            if 'train' in key:
                tboards['train'].add_scalar(key, self.headmap[key], step)
            elif 'val' in key:
                tboards['val'].add_scalar(key, self.headmap[key], step)

    def logPolyaxon(self, exp, step, rank=-1):
        """Logs results of a cycle to Polyaxon

        Parameters
        ----------
        exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
            polyaxon experiment
        step : `int <https://docs.python.org/3/library/functions.html#int>`_
            current step/iteration number
        rank : `int <https://docs.python.org/3/library/functions.html#int>`_, optional
            rank of node, by default -1
        """
        if rank == -1:
            exp.log_metrics(step=step, **self.headmap)
        else:
            exp.log_metrics(step=step, rank=rank, **self.headmap)