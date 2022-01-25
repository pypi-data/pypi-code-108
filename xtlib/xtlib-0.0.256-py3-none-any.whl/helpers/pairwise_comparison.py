# pairwise_comparison.py: test out how to vectorize pairwise comparisons

import time
import torch
import torch.nn as nn
from torch.serialization import INT_SIZE

class PairwiseComparison(nn.Module):
    def __init__(self, in_size, n_features):
        super().__init__()

        self.in_size = in_size
        self.n_features = n_features

        self.ones = torch.ones(1, n_features, in_size*in_size)

        w = nn.Parameter(data=torch.Tensor(1, n_features, 3, 1))
        torch.nn.init.xavier_normal_(w)
        self.w = w.expand(1, n_features, 3, in_size*in_size)

        #print("ones: ", ones)
        # print("w=", w)

    def forward(self, t):
        '''
        compute pairwise comparisons of all featues in t
        '''
        bsz, sz = t.shape
        assert sz == self.in_size
        n_features = self.n_features

        # build a set of slow changing t values (of shape: bsz, n_features, sz*sz)
        t0 = t.unsqueeze(-1).expand(bsz, sz, sz)
        t0 = t0.unsqueeze(1).expand(bsz, n_features, sz, sz)
        t0 = t0.reshape(bsz, n_features, sz*sz)

        # build a set of fast changing t values (of shape: bsz, n_features, sz*sz)
        t1 = t.unsqueeze(1).expand(bsz, sz, sz)
        t1 = t1.unsqueeze(1).expand(bsz, n_features, sz, sz)
        t1 = t1.reshape(bsz, n_features, sz*sz)

        # expand ones to shape: bsz, n_features, sz*sz
        ones = self.ones.expand(bsz, n_features, sz*sz).to(t.device)

        # expand ones to shape: bsz, n_features, sz*sz
        w = self.w.expand(bsz, n_features, 3, sz*sz).to(t.device)

        # reshape into a tensor of triples
        s = torch.cat([t0, t1, ones], dim=-1).reshape(bsz, n_features, 3, -1)

        # multiple our triples by the learned weights
        # take dot product (linear projection of pairwise features + 1 for bias)
        dp = torch.einsum('bftx,bftx->bfx', s, w)
        dp = torch.relu(dp)

        # print("t0:   ", t0)
        # print("t1:    ", t1)
        # print("s:    ", s)
        # print("w:    ", self.w)
        # print("dp=", dp)

        return dp

def main():
    # test PairwiseCompare module
    # t = torch.FloatTensor( [0, 1, 2, 3, 4, 5] )
    # t = t.unsqueeze(0).expand(4, 6)    # batch size=4
    t = torch.rand(32, 512)
    pc = PairwiseCompare(in_size=t.shape[-1], n_features=2)

    # time PAIRWISE
    start = time.time()
    result = pc(t)
    elapsed = time.time() - start
    print("pc elapsed: {:.5f} secs".format(elapsed))

    #print("result.shape=", result.shape, ", result=", result)

    # time LINEAR
    linear = nn.Linear(512, 512)
    start = time.time()
    result2 = linear(t)
    elapsed = time.time() - start
    print("linear elapsed: {:.7f} secs".format(elapsed))


if __name__ == "__main__":
    main()