from typing import Container, Sequence

import numpy as np
import torch
from catalyst.callbacks import IMetricCallback
from catalyst.contrib.tools import SummaryWriter
from catalyst.core import IRunner
from torch.utils.data import SequentialSampler

from dnn_cool.tensorboard.base import ITensorboardPublisher


class SingleLossInterpretationCallback(IMetricCallback):
    def __init__(
            self,
            criterion,
            loaders_to_skip: Container[str] = (),
            prefix: str = "",
            input_key: str = "targets",
            output_key: str = "logits",
            idx_key=None,
            top_k=10,
            tensorboard_sequence: Sequence = None,
            tensorboard_publishers: Sequence[ITensorboardPublisher] = (),
            **loss_kwargs,
    ):
        super().__init__(prefix, input_key, output_key, **loss_kwargs)
        self.metric = criterion
        self.interpretations = {}
        self.top_k = top_k
        self.loggers = {}
        self.tensorboard_sequence = tensorboard_sequence
        self.tensorboard_publishers = tensorboard_publishers
        self._loaders_to_skip = loaders_to_skip
        self._idx_key = idx_key

    def _should_interpret_loader(self, runner: IRunner):
        if runner.loader_key in self._loaders_to_skip:
            return False
        if isinstance(runner.loaders[runner.loader_key].sampler, SequentialSampler):
            return True

        """
        If the sampler is not sequential, we cannot recover the original index of the sample,
        unless the user has provided `idx_key`.
        See: https://github.com/catalyst-team/catalyst/issues/950#issuecomment-703220633
        """
        return self._idx_key is not None

    def on_loader_start(self, runner: IRunner):
        if not self._should_interpret_loader(runner):
            return
        if runner.loader_key not in self.loggers:
            logdir = runner.logdir / f"{runner.loader_key}_log"
            self.loggers[runner.loader_key] = SummaryWriter(str(logdir))
        if runner.loader_key not in self.interpretations:
            self.interpretations[runner.loader_key] = {
                "loss": [],
                "indices": [],
            }

    def on_loader_end(self, runner: IRunner):
        if not self._should_interpret_loader(runner):
            return

        self.interpretations[runner.loader_key] = {
            key: np.concatenate(value, axis=0)
            for key, value in self.interpretations[runner.loader_key].items()
        }

        out_file = runner.logdir / f"{runner.loader_key}_interpretations.pkl"
        torch.save(self.interpretations[runner.loader_key], out_file)

        loss_sorter = self.interpretations[runner.loader_key]["loss"].argsort()
        indices_sorted = self.interpretations[runner.loader_key]["indices"][loss_sorter]
        indices = {
            "best": indices_sorted[: self.top_k],
            "worst": indices_sorted[-self.top_k:][::-1],
        }

        writer: SummaryWriter = self.loggers[runner.loader_key]
        for type_prefix in ["best", "worst"]:
            for idx in indices[type_prefix]:
                tag = f"{self.prefix}{type_prefix}"
                for tensorboard_publisher in self.tensorboard_publishers:
                    sample = self.tensorboard_sequence[idx]
                    tensorboard_publisher(writer, tag, sample, idx)

    def on_batch_end(self, runner: IRunner):
        if not self._should_interpret_loader(runner):
            return
        if self.metric is None:
            return
        loss_items: torch.Tensor = self._compute_metric_value(runner.output, runner.input)
        if len(loss_items.shape) > 1:
            dims = tuple(range(1, len(loss_items.shape)))
            loss_items = loss_items.mean(dim=dims)

        if self._idx_key is None:
            bs = len(loss_items)
            indices_so_far = self.interpretations[runner.loader_key]["indices"]
            start_idx = (0 if len(indices_so_far) == 0 else (indices_so_far[-1][-1] + 1))
            indices = np.arange(start_idx, start_idx + bs)
        else:
            indices = runner.input[self._idx_key].detach().cpu().numpy()

        self.interpretations[runner.loader_key]["loss"].append(loss_items.detach().cpu().numpy())
        self.interpretations[runner.loader_key]["indices"].append(indices)

    @property
    def metric_fn(self):
        return self.metric