import torch.nn as nn

class Residual(nn.Module):

    def __init__(self, module, layer_norm=None):
        super().__init__()
        self.module = module
        self.ln = nn.LayerNorm(layer_norm) if layer_norm is not None else nn.Identity()

    def forward(self, x):
        return self.ln(self.module(x) + x)
