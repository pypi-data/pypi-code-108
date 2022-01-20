import torch as tr
import numpy as np
from nwmodule.pytorch import FeedForwardNetwork
from nwmodule.nwtrainer import NWTrainer
from torch.utils.data import Dataset, DataLoader
from nwutils.batched import defaultBatchFn
from torch.optim import SGD
from torch import nn

device = tr.device("cuda") if tr.cuda.is_available() else tr.device("cpu")

class Reader(Dataset):
    def __init__(self, data: np.ndarray, labels: np.ndarray):
        self.data = data
        self.labels = labels

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return {
            "data": self.data[index],
            "labels": self.labels[index]
        }

def getReader(data, labels, batchSize: int, seed: int=None):
    g = None
    if seed is not None:
        g = tr.Generator()
        g.manual_seed(seed)

    reader = Reader(data, labels)
    loader = DataLoader(reader, collate_fn=defaultBatchFn, batch_size=batchSize, num_workers=4, generator=g)
    return loader

class Model(FeedForwardNetwork):
    def __init__(self, inputSize, hiddenSize, outputSize):
        super().__init__()
        self.fc1 = nn.Linear(inputSize, hiddenSize)
        self.fc2 = nn.Linear(hiddenSize, hiddenSize)
        self.fc3 = nn.Linear(hiddenSize, outputSize)

    def forward(self, x):
        y1 = self.fc1(x)
        y2 = self.fc2(y1)
        y3 = self.fc3(y2)
        return y3

    def getCriterion(self):
        return lambda y, t : tr.sum((y - t)**2)

class TestTrainer:
    def test_trainer_1(self):
        N, I, H, O = 50, 100, 50, 30
        inputs = np.float32(np.random.randn(N, I))
        targets = np.float32(np.random.randn(N, O))
        reader = getReader(inputs, targets, 10)

        testData = np.random.randn(N, I).astype(np.float32)
        model = Model(I, H, O).to(device)
        resBefore = model.npForward(testData)
        model.setOptimizer(SGD, lr=0.005)
        NWTrainer(model).train(reader, numEpochs=5)
        resAfter = model.npForward(testData)
        assert (resBefore != resAfter).sum() != 0

    def test_trainer_reproductibility_1(self):
        N, I, H, O = 50, 100, 50, 30
        inputs = np.float32(np.random.randn(N, I))
        targets = np.float32(np.random.randn(N, O))
        reader = getReader(inputs, targets, 10)
        testData = np.random.randn(N, I).astype(np.float32)

        models = []
        for _ in range(5):
            tr.manual_seed(42)
            np.random.seed(42)
            models.append(Model(I, H, O).to(device))
        res_before = [model.npForward(testData) for model in models]
        assert np.std(res_before, axis=0).sum() <= 1e-3

        for model in models:
            model.setOptimizer(SGD, lr=0.005)
            NWTrainer(model).train(reader, numEpochs=5)
        res_after = [model.npForward(testData) for model in models]
        assert np.std(res_after, axis=0).sum() <= 1e-3

    def test_trainer_reproductibility_2(self):
        N, I, H, O = 50, 100, 50, 30
        inputs = np.float32(np.random.randn(N, I))
        targets = np.float32(np.random.randn(N, O))
        reader = getReader(inputs, targets, 10)
        testData = np.random.randn(N, I).astype(np.float32)

        models = []
        for i in range(5):
            tr.manual_seed(i)
            np.random.seed(i)
            models.append(Model(I, H, O).to(device))
        res_before = [model.npForward(testData) for model in models]
        assert np.std(res_before, axis=0).sum() >= 1e-3

        for model in models:
            model.setOptimizer(SGD, lr=0.005)
            NWTrainer(model).train(reader, numEpochs=5)
        res_after = [model.npForward(testData) for model in models]
        assert np.std(res_after, axis=0).sum() >= 1e-3


if __name__ == "__main__":
    TestTrainer().test_trainer_reproductibility_2()
