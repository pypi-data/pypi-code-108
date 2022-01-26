import atexit
from concurrent.futures import ALL_COMPLETED, wait
from datetime import datetime, timezone
from functools import partial
import logging
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

from numpy import ndarray

from aporia.core.base_model import BaseModel, validate_model_ready
from aporia.core.errors import handle_error
from aporia.core.logging_utils import LOGGER_NAME
from aporia.core.types.field import FieldValue
from aporia.inference.api.log_model_properties import (
    log_index_to_word_mapping,
    upload_model_artifact,
    set_feature_importance
)
from .api.inference_fragment import ActualsFragment, Fragment, PredictionFragment, RawInputsFragment
from .api.log_inference import log_inference_fragments
from .api.log_json import log_json
from .inference_queue import InferenceQueue
from .types.model_artifact import ModelArtifactType

logger = logging.getLogger(LOGGER_NAME)


class InferenceModel(BaseModel):
    """Model object for logging inference events."""

    def __init__(self, model_id: str, model_version: str):
        """Initializes an inference model object.

        Args:
            model_id: Model identifier, as received from the Aporia dashboard.
            model_version: Model version - this can be any string that represents the model
                version, such as "v1" or a git commit hash.
        """
        try:
            super().__init__(
                model_id=model_id, model_version=model_version, set_ready_when_done=False
            )

            # We keep a list of all tasks that were not awaited, to allow flushing
            # We have to do this manually to support python versions below
            # 3.7 (otherwise we could use asyncio.all_tasks())
            self._futures = []  # type: ignore
            self._queue = InferenceQueue(
                event_loop=self._event_loop,
                batch_size=self._config.queue_batch_size,
                max_size=self._config.queue_max_size,
                flush_interval=self._config.queue_flush_interval,
                flush_callback=self._flush_inference_callback,
            )

            self._model_ready = True

            if self._config.verbose:
                atexit.register(self._warn_about_unfinished_tasks)

        except Exception as err:
            config = getattr(self, "_config", None)
            handle_error(
                message_format="Model initialization failed, error: {}",
                verbose=False if config is None else config.verbose,
                throw_errors=False if config is None else config.throw_errors,
                debug=False if config is None else config.debug,
                log_level=logging.ERROR,
                original_exception=err,
            )

    @validate_model_ready
    def log_prediction(
        self,
        id: str,
        features: Union[Dict[str, FieldValue], ndarray],
        predictions: Dict[str, FieldValue],
        metrics: Optional[Dict[str, FieldValue]] = None,
        occurred_at: Optional[datetime] = None,
        confidence: Optional[Union[float, List[float]]] = None,
        raw_inputs: Optional[Dict[str, FieldValue]] = None,
        actuals: Optional[Dict[str, FieldValue]] = None,
    ):
        """Logs a single prediction.

        Args:
            id: Prediction identifier.
            features: Values for all the features in the prediction
            predictions: Prediction result
            metrics: Prediction metrics.
            occurred_at: Prediction timestamp.
            confidence: Prediction confidence.
            raw_inputs: Raw inputs of the prediction.
            actuals: Actual prediction results.

        Note:
            * If occurred_at is None, it will be reported as datetime.now()
        """
        self.log_batch_prediction(
            batch_predictions=[
                dict(
                    id=id,
                    features=features,
                    predictions=predictions,
                    metrics=metrics,
                    occurred_at=occurred_at,
                    confidence=confidence,
                    raw_inputs=raw_inputs,
                    actuals=actuals,
                )
            ]
        )

    @validate_model_ready
    def log_batch_prediction(self, batch_predictions: Iterable[dict]):
        """Logs multiple predictions.

        Args:
            batch_predictions: An iterable that produces prediction dicts.

                * Each prediction dict MUST contain the following keys:
                    * id (str): Prediction identifier.
                    * features (Dict[str, FieldValue]): Values for all the features in the prediction
                    * predictions (Dict[str, FieldValue]): Prediction result

                * Each prediction dict MAY also contain the following keys:
                    * occurred_at (datetime): Prediction timestamp.
                    * metrics (Dict[str, FieldValue]): Prediction metrics
                    * confidence (Union[float, List[float]]): Prediction confidence.
                    * raw_inputs (Dict[str, FieldValue]): Raw inputs of the prediction.
                    * actuals (Dict[str, FieldValue]) Actual prediction results.

        Notes:
            * If occurred_at is None in any of the predictions, it will be reported as datetime.now()
        """
        self._log_batch_inference(
            batch=batch_predictions,
            fragment_class=partial(PredictionFragment, timestamp=datetime.now(tz=timezone.utc)),
            error_message="Logging prediction batch failed, error: {}",
        )

    @validate_model_ready
    def log_raw_inputs(self, id: str, raw_inputs: Dict[str, FieldValue]):
        """Logs raw inputs of a single prediction.

        Args:
            id: Prediction identifier.
            raw_inputs: Raw inputs of the prediction.
        """
        self.log_batch_raw_inputs(batch_raw_inputs=[dict(id=id, raw_inputs=raw_inputs)])

    @validate_model_ready
    def log_batch_raw_inputs(self, batch_raw_inputs: Iterable[dict]):
        """Logs raw inputs of multiple predictions.

        Args:
            batch_raw_inputs: An iterable that produces raw_inputs dicts.

                * Each dict MUST contain the following keys:
                    * id (str): Prediction identifier.
                    * raw_inputs (Dict[str, FieldValue]): Raw inputs of the prediction.
        """
        self._log_batch_inference(
            batch=batch_raw_inputs,
            fragment_class=RawInputsFragment,
            error_message="Logging raw inputs batch failed, error: {}",
        )

    @validate_model_ready
    def log_actuals(self, id: str, actuals: Dict[str, FieldValue]):
        """Logs actual values of a single prediction.

        Args:
            id: Prediction identifier.
            actuals: Actual prediction results.

        Note:
            * The fields reported in actuals must be a subset of the fields reported
              in predictions.
        """
        self.log_batch_actuals(batch_actuals=[dict(id=id, actuals=actuals)])

    @validate_model_ready
    def log_batch_actuals(self, batch_actuals: Iterable[dict]):
        """Logs actual values of multiple predictions.

        Args:
            batch_actuals: An iterable that produces actuals dicts.

                * Each dict MUST contain the following keys:
                    * id (str): Prediction identifier.
                    * actuals (Dict[str, FieldValue]): Actual prediction results.

        Note:
            * The fields reported in actuals must be a subset of the fields reported
              in predictions.
        """
        self._log_batch_inference(
            batch=batch_actuals,
            fragment_class=ActualsFragment,
            error_message="Logging actuals batch failed, error: {}",
        )

    def _log_batch_inference(
        self,
        batch: Iterable[dict],
        fragment_class: Callable,
        error_message: str,
    ):
        with self.handle_error(error_message):
            fragments = [fragment_class(data_point) for data_point in batch]

            if self._config.verbose:
                for i, fragment in enumerate(fragments):
                    if fragment.is_valid():
                        logger.debug("{} {} is valid".format(fragment.type.value, i))
                    else:
                        logger.warning("{} {} is not valid".format(fragment.type.value, i))

            count = self._event_loop.run_coroutine(self._queue.put(fragments=fragments))

            dropped_fragments = len(fragments) - count
            if dropped_fragments > 0:
                logger.warning(
                    "Message queue reached size limit, dropped {} messages.".format(
                        dropped_fragments
                    )
                )

    async def _flush_inference_callback(self, fragments: List[Fragment]):
        with self.handle_error("Server error: {}", throw_errors=False):
            serialized_fragments = []
            for fragment in fragments:
                try:
                    serialized_fragments.append(fragment.serialize())
                except Exception as err:
                    logger.error("Serializing data failed, error: {}".format(err))

            if len(serialized_fragments) > 0:
                await log_inference_fragments(
                    http_client=self._http_client,
                    model_id=self.model_id,
                    model_version=self.model_version,
                    environment=self._config.environment,
                    serialized_fragments=serialized_fragments,
                    await_insert=self._config.verbose,
                )

    @validate_model_ready
    def log_json(self, data: Any):
        """Logs arbitrary data.

        Args:
            data: Data to log, must be JSON serializable
        """
        logger.debug("Logging arbitrary data.")
        with self.handle_error("Logging arbitrary data failed, error: {}"):
            future = self._event_loop.create_task(self._log_json(data=data))
            self._futures.append(future)

    async def _log_json(self, data: Any):
        with self.handle_error("Logging arbitrary data failed, error: {}", throw_errors=False):
            await log_json(
                http_client=self._http_client,
                model_id=self.model_id,
                model_version=self.model_version,
                environment=self._config.environment,
                data=data,
            )

    @validate_model_ready
    def upload_model_artifact(
        self, model_artifact: Any, artifact_type: Union[str, ModelArtifactType]
    ):
        """Uploads binary model artifact.

        Args:
            model_artifact: Binary model artifact.
            artifact_type: The type of model artifact (see below)

        Model Artifact Types:
            - onnx
            - h5
        """
        with self.handle_error("Uploading model artifact failed, error: {}"):
            artifact_type = ModelArtifactType(artifact_type)

            self._event_loop.run_coroutine(
                upload_model_artifact(
                    http_client=self._http_client,
                    model_id=self.model_id,
                    model_version=self.model_version,
                    model_artifact=model_artifact,
                    artifact_type=artifact_type,
                )
            )

    @validate_model_ready
    def set_feature_importance(self, feature_importance: Dict[str, float]):
        """Update the features' importance of the model.

        Args:
            feature_importance: feature name to importance mapping
        """
        with self.handle_error("Setting feature importance failed, error: {}", throw_errors=False):
            self._event_loop.run_coroutine(
                set_feature_importance(
                    http_client=self._http_client,
                    model_id=self.model_id,
                    model_version=self.model_version,
                    feature_importance=feature_importance
                )
            )

    @validate_model_ready
    def log_index_to_word_mapping(self, index_to_word_mapping: Dict[Any, Any]):
        """Logs index to word mapping.

        Args:
            index_to_word_mapping: A mapping between a numeric index to a word.
        """
        with self.handle_error(
            "Logging index to word mapping failed, error: {}", throw_errors=False
        ):
            self._event_loop.run_coroutine(
                log_index_to_word_mapping(
                    http_client=self._http_client,
                    model_id=self.model_id,
                    model_version=self.model_version,
                    index_to_word_mapping=index_to_word_mapping,
                )
            )

    @validate_model_ready
    def flush(self, timeout: Optional[int] = None) -> Optional[int]:
        """Waits for all currently scheduled tasks to finish.

        Args:
            timeout: Maximum number of seconds to wait for tasks to
                complete. Default to None (No timeout).

        Returns:
            Number of tasks that haven't finished running.
        """
        with self.handle_error("Flushing remaining data failed, error: {}"):
            futures = self._futures
            self._futures = []

            logger.debug("Flushing predictions.")
            # Add a task that flushes the queue, and another that waits for the flush to complete
            futures.append(self._event_loop.create_task(self._queue.flush()))
            futures.append(self._event_loop.create_task(self._queue.join()))

            logger.debug("Waiting for {} scheduled tasks to finish executing.".format(len(futures)))
            done, not_done = wait(futures, timeout=timeout, return_when=ALL_COMPLETED)

            logger.debug(
                "{} tasks finished, {} tasks not finished.".format(len(done), len(not_done))
            )
            self._futures.extend(not_done)

            return len(not_done)

        return None

    def _warn_about_unfinished_tasks(self):
        if len(self._queue) > 0:
            logger.warning(
                "The process was closed before the SDK finished flushing all of the logged "
                "predictions, please call apr_model.flush() before the end of your "
                "program to ensure that all of the predictions have reached the server."
            )
