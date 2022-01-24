# Copyright 2019 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import yaml
import logging

from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk
from elasticsearch.helpers import BulkIndexError

from zuul.connection import BaseConnection


class ElasticsearchConnection(BaseConnection):
    driver_name = 'elasticsearch'
    log = logging.getLogger("zuul.ElasticSearchConnection")
    properties = {
        #  Common attribute
        "uuid": {"type": "keyword"},
        "build_type": {"type": "keyword"},
        "result": {"type": "keyword"},
        "duration": {"type": "integer"},
        "@timestamp": {"type": "date"},
        # BuildSet type specific attributes
        "zuul_ref": {"type": "keyword"},
        "pipeline": {"type": "keyword"},
        "project": {"type": "keyword"},
        "branch": {"type": "keyword"},
        "change": {"type": "integer"},
        "patchset": {"type": "keyword"},
        "ref": {"type": "keyword"},
        "oldrev": {"type": "keyword"},
        "newrev": {"type": "keyword"},
        "ref_url": {"type": "keyword"},
        "message": {"type": "text"},
        "tenant": {"type": "keyword"},
        # Build type specific attibutes
        "buildset_uuid": {"type": "keyword"},
        "job_name": {"type": "keyword"},
        "start_time": {"type": "date", "format": "epoch_second"},
        "end_time": {"type": "date", "format": "epoch_second"},
        "voting": {"type": "boolean"},
        "log_url": {"type": "keyword"},
        "nodeset": {"type": "keyword"}
    }

    def __init__(self, driver, connection_name, connection_config):
        super(ElasticsearchConnection, self).__init__(
            driver, connection_name, connection_config)
        self.uri = self.connection_config.get('uri').split(',')
        self.cnx_opts = {}
        use_ssl = self.connection_config.get('use_ssl', True)
        if isinstance(use_ssl, str):
            if use_ssl.lower() == 'false':
                use_ssl = False
            else:
                use_ssl = True
        self.cnx_opts['use_ssl'] = use_ssl
        if use_ssl:
            verify_certs = self.connection_config.get('verify_certs', True)
            if isinstance(verify_certs, str):
                if verify_certs.lower() == 'false':
                    verify_certs = False
                else:
                    verify_certs = True
            self.cnx_opts['verify_certs'] = verify_certs
            self.cnx_opts['ca_certs'] = self.connection_config.get(
                'ca_certs', None)
            self.cnx_opts['client_cert'] = self.connection_config.get(
                'client_cert', None)
            self.cnx_opts['client_key'] = self.connection_config.get(
                'client_key', None)
        self.es = Elasticsearch(
            self.uri, **self.cnx_opts)
        try:
            self.log.debug("Elasticsearch info: %s" % self.es.info())
        except Exception as e:
            self.log.warn("An error occured on estabilishing "
                          "connection to Elasticsearch: %s" % e)
        self.ic = IndicesClient(self.es)

    def setIndex(self, index):
        settings = {
            'mappings': {
                'zuul': {
                    "properties": self.properties
                }
            }
        }
        try:
            self.ic.create(index=index, ignore=400, body=settings)
        except Exception:
            self.log.exception(
                "Unable to create the index %s on connection %s" % (
                    index, self.connection_name))

    def gen(self, it, index):
        for source in it:
            d = {}
            source['@timestamp'] = datetime.utcfromtimestamp(
                int(source['start_time'])).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            d['_index'] = index
            d['_type'] = 'zuul'
            d['_op_type'] = 'index'
            d['_source'] = source
            yield d

    def add_docs(self, source_it, index):

        self.setIndex(index)

        try:
            bulk(self.es, self.gen(source_it, index))
            self.es.indices.refresh(index=index)
            self.log.debug('%s docs indexed to %s' % (
                len(source_it), self.connection_name))
        except BulkIndexError as exc:
            self.log.warn("Some docs failed to be indexed (%s)" % exc)
            # We give flexibility by allowing any type of job's vars and
            # zuul return data to be indexed with EL dynamic mapping enabled.
            # It may happen that a doc own a field with a value that does not
            # match the previous data type that EL has detected for that field.
            # In that case the whole doc is not indexed by EL.
            # Here we want to mitigate by indexing the errorneous docs in a
            # <index-name>.errorneous index by flattening the doc data as yaml.
            # This ensures the doc is indexed and can be tracked and eventually
            # be modified and re-indexed by an operator.
            errorneous_docs = []
            for d in exc.errors:
                if d['index']['error']['type'] == 'mapper_parsing_exception':
                    errorneous_doc = {
                        'uuid': d['index']['data']['uuid'],
                        'blob': yaml.dump(d['index']['data'])
                    }
                    errorneous_docs.append(errorneous_doc)
            try:
                mapping_errorneous_index = "%s.errorneous" % index
                bulk(
                    self.es,
                    self.gen(errorneous_docs, mapping_errorneous_index))
                self.es.indices.refresh(index=mapping_errorneous_index)
                self.log.info(
                    "%s errorneous docs indexed" % (len(errorneous_docs)))
            except BulkIndexError as exc:
                self.log.warn(
                    "Some errorneous docs failed to be indexed (%s)" % exc)
