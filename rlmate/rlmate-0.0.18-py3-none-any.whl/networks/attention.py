import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

def init_rand(stdv, *sizes):
    return 2 * stdv * torch.rand(*sizes) - stdv

class Attention(nn.Module):

    def __init__(self, d):
        super().__init__()
        self.d = d
        self.register_buffer("scaling", torch.sqrt(torch.FloatTensor([d])))
        self.register_buffer("eps", torch.FloatTensor([1e-6]))

    def forward(self, queries, keys, values, mask=None):
        """forward.

        :param queries: N x n_q x d
        :param keys: N x n_k x d
        :param values: N x n_k x d
        :param mask: N x n_q x n_k
        """

        # calculate scores
        # (N x n_q x d) * (N x d x n_k) -> (N x n_q x n_k)
        raw_scores = torch.bmm(queries, keys.transpose(1,2))
        scaled_scores = raw_scores / self.scaling
        attention = F.softmax(scaled_scores, dim=2)
        if mask != None:
            attention = attention * mask
            attention = attention / (attention.sum(dim=2, keepdim=True) + self.eps)

        # calculate weighted value sums
        # (N x n_q x n_k) * (N x n_k x d) -> (N x n_q x d)
        return torch.bmm(attention, values)

class MultiheadAttention(nn.Module):

    def __init__(self, d, num_heads=4):
        super().__init__()
        self.d = d
        self.num_heads = num_heads
        self.d_head = self.d // self.num_heads
        assert self.d_head * self.num_heads == self.d

        self.attention = Attention(self.d_head)

        self.q_proj = nn.ModuleList(nn.Linear(self.d, self.d_head, bias=False) for _ in range(self.num_heads))
        self.k_proj = nn.ModuleList(nn.Linear(self.d, self.d_head, bias=False) for _ in range(self.num_heads))
        self.v_proj = nn.ModuleList(nn.Linear(self.d, self.d_head, bias=False) for _ in range(self.num_heads))
        self.out_proj = nn.Linear(self.d , self.d, bias=False)

    def forward(self, queries, keys, values, mask=None):
        """forward.

        :param queries: N x n_q x d
        :param keys: N x n_k x d
        :param values: N x n_k x d
        :param mask: N x n_q x n_k

        returns n_q weighted (by attention score) sums of values (N x n_q x d)
        """

        # (N * num_heads) x * x d_head
        q = torch.cat(tuple(W_q(queries) for W_q in self.q_proj), dim=0)
        k = torch.cat(tuple(W_k(keys) for W_k in self.k_proj), dim=0)
        v = torch.cat(tuple(W_v(values) for W_v in self.v_proj), dim=0)

        # (N * num_heads) x n_q x d_head -> num_heads size tuple of (N x n_q x d)
        att_results = self.attention(q, k, v, mask).chunk(self.num_heads, 0)
        output = self.out_proj(torch.cat(att_results, dim=2))

        return output


class MAB(nn.Module):

    def __init__(self, d, num_heads=4):
        super().__init__()
        self.mha = MultiheadAttention(d, num_heads)
        self.fc = nn.Linear(d,d)
        self.ln1 = nn.LayerNorm(d)
        self.ln2 = nn.LayerNorm(d)

    def forward(self, q, k, v, mask=None):
        """forward.

        :param q (Tensor): Query Tensor of size (B, *, n_q, d) where * are  (>= 1) batch dimensions
        :param k, v (Tensor): Key/Values Tensor of size (B, *, n_k, d)
        :param mask (Tensor): Attention Mask Tensor of size (B, *, n_q, n_k)
        """

        r_size = list(k.size()[0:k.dim()-2]) + [q.size()[-2],k.size()[-1]]
        # (*, n_q, d) -> (N, n_q, d)
        if q.dim() > 3:
            q = torch.flatten(q, start_dim=0, end_dim=q.dim()-3)
        if k.dim() > 3:
            k = torch.flatten(k, start_dim=0, end_dim=k.dim()-3)
        if v.dim() > 3:
            v = torch.flatten(v, start_dim=0, end_dim=v.dim()-3)

        # attn_out [final result] : (n_q, N, d)
        attn_out = self.mha(q, k, v, mask)

        # (N, n_q, d)
        h = self.ln1(q + attn_out)
        result = self.ln2(h + F.relu(self.fc(h)))

        # bring back into original shape
        result = result.view(r_size)
        return result

class SAB(MAB):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def forward(self, x):
        return super().forward(x, x, x)


class ISAB(nn.Module):

    def __init__(self, d, inducing_points=8, num_heads=4):
        super().__init__()
        self.inducing_points = nn.Parameter(init_rand(1/np.sqrt(d), m, d))
        self.transform = MAB(d, h=h)
        self.mba = MAB(d, h=h)

    def forward(self, x, mask=None):
        t = self.transform(self.inducing_points, x, x)
        isa = self.mba(x, t)
        return isa

class PMA(nn.Module):

    def __init__(self, d, num_heads=4, seeds=1):
        super().__init__()
        stdv = 1 / np.sqrt(d)
        self.seed = nn.Parameter(init_rand(stdv, 1, seeds, d))
        self.fc = nn.Linear(d,d)
        self.mab = MAB(d, num_heads)

    def forward(self, z):
        """forward.

        :param z: B x * x n x d
        """
        z = F.relu(self.fc(z))
        return self.mab(self.seed.repeat(math.prod(z.size()[0:z.dim()-2]), 1, 1), z, z)


if __name__ == '__main__':
    def print_params(model, only_total=False):
        total = 0
        for n,p in model.named_parameters():
            total += p.numel()
            if not only_total:
                print(n, p.size(), p.numel())
        print('total', '---', total)

    print_params(MAB(64, 1))
    print_params(MAB(64, 2))
    print_params(MAB(64, 4))
    print_params(MAB(64, 8))

