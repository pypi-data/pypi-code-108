import torch as tr
import numpy as np
from typing import List, Union

class Message:
    def __init__(self, path:List, input:Union[np.ndarray, tr.Tensor], output:Union[np.ndarray, tr.Tensor]):
        self.path = tuple(path)
        self.input = input
        self.output = output
        assert isinstance(self.path, tuple), f"Wrong type: {type(self.path)}"
        assert isinstance(self.input, (np.ndarray, tr.Tensor)), "Wrong type: {type(self.inpput)}"
        assert isinstance(self.output, (np.ndarray, tr.Tensor)), "Wrong type: {type(self.output)}"

    def __repr__(self) -> str:
        return str(self)

    def summary(self) -> str:
        strInput = self.input.shape if self.input is not None else None
        Str = f"[Message] Path: {self.path}. Input Shape: {strInput}. Output Shape: {self.output.shape}"
        return Str

    def __str__(self) -> str:
        from .edge import Edge
        strItems = []
        for item in self.path:
            if isinstance(item, Edge):
                strType = str(type(item)).split(".")[-1][0 : -2]
                A, B = item.inputNode, item.outputNode
                item = f"[{A} -> {B} ({strType})]"
            strItems.append(item)
        return " -> ".join(strItems)

    # These are so we can use sets in the graph library to add unique nodes only.
    def __eq__(self, other):
        Input = self.input.cpu() if isinstance(self.input, tr.Tensor) else self.input
        Other = other.input.cpu() if isinstance(other.input, tr.Tensor) else other.input
        return np.allclose(Input, Other)

    def __hash__(self):
        try:
            return hash(self.path)
        except:
            assert False, self.path
