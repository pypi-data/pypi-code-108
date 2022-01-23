from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler

import torch.distributed as dist
import webdataset as wds

modes = ['train', 'val']

def urlSampler(url, rank, world_size):
    front, out = url.split('{')
    out, back = out.split('}')
    m, n = out.split('..')
    index_len = len(m)
    m, n = int(m), int(n)
    sz = n-m+1
    print(world_size, sz)
    assert world_size <= sz, "Total URL tars are less than world_size"
    sz_ = int(sz // world_size)
    #smart sampling 
    remainder = sz-sz_*world_size
    cond = world_size-remainder
    start_ind = rank*sz_+m
    end_ind = (rank+1)*sz_+m-1
    if rank >= cond:
        gap=rank-cond
        start_ind += gap
        end_ind += gap+1

    return f"{front}{'{'}{str(start_ind).zfill(index_len)}..{str(end_ind).zfill(index_len)}{'}'}{back}"

def getWebDataSets(posixes, transforms=None, shuffle=True, distributed=False):
    """Creates datasets from posix urls for shard based training

    Parameters
    ----------
    posixes : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map of posix URLs
    transforms : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_, optional
        map of transforms, by default ``None``
    shuffle : `boolean <https://docs.python.org/3/library/functions.html#bool>`_, optional
        flag representing whether dataset samples need to be shuffled, by default ``True``
    distributed : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        flag to represent if model is to train in distributed mode, by default ``False``

    Returns
    -------
    `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of datasets

    Examples
    --------
    Use a map of posix URLs e.g:

    >>> urlmap = {
    ...     'train': 'http://aistore.granular.ai/v1/objects/test_ais/train/train-{0..4}.tar?provider=gcp',
    ...     'val': 'http://aistore.granular.ai/v1/objects/test_ais/val/val-{0..4}.tar?provider=gcp',
    ... }

    and a map of transforms e.g:

    >>> def preproc(data):
    ...     inp1 = data['x.pth']
    ...     inp1 = torch.unsqueeze(inp1,0)
    ... 
    ...     out1 = data['y.cls']
    ... 
    ...     x = {'inp1': inp1}
    ...     y = {'out1': out1}
    ... 
    ...     return x,y
    >>> 
    >>> transmap = {'train': preproc, 'val': preproc }
    >>>

    To create datasets

    >>> datasets = getWebDataSets(
    ...     posixes=urlmap,
    ...     transforms=transmap,
    ... )
    >>>
    """
    samplers, datasets = {}, {}
    
    for mode in modes:
        samplers[mode] = None

        if distributed:
            samplers[mode] = urlSampler(posixes[mode], dist.get_rank(), dist.get_world_size())
        if not samplers[mode]:
            samplers[mode] = posixes[mode]

        if transforms and transforms[mode]:
            datasets[mode] = (wds.WebDataset(samplers[mode])
                .shuffle(shuffle)
                .decode()
                .map(transforms[mode])
                )
        else:
            datasets[mode] = (wds.WebDataset(samplers[mode])
                .shuffle(shuffle)
                .decode()
                )

    return datasets

def getDataLoaders(datasets, batch_size, num_workers, shuffle=True, distributed=False, load = 'wds'):
    """Creates data loaders from dataset map

    Parameters
    ----------
    datasets : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map of datasets
    batch_size : `int <https://docs.python.org/3/library/functions.html#int>`_
        batch size
    num_workers : `int <https://docs.python.org/3/library/functions.html#int>`_
        number of workers
    shuffle : `boolean <https://docs.python.org/3/library/functions.html#bool>`_, optional
        flag to represent if samples need to be shuffled, by default ``True``
    distributed : `boolean <https://docs.python.org/3/library/functions.html#bool>`_, optional
        flag to represent if model is to train in distributed mode, by default ``False``
    load : `str <https://docs.python.org/3/library/stdtypes.html#str>`_, optional
        load type for dataloader, by default ``wds``. phobos supports following load types 

        * full : fully loads dataset to memory
        * wds : loads dataset shards to memory

    Returns
    -------
    `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of dataloaders
    
    Examples
    --------
    1. For full load based datasets

    Create map of datasets e.g

    >>> transform=transforms.Compose([
    ...     transforms.ToTensor(),
    ...     transforms.Normalize((0.1307,), (0.3081,))
    ... ])
    >>> 
    >>> dataset_train = datasets.MNIST('data', train=True, download=True,transform=transform)
    >>> dataset_test = datasets.MNIST('data',train=False,download=True,transform=transform)
    >>> 
    >>> class DatasetM(Dataset):
    ...     def __init__(self,data):
    ...         super(DatasetM,self).__init__()
    ...         self.data = data
    ... 
    ...     def __len__(self):
    ...         return len(self.data)
    ... 
    ...     def __getitem__(self, index):
    ...         x,y = self.data.__getitem__(index)
    ... 
    ...         inputs = {'inp1': x}
    ...         labels = {'out1': y}
    ... 
    ...         return inputs, labels
    >>> 
    >>> datasets = { 'train': DatasetM(dataset_train), 'val': DatasetM(dataset_test) }
    >>>

    2. For wds/shard load based datasets
    
    Use ``getWebDataSets`` method to create map of datasets e.g

    >>> urlmap = {
    ...     'train': 'http://aistore.granular.ai/v1/objects/aistore_test/dir_poc/train-{00000..00011}.tar?provider=gcp',
    ...     'val': 'http://aistore.granular.ai/v1/objects/aistore_test/dir_poc/val-{00000..00018}.tar?provider=gcp',
    ... }
    >>>
    >>> def preproc(data):
    ...     x = {'inp1': data['x.pth']}
    ...     y = {'out1': data['y.pth']}
    ...     return x,y
    >>> 
    >>> transmap = {'train': preproc, 'val': preproc }
    >>>
    >>> datasets = getWebDataSets(
    ...     posixes=urlmap,
    ...     transforms=transmap,
    ... )
    >>>

    Use dataset map to create dataloaders

    >>> loaders = getDataLoaders(
    ...     datasets=datasets,
    ...     batch_size=args.batch_size,
    ...     num_workers=args.num_workers,
    ...     distributed=args.distributed,
    ...     load=args.load
    ... )
    >>>

    """
    loaders = {}
    
    for mode in modes:
        sampler = None

        if distributed and load == 'full':
            rank, wsize = dist.get_rank(), dist.get_world_size()

            sampler = DistributedSampler(
                datasets[mode],
                rank=rank,
                num_replicas=wsize
            )

        if sampler:
            loaders[mode] = DataLoader(
                datasets[mode],
                batch_size=batch_size,
                num_workers=num_workers,
                sampler=sampler,
                pin_memory=True
            )
        else:
            loaders[mode] = DataLoader(
                datasets[mode],
                batch_size=batch_size,
                num_workers=num_workers,
                shuffle=shuffle,
                pin_memory=True
            )

    return loaders

def getWebDataLoaders(posixes, batch_size, num_workers, transforms=None, shuffle=True, distributed=False): 
    """Creates datasets from posix urls for shard based training

    Parameters
    ----------
    posixes : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map of posix URLs
    batch_size : `int <https://docs.python.org/3/library/functions.html#int>`_
        batch size
    num_workers : `int <https://docs.python.org/3/library/functions.html#int>`_
        number of workers
    transforms : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_, optional
        map of transforms, by default ``None``
    shuffle : `boolean <https://docs.python.org/3/library/functions.html#bool>`_, optional
        flag representing whether dataset samples need to be shuffled, by default ``True``
    distributed : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        flag to represent if model is to train in distributed mode, by default ``False``

    Returns
    -------
    `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of dataloaders

    Examples
    --------
    Use a map of posix URLs e.g:

    >>> urlmap = {
    ...     'train': 'http://aistore.granular.ai/v1/objects/test_ais/train/train-{0..4}.tar?provider=gcp',
    ...     'val': 'http://aistore.granular.ai/v1/objects/test_ais/val/val-{0..4}.tar?provider=gcp',
    ... }

    and a map of transforms e.g:

    >>> def preproc(data):
    ...     inp1 = data['x.pth']
    ...     inp1 = torch.unsqueeze(inp1,0)
    ... 
    ...     out1 = data['y.cls']
    ... 
    ...     x = {'inp1': inp1}
    ...     y = {'out1': out1}
    ... 
    ...     return x,y
    >>> 
    >>> transmap = {'train': preproc, 'val': preproc }
    >>>

    And configs to create dataloaders

    >>> datasets = getWebDataLoaders(
    ...     posixes=urlmap,
    ...     transforms=transmap,
    ...     batch_size=args.batch_size,
    ...     num_workers=args.num_workers,
    ...     shuffle=args.shuffle,
    ...     distributed=args.distributed
    ... )
    >>>    
    """
    datasets = getWebDataSets(
        posixes=posixes,
        shuffle=shuffle,
        transforms=transforms,
        distributed=distributed
    )

    loaders = getDataLoaders(
        datasets,
        batch_size=batch_size,
        num_workers=num_workers,
        shuffle=False,
        distributed=distributed
    )

    return loaders