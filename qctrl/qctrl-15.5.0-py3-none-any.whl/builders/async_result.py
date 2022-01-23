"""Module for `AsyncResult`."""
import logging
from typing import (
    List,
    Optional,
)

from graphql import GraphQLType
from tqdm.auto import tqdm

from .result_mixin import ResultMixin
from .utils import _get_function_name

LOGGER = logging.getLogger(__name__)


def _format_action(result: ResultMixin):
    """
    Returns a string representing the result's action (including name and action ID).
    """
    func_name = _get_function_name(result.action.name)
    action_id = result.action_id

    return f'{func_name} (action_id="{action_id}")'


class AsyncResult:
    """Wrapper around the result object which performs
    updating and progress reporting."""

    # statuses
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"

    def __init__(self, field_type: GraphQLType, result_object: ResultMixin):
        self._field_type = field_type
        self._result_object = result_object
        self._sent_messages = set()

    @property
    def result_object(self) -> ResultMixin:
        """Exposes the internal result object."""
        return self._result_object

    def update(self, env: "GraphQLEnvironment", data: dict, progress_bar: tqdm = None):
        """Updates the result object with the response data. Prints
        any progress updates to the progress bar."""

        env.update_data(self._field_type, self._result_object, data)

        # display progress message if required
        if progress_bar is not None:
            message = self._get_progress_message()

            if message and message not in self._sent_messages:
                progress_bar.write(message)
                self._sent_messages.add(message)

    def _get_progress_message(self) -> Optional[str]:
        """Returns the current progress message."""

        status = self._result_object.action.status
        action = _format_action(self._result_object)

        if status == self.PENDING:
            return (
                f"Your task {action} is currently in a queue waiting to be processed."
            )

        if status == self.STARTED:
            return (
                f"Your task {action} has started. You can use the `qctrl.get_result` method to "
                "retrieve previous results."
            )

        if status == self.SUCCESS:
            return f"Your task {action} has completed."

        return None


class AsyncResultCollection:
    """Represents a set of AsyncResult objects made in the one request."""

    def __init__(self, *async_results: AsyncResult):
        self._async_results = async_results
        self._current_progress = 0

    @property
    def is_completed(self) -> bool:
        """Checks if all AsyncResult objects are completed."""
        return all(  # pylint:disable=use-a-generator
            [
                async_result.result_object.is_completed
                for async_result in self._async_results
            ]
        )

    def update_progress(self, progress_bar: tqdm):
        """Updates the progress bar according to the
        current progress of the AsyncResult objects."""
        new_progress = [
            async_result.result_object.progress * 100
            for async_result in self._async_results
        ]
        new_progress = int(sum(new_progress) / len(new_progress))

        delta = new_progress - self._current_progress
        self._current_progress += delta
        progress_bar.update(delta)

    def get_action_ids(self) -> List[str]:
        """Returns the action IDs for the AsyncResult objects."""
        return [
            async_result.result_object.action_id for async_result in self._async_results
        ]

    def update_data(
        self, env: "GraphQLEnvironment", response_data: dict, progress_bar: tqdm
    ):
        """Updates the related AsyncResult objects with the response data."""

        # a single action will be returned as a dict
        if isinstance(response_data, dict):
            response_data = [response_data]

        if len(self._async_results) != len(response_data):
            raise RuntimeError(
                f"Unexpected responses ({len(response_data)}) for "
                f"results ({len(self._async_results)})"
            )

        for index, async_result in enumerate(self._async_results):
            _response_data = response_data[index]
            async_result.update(env, _response_data, progress_bar)

    def finalize(self):
        """Reports on final status."""

        # List of (identifier string, exception message) tuples for each failure.
        failures = []

        for async_result in self._async_results:

            LOGGER.info(
                "Action %s finished with status: %s",
                str(async_result.result_object.action_id),
                async_result.result_object.status,
            )

            if not async_result.result_object.is_successful:

                identifier = _format_action(async_result.result_object)

                if async_result.result_object.job_errors:
                    LOGGER.info(
                        "Action %s failed: %s",
                        async_result.result_object.action_id,
                        async_result.result_object.job_errors.exception,
                    )
                    exception = f"{async_result.result_object.job_errors.exception}"

                elif async_result.result_object.status == "FAILURE":
                    LOGGER.info(
                        "Action %s resulted with status 'FAILURE'("
                        "no extra details about the errors are "
                        "available).",
                        async_result.result_object.action_id,
                    )
                    exception = "Unknown failure"

                failures.append((identifier, exception))

        if not failures:
            return

        failure_message = "\n".join(": ".join(failure) for failure in failures)

        if len(self._async_results) == 1:
            raise RuntimeError(failure_message)

        raise RuntimeError(
            f"Action failures: {len(failures)} of {len(self._async_results)}\n"
            f"{failure_message}"
        )
