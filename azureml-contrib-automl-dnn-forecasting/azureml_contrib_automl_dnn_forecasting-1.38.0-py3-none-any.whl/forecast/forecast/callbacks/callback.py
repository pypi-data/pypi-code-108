"""Non user-facing callbacks which are leveraged by derived types or the `Forecaster` itself."""

from typing import Mapping, MutableMapping, Optional, Sequence

import torch

from forecast.metrics import Metric
from forecast.models import ForecastingModel


class Callback:
    """The base callback from which all callbacks are derived."""

    def __init__(self) -> None:
        """Instantiates a callback."""
        self._model: Optional[ForecastingModel] = None

    def set_model(self, model: ForecastingModel) -> None:
        """Sets the callback's model reference.

        Parameters
        ----------
        model: ForecastingModel
            The model to be trained

        Returns
        -------
        None

        """
        self._model = model

    def on_train_begin(self) -> None:
        """Invoked prior to the beginning of training in `model.fit()`."""
        pass

    def on_train_end(self) -> None:
        """Invoked just prior to completion of training in `model.fit()`."""
        pass

    def on_train_epoch_begin(self, epoch: int) -> None:
        """Invoked prior to the beginning of an epoch in `model.fit()`."""
        pass

    def on_train_epoch_end(self, epoch: int, loss: float, metrics: Mapping[str, float]) -> None:
        """Invoked after a training epoch but before a evaluating the validation dataset in `model.fit()`."""
        pass

    def on_train_batch_begin(self, epoch: int, batch: int) -> None:
        """Invoked prior to the beginning of a training batch in `model.fit()`."""
        pass

    def on_train_batch_end(self, epoch: int, batch: int, loss: float) -> None:
        """Invoked after a training batch in `model.fit()`."""
        pass

    def on_train_batch_before_backward(self, loss: torch.Tensor) -> None:
        """Invoked prior to `loss.backward()` in a training batch; this is useful for modifying the loss."""
        pass

    def on_train_batch_before_step(self) -> None:
        """Invoked prior to `optimizer.step()` in a training batch; this is useful for modifying the gradients."""
        pass

    def on_val_begin(self, epoch: int) -> None:
        """Invoked prior to evaluating the val dataset in `model.fit()`."""
        pass

    def on_val_end(self, epoch: int, loss: float, metrics: Mapping[str, float]) -> None:
        """Invoked after evaluating the val dataset in `model.fit()`."""
        pass

    def on_val_batch_begin(self, epoch: int, batch: int) -> None:
        """Invoked prior to evaluating a batch in `model.fit()`."""
        pass

    def on_val_batch_end(self, epoch: int, batch: int, loss: float) -> None:
        """Invoked after evaluating a batch in `model.fit()`."""
        pass

    def on_train_val_epoch_end(self, epoch: int) -> None:
        """Invoked after a train/val on an epoch, regardless of whether a val dataset is provided."""
        pass

    def on_predict_begin(self) -> None:
        """Invoked prior to beginning inference in `model.predict()`."""
        pass

    def on_predict_end(self) -> None:
        """Invoked upon completion of inference in `model.predict()`."""
        pass

    def on_predict_batch_begin(self, batch: int) -> None:
        """Invoked prior to beginning inference of a batch in `model.predict()`."""
        pass

    def on_predict_batch_end(self, batch: int) -> None:
        """Invoked upon completion of inference of a batch in `model.predict()`."""
        pass


