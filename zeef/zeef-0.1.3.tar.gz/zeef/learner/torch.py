"""
    Basic PyTorch learner class for different platform.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 15/12/2021
"""
import numpy as np
from tqdm import tqdm
from .base import BaseLearner
from ..util.file_util import check_torch_version

try:
    import torch
    import torch.nn.functional as F
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "No module named 'torch', and zeef PyTorch Learner class depends on PyTorch"
        "(aka 'torch'). "
        "Visit https://pytorch.org/ for installation instructions.")

check_torch_version()


class Learner(BaseLearner):
    """
    The PyTorch implementation of base learner class.
    """

    def __init__(self, net, optimizer, criterion, transform=None, device=None):
        self.optimizer = optimizer
        self.criterion = criterion
        self.transform = transform
        if device:
            self.device = device
        else:  # initialize the dispatch device.
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net = net.to(self.device)

    def learn(self, data_x, data_y, n_epoch, batch_size, **kwargs):
        """
        learn: to fit the pytorch model by given X and Y data.
        @param data_x: the training data.
        @param data_y: the corresponding labels of the training data (data_x).
        @param n_epoch: the training number of epoch.
        @param batch_size: the training batch size.
        @return: None.
        """
        if self.transform:
            input_tensor = self.transform(data_x)
        else:
            input_tensor = torch.stack(data_x)
        batches = torch.split(input_tensor, batch_size)
        targets = torch.split(torch.as_tensor(data_y), batch_size)

        for _ in range(n_epoch):
            self.net.train()
            for x, y in tqdm(zip(batches, targets)):
                x, y = x.to(self.device), y.to(self.device)
                self.optimizer.zero_grad()
                out = self.net(x)
                loss = self.criterion(out, y)
                loss.backward()
                self.optimizer.step()

    def _infer(self, data, batch_size, n_drop=1):
        """
        inner inference function.
        @param data: the request data to perform inference.
        @param batch_size: the inference batch_size.
        @param n_drop: the number of dropout runs to use to generate MC samples (int, optional).
        """
        self.net.eval()
        if self.transform:
            input_tensor = self.transform(data)
        else:
            input_tensor = torch.Tensor(np.stack(data))
        batches = torch.split(input_tensor.to(self.device), batch_size)

        output_data = []
        for _ in range(n_drop):
            outputs = []
            for batch in batches:
                batch = batch.to(self.device)
                with torch.no_grad():
                    outputs.append(self.net(batch))
            output_data.append(torch.cat(outputs))

        output_data = torch.sum(torch.stack(output_data), dim=0)
        output_data /= n_drop
        return output_data

    def infer_proba(self, data, batch_size, n_drop=1):
        """
        infer: inference function that returns the prediction probability.
        @param data: the request data to perform inference.
        @param batch_size: the inference batch_size.
        @param n_drop: the number of dropout runs to use to generate MC samples (int, optional).
        @return: a list of inference probability or a single result if given a single request.
        """
        return F.softmax(self._infer(data, batch_size, n_drop), dim=1).cpu().detach().numpy()

    def infer(self, data, batch_size):
        """
        infer: inference function that returns the prediction results.
        @param data: the request data to perform inference.
        @param batch_size: the inference batch_size.
        @return: a list of inference results or a single result if given a single request.
        """
        return self._infer(data, batch_size).max(1)[1].cpu().detach().numpy()
