# -*- coding: utf-8 -*-
from enum import Enum

from arkindex_worker import logger
from arkindex_worker.models import Element


class MetaType(Enum):
    Text = "text"
    HTML = "html"
    Date = "date"
    Location = "location"
    # Element's original structure reference (intended to be indexed)
    Reference = "reference"
    Numeric = "numeric"
    URL = "url"


class MetaDataMixin(object):
    def create_metadata(self, element, type, name, value, entity=None):
        """
        Create a metadata on the given element through API
        """
        assert element and isinstance(
            element, Element
        ), "element shouldn't be null and should be of type Element"
        assert type and isinstance(
            type, MetaType
        ), "type shouldn't be null and should be of type MetaType"
        assert name and isinstance(
            name, str
        ), "name shouldn't be null and should be of type str"
        assert value and isinstance(
            value, str
        ), "value shouldn't be null and should be of type str"
        if entity:
            assert isinstance(entity, str), "entity should be of type str"
        if self.is_read_only:
            logger.warning("Cannot create metadata as this worker is in read-only mode")
            return

        metadata = self.request(
            "CreateMetaData",
            id=element.id,
            body={
                "type": type.value,
                "name": name,
                "value": value,
                "entity_id": entity,
                "worker_version": self.worker_version_id,
            },
        )
        self.report.add_metadata(element.id, metadata["id"], type.value, name)

        return metadata["id"]
