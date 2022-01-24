import torch
import torchvision.transforms as transforms

from typing import Any, Optional, Tuple
from torch.utils.data import DataLoader, Dataset
from torch.utils.data.dataset import random_split

from torchvision.datasets import MNIST

from pytorch_lightning import LightningDataModule

from lightning_nets.data.torch_dataset import TrainingTorchDataset

class MnistDataSet(Dataset):
    def __init__(self, train: bool = True, transform: Any = None, latent_size:int = 0):
        if transform == None:
            self.transform = transforms.Compose([ transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,)), transforms.Resize((28, 28)) ])
        else:
            self.transform = transform
        
        self.latent_size = latent_size
        self.mnist_train_data = MNIST(root = 'data', train = True, transform = self.transform, download = True)

    def __len__(self):
        return int(len(self.mnist_train_data))

    def __getitem__(self, index):
        output, input = self.mnist_train_data.__getitem__(index)
        if self.latent_size == 0 or self.latent_size == None:
            return input, output.squeeze()
        else:
            z = torch.randn(self.latent_size + 1).numpy()
            z[0] = float(input)
            return z, output.squeeze()

    @property
    def input_shape(self):
        return self.__getitem__(0)[0].shape

    @property
    def output_shape(self):
        return self.__getitem__(0)[1].shape

class MNISTDataModule(LightningDataModule):
    def __init__(self, data_dir: str = "./data/mnist", batch_size:int = 32, image_size: Tuple[int, int] = [28, 28], latent_size:int = 0):
        super().__init__()
        self.batch_size = batch_size
        self.data_dir = data_dir
        self.transform = transforms.Compose([ transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,)), transforms.Resize(image_size) ])

        # download
        self.mnist_train = MnistDataSet(True, transform=self.transform, latent_size=latent_size)# MNIST(self.data_dir, train=True, transform=self.transform)
        self.mnist_val = MnistDataSet(False, transform=self.transform, latent_size=latent_size)#MNIST(self.data_dir, train=False, transform=self.transform)
        self.mnist_test = MnistDataSet(False, transform=self.transform, latent_size=latent_size)#MNIST(self.data_dir, train=False, transform=self.transform)
        self.mnist_predict = MnistDataSet(False, transform=self.transform, latent_size=latent_size)# MNIST(self.data_dir, train=False, transform=self.transform)

    def prepare_data(self):
        return

    def setup(self, stage: Optional[str] = None):
        return

    def train_dataloader(self):
        return DataLoader(self.mnist_train, batch_size=self.batch_size)

    def val_dataloader(self):
        return DataLoader(self.mnist_val, batch_size=self.batch_size)

    def test_dataloader(self):
        return DataLoader(self.mnist_test, batch_size=self.batch_size)

    def predict_dataloader(self):
        return DataLoader(self.mnist_predict, batch_size=self.batch_size)