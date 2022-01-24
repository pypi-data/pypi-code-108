import random
import numpy as np
import torch.optim as optim
import torch.nn.functional as F

from util.data_loader import get_dataloader_keyword, readlines
from model import STFT_TCResnet
from zeef.data import Pool
from zeef.learner.torch import Learner
from zeef.strategy import MarginConfidence

SEED = 1234

# parameters
TOTAL_NUM = 3500
NUM_INIT_LB = 1000
NUM_QUERY = 250
NUM_ROUND = 10

if __name__ == '__main__':
    random.seed(SEED)
    class_list = ["yes", "no", "unknown", "silence"]
    # load dataset
    train_filename = readlines(f"./dataset/splits/train.txt")
    valid_filename = readlines(f"./dataset/splits/valid.txt")
    class_encoding = {category: index for index, category in enumerate(class_list)}
    train_loader, test_loader = get_dataloader_keyword('./dataset', class_list, class_encoding, 128)
    # prepare the data
    X_train = []
    Y_train = []
    X_test = []
    Y_test = []
    for batch_idx, (waveform, labels) in enumerate(train_loader):
        for i in range(128):
            X_train.append(waveform[i])
            Y_train.append(labels[i])
    for batch_idx, (waveform, labels) in enumerate(test_loader):
        for i in range(128):
            X_test.append(waveform[i])
            Y_test.append(labels[i])

    X_train = X_train[:TOTAL_NUM]
    Y_train = Y_train[:TOTAL_NUM]

    # builds the model
    model = STFT_TCResnet(
        filter_length=256, hop_length=129, bins=129,
        channels=[16, 24, 24, 32, 32, 48, 48], channel_scale=3, num_classes=len(class_list))
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    torch_learner = Learner(model, criterion=F.cross_entropy, optimizer=optimizer)

    # generate the data pool and the sampling strategy
    data_pool = Pool(X_train)

    # strategy = RandomSampling(data_pool, learner=torch_learner)
    # strategy = EntropySampling(data_pool, learner=torch_learner)
    strategy = MarginConfidence(data_pool, learner=torch_learner)
    # strategy = LeastConfidence(data_pool, learner=torch_learner)
    # strategy = RatioConfidence(data_pool, learner=torch_learner)
    # strategy = KMeansSampling(data_pool, learner=torch_learner)

    print("labeled data: ", len(data_pool.labeled_ids))

    # init the labels
    data_pool.label_by_ids(range(NUM_INIT_LB), Y_train[:NUM_INIT_LB])
    print("labeled data: ", len(data_pool.labeled_ids))

    # round 0: pretraining
    strategy.learn(batch_size=128)
    predictions = strategy.infer(X_test, batch_size=128)
    acc = np.zeros(NUM_ROUND + 1)
    acc[0] = sum(1 for x, y in zip(Y_test, predictions) if x == y) / len(Y_test)
    print('Round 0\ntesting accuracy {}'.format(acc[0]))

    # start the active learning process.
    for r in range(1, NUM_ROUND + 1):
        print('Round {}'.format(r))

        # query by given strategy.
        query_ids = strategy.query(NUM_QUERY)
        data_pool.label_by_ids(query_ids,
                               [Y_train[i] for i in query_ids])  # update the data pool with newly labeled data.
        print(f"labeled: {len(data_pool.labeled_ids)}, unlabeled: {len(data_pool.get_unlabeled_ids())}")
        strategy.learn(batch_size=128)  # update the model.
        predictions = strategy.infer(X_test, batch_size=128)  # round accuracy
        acc[r] = sum(1 for x, y in zip(Y_test, predictions) if x == y) / len(Y_test)
        print('testing accuracy {}'.format(acc[r]))

    # print results
    print(acc)
