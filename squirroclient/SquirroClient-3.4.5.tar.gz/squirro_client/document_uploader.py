import base64
import hashlib
import logging
import os

from .item_uploader import ItemUploader
from .util import deprecation

log = logging.getLogger(__name__)


# Increased read timeout for file uploads, as file processing can take a
# moment.
TIMEOUT_SECS = 300


class DocumentUploader(object):
    """Document uploader class which simplifies the indexing of office
    documents. Default parameters are loaded from your home directories
    .squirrorc. See the documentation of [[ItemUploader]] for a complete
    list of options regarding project selection, source selection,
    configuration, etc.

    :param batch_size: Number of items to send in one request.
    :param batch_size_mb: Size of documents to send in one request. If this
        file size is reached, the client uploads the existing documents.
    :param metadata_mapping: A dictionary which contains the meta-data mapping.
    :param default_mime_type_keyword: If set to ``True`` a default keyword
        is added to the document which contains the mime-type.
    :param timeout_secs: How many seconds to wait for data before giving up
        (default 300).
    :param kwargs: Any additional keyword arguments are passed on to the
        [[ItemUploader]]. See the documentation of that class for details.

    Typical usage:

        >>> from squirro_client import DocumentUploader
        >>> import os
        >>> uploader = DocumentUploader(
        ...     project_title='My Project', token='<your token>',
        ...     cluster='https://demo.squirro.net/')
        >>> uploader.upload(os.path.expanduser('~/Documents/test.pdf'))
        >>> uploader.flush()

    Meta-data mapping usage:

    * By default (i.e. for all document mime-types) map the original document
      size to a keyword field named "Doc Size":

        >>> mapping = {'default': {'sq:size_orig': 'Doc Size',
        ...                        'sq:content-mime-type': 'Mime Type'}}
        >>> uploader = DocumentUploader(metadata_mapping=mapping)

    * For a specific mime-type (i.e.
      'application/vnd.oasis.opendocument.text') map the "meta:word-count"
      meta-data filed value to a keyword field named "Word Count":

        >>> mapping = {'application/vnd.oasis.opendocument.text': {
        ...     'meta:word-count': 'Word Count'}}
        >>> uploader = DocumentUploader(metadata_mapping=mapping)

    Default meta-data fields available for mapping usage:

    * ``sq:doc_size``: Converted document file size.
    * ``sq:doc_size_orig``: Original uploaded document file size.
    * ``sq:content-mime-type``: Document mime-type specified during upload
      operation.

    """

    def __init__(
        self,
        metadata_mapping=None,
        batch_size=10,
        batch_size_mb=150,
        default_mime_type_keyword=True,
        timeout_secs=TIMEOUT_SECS,
        **kwargs
    ):

        # assemble steps_config configuration
        source_id = kwargs.pop("source_id", None)
        pipeline_workflow_id = kwargs.pop("pipeline_workflow_id", None)
        pipeline_workflow_name = kwargs.pop("pipeline_workflow_name", None)
        steps_config = kwargs.pop("steps_config", None)

        # deprecation warning for an explicit processing config
        if "processing_config" in kwargs:
            msg = (
                "processing_config is deprecated and is not supported"
                "anymore. Please use pipeline_workflow_id or "
                "pipeline_workflow_name instead."
            )
            deprecation(msg)
            raise NotImplementedError(msg)

        # disable bulk indexing as document conversion is not supported
        # For compatibility.
        if "bulk_index" in kwargs:
            msg = (
                "bulk_index is supported by the new ingester automatically "
                "and can not be specified from outside anymore. Please "
                "remove this parameter from the class constructor"
            )
            deprecation(msg)
            raise NotImplementedError(msg)

        kwargs["batch_size"] = batch_size
        kwargs["timeout_secs"] = timeout_secs
        self.batch_size = batch_size
        self.batch_size_mb = batch_size_mb

        # Initialize priority
        mapping = metadata_mapping or {}
        if default_mime_type_keyword and "sq:content-mime-type" not in mapping.get(
            "default", {}
        ):
            mapping.setdefault("default", {})["sq:content-mime-type"] = "MIME Type"
        default_steps_config = [
            {
                "id": "deduplication",
                "name": "Deduplication",
                "type": "deduplication",
                "config": {"policy": "replace"},
            },
            {
                "id": "content-augmentation",
                "name": "Content Augmentation",
                "type": "content-augmentation",
            },
            {
                "id": "content-conversion",
                "name": "Content Extraction",
                "type": "content-conversion",
                "metadata-mapping": mapping,
            },
            {
                "id": "language-detection",
                "name": "Language Detection",
                "type": "language-detection",
            },
            {"id": "cleanup", "name": "Content Standardization", "type": "cleanup"},
            {"id": "index", "name": "Indexing", "type": "index"},
            {"id": "cache", "name": "Cache Cleaning", "type": "cache"},
        ]

        if source_id:
            # Use existing source
            self.uploader = ItemUploader(source_id=source_id, **kwargs)

        elif pipeline_workflow_id:
            # Use existing pipeline workflow
            self.uploader = ItemUploader(
                pipeline_workflow_id=pipeline_workflow_id, **kwargs
            )

        elif not steps_config:
            # Create pipeline workflow with default steps config
            self.uploader = ItemUploader(
                pipeline_workflow_name=pipeline_workflow_name,
                steps_config=default_steps_config,
                **kwargs
            )

        else:
            # Create pipeline workflow with given steps config
            self.uploader = ItemUploader(
                pipeline_workflow_name=pipeline_workflow_name,
                steps_config=steps_config,
                **kwargs
            )

        # internal state
        self._items = []
        self._items_size_mb = 0

    def upload(
        self,
        filename,
        mime_type=None,
        title=None,
        doc_id=None,
        keywords=None,
        link=None,
        created_at=None,
        filename_encoding=None,
        content_url=None,
        priority=0,
        pipeline_workflow_id=None,
    ):
        """Method which will use the provided ``filename`` to create a Squirro
        item for upload. Items are buffered internally and uploaded according
        to the specified batch size. If `mime_type` is not provided a simple
        filename extension based lookup is performed.

        :param filename: Read content from the provided filename.
        :param mime_type: Optional mime-type for the provided filename.
        :param title: Optional title for the uploaded document.
        :param doc_id: Optional external document identifier.
        :param keywords: Optional dictionary of document meta data keywords.
            All values must be lists of string.
        :param link: Optional URL which points to the origin document.
        :param created_at: Optional document creation date and time.
        :param filename_encoding: Encoding of the filename.
        :param content_url: Storage URL of this file. If this is set, the
            Squirro cluster will not copy the file.
        :param priority: int, describing the priority of ingestion for the
            dataset to be loaded. Currently only supports a value of `0` or `1`.
            `0` means that the items are loaded in an asynchronous fashion and
            `1` would mean that the items are loaded in a synchronous fashion.
        :param pipeline_workflow_id: str, id of an existing pipeline
            workflow which should be used to process the current batch of items.
            Can only be used with parameter `priority` set to 1.

        Example:

        >>> filename = 'test.pdf'
        >>> mime_type = 'application/pdf'
        >>> title = 'My Test Document'
        >>> doc_id = 'doc01'
        >>> keywords = {'Author': ['John Smith'], 'Tags': ['sales',
        ...                                                'marketing']}
        >>> link = 'http://example.com/test.pdf'
        >>> created_at = '2014-07-10T21:26:15'
        >>> uploader.upload(filename, mime_type, title, doc_id, keywords,
        ...                 link, created_at)
        """

        self.priority = priority
        self.adhoc_pipeline_workflow_id = pipeline_workflow_id

        item_id = doc_id
        content_size = 0
        content = None

        if not content_url or not item_id:
            # read the raw file content and encode it
            raw = open(filename, "rb").read()
            content = base64.b64encode(raw)
            content_size = len(content) / 1024 / 1024

            # build a checksum over the original file content and use it as the
            # item identifier
            if not item_id:
                item_id = hashlib.sha256(raw).hexdigest()

            # free up the memory
            raw = None

        # Upload the documents if the maximum size would be exceeded with this
        # new file.
        if self._items_size_mb + content_size >= self.batch_size_mb:
            self.flush()

        # TODO: python3 test this
        if isinstance(filename, str):
            decoded_name = filename.encode("utf8")
        elif filename_encoding:
            decoded_name = filename.decode(filename_encoding).encode("utf8")
        else:
            decoded_name = filename

        item = {"id": item_id, "files": [{"name": os.path.basename(decoded_name)}]}

        # Optional MIME type
        if mime_type:
            item["files"][0]["mime_type"] = mime_type

        # Optional storage URL
        if content_url:
            item["files"][0]["content_url"] = content_url
        else:
            item["files"][0]["content"] = content

        # check if an explicit title was provided, otherwise the content
        # conversion step will figure something out
        if title is not None:
            item["title"] = title

        # check for any other provided document attributes
        if keywords is not None:
            item["keywords"] = keywords
        if link is not None:
            item["link"] = link
        if created_at is not None:
            item["created_at"] = created_at

        # upload items
        self._items.append(item)
        self._items_size_mb += content_size

        if self.priority == 1:
            self.flush()

        if len(self._items) >= self.batch_size:
            self.flush()

    def flush(self):
        """Flush the internal buffer by uploading all documents."""
        if self._items:
            if self.priority:
                self.uploader.upload(
                    self._items,
                    priority=self.priority,
                    pipeline_workflow_id=self.adhoc_pipeline_workflow_id,
                )
                self.adhoc_pipeline_workflow_id = None
                self.priority = 0
            else:
                self.uploader.upload(self._items)
            self._items = []
            self._items_size_mb = 0
