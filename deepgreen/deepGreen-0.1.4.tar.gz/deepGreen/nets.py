import numpy as np
import os
import random
from skorch import NeuralNetRegressor
from skorch.callbacks import ProgressBar, Checkpoint
from skorch.callbacks import EarlyStopping, LRScheduler
import torch.nn.functional as F
import torch


def shuffle_n(input, n, verbose=False, seed=2333):
    
    seed_torch(seed)
    # import ipdb; ipdb.set_trace()
    idx = np.arange(len(input)//n)
    np.random.shuffle(idx)

    out = input[n*idx[0]:np.minimum(n*(idx[0]+1), len(input))]
    for i in np.arange(1, len(idx)):
        out = np.hstack((out,
                         input[n*idx[i]:np.minimum(n*(idx[i]+1),
                                                   len(input))]))
    # import ipdb; ipdb.set_trace()
    if verbose:
        print('Shape after shuffling:', out.shape)
    return out


def seed_torch(seed=2333):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


def init_weights(m):
    if type(m) == torch.nn.Linear:
        torch.nn.init.xavier_normal_(m.weight)
        m.bias.data.fill_(0.01)

my_callbacks = [
    Checkpoint(),
    EarlyStopping(patience=5),
    LRScheduler,
    ProgressBar(),
]


class CNN_1D(torch.nn.Module):
    def __init__(self, num_channel=9):
        super(CNN_1D, self).__init__()
        self.conv1 = torch.nn.Conv1d(num_channel, 18, kernel_size=2)
        # 9 input channels, 18 output channels
        self.conv2 = torch.nn.Conv1d(18, 36, kernel_size=2)
        # 18 input channels from previous Conv. layer, 36 out
        self.conv2_drop = torch.nn.Dropout2d(p=0.2)
        # dropout
        self.fc1 = torch.nn.Linear(36*14, 72)
        # Fully-connected classifier layer
        self.fc2 = torch.nn.Linear(72, 16)
        # Fully-connected classifier layer
        self.fc3 = torch.nn.Linear(16, 1)
        # Fully-connected classifier layer

    def forward(self, x):
        x = F.relu(F.max_pool1d(self.conv1(x), 2))
        # print(x.shape)
        x = F.relu(F.max_pool1d(self.conv2_drop(self.conv2(x)), 2))
        # print(x.shape)

        # point A
        x = x.view(x.shape[0], -1)

        # point B
        x = self.fc1(x)
        x = F.leaky_relu(x)
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        x = self.fc3(x)
        # return F.log_softmax(x, dim=1)
        return x


class lstm_reg(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size=1, num_layers=2):
        super(lstm_reg, self).__init__()
        # ipdb.set_trace()
        self.rnn = torch.nn.GRU(input_size, hidden_size,
                                num_layers,
                                bidirectional=True)  # , bidirectional=True
        self.gru1 = torch.nn.GRU(input_size,hidden_size,hidden_size, bidirectional=True) #, bidirectional=True
        self.gru2 = torch.nn.GRU(hidden_size*2,hidden_size,num_layers, bidirectional=True) #, bidirectional=True
        self.rnn1 = torch.nn.LSTM(input_size,hidden_size,hidden_size, bidirectional=True) #, bidirectional=True
        self.rnn2 = torch.nn.LSTM(hidden_size,hidden_size,num_layers, bidirectional=False) #, bidirectional=True
        
        self.reg = torch.nn.Linear(hidden_size*2,output_size)

    def forward(self,x):
        x, _ = self.rnn(x)
        
        s,b,h = x.shape
        x = x.view(s*b, h)
        #ipdb.set_trace()
        x = self.reg(x)
        x = x.view(s,b,-1)
        return x
    
class PhysinformedNet(NeuralNetRegressor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ReLU = torch.nn.ReLU()
        self.ReLU6 = torch.nn.ReLU6()

    def get_loss(self, y_pred, y_true, X, training=False):
        # print('y_pred:', y_pred.shape)
        # print('y_true:', y_true.shape)
        # print('X:', X.shape)
        loss_ori = super().get_loss(y_pred.sum(axis=1),
                                    y_true, X=X, training=training)
        # loss += self.lambda1 * sum([w.abs().sum() for w in self.module_.parameters()])
        # X = X.cuda()

        '''

        loss_RMS = torch.mean((y_pred.sum(axis=1) -
                          y_true.cuda())**2)

        loss_RMS = torch.mean((y_pred.std(axis=1) -
                          y_true.cuda())**2)

        loss_RMS = torch.mean((y_pred[:,:, 0] -
                          y_true[:,:].cuda())**2)
        loss_RE = torch.mean((y_pred[:,:, 0] -
                          y_true[:,:].cuda())**2)
        '''

        # ipdb.set_trace()

        # print('loss_term1:', loss_term1)
        # print('loss:', loss)
        # ipdb.set_trace()
        loss = loss_ori

        # loss += loss_term0.mean()
        # print('loss+0:', loss)
        # loss += loss_term1.squeeze()
        # print('loss+1:', loss)
        # loss += loss_term2.squeeze()
        # print('loss+2:', loss)
        # loss += loss_term3.squeeze()
        # print('loss+3:', loss)

        return loss