class CallbackList(Callback):
    """Encapsulates a ordered sequence of callbacks into a single callback invocation."""

    def __init__(self, callbacks: Sequence[Callback], model: ForecastingModel):
        """Encapsulates a ordered sequence of callbacks into a single callback invocation.

        Parameters
        ----------
        callbacks: Sequence[Callback]
            An ordered sequence of callbacks to be invoked

        """
        super().__init__()
        self._callbacks = list(callbacks)
        self.set_model(model)

        # subclasses of `Forecaster` may implement custom train_batch and predict_batch methods. These vars are
        # set to False in `on_train_batch_begin`, set to True in their corresponding methods, and inspected in
        # `on_train_batch_end`. If these methods were found not to be invoked, which could potentially break one or
        # more callbacks, a RuntimeError is raised.
        self._invoked_on_train_batch_before_backward = False
        self._invoked_on_train_batch_before_step = False

    def set_model(self, model: ForecastingModel) -> None:
        """Sets the callbacks' model references.

        Parameters
        ----------
        model: ForecastingModel
            The model to be trained

        Returns
        -------
        None

        """
        for cb in self._callbacks:
            cb.set_model(model)

    def on_train_begin(self) -> None:
        """Invoked prior to the beginning of training in `model.fit()`."""
        for cb in self._callbacks:
            cb.on_train_begin()

    def on_train_end(self) -> None:
        """Invoked just prior to completion of training in `model.fit()`."""
        for cb in self._callbacks:
            cb.on_train_end()

    def on_train_epoch_begin(self, epoch: int) -> None:
        """Invoked prior to the beginning of an epoch in `model.fit()`."""
        for cb in self._callbacks:
            cb.on_train_epoch_begin(epoch)

    def on_train_epoch_end(self, epoch: int, loss: float, metrics: Mapping[str, float]) -> None:
        """Invoked after a training epoch but before a evaluating the validation dataset in `model.fit()`."""
        for cb in self._callbacks:
            cb.on_train_epoch_end(epoch, loss, metrics)

    def on_train_batch_begin(self, epoch: int, batch: int) -> None:
        """Invoked prior to the beginning of a training batch in `model.fit()`."""
        self._invoked_on_train_batch_before_backward = False
        self._invoked_on_train_batch_before_step = False
        for cb in self._callbacks:
            cb.on_train_batch_begin(epoch, batch)

    def on_train_batch_end(self, epoch: int, batch: int, loss: float) -> None:
        """Invoked after a training batch in `model.fit()`."""
        if not self._invoked_on_train_batch_before_backward:
            raise RuntimeError('`on_train_batch_end` invoked without calling `on_train_batch_before_backward`. '
                               'If you have subclassed `Forecaster`, please invoke this method in `train_batch`.')
        elif not self._invoked_on_train_batch_before_step:
            raise RuntimeError('`on_train_batch_end` invoked without calling `on_train_batch_before_step`. '
                               'If you have subclassed `Forecaster`, please invoke this method in `train_batch`.')
        for cb in self._callbacks:
            cb.on_train_batch_end(epoch, batch, loss)

    def on_train_batch_before_backward(self, loss: torch.Tensor) -> None:
        """Invoked prior to `loss.backward()` in a training batch; this is useful for modifying the loss IN-PLACE."""
        self._invoked_on_train_batch_before_backward = True
        for cb in self._callbacks:
            cb.on_train_batch_before_backward(loss)

    def on_train_batch_before_step(self) -> None:
        """Invoked prior to `opt.step()` in a training batch; this is useful for modifying the gradients IN-PLACE."""
        self._invoked_on_train_batch_before_step = True
        for cb in self._callbacks:
            cb.on_train_batch_before_step()

    def on_val_begin(self, epoch: int) -> None:
        """Invoked prior to evaluating the val dataset in `model.fit()`."""
        for cb in self._callbacks:
            cb.on_val_begin(epoch)

    def on_val_end(self, epoch: int, loss: float, metrics: Mapping[str, float]) -> None:
        """Invoked after evaluating the val dataset in `model.fit()`."""
        for cb in self._callbacks:
            cb.on_val_end(epoch, loss, metrics)

    def on_val_batch_begin(self, epoch: int, batch: int) -> None:
        """Invoked prior to evaluating a batch in `model.fit()`."""
        for cb in self._callbacks:
            cb.on_val_batch_begin(epoch, batch)

    def on_val_batch_end(self, epoch: int, batch: int, loss: float) -> None:
        """Invoked after evaluating a batch in `model.fit()`."""
        for cb in self._callbacks:
            cb.on_val_batch_end(epoch, batch, loss)

    def on_train_val_epoch_end(self, epoch: int) -> None:
        """Invoked after a train/val on an epoch, regardless of whether a val dataset is provided."""
        for cb in self._callbacks:
            cb.on_train_val_epoch_end(epoch)

    def on_predict_begin(self) -> None:
        """Invoked prior to beginning inference in `model.predict()`."""
        for cb in self._callbacks:
            cb.on_predict_begin()

    def on_predict_end(self) -> None:
        """Invoked upon completion of inference in `model.predict()`."""
        for cb in self._callbacks:
            cb.on_predict_end()

    def on_predict_batch_begin(self, batch: int) -> None:
        """Invoked prior to beginning inference of a batch in `model.predict()`."""
        for cb in self._callbacks:
            cb.on_predict_batch_begin(batch)

    def on_predict_batch_end(self, batch: int) -> None:
        """Invoked upon completion of inference of a batch in `model.predict()`."""
        for cb in self._callbacks:
            cb.on_predict_batch_end(batch)


class MetricCallback(Callback):
    """A callback which computes the train and validation metrics upon epoch end."""

    def __init__(self, train_metrics: Mapping[str, Metric], val_metrics: Mapping[str, Metric]):
        """A callback which computes the train and validation metrics upon epoch end.

        Parameters
        ----------
        train_metrics: Mapping[str, Metric]
            The metrics which should be executed upon completion of an epoch of the training dataset
        val_metrics: Mapping[str, Metric]
            The metrics which should be computed upon completion of an epoch of the validation dataset

        """
        super().__init__()
        self._train_metrics = train_metrics
        self._val_metrics = val_metrics

    def on_train_epoch_begin(self, epoch: int) -> None:
        """Resets the state of the training metrics."""
        for cb in self._train_metrics.values():
            cb.reset_state()

    def on_train_epoch_end(self, epoch: int, loss: float, metrics: MutableMapping[str, float]) -> None:  # type: ignore
        """Computes the training metrics and populates the metrics mapping.

        Parameters
        ----------
        epoch: int
            The current epoch
        loss: float
            The current loss value for the training dataset
        metrics: MutableMapping[str, float]
            The mutable mapping which will be populated with the various metrics

        Returns
        -------
        None

        """
        for name, cb in self._train_metrics.items():
            metrics[name] = cb.result()

    def on_val_begin(self, epoch: int) -> None:
        """Resets the state of the validation metrics."""
        for cb in self._val_metrics.values():
            cb.reset_state()

    def on_val_end(self, epoch: int, loss: float, metrics: MutableMapping[str, float]) -> None:  # type: ignore
        """Computes the validation metrics and populates the metrics mapping.

        Parameters
        ----------
        epoch: int
            The current epoch
        loss: float
            The current loss value for the validation dataset
        metrics: MutableMapping[str, float]
            The mutable mapping which will be populated with the various metrics

        Returns
        -------
        None

        """
        for name, cb in self._val_metrics.items():
            metrics[name] = cb.result()
