# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A PyTorch N-D implementation of sparsemax, both as an `autograd.Function` and `nn.Module`."""

import torch
import torch.nn.functional as f


class SparsemaxFunction(torch.autograd.Function):
    """Sparsemax operation as defined in https://arxiv.org/pdf/1602.02068.pdf."""

    @staticmethod
    def forward(ctx, x, dim=-1):
        """Sparsemax operation as defined in https://arxiv.org/pdf/1602.02068.pdf (x -> z in the paper).

        Parameters
        ----------
        ctx:
            The operation's context
        x: torch.Tensor
            The tensor on which to operate
        dim: int, optional
            The dimension on which to perform the operation. Defaults to -1.

        Returns
        -------
        torch.Tensor

        """
        # convert dim to positive integer and store for backprop
        dim = dim % x.dim()
        ctx.dim = dim

        # sort the inputs
        x_sorted, _ = x.sort(dim=dim, descending=True)

        # compute the constraint
        x_cum = x_sorted.cumsum(dim=dim)
        k = torch.arange(1, x.shape[dim] + 1, dtype=x.dtype, device=x.device)  # k goes from 1..N
        k_expanded = k.view([1] * dim + list(k.shape) + [1] * (x.dim() - dim - 1))
        constraint = 1 + k_expanded * x_sorted > x_cum

        # find the greatest k such that the constraint is True
        # since all prior elements will also satisfy the constraint (x_sorted is in descending order),
        # the sum of constraint will be the first zero in a zero-based indexing scheme. however, since we're looking at
        # values of k which are 1-indexed, this will be the last k_i st k[i] == 1.
        k_x = constraint.sum(dim=dim, dtype=torch.int32)

        # handle invalid k_x. if x contains NaN/Inf or all values are -Inf, k_x will be 0.
        # in other words, the constraint was never satisfied, which is not possible for finite values of x.
        # to handle this, we'll set k=1 (arbitrary) so things don't break and correct this change prior to returning.
        k_x = torch.max(k_x, torch.tensor(1, dtype=k_x.dtype, device=k_x.device))

        # compute the threshold function (tau)
        # first we compute the numerator
        # we use the cumsum from earlier, but reduce k_x by 1 to convert it to 0-based index
        # rather than the 1-based index
        tau_sum = x_cum.gather(dim=dim, index=(k_x.unsqueeze(dim=dim) - 1).type(torch.long))
        tau = (tau_sum - 1) / k_x.unsqueeze(dim=dim).type_as(tau_sum)

        # compute output
        out = f.relu(x - tau.type_as(x))

        # undo our hack from earlier to handle bad k_x
        out = torch.where(torch.isfinite(out), out, torch.tensor(float('nan'), dtype=x.dtype, device=x.device))
        ctx.save_for_backward(out)
        return out

    @staticmethod
    def backward(ctx, x):
        """Computes the gradients of the sparsemax layer.

        Parameters
        ----------
        ctx:
            A context object containing the activations from the forward pass
        x: torch.Tensor
            Gradients from the previous step during backprop

        Returns
        -------
        Tuple[torch.Tensor, None]

        """
        fwd_out, = ctx.saved_tensors
        dim = ctx.dim

        # as defined in equ 14 of paper
        support = (fwd_out > 0).type_as(x)
        return support * (x - (x * support).sum(dim=dim, keepdim=True) / support.sum(dim=dim, keepdim=True)), None


def sparsemax(x: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """Applies a sparsemax to the given tensor along the specified dimension.

    Parameters
    ----------
    x: torch.Tensor
        The tensor to which the sparsemax operation should be performed.
    dim: int, optional
        The dimension along which the sparsemax should be applied (defaults to -1).

    Returns
    -------
    torch.Tensor

    """
    return SparsemaxFunction.apply(x, dim)


class Sparsemax(torch.nn.Module):
    """Sparsemax operation as defined in https://arxiv.org/pdf/1602.02068.pdf."""

    __constants__ = ['_dim']

    def __init__(self, dim=-1):
        """Creates a sparsemax layer that operates along `dim` of the input tensor."""
        super().__init__()
        self._dim = dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the sparsemax operation along the dimension provided in the `__init__` method.

        Parameters
        ----------
        x: torch.Tensor
            The tensor on which the sparsemax operation should be performed.

        Returns
        -------
        torch.Tensor

        """
        return SparsemaxFunction.apply(x, self._dim)
