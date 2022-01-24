import torch.nn as nn

class Linear(nn.Module):
    """
    Wrapper class for linear layers optionally using ReLU activation (defaults to
    true) and layer normalization (defaults to false)
    """

    def __init__(self, in_features: int, out_features: int, bias: bool = True, relu: bool = True, layer_norm: bool = False):
        super().__init__()
        net = [nn.Linear(in_features, out_features, bias=bias)]
        if relu:
            net.append(nn.ReLU())
        if layer_norm:
            net.append(nn.LayerNorm(out_features))
        self.net = nn.Sequential(*net)

    def forward(self, x):
        return self.net(x)
