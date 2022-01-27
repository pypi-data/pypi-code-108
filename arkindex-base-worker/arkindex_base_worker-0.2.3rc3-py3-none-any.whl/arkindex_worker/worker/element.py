# -*- coding: utf-8 -*-

import uuid

from peewee import IntegrityError

from arkindex_worker import logger
from arkindex_worker.cache import CachedElement, CachedImage
from arkindex_worker.models import Element


class MissingTypeError(Exception):
    """
    A required element type was not found in a corpus.
    """


class ElementMixin(object):
    def check_required_types(self, corpus_id: str, *type_slugs: str) -> bool:
        """
        Check that a corpus has a list of required element types,
        and raise an exception if any of them are missing.
        """
        assert isinstance(
            corpus_id, (uuid.UUID, str)
        ), "Corpus ID should be a string or UUID"
        assert len(type_slugs), "At least one element type slug is required."
        assert all(
            isinstance(slug, str) for slug in type_slugs
        ), "Element type slugs must be strings."

        corpus = self.request("RetrieveCorpus", id=corpus_id)
        available_slugs = {element_type["slug"] for element_type in corpus["types"]}
        missing_slugs = set(type_slugs) - available_slugs

        if missing_slugs:
            raise MissingTypeError(
                f'Element type(s) {", ".join(sorted(missing_slugs))} were not found in the {corpus["name"]} corpus ({corpus["id"]}).'
            )

        return True

    def create_sub_element(self, element, type, name, polygon):
        """
        Create a child element on the given element through API
        Return the ID of the created sub element
        """
        assert element and isinstance(
            element, Element
        ), "element shouldn't be null and should be of type Element"
        assert type and isinstance(
            type, str
        ), "type shouldn't be null and should be of type str"
        assert name and isinstance(
            name, str
        ), "name shouldn't be null and should be of type str"
        assert polygon and isinstance(
            polygon, list
        ), "polygon shouldn't be null and should be of type list"
        assert len(polygon) >= 3, "polygon should have at least three points"
        assert all(
            isinstance(point, list) and len(point) == 2 for point in polygon
        ), "polygon points should be lists of two items"
        assert all(
            isinstance(coord, (int, float)) for point in polygon for coord in point
        ), "polygon points should be lists of two numbers"
        if self.is_read_only:
            logger.warning("Cannot create element as this worker is in read-only mode")
            return

        sub_element = self.request(
            "CreateElement",
            body={
                "type": type,
                "name": name,
                "image": element.zone.image.id,
                "corpus": element.corpus.id,
                "polygon": polygon,
                "parent": element.id,
                "worker_version": self.worker_version_id,
            },
        )
        self.report.add_element(element.id, type)

        return sub_element["id"]

    def create_elements(self, parent, elements):
        """
        Create children elements on the given element through API
        Return the IDs of created elements
        """
        if isinstance(parent, Element):
            assert parent.get(
                "zone"
            ), "create_elements cannot be used on parents without zones"
        elif isinstance(parent, CachedElement):
            assert (
                parent.image_id
            ), "create_elements cannot be used on parents without images"
        else:
            raise TypeError(
                "Parent element should be an Element or CachedElement instance"
            )

        assert elements and isinstance(
            elements, list
        ), "elements shouldn't be null and should be of type list"

        for index, element in enumerate(elements):
            assert isinstance(
                element, dict
            ), f"Element at index {index} in elements: Should be of type dict"

            name = element.get("name")
            assert name and isinstance(
                name, str
            ), f"Element at index {index} in elements: name shouldn't be null and should be of type str"

            type = element.get("type")
            assert type and isinstance(
                type, str
            ), f"Element at index {index} in elements: type shouldn't be null and should be of type str"

            polygon = element.get("polygon")
            assert polygon and isinstance(
                polygon, list
            ), f"Element at index {index} in elements: polygon shouldn't be null and should be of type list"
            assert (
                len(polygon) >= 3
            ), f"Element at index {index} in elements: polygon should have at least three points"
            assert all(
                isinstance(point, list) and len(point) == 2 for point in polygon
            ), f"Element at index {index} in elements: polygon points should be lists of two items"
            assert all(
                isinstance(coord, (int, float)) for point in polygon for coord in point
            ), f"Element at index {index} in elements: polygon points should be lists of two numbers"

        if self.is_read_only:
            logger.warning("Cannot create elements as this worker is in read-only mode")
            return

        created_ids = self.request(
            "CreateElements",
            id=parent.id,
            body={
                "worker_version": self.worker_version_id,
                "elements": elements,
            },
        )

        for element in elements:
            self.report.add_element(parent.id, element["type"])

        if self.use_cache:
            # Create the image as needed and handle both an Element and a CachedElement
            if isinstance(parent, CachedElement):
                image_id = parent.image_id
            else:
                image_id = parent.zone.image.id
                CachedImage.get_or_create(
                    id=parent.zone.image.id,
                    defaults={
                        "width": parent.zone.image.width,
                        "height": parent.zone.image.height,
                        "url": parent.zone.image.url,
                    },
                )

            # Store elements in local cache
            try:
                to_insert = [
                    {
                        "id": created_ids[idx]["id"],
                        "parent_id": parent.id,
                        "type": element["type"],
                        "image_id": image_id,
                        "polygon": element["polygon"],
                        "worker_version_id": self.worker_version_id,
                    }
                    for idx, element in enumerate(elements)
                ]
                CachedElement.insert_many(to_insert).execute()
            except IntegrityError as e:
                logger.warning(f"Couldn't save created elements in local cache: {e}")

        return created_ids

    def list_element_children(
        self,
        element,
        best_class=None,
        folder=None,
        name=None,
        recursive=None,
        type=None,
        with_best_classes=None,
        with_corpus=None,
        with_has_children=None,
        with_zone=None,
        worker_version=None,
    ):
        """
        List children of an element
        """
        assert element and isinstance(
            element, (Element, CachedElement)
        ), "element shouldn't be null and should be an Element or CachedElement"
        query_params = {}
        if best_class is not None:
            assert isinstance(best_class, str) or isinstance(
                best_class, bool
            ), "best_class should be of type str or bool"
            query_params["best_class"] = best_class
        if folder is not None:
            assert isinstance(folder, bool), "folder should be of type bool"
            query_params["folder"] = folder
        if name:
            assert isinstance(name, str), "name should be of type str"
            query_params["name"] = name
        if recursive is not None:
            assert isinstance(recursive, bool), "recursive should be of type bool"
            query_params["recursive"] = recursive
        if type:
            assert isinstance(type, str), "type should be of type str"
            query_params["type"] = type
        if with_best_classes is not None:
            assert isinstance(
                with_best_classes, bool
            ), "with_best_classes should be of type bool"
            query_params["with_best_classes"] = with_best_classes
        if with_corpus is not None:
            assert isinstance(with_corpus, bool), "with_corpus should be of type bool"
            query_params["with_corpus"] = with_corpus
        if with_has_children is not None:
            assert isinstance(
                with_has_children, bool
            ), "with_has_children should be of type bool"
            query_params["with_has_children"] = with_has_children
        if with_zone is not None:
            assert isinstance(with_zone, bool), "with_zone should be of type bool"
            query_params["with_zone"] = with_zone
        if worker_version:
            assert isinstance(
                worker_version, str
            ), "worker_version should be of type str"
            query_params["worker_version"] = worker_version

        if self.use_cache:
            # Checking that we only received query_params handled by the cache
            assert set(query_params.keys()) <= {
                "type",
                "worker_version",
            }, "When using the local cache, you can only filter by 'type' and/or 'worker_version'"

            query = CachedElement.select().where(CachedElement.parent_id == element.id)
            if type:
                query = query.where(CachedElement.type == type)
            if worker_version:
                query = query.where(CachedElement.worker_version_id == worker_version)

            return query
        else:
            children = self.api_client.paginate(
                "ListElementChildren", id=element.id, **query_params
            )

        return children
