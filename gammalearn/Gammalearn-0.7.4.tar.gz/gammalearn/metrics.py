from collections import deque
import torch
from torchmetrics import Metric
from torchmetrics.functional import auroc
from .constants import GAMMA_ID


class AUCMultiClass(Metric):
    r"""
    Computes the area under the roc curve for a series of batches.
    Gamma is the positive class.
    """
    def __init__(
            self,
            compute_on_step=True,
            dist_sync_on_step=False,
            average='macro',
            process_group=None,
            dist_sync_fn=None,
            positive_class=GAMMA_ID,
            buffer_size=None,
    ):
        super().__init__(
            compute_on_step=compute_on_step,
            dist_sync_on_step=dist_sync_on_step,
            process_group=process_group,
            dist_sync_fn=dist_sync_fn,
        )

        self.positive_class = positive_class
        self.window = buffer_size
        self.average = average

        pred_buffer = []
        target_buffer = []

        self.add_state("predictions", default=pred_buffer,  dist_reduce_fx=None)
        self.add_state("targets", default=target_buffer, dist_reduce_fx=None)

    def update(self, preds, target):
        """
        Update state with predictions and targets.

        Args:
            preds: Predictions from model (after a log_softmax)
            target: Ground truth values
        """
        binarized_class = torch.ones_like(target)
        binarized_class[target != self.positive_class] = 0

        self.predictions.append(preds[:, self.positive_class])
        self.targets.append(binarized_class)
        if len(self.predictions) > self.window:
            self.predictions.pop(0)
        if len(self.targets) > self.window:
            self.targets.pop(0)

    def compute(self):
        """
        Computes auc over state.
        """
        _predictions = torch.cat(self.predictions)
        _targets = torch.cat(self.targets)
        if len(torch.unique(_targets)) > 1:
            return auroc(_predictions, _targets)
        else:
            return torch.tensor(0, device=_targets.device)

