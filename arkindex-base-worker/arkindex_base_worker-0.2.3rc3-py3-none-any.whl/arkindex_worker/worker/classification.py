# -*- coding: utf-8 -*-
import os

from apistar.exceptions import ErrorResponse
from peewee import IntegrityError

from arkindex_worker import logger
from arkindex_worker.cache import CachedClassification, CachedElement
from arkindex_worker.models import Element


class ClassificationMixin(object):
    def load_corpus_classes(self, corpus_id):
        """
        Load ML classes for the given corpus ID
        """
        corpus_classes = self.api_client.paginate(
            "ListCorpusMLClasses",
            id=corpus_id,
        )
        self.classes[corpus_id] = {
            ml_class["name"]: ml_class["id"] for ml_class in corpus_classes
        }
        logger.info(f"Loaded {len(self.classes[corpus_id])} ML classes")

    def get_ml_class_id(self, corpus_id, ml_class):
        """
        Return the ID corresponding to the given class name on a specific corpus
        This method will automatically create missing classes
        """
        if corpus_id is None:
            corpus_id = os.environ.get("ARKINDEX_CORPUS_ID")

        if not self.classes.get(corpus_id):
            self.load_corpus_classes(corpus_id)

        ml_class_id = self.classes[corpus_id].get(ml_class)
        if ml_class_id is None:
            logger.info(f"Creating ML class {ml_class} on corpus {corpus_id}")
            try:
                response = self.request(
                    "CreateMLClass", id=corpus_id, body={"name": ml_class}
                )
                ml_class_id = self.classes[corpus_id][ml_class] = response["id"]
                logger.debug(f"Created ML class {response['id']}")
            except ErrorResponse as e:
                # Only reload for 400 errors
                if e.status_code != 400:
                    raise

                # Reload and make sure we have the class
                logger.info(
                    f"Reloading corpus classes to see if {ml_class} already exists"
                )
                self.load_corpus_classes(corpus_id)
                assert (
                    ml_class in self.classes[corpus_id]
                ), "Missing class {ml_class} even after reloading"
                ml_class_id = self.classes[corpus_id][ml_class]

        return ml_class_id

    def create_classification(
        self, element, ml_class, confidence, high_confidence=False
    ):
        """
        Create a classification on the given element through API
        """
        assert element and isinstance(
            element, (Element, CachedElement)
        ), "element shouldn't be null and should be an Element or CachedElement"
        assert ml_class and isinstance(
            ml_class, str
        ), "ml_class shouldn't be null and should be of type str"
        assert (
            isinstance(confidence, float) and 0 <= confidence <= 1
        ), "confidence shouldn't be null and should be a float in [0..1] range"
        assert isinstance(
            high_confidence, bool
        ), "high_confidence shouldn't be null and should be of type bool"
        if self.is_read_only:
            logger.warning(
                "Cannot create classification as this worker is in read-only mode"
            )
            return

        try:
            created = self.request(
                "CreateClassification",
                body={
                    "element": str(element.id),
                    "ml_class": self.get_ml_class_id(None, ml_class),
                    "worker_version": self.worker_version_id,
                    "confidence": confidence,
                    "high_confidence": high_confidence,
                },
            )

            if self.use_cache:
                # Store classification in local cache
                try:
                    to_insert = [
                        {
                            "id": created["id"],
                            "element_id": element.id,
                            "class_name": ml_class,
                            "confidence": created["confidence"],
                            "state": created["state"],
                            "worker_version_id": self.worker_version_id,
                        }
                    ]
                    CachedClassification.insert_many(to_insert).execute()
                except IntegrityError as e:
                    logger.warning(
                        f"Couldn't save created classification in local cache: {e}"
                    )
        except ErrorResponse as e:
            # Detect already existing classification
            if (
                e.status_code == 400
                and "non_field_errors" in e.content
                and "The fields element, worker_version, ml_class must make a unique set."
                in e.content["non_field_errors"]
            ):
                logger.warning(
                    f"This worker version has already set {ml_class} on element {element.id}"
                )
                return

            # Propagate any other API error
            raise

        self.report.add_classification(element.id, ml_class)

        return created

    def create_classifications(self, element, classifications):
        """
        Create multiple classifications at once on the given element through the API
        """
        assert element and isinstance(
            element, (Element, CachedElement)
        ), "element shouldn't be null and should be an Element or CachedElement"
        assert classifications and isinstance(
            classifications, list
        ), "classifications shouldn't be null and should be of type list"

        for index, classification in enumerate(classifications):
            class_name = classification.get("class_name")
            assert class_name and isinstance(
                class_name, str
            ), f"Classification at index {index} in classifications: class_name shouldn't be null and should be of type str"

            confidence = classification.get("confidence")
            assert (
                confidence is not None
                and isinstance(confidence, float)
                and 0 <= confidence <= 1
            ), f"Classification at index {index} in classifications: confidence shouldn't be null and should be a float in [0..1] range"

            high_confidence = classification.get("high_confidence")
            if high_confidence is not None:
                assert isinstance(
                    high_confidence, bool
                ), f"Classification at index {index} in classifications: high_confidence should be of type bool"

        if self.is_read_only:
            logger.warning(
                "Cannot create classifications as this worker is in read-only mode"
            )
            return

        created_cls = self.request(
            "CreateClassifications",
            body={
                "parent": str(element.id),
                "worker_version": self.worker_version_id,
                "classifications": classifications,
            },
        )["classifications"]

        for created_cl in created_cls:
            self.report.add_classification(element.id, created_cl["class_name"])

        if self.use_cache:
            # Store classifications in local cache
            try:
                to_insert = [
                    {
                        "id": created_cl["id"],
                        "element_id": element.id,
                        "class_name": created_cl["class_name"],
                        "confidence": created_cl["confidence"],
                        "state": created_cl["state"],
                        "worker_version_id": self.worker_version_id,
                    }
                    for created_cl in created_cls
                ]
                CachedClassification.insert_many(to_insert).execute()
            except IntegrityError as e:
                logger.warning(
                    f"Couldn't save created classifications in local cache: {e}"
                )

        return created_cls
