from collections import defaultdict

import numpy as np
import torch


def get_synthetic_token_classification_dataset(n):
    samples = defaultdict(list)
    for i in range(n):
        ss = defaultdict(list)
        m = np.random.randint(6, 11)
        for j in range(m):
            len_t = np.random.randint(2, 20)
            a = np.random.randint(0, 3, size=len_t)
            n0 = (a == 0).sum()
            n1 = (a == 1).sum()
            n2 = (a == 2).sum()
            r = a.copy()
            r[a == 0] = np.random.randint(0, 2, size=n0)
            r[a == 1] = np.random.randint(10, 12, size=n1)
            r[a == 2] = np.random.randint(20, 22, size=n2)

            ss['tokens'].append(torch.tensor(a))
            ss['is_less_than_100'].append(torch.tensor(a == 0).float().unsqueeze(-1))
            ss['is_more_than_150'].append(torch.tensor(a == 2).float().unsqueeze(-1))
        samples['tokens'].append(ss['tokens'])
        samples['is_less_than_100'].append(ss['is_less_than_100'])
        samples['is_more_than_150'].append(ss['is_more_than_150'])
    return samples