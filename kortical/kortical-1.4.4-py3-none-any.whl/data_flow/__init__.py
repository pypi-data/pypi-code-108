from functools import wraps
from . import data_flow_node_api


def transform(*args):
    data_ids = args

    def real_decorator(func):
        @wraps(func)
        def func_wrapper(data):
            reduced_data = {}
            for d in data_ids:
                if not d in data:
                    raise Exception(f"Function [{func.__name__}] requires [{d}] but it is not present in data.")
                reduced_data[d] = data[d][0]
            output = func(reduced_data)
            return output

        func_wrapper.data_ids = data_ids
        return func_wrapper
    return real_decorator


class DataFlow(data_flow_node_api.DataFlowNodeApi):

    def __init__(self):
        super().__init__("data_flow")
        self.hash = "hash"

    def get_hash(self):
        return self.hash

    def run(self, data_dict={}, run_tests=True, cache_data=True):
        layer_index = 0
        layers = [set()]
        layers[layer_index].update(self._children)
        while True:
            children = set()
            for c in layers[layer_index]:
                children.update(c._children)
            if len(children) == 0:
                break
            layers.append(children)
            layer_index += 1

        # Check that layers don't overlap and fix
        to_remove = []
        for layer_index in range(len(layers)-1):
            for c in layers[layer_index]:
                for layer_index2 in range(layer_index+1, len(layers)):
                    if c in layers[layer_index2]:
                        to_remove.append([layer_index, c])

        for layer_index, node in to_remove:
            layers[layer_index].remove(node)

        if len(data_dict) > 0 and cache_data:
            raise Exception("Dynamic parameters are not compatible with caching.")
        data = {k: [v, None] for k, v in data_dict.items()}
        for l in layers:
            new_data = {}
            for c in l:
                output = c._run(data, run_tests, cache_data)
                if output:
                    for k, v in output.items():
                        if k in new_data:
                            raise Exception(f"The same layer can't produce the data [{k}] in two children.")
                    new_data.update(output)
            data.update(new_data)
        return {} if output is None else {k: v[0] for k, v in output.items()}