import logging
import os
import warnings

import elasticsearch
import elasticsearch_dsl
from elasticsearch.helpers import bulk
from elasticsearch_dsl import DenseVector, Keyword, Long, Mapping, Nested

from . import utils
from .utils import ParserOutputType
from ..settings import ELASTIC_BULK_BATCH_SIZE, ELASTIC_GLOBAL_TIMEOUT, ES_URL, META_FIELD


logging.basicConfig(
    format='%(levelname)s %(asctime)s: %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.INFO
)


class ESImporter:


    def __init__(self, elastic_url: str, index_prefix: str):
        """
        :param elastic_url: Url to elasticsearch
        :param index_prefix: Prefix used for naming indices in elasticsearch
        """
        self.index_prefix = index_prefix
        self.es = elasticsearch.Elasticsearch(elastic_url, timeout=ELASTIC_GLOBAL_TIMEOUT)


    @staticmethod
    def build_flavor(elastic_url: str) -> str:
        es = elasticsearch.Elasticsearch(elastic_url, timeout=ELASTIC_GLOBAL_TIMEOUT)
        return es.info()["version"]["build_flavor"]


    @staticmethod
    def version_number(elastic_url: str) -> int:
        es = elasticsearch.Elasticsearch(elastic_url)
        number_string = es.info()["version"]["number"]
        first, second, third = number_string.split(".")
        main_version = int(first)
        return main_version


    def _importer_generator(self, generator, index_name: str):
        """
        Used to generate the payload for the Bulk API of the Python Elasticsearch Clients
        helper.
        :param generator: Output of the entity-linker (concatenator)
        :param index_name: Full name of the index into which the document is pushed.
        """
        for item in generator:
            yield {
                "_index": index_name,
                "_type": "_doc",
                "_source": item
            }


    def push_linked_entities_into_elastic(self, generator, index_name: str) -> bool:
        """
        Generator for pushing the EntityLinker results into an Elasticsearch index.

        :param generator: Generator which yields the results of the entity-linking (concatenation)
        :param index_name: Full name of the index you want to push the results into.
        :return: As this is meant as the final part of the pipeline, this will only return True.
        """
        self._add_texta_facts_mapping(index_name)
        generator = self._importer_generator(generator, index_name)
        generator = list(generator)
        bulk(client=self.es, actions=generator, chunk_size=ELASTIC_BULK_BATCH_SIZE, refresh="wait_for")
        logging.info("Finished pushing person info into Elasticsearch!")
        return True


    def insert_from_generator(self, generator, toolkit_url=None, tk_media_folder=None):
        """ Inserts data to elasticsearch from given generator object.
           
        # Parameters
        toolkit_url(str): ONLY FOR EMAILS! If this is specified then filepath field is converted to an HTML link by combining toolkit URL with filepath. This is only done
        for convenient purpose to make it possible to wiew and download original files directly from toolkit. However, assumes that original files are saved to toolkit's
        media folder during parsing, otherwise the links won't work.
        tk_media_folder(str): ONLY FOR EMAILS! A path to toolkit's media folder. Is only used when toolkit_url is set.
        """
        if (toolkit_url != None and tk_media_folder == None):
            raise ValueError("Argument tk_media_folder can not be None if toolkit_url is given.")

        actions = self._get_es_data(generator, toolkit_url, tk_media_folder)
        bulk(actions=actions, client=self.es, chunk_size=ELASTIC_BULK_BATCH_SIZE, refresh="wait_for")


    def _get_es_data(self, generator, toolkit_url, tk_media_folder):
        has_mails_mapping = False
        has_attachments_mapping = False
        has_index_mapping = False

        for item in generator:

            # Get index name. It depends on the original file extension
            index_name = self._get_index_name(item)

            # Check if from email generator
            if type(item) == tuple:
                # Append "mails" or "attachments" to index name to put them to different indices
                mails_index = index_name + "_mails"
                attachments_index = index_name + "_attachments"
                mail, attachments = item

                self._try_add_file_url(mail, toolkit_url, tk_media_folder)
                if has_mails_mapping is False:
                    self._add_texta_facts_mapping(mails_index)
                    has_mails_mapping = True

                yield {
                    "_index": mails_index,
                    "_type": "_doc",
                    "_source": mail
                }

                for attachment in attachments:
                    if has_attachments_mapping is False:
                        self._add_texta_facts_mapping(attachments_index)
                        has_attachments_mapping = True

                    self._try_add_file_url(attachment, toolkit_url, tk_media_folder)
                    yield {
                        "_index": attachments_index,
                        "_type": "_doc",
                        "_source": attachment
                    }
            else:

                if has_index_mapping is False:
                    self._add_texta_facts_mapping(index_name)
                    has_index_mapping = True

                yield {
                    "_index": index_name,
                    "_type": "_doc",
                    "_source": item
                }


    def parse_doc_type_from_mapping(self, mapping: dict, default_es7_doctype="_doc") -> str:
        """
        Parse the result of the indexes _mapping endpoint to fetch the set
        doc_type and if it doesn't exist yet (fresh index) put it into the default _doc.
        From the start of ES6, only a single doc_type is allowed per index.
        """
        doc_types = []

        for index, mappings in mapping.items():
            mappings = mappings["mappings"]
            for doc_type in mappings:
                if doc_type != "properties":
                    doc_types.append(doc_type)

        return doc_types[0] if doc_types else default_es7_doctype


    def get_doc_type_for_index(self, index: str):
        index_interface = elasticsearch_dsl.Index(index, using=self.es)
        mapping = index_interface.get_mapping(include_type_name=True)
        doc_type = self.parse_doc_type_from_mapping(mapping)
        return doc_type


    def _add_texta_facts_mapping(self, index):
        self.es.indices.create(index, ignore=[400, 404])
        m = Mapping()
        texta_facts = Nested(
            properties={
                "spans": Keyword(),
                "fact": Keyword(),
                "str_val": Keyword(),
                "doc_path": Keyword(),
                "num_val": Long(),
            }
        )

        # Set the name of the field along with its mapping body
        mapping = m.field("texta_facts", texta_facts).to_dict()
        doc_type = self.get_doc_type_for_index(index)
        self.es.indices.put_mapping(body=mapping, index=index, doc_type=doc_type, include_type_name=True)


    def _get_index_name(self, item):
        item_type = utils.get_output_type(item)

        if (item_type == ParserOutputType.EMAIL):
            # just return prefix, finish naming later
            return self.index_prefix
        elif (item_type == ParserOutputType.COLLECTION):
            # use file name in naming as well to put different collections to different indices
            filename = os.path.basename(item[META_FIELD]["origin"]).replace(".", "_").lower()
            return self.index_prefix + "_collection_" + filename
        else:
            # put everything else (texts, images, audio etc.) to general "files" index
            return self.index_prefix + "_files"


    def _try_add_file_url(self, item, toolkit_url, tk_media_folder):
        if item != {}:
            if toolkit_url != None:
                tk_url_path = self._get_file_url(item, toolkit_url, tk_media_folder)
                if (tk_url_path != None):
                    item["filepath"] = tk_url_path


    def _get_file_url(self, data_json, toolkit_url, tk_media_folder):
        if "filepath" in data_json:
            data_filepath = data_json["filepath"]
            if (data_filepath.startswith(tk_media_folder) == False):
                warnings.warn("File with filepath '{0}' is not located in '{1}'. Can not create URL for this file.".format(data_filepath, tk_media_folder))
            else:
                file_part = data_filepath.replace(tk_media_folder, "").strip("/")
                file_url = os.path.join(toolkit_url, "data/media", file_part)
                return file_url
