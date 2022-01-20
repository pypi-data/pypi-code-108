"""
Data structures for messages placed on the interservice bus
"""
from talus.message import message_class


@message_class(routing_key="catalog.frame.m", queues=["catalog.frame.q"])
class CatalogFrameMessage:
    """
    Class to hold the catalog_frame_message to be sent to RabbitMQ
    """

    objectName: str
    conversationId: str
    bucket: str
    incrementDatasetCatalogReceiptCount: bool = True


@message_class(routing_key="catalog.object.m", queues=["catalog.object.q"])
class CatalogObjectMessage:
    """
    Class to hold the catalog_object_message to be sent to RabbitMQ
    """

    objectType: str
    objectName: str
    conversationId: str
    bucket: str
    groupId: str = "default_group_id"
    groupName: str = "DATASET"
    incrementDatasetCatalogReceiptCount: bool = True


@message_class(routing_key="create.quality.report.m", queues=["create.quality.report.q"])
class CreateQualityReportMessage:
    datasetId: str
    bucket: str
    objectName: str
    conversationId: str
