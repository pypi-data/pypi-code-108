from torch.utils.data import Dataset, Subset


class PreProcess(Dataset):
    """
    Modify dataset samples on the fly.

    Usage:

        # assume a standard setting, where data isn't pre-processed:
        >>> dset = SomePytorchDataset()
        >>> x, y = dset[0]

        # use this class to fix it by applying a lambda function:
        >>> dset = PreProcess(
            SomePytorchDataset(),
            lambda xy: (xy[0] / xy[0].max(), xy[1])

        # or use torchvision.transforms.Compose:
        >>> dset = PreProcess(
            SomePytorchDataset(),
            Compose([
                CenterCrop(10),
                ToTensor()
            ])
    """
    def __init__(self, dset:Dataset, transform_fn):
        self._fn = transform_fn
        self._dset = dset

    def __getitem__(self, x):
        return self._fn(self._dset[x])

    def __len__(self):
        return len(self._dset)

    def __iter__(self):
        return iter(self._dset)

    def __getattr__(self, x):
        """Pass-through to the wrapped dataset"""
        return getattr(self._dset, x)

    def __repr__(self):
        if isinstance(self._dset, Subset):
            x = f'Subset[{repr(self._dset.dataset)}]'
        else:
            x = repr(self._dset)
        return f'Preprocess[{x}]'
