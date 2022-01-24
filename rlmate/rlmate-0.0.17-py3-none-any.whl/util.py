from __future__ import annotations

import torch
import numpy as np
import leb128
import json
import typing as t
import os
import sys
import importlib


def load_network_class_from_experiment_directory(
    path: str,
) -> t.Callable[..., torch.nn.Module]:
    """
    Old feature from 'rlassistant', that is still used by modipro project.
    Should be deprecated in the future.

    Args:
        path (str): path to a hermes experiment directory

    Returns:
        t.Callable[..., torch.nn.Module]: Network constructor
    """

    def _correct_path(path):
        slash = '\\' if os.name == 'nt' else '/'
        if not path.endswith(slash):
            path += slash

        return slash, path

    slash, path = _correct_path(path)

    neural_network_file = None
    with open(path + "exec_arguments") as f:
        for line in f:
            for idx in ["-nnf", "--neural_network_file"]:
                if line.startswith(idx):
                    neural_network_file = line[len(idx) + 1 :]
                    neural_network_file = neural_network_file.split(".")[-1]
                    continue
    if neural_network_file == None:
        neural_network_file = "fcn"  # assume this as std
    else:
        for td in [".py", ".py\n", "\n"]:
            if neural_network_file.endswith(td):
                neural_network_file = neural_network_file[: -(len(td))]

    sys.path.append(path)
    network_module = importlib.import_module(neural_network_file)

    return network_module.Network


class UnsupportedLayerError(Exception):
    pass


def save_network(model, path):
    torch.save(model.state_dict(), path)


def load_network(model, path):
    d = torch.load(path, map_location=model.device)
    model.load_state_dict(d)
    model.eval()


def _make_if_necessary(p):
    if not os.path.exists(p):
        os.mkdir(p)


def _moving_average(x, w):
    return np.convolve(x, np.ones(w), "valid") / w


def _is_numeric(val):
    return isinstance(val, int) or isinstance(val, float)


# copyright TorchSharp
# https://github.com/dotnet/TorchSharp
def _elem_type(t):
    dt = t.dtype

    if dt == torch.uint8:
        return 0
    elif dt == torch.int8:
        return 1
    elif dt == torch.int16:
        return 2
    elif dt == torch.int32:
        return 3
    elif dt == torch.int64:
        return 4
    elif dt == torch.float16:
        return 5
    elif dt == torch.float32:
        return 6
    elif dt == torch.float64:
        return 7
    elif dt == torch.bool:
        return 0
    elif dt == torch.bfloat16:
        return 15
    else:
        return 4711


# copyright TorchSharp
# https://github.com/dotnet/TorchSharp
def _write_tensor(t, stream):
    stream.write(leb128.u.encode(_elem_type(t)))
    stream.write(leb128.u.encode(len(t.shape)))
    for s in t.shape:
        stream.write(leb128.u.encode(s))
    stream.write(t.numpy().tobytes())


# copyright TorchSharp
# https://github.com/dotnet/TorchSharp
def _save_state_sharp_dict(sd, stream):
    """
    Saves a PyToch state dictionary using the format that TorchSharp can
    read.
    :param sd: A dictionary produced by 'model.state_dict()'
    :param stream: An write stream opened for binary I/O.
    """
    stream.write(leb128.u.encode(len(sd)))
    for entry in sd:
        stream.write(leb128.u.encode(len(entry)))
        stream.write(bytes(entry, "utf-8"))
        _write_tensor(sd[entry], stream)


def save_network_as_dat(model, path):
    assert path.endswith(".dat"), "This method can only be used to save a .dat file"
    f = open(path, "wb")
    _save_state_sharp_dict(model.to("cpu").state_dict(), f)
    f.close()


# Copyright (C) 2021, Saarland University
# Copyright (C) 2021, Maximilian Köhl <koehl@cs.uni-saarland.de>
def _dump_layer(name: str, layer: torch.nn.Module) -> t.Any:
    result = {"name": name, "kind": layer.__class__.__name__}
    if isinstance(layer, torch.nn.Linear):
        result["inputSize"] = layer.in_features
        result["outputSize"] = layer.out_features
        result["hasBiases"] = getattr(layer, "bias", None) is not None
        result["weights"] = layer.weight.tolist()
        result["biases"] = layer.bias.tolist()
    elif isinstance(layer, torch.nn.ReLU):
        pass
    elif isinstance(layer, torch.nn.CELU):
        result["alpha"] = layer.alpha
    else:
        raise UnsupportedLayerError(f"layer of type {type(layer)} not supported")
    return result


# Copyright (C) 2021, Saarland University
# Copyright (C) 2021, Maximilian Köhl <koehl@cs.uni-saarland.de>
def _dump_layers(net: torch.nn.Sequential) -> t.Any:
    return [_dump_layer(name, layer) for name, layer in net.named_children()]


# Copyright (C) 2021, Saarland University
# Copyright (C) 2021, Maximilian Köhl <koehl@cs.uni-saarland.de>
def dump_nn(net: torch.nn.Module) -> str:
    if not isinstance(net, torch.nn.Sequential):
        result = net.forward(_FakeTensor())
        assert isinstance(
            result, _FakeTensor
        ), "the result of forwarding should be a `_FakeTensor`"
        layers = []
        while result.module is not None:
            layers.append(result.module)
            result = result.parent
        net = torch.nn.Sequential(*reversed(layers))
    return json.dumps({"layers": _dump_layers(net)}, indent=2)


# Copyright (C) 2021, Saarland University
# Copyright (C) 2021, Maximilian Köhl <koehl@cs.uni-saarland.de>
class _FakeTensor:
    parent: t.Optional[_FakeTensor]
    module: t.Optional[torch.nn.Module]

    def __init__(
        self,
        parent: t.Optional[_FakeTensor] = None,
        module: t.Optional[torch.nn.Module] = None,
    ):
        self.parent = parent
        self.module = module

    def __torch_function__(self, func, types, args=(), kwargs=None):
        if func is torch.functional.F.linear:
            (_, weight) = args
            bias = kwargs.get("bias", None)
            out_features, in_features = weight.shape
            module = torch.nn.Linear(in_features, out_features, bias=bias is not None)
            module.weight = weight
            if bias is not None:
                module.bias = bias
            return _FakeTensor(self, module)
        elif func is torch.functional.F.relu:
            return _FakeTensor(self, torch.nn.ReLU())
        elif func is torch.functional.F.celu:
            return _FakeTensor(self, torch.nn.CELU(alpha=kwargs.get("alpha", 1.0)))
        else:
            raise UnsupportedLayerError(
                f"unsupported function {func!r} applied to layer"
            )


def save_network_as_json(model, path):
    """save network as json file

    Args:
        model (network): network to be saved
        path (string): path to be used for saving.
    """
    assert path.endswith(".json"), "This method can only be used to save a .json file"
    f = open(path, "w")
    f.write(dump_nn(model))
    f.close()


def save_dict(d, name):
    """save the given dictionary

    Args:
        d (dictionary): dictionary to be saved
        name (string): name to be used for saving
    """
    with open(name + ".parameters", "w") as f:
        keys = d.keys()
        keys = sorted(keys)
        num = len(keys)
        for i, key in enumerate(keys):
            f.write(str(key) + ":" + str(d[key]))
            if i != num - 1:
                f.write("\n")


def save_namespace(namespace, name):
    """save the given namespace

    Args:
        namespace (namespace): namespace to be saved
        name (string): name to be used for saving
    """
    d = vars(namespace)
    save_dict(d, name)
