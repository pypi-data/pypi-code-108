from typing import Optional

import numpy as np
from catalyst.core import Callback, CallbackOrder, IRunner

from dnn_cool.catalyst_utils.base import should_skip_loader
from dnn_cool.serialization.base import to_dict_of_lists
from dnn_cool.tensorboard.base import TensorboardConverters


class InterpretationCallback(Callback):
    """
    This callback publishes best and worst images per task, according to the configuration supplied via the constructor.
    """

    def __init__(self, per_sample_criterion,
                 tensorboard_converters: Optional[TensorboardConverters] = None,
                 infer_logdir=None,
                 loaders_to_skip=()):
        """
        :param flow: The task flow, which holds the per sample loss functions for every task.

        :param tensorboard_converters: A :class:`TensorboardConverters` object which is responsible for the Tensorboard
        logging settings.

        :param loaders_to_skip: Optional loaders to be skipped, for example because labels aren't available for them.
        """
        super().__init__(CallbackOrder.Metric)
        self.loaders_to_skip = loaders_to_skip

        self.overall_loss = per_sample_criterion
        self.leaf_losses = self.overall_loss.get_leaf_losses_per_sample()
        self.interpretations = {}
        self.loader_counts = {}
        self.infer_logdir = infer_logdir
        self.tensorboard_converters = tensorboard_converters

    def _initialize_interpretations(self):
        interpretation_dict = {
            'overall': [],
            'indices|overall': []
        }
        for path in self.leaf_losses:
            interpretation_dict[path] = []
            interpretation_dict[f'indices|{path}'] = []
        return interpretation_dict

    def on_loader_start(self, state: IRunner):
        if should_skip_loader(state, self.loaders_to_skip):
            return
        self.interpretations[state.loader_key] = self._initialize_interpretations()
        self.loader_counts[state.loader_key] = 0

        if self.tensorboard_converters is not None:
            self.tensorboard_converters.initialize(state)

    def on_batch_end(self, state: IRunner):
        if should_skip_loader(state, self.loaders_to_skip):
            return
        outputs = state.output['logits']
        targets = state.input['targets']
        overall_res = self.overall_loss(outputs, targets)
        start = self.loader_counts[state.loader_key]

        n = 0
        for path, loss in overall_res.items():
            if path.startswith('indices'):
                continue
            self.interpretations[state.loader_key][path].append(loss.detach().cpu().numpy())
            ind_key = f'indices|{path}'
            indices = overall_res[ind_key] + start
            self.interpretations[state.loader_key][ind_key].append(indices.detach().cpu().numpy())
            n = len(indices)

        self.loader_counts[state.loader_key] += n

    def on_loader_end(self, state: IRunner):
        if should_skip_loader(state, self.loaders_to_skip):
            return
        self.interpretations[state.loader_key] = self.prepare_interpretations(state)

        if self.tensorboard_converters is not None:
            self.tensorboard_converters.publish(state, self.interpretations[state.loader_key])
        nested_dict = self.interpretations[state.loader_key]
        self.interpretations[state.loader_key] = to_dict_of_lists(self.interpretations[state.loader_key],
                                                                  nested_dict,
                                                                  self.infer_logdir,
                                                                  'interpretations',
                                                                  state.loader_key,
                                                                  interpretation_mode=True)

    def prepare_interpretations(self, state):
        res = {}
        for key, value in self.interpretations[state.loader_key].items():
            arrs = []
            for arr in value:
                try:
                    if len(arr) > 0:
                        arrs.append(arr)
                except TypeError:
                    pass
            value = np.concatenate(arrs)
            res[key] = value
        return res

    def on_stage_end(self, state: IRunner):
        if should_skip_loader(state, self.loaders_to_skip):
            return
        if self.tensorboard_converters is not None:
            self.tensorboard_converters.close(state)


