# -*- coding: utf-8 -*-
import json
import os
import sys
import uuid
from enum import Enum

from apistar.exceptions import ErrorResponse

from arkindex_worker import logger
from arkindex_worker.cache import CachedElement
from arkindex_worker.models import Element
from arkindex_worker.reporting import Reporter
from arkindex_worker.worker.base import BaseWorker
from arkindex_worker.worker.classification import ClassificationMixin
from arkindex_worker.worker.element import ElementMixin
from arkindex_worker.worker.entity import EntityMixin, EntityType  # noqa: F401
from arkindex_worker.worker.metadata import MetaDataMixin, MetaType  # noqa: F401
from arkindex_worker.worker.transcription import TranscriptionMixin
from arkindex_worker.worker.version import WorkerVersionMixin  # noqa: F401


class ActivityState(Enum):
    Queued = "queued"
    Started = "started"
    Processed = "processed"
    Error = "error"


class ElementsWorker(
    BaseWorker,
    ClassificationMixin,
    ElementMixin,
    TranscriptionMixin,
    WorkerVersionMixin,
    EntityMixin,
    MetaDataMixin,
):
    def __init__(self, description="Arkindex Elements Worker", support_cache=False):
        super().__init__(description, support_cache)

        # Add report concerning elements
        self.report = Reporter("unknown worker")

        # Add mandatory argument to process elements
        self.parser.add_argument(
            "--elements-list",
            help="JSON elements list to use",
            type=open,
            default=os.environ.get("TASK_ELEMENTS"),
        )
        self.parser.add_argument(
            "--element",
            type=uuid.UUID,
            nargs="+",
            help="One or more Arkindex element ID",
        )
        self.classes = {}

        self._worker_version_cache = {}

    def list_elements(self):
        assert not (
            self.args.elements_list and self.args.element
        ), "elements-list and element CLI args shouldn't be both set"
        out = []

        # Load from the cache when available
        # Flake8 wants us to use 'is True', but Peewee only supports '== True'
        cache_query = CachedElement.select().where(
            CachedElement.initial == True  # noqa: E712
        )
        if self.use_cache and cache_query.exists():
            return cache_query
        # Process elements from JSON file
        elif self.args.elements_list:
            data = json.load(self.args.elements_list)
            assert isinstance(data, list), "Elements list must be a list"
            assert len(data), "No elements in elements list"
            out += list(filter(None, [element.get("id") for element in data]))
        # Add any extra element from CLI
        elif self.args.element:
            out += self.args.element

        return out

    @property
    def store_activity(self):
        if self.args.dev:
            return False
        assert (
            self.process_information
        ), "Worker must be configured to access its process activity state"
        return self.process_information.get("activity_state") == "ready"

    def run(self):
        """
        Process every elements from the provided list
        """
        self.configure()

        # List all elements either from JSON file
        # or direct list of elements on CLI
        elements = self.list_elements()
        if not elements:
            logger.warning("No elements to process, stopping.")
            sys.exit(1)

        if not self.store_activity:
            logger.info(
                "No worker activity will be stored as it is disabled for this process"
            )

        # Process every element
        count = len(elements)
        failed = 0
        for i, item in enumerate(elements, start=1):
            element = None
            try:
                if self.use_cache:
                    # Just use the result of list_elements as the element
                    element = item
                else:
                    # Load element using the Arkindex API
                    element = Element(**self.request("RetrieveElement", id=item))

                logger.info(f"Processing {element} ({i}/{count})")

                # Process the element and report its progress if activities are enabled
                if self.update_activity(element.id, ActivityState.Started):
                    self.process_element(element)
                    self.update_activity(element.id, ActivityState.Processed)
                else:
                    logger.info(
                        f"Skipping element {element.id} as it was already processed"
                    )
                    continue
            except Exception as e:
                # Handle errors occurring while retrieving, processing or patching the activity for this element.
                # Count the element as failed in case the activity update to "started" failed with no conflict.
                # This prevent from processing the element
                failed += 1

                # Handle the case where we failed retrieving the element
                element_id = element.id if element else item

                if isinstance(e, ErrorResponse):
                    message = f"An API error occurred while processing element {element_id}: {e.title} - {e.content}"
                else:
                    message = f"Failed running worker on element {element_id}: {e}"

                logger.warning(
                    message,
                    exc_info=e if self.args.verbose else None,
                )
                if element:
                    # Try to update the activity to error state regardless of the response
                    try:
                        self.update_activity(element.id, ActivityState.Error)
                    except Exception:
                        pass
                self.report.error(element_id, e)

        # Save report as local artifact
        self.report.save(os.path.join(self.work_dir, "ml_report.json"))

        if failed:
            logger.error(
                "Ran on {} elements: {} completed, {} failed".format(
                    count, count - failed, failed
                )
            )
            if failed >= count:  # Everything failed!
                sys.exit(1)

    def process_element(self, element):
        """Override this method to analyze an Arkindex element from the provided list"""

    def update_activity(self, element_id, state):
        """
        Update worker activity for this element
        Returns False when there is a conflict initializing the activity
        Otherwise return True or the response payload
        """
        if not self.store_activity:
            logger.debug(
                "Activity is not stored as the feature is disabled on this process"
            )
            return True

        assert element_id and isinstance(
            element_id, (uuid.UUID, str)
        ), "element_id shouldn't be null and should be an UUID or str"
        assert isinstance(state, ActivityState), "state should be an ActivityState"

        if self.is_read_only:
            logger.warning("Cannot update activity as this worker is in read-only mode")
            return True

        try:
            self.request(
                "UpdateWorkerActivity",
                id=self.worker_version_id,
                body={
                    "element_id": str(element_id),
                    "process_id": self.process_information["id"],
                    "state": state.value,
                },
            )
        except ErrorResponse as e:
            if state == ActivityState.Started and e.status_code == 409:
                # 409 conflict error when updating the state of an activity to "started" mean that we
                # cannot process this element. We assume that the reason is that the state transition
                # was forbidden i.e. that the activity was already in a started or processed state.
                # This allow concurrent access to an element activity between multiple processes.
                # Element should not be counted as failed as it is probably handled somewhere else.
                logger.debug(
                    f"Cannot start processing element {element_id} due to a conflict. "
                    f"Another process could have processed it with the same version already."
                )
                return False
            logger.warning(
                f"Failed to update activity of element {element_id} to {state.value} due to an API error: {e.content}"
            )
            raise e

        logger.debug(f"Updated activity of element {element_id} to {state}")
        return True
