from tensorflow.keras.callbacks import Callback
from mlsteam.track import Track


class MLSteamCallback(Callback):
    def __init__(self, track: Track):
        super().__init__()
        self._track = track
        # self._track.tags_set(['keras'])
    
    def _log_metrics(self, logs, category: str, trigger: str):
        if not logs:
            return

        namespace = f"{category}/{trigger}"
        for metric, value in logs.items():
            try:
                if metric in ('batch', 'size') or metric.startswith('val_'):
                    continue
                self._track[f"{namespace}/{metric}"].log(value)
            except Exception:
                pass

    def on_train_batch_end(self, batch, logs=None):  # pylint:disable=unused-argument
        self._log_metrics(logs, 'train', 'batch')

    def on_epoch_end(self, epoch, logs=None):  # pylint:disable=unused-argument
        self._log_metrics(logs, 'train', 'epoch')

    def on_test_batch_end(self, batch, logs=None):  # pylint:disable=unused-argument
        self._log_metrics(logs, 'test', 'batch')

    def on_test_end(self, logs=None):
        self._log_metrics(logs, 'test', 'epoch')
