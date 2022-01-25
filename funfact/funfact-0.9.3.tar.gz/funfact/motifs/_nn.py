#!/usr/bin/env python
# -*- coding: utf-8 -*-
from funfact.lang import tensor, template, indices, _0


def linear_layer(name, in_dim, out_dim):
    W = tensor(f'W{name}', in_dim, out_dim)
    b = tensor(f'b{name}', out_dim)
    p, q = indices(2)
    return template(_0[...] * W[p, ~q] + b[~q])
