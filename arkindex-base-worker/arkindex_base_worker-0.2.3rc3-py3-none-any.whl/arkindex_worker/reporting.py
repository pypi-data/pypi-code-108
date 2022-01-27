# -*- coding: utf-8 -*-
import json
import traceback
from collections import Counter
from datetime import datetime

from apistar.exceptions import ErrorResponse

from arkindex_worker import logger


class Reporter(object):
    def __init__(self, name):
        # TODO: use real data from workers
        self.report_data = {
            "slug": name,
            "version": "0.0",
            "started": datetime.utcnow().isoformat(),
            "elements": {},
        }
        logger.info(f"Starting ML report for {name}")

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.report_data["slug"])

    def _get_element(self, element_id):
        return self.report_data["elements"].setdefault(
            str(element_id),
            {
                "started": datetime.utcnow().isoformat(),
                # Created element counts, by type slug
                "elements": {},
                # Created transcriptions count
                "transcriptions": 0,
                # Created classification counts, by class
                "classifications": {},
                # Created entities ({"id": "", "type": "", "name": ""}) from this element
                "entities": [],
                # Created metadata ({"id": "", "type": "", "name": ""}) from this element
                "metadata": [],
                "errors": [],
            },
        )

    def process(self, element_id):
        """
        Report that a specific element ID is being processed.
        """
        # Just call the element initializer
        self._get_element(element_id)

    def add_element(self, parent_id, type, type_count=1):
        """
        Report creating a single element with a parent.
        Multiple elements with the same type and parent can be declared with the type_count parameter.
        """
        elements = self._get_element(parent_id)["elements"]
        elements.setdefault(type, 0)
        elements[type] += type_count

    def add_classification(self, element_id, class_name):
        """
        Report creating a classification on an element.
        """
        classifications = self._get_element(element_id)["classifications"]
        classifications.setdefault(class_name, 0)
        classifications[class_name] += 1

    def add_classifications(self, element_id, classifications):
        """
        Report one or more classifications at once.
        """
        assert isinstance(
            classifications, list
        ), "A list is required for classifications"
        element = self._get_element(element_id)
        # Retrieve the previous existing classification counts, if any
        counter = Counter(**element["classifications"])
        # Add the new ones
        counter.update(
            [classification["class_name"] for classification in classifications]
        )
        element["classifications"] = dict(counter)

    def add_transcription(self, element_id, count=1):
        """
        Report creating a transcription on an element.
        Multiple transcriptions with the same parent can be declared with the type_count parameter.
        """
        self._get_element(element_id)["transcriptions"] += count

    def add_entity(self, element_id, entity_id, type, name):
        """
        Report creating an entity from an element.
        """
        entities = self._get_element(element_id)["entities"]
        entities.append({"id": entity_id, "type": type, "name": name})

    def add_entity_link(self, *args, **kwargs):
        raise NotImplementedError

    def add_entity_role(self, *args, **kwargs):
        raise NotImplementedError

    def add_metadata(self, element_id, metadata_id, type, name):
        """
        Report creating a metadata from an element.
        """
        metadata = self._get_element(element_id)["metadata"]
        metadata.append({"id": metadata_id, "type": type, "name": name})

    def error(self, element_id, exception):
        error_data = {
            "class": exception.__class__.__name__,
            "message": str(exception),
        }
        if exception.__traceback__ is not None:
            error_data["traceback"] = "\n".join(
                traceback.format_tb(exception.__traceback__)
            )

        if isinstance(exception, ErrorResponse):
            error_data["message"] = exception.title
            error_data["status_code"] = exception.status_code
            error_data["content"] = exception.content

        self._get_element(element_id)["errors"].append(error_data)

    def save(self, path):
        logger.info(f"Saving ML report to {path}")
        with open(path, "w") as f:
            json.dump(self.report_data, f)
