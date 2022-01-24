# Copyright 2019 StreamSets Inc.

"""Classes for SCH-related models.

This module provides implementations of classes with which users may interact in the course of
writing tests that exercise SCH functionality.
"""

import collections
import copy
import json
import logging
import re
import requests
import time
import urllib3
import uuid
import warnings
from datetime import datetime
from functools import partial

import inflection
import yaml

from . import sch_api
from .exceptions import TopologyIssuesError
from .sdc import DataCollector as SdcDataCollector
from .sdc_models import PipelineBuilder as SdcPipelineBuilder, Stage as SdcStage
from .st import Transformer as StTransformer
from .st_models import PipelineBuilder as StPipelineBuilder, Stage as StStage
from .utils import (DEFAULT_PROVISIONING_SPEC, MutableKwargs, SDC_DEFAULT_EXECUTION_MODE, SeekableList,
                    TRANSFORMER_DEFAULT_EXECUTION_MODE, Version, build_tag_from_raw_tag, format_sch_log, get_params,
                    get_topology_nodes, reversed_dict, set_acl, update_acl_permissions)

logger = logging.getLogger(__name__)

json_to_python_style = lambda x: inflection.underscore(x)
python_to_json_style = lambda x: inflection.camelize(x, uppercase_first_letter=False)

ModelCollectionResults = collections.namedtuple('ModelCollectionResults', ['results', 'kwargs'])
# CollectionModelResults contains API results from classes that subclass PaginationMixin. The 'class_type' attribute
# indicates which class PaginationMixin._paginate should instantiate before iterating over results.
CollectionModelResults = collections.namedtuple('CollectionModelResults', ['results', 'kwargs', 'class_type',
                                                                           'class_kwargs'])

ALL_TOPOLOGY_SYSTEMS = [
    {'label': 'ADLS Gen1', 'icon': 'adls1.png', 'colorIcon': 'Destination_Azure_Data_Lake_Storage_Gen1.png'},
    {'label': 'ADLS Gen2', 'icon': 'adls2.png', 'colorIcon': 'Destination_Azure_Data_Lake_Storage_Gen2.png'},
    {'label': 'Amazon S3', 'icon': 's3.png', 'colorIcon': 'Origin_Amazon_S3.png'},
    {'label': 'Azure Data Lake Store', 'icon': 'data-lake-store.png',
     'colorIcon': 'Destination_Azure_Data_Lake_Storage_Legacy.png'},
    {'label': 'Azure SQL', 'icon': 'azuresql.png', 'colorIcon': 'Destination_Azure_SQL.png'},
    {'label': 'Cassandra', 'icon': 'cassandra.png', 'colorIcon': 'Destination_Cassandra.png'},
    {'label': 'CoAP', 'icon': 'coap.png', 'colorIcon': 'Destination_CoAP_Client.png'},
    {'label': 'Delta Lake', 'icon': 'delta.png', 'colorIcon': 'Destination_Delta_Lake.png'},
    {'label': 'Dev Data', 'icon': 'dev.png', 'colorIcon': 'Origin_Dev_Data_Generator.png'},
    {'label': 'Directory', 'icon': 'directory.png', 'colorIcon': 'Origin_Directory.png'},
    {'label': 'Elasticsearch', 'icon': 'elasticsearch.png', 'colorIcon': 'Origin_Elasticsearch.png'},
    {'label': 'File Tail', 'icon': 'fileTail.png', 'colorIcon': 'Origin_File_Tail.png'},
    {'label': 'Flume', 'icon': 'flume.png', 'colorIcon': 'Destination_Flume.png'},
    {'label': 'Google Bigtable', 'icon': 'bigtable.png', 'colorIcon': 'Destination_Google_Bigtable.png'},
    {'label': 'HBase', 'icon': 'hbase.png', 'colorIcon': 'Destination_HBase.png'},
    {'label': 'HTTP Client', 'icon': 'httpclient.png', 'colorIcon': 'Destination_HTTP_Client.png'},
    {'label': 'Hadoop FS', 'icon': 'hdfs.png', 'colorIcon': 'Destination_Hadoop_FS.png'},
    {'label': 'Hive', 'icon': 'hive.png', 'colorIcon': 'Destination_Hive.png'},
    {'label': 'InfluxDB', 'icon': 'influxdb.png', 'colorIcon': 'Destination_InfluxDB.png'},
    {'label': 'JDBC', 'icon': 'rdbms.png', 'colorIcon': 'Destination_JDBC_Producer.png'},
    {'label': 'JMS', 'icon': 'jms.png', 'colorIcon': 'Destination_JMS_Producer.png'},
    {'label': 'Kafka', 'icon': 'kafka.png', 'colorIcon': 'Origin_Kafka.png'},
    {'label': 'Kinesis', 'icon': 'kinesis.png', 'colorIcon': 'Destination_Kinesis_Producer.png'},
    {'label': 'Kinesis Firehose', 'icon': 'kinesisfirehose.png', 'colorIcon': 'Destination_Kinesis_Firehose.png'},
    {'label': 'Kudu', 'icon': 'kudu.png', 'colorIcon': 'Destination_Kudu.png'},
    {'label': 'Local FS', 'icon': 'localfilesystem.png', 'colorIcon': 'Destination_Local_FS.png'},
    {'label': 'MapR FS', 'icon': 'mapr.png', 'colorIcon': 'Destination_MapR_FS.png'},
    {'label': 'MapR Streams', 'icon': 'mapr.png', 'colorIcon': 'Destination_MapR_Streams_Producer.png'},
    {'label': 'MapR DB', 'icon': 'mapr.png', 'colorIcon': 'Destination_MapR_DB.png'},
    {'label': 'MapR DB JSON', 'icon': 'mapr.png', 'colorIcon': 'Destination_MapR_DB.png'},
    {'label': 'MemSQL', 'icon': 'memsql.png', 'colorIcon': 'Destination_MemSQL_Fast_Loader.png'},
    {'label': 'MongoDB', 'icon': 'mongodb.png', 'colorIcon': 'Destination_MongoDB.png'},
    {'label': 'MQTT', 'icon': 'Origin_MQTT_Subscriber.png', 'colorIcon': 'Origin_MQTT_Subscriber.png'},
    {'label': 'Omniture', 'icon': 'omniture_icon.png', 'colorIcon': 'Origin_Omniture.png'},
    {'label': 'Oracle', 'icon': 'oracle.png', 'colorIcon': 'Origin_Oracle_CDC_Client.png'},
    {'label': 'Pulsar', 'icon': 'Origin_Pulsar_Consumer.png', 'colorIcon': 'Origin_Pulsar_Consumer.png'},
    {'label': 'RabbitMQ', 'icon': 'rabbitmq.png', 'colorIcon': 'Origin_RabbitMQ_Consumer.png'},
    {'label': 'Redis', 'icon': 'redis.png', 'colorIcon': 'Origin_Redis_Consumer.png'},
    {'label': 'Salesforce', 'icon': 'salesforce.png', 'colorIcon': 'Origin_Salesforce.png'},
    {'label': 'SAP HANA', 'icon': 'Origin_SAP_HANA_Query_Consumer.png',
     'colorIcon': 'Origin_SAP_HANA_Query_Consumer.png'},
    {'label': 'SDC RPC', 'icon': 'sdcipc.png', 'colorIcon': 'Origin_SDC_RPC.png'},
    {'label': 'SFTP/FTP Client', 'icon': 'sftp-client.png', 'colorIcon': 'Origin_SFTP_FTP_FTPS_Client.png'},
    {'label': 'Snowflake', 'icon': 'snowflake.png', 'colorIcon': 'Destination_Snowflake.png'},
    {'label': 'Solr', 'icon': 'solr.png', 'colorIcon': 'Destination_Solr.png'},
    {'label': 'TCP', 'icon': 'ethernet.png', 'colorIcon': 'Origin_TCP_Server.png'},
    {'label': 'Teradata', 'icon': 'teradata.png', 'colorIcon': 'Origin_Teradata_Consumer.png'},
    {'label': 'To Error', 'icon': 'toerror.png', 'colorIcon': 'Destination_To_Error.png'},
    {'label': 'Trash', 'icon': 'trash.png', 'colorIcon': 'Destination_Trash.png'},
    {'label': 'UDP Source', 'icon': 'udp.png', 'colorIcon': 'Origin_UDP_Source.png'},
    {'label': 'Wave Analytics', 'icon': 'waveanalytics.png', 'colorIcon': 'Destination_Einstein_Analytics.png'},
    {'label': 'WebSocket', 'icon': 'websockets.png', 'colorIcon': 'Origin_WebSocket_Server.png'}
]


class BaseModel:
    """Base class for Control Hub models that essentially just wrap a dictionary.

    Args:
        data (:obj:`dict`): The underlying JSON representation of the model.
        attributes_to_ignore (:obj:`list`, optional): A list of string attributes to mask from being handled
            by this class' __setattr__ method. Default: ``None``.
        attributes_to_remap (:obj:`dict`, optional): A dictionary of attributes to remap with the desired attributes
            as keys and the corresponding property name in the JSON representation as values. Default: ``None``.
        repr_metadata (:obj:`list`, optional): A list of attributes to use in the model's __repr__ string.
            Default: ``None``.
    """

    def __init__(self, data, attributes_to_ignore=None, attributes_to_remap=None, repr_metadata=None):
        # _data_internal is introduced to  help inherited classes that need to load _data when _data is accessed
        # eg. Pipeline
        super().__setattr__('_data_internal', data)
        super().__setattr__('_attributes_to_ignore', attributes_to_ignore or [])
        super().__setattr__('_attributes_to_remap', attributes_to_remap or {})
        super().__setattr__('_repr_metadata', repr_metadata or [])

    # By default these properties don't do anything by can be overrided by inherited classes to load something
    @property
    def _data_internal(self):
        return self.__dict__['_data'] if '_data' in self.__dict__ else None

    @_data_internal.setter
    def _data_internal(self, data):
        self.__dict__['_data'] = data

    @property
    def _data(self):
        return self._data_internal

    @_data.setter
    def _data(self, data):
        self._data_internal = data

    def __getattr__(self, name):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            return self._data_internal[remapped_name]
        elif (name_ in self._data_internal and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            return self._data_internal[name_]
        raise AttributeError('Could not find attribute {}.'.format(name_))

    def __setattr__(self, name, value):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            self._data_internal[remapped_name] = value
        elif (name_ in self._data_internal and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            self._data_internal[name_] = value
        else:
            super().__setattr__(name, value)

    def __dir__(self):
        return sorted(set(dir(self.__class__))
                      | set(self.__dict__.keys())
                      | set(json_to_python_style(key)
                            for key in self._data_internal.keys()
                            if key not in (list(self._attributes_to_remap.values())
                                           + self._attributes_to_ignore))
                      | set(self._attributes_to_remap.keys()))

    def __eq__(self, other):
        return self._data_internal == other._data_internal

    def __repr__(self):
        return '<{} ({})>'.format(self.__class__.__name__,
                                  ', '.join('{}={}'.format(key, getattr(self, key)) for key in self._repr_metadata))


class UiMetadataBaseModel(BaseModel):
    def __getattr__(self, name):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            return self._data_internal[remapped_name]['value']
        elif (name_ in self._data_internal and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            if isinstance(self._data_internal[name_], dict):
                return self._data_internal[name_]['value']
            else:
                return self._data_internal[name_]
        raise AttributeError('Could not find attribute {}.'.format(name_))

    def __setattr__(self, name, value):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            self._data_internal[remapped_name]['value'] = value
        elif (name_ in self._data_internal and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            if isinstance(self._data_internal[name_], dict):
                self._data_internal[name_]['value'] = value
            else:
                self._data_internal[name_] = value
        else:
            super().__setattr__(name, value)


class ModelCollection:
    """Base class wrapper with Abstractions.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
    """

    def __init__(self, control_hub):
        self._control_hub = control_hub
        self._id_attr = 'id'

    def _get_all_results_from_api(self, **kwargs):
        """Used to get multiple (all) results from api.

        Args:
            Optional arguments to be passed to filter the results.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of inherited instances of
                :py:class:`streamsets.sdk.sch_models.BaseModel` and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        pass

    def __iter__(self):
        """Enables the list enumeration or iteration."""
        for item in self._get_all_results_from_api().results:
            yield item

    def __getitem__(self, i):
        """Enables the user to fetch items by index.

        Args:
            i (:obj:`int`): Index of the item.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        return self._get_all_results_from_api().results[i]

    def __len__(self):
        """Provides length (count) of items.

        Returns:
            A :py:obj:`int` object.
        """
        results = self._get_all_results_from_api().results
        return len(results['data'] if 'data' in results else results)

    def __contains__(self, item_given):
        """Checks if given item is in the list of items by comparing the ids.

        Returns:
            A :py:obj:`boolean` object.
        """
        return self.contains(**{self._id_attr: getattr(item_given, self._id_attr)})

    def get(self, **kwargs):
        """
        Args:
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        result, new_kwargs = self._get_all_results_from_api(**kwargs)
        return result.get(**new_kwargs)

    def get_all(self, **kwargs):
        """
        Args:
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of inherited instances of
            :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        result, new_kwargs = self._get_all_results_from_api(**kwargs)
        return result.get_all(**new_kwargs)

    def __repr__(self):
        results, kwargs, class_type, class_kwargs = self._get_all_results_from_api()
        return str([class_type(result, **class_kwargs) for result in results['data']] if 'data' in results
                   else [class_type(result, **class_kwargs) for result in results])


class CollectionModel:
    """Base class wrapper with abstractions for pagination.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
    """
    PAGE_LENGTH = 50
    PAGINATION_PARAMS = ['offset', 'len']

    def _paginate(self, **kwargs):
        """Allows fetching of items in batches (pages)

        Workflow:

        1. Determine the total number of items that we need to fetch based on the ``len`` parameter (If not specified,
           assume infinite and fetch until Control Hub returns results).
        2. Use the len(self) (which calls :py:meth:`streamsets.sdk.sch_api.ApiClient.get_pipelines_count`) as a source
           of truth for the total number of pipelines existing in the Control Hub pipeline repository.
        3. Keep incrementing the offset with ``PAGE_LENGTH`` and query with new offset and ``PAGE_LENGTH`` until we
           reach requested number of items or we don't get any more items from Control Hub.
        4. While fetching these items in a loop, it is possible that some of the items are deleted by someone else
           affecting the current offset we are using. To handle this, in the while loop, if the len(self) decreases, we
           reduce the current offset by the number of items decreased (making sure, we aren't missing any items).
        5. In the list of items (order in which Control Hub returns the items), if the items that we already queried are
           deleted, the actual offset we have to use would reduce by the number of items deleted. On the otherhand, if
           the items that are deleted are the ones we haven't fetched yet, then we have reduced the offset which is not
           needed and hence end up getting duplicates. To handle this, we use a set to store all the item ids and
           yield only the one's we haven't fetched yet.
           eg. Lets say there are 59 pipelines in Control Hub and the parameter len is not specified. After we fetch the
           first 50 pipelines, if index 48, 49 and 50 pipelines are deleted, the next fetch would miss the new 48th and
           49th pipelines since the offset we would be using would be wrong. To handle this, we will reduce the next
           offset from 50 to 47 which would mean we would be fetching the 47th pipeline again and we handle this using
           the all_ids set but we won't be missing the new 48th and 49th index pipelines (old 50 and 51).
        """
        all_ids = set()
        previous_length = len(self)
        requested_length = kwargs.get('len', float('inf'))
        page_length = CollectionModel.PAGE_LENGTH
        current_offset = kwargs.get('offset', 0)
        # Fetch results with default offset and length or specified values
        kwargs_without_pagination_params = {k: v for k,v in kwargs.items()
                                            if k not in CollectionModel.PAGINATION_PARAMS}
        response, current_new_kwargs, class_type, class_kwargs = self._get_all_results_from_api(
                                                                      offset=current_offset,
                                                                      len=min(requested_length, page_length),
                                                                      **kwargs_without_pagination_params)
        # If an API is paginated, the result set we need to page through will be contained in the response's 'data'
        # attribute. If there is no 'data' attribute, the response itself is the result set (unpaginated API).
        if 'data' in response:
            current_results = SeekableList(class_type(item, **class_kwargs) for item in response['data'])
        else:
            current_results = SeekableList(class_type(item, **class_kwargs) for item in response)

        # Iterate over pages
        while current_results:
            # Filter results based on kwargs specified (ones that are not accepted as arguments for the control hub api
            # endpoints)
            current_results = current_results.get_all(**current_new_kwargs)
            for result in current_results:
                if len(all_ids) == requested_length:
                    # We fetched specified number of items so, return
                    return
                # This check is to avoid duplicates especially since we are doing the
                # if current_length < previous_length check below to handle deleted entities.
                item_id = getattr(result, self._id_attr)
                if item_id not in all_ids:
                    all_ids.add(item_id)
                    yield result
            current_offset += page_length
            current_length = len(self)
            # If the total number of items decreased, reduce the offset by the difference to make sure we return all the
            # items. If duplicates occur in the process as described in step 5 of workflow in the docstring are handled
            # above by checking for the id in all_ids.
            if current_length < previous_length:
                current_offset -= (previous_length - current_length)
            previous_length = current_length
            # If the API we're paging over isn't enabled for pagination, break the loop after returning the first
            # set of results to avoid an infinite loop.
            if 'offset' not in response and 'len' not in response:
                break
            logger.debug('Fetching items with offset=%d and len=%d', current_offset, page_length)
            response, current_new_kwargs, class_type, class_kwargs = self._get_all_results_from_api(
                                                                          offset=current_offset,
                                                                          len=page_length,
                                                                          **kwargs_without_pagination_params)
            current_results = SeekableList(class_type(item, **class_kwargs) for item in response['data'])

    def __init__(self, control_hub):
        self._control_hub = control_hub
        self._id_attr = 'id'

    def __repr__(self):
        response, kwargs, class_type, class_kwargs = self._get_all_results_from_api()
        return str([class_type(result, **class_kwargs) for result in response['data']]
                   if 'data' in response
                   else [class_type(result, **class_kwargs) for result in response])

    def __iter__(self):
        for item in self._paginate():
            yield item

    def __contains__(self, item_given):
        return self.contains(**{self._id_attr: getattr(item_given, self._id_attr)})

    def __len__(self):
        """Provides length (count) of items.

        Returns:
            A :py:obj:`int` object.
        """
        results = self._get_all_results_from_api().results
        return len(results['data'] if 'data' in results else results)

    def __getitem__(self, i):
        """Enables the user to fetch items by index.

        Args:
            i (:obj:`int`): Index of the item.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        if not isinstance(i, int) and not isinstance(i, slice):
            raise TypeError('list indices must be integers or slices, not {}'.format(type(i).__name__))

        total_number_of_items = len(self)

        if isinstance(i, int):
            # Convert negative index to positive index
            offset = total_number_of_items + i if i < 0 else i

            if not (0 <= offset < total_number_of_items):
                raise IndexError('list index out of range')

            len_ = 1
            new_i = 0
        else:
            # i is a slice
            if i.step == 0:
                raise ValueError('slice step cannot be zero')
            # i.start could be None
            start = i.start or 0
            # Convert negative index to positive index
            start = total_number_of_items + start if start < 0 else start

            # i.stop could be None and if i.stop is 0, we want it to be 0 so can't do i.stop or total_number_of_items
            # here
            stop = total_number_of_items if i.stop is None else i.stop
            # Convert negative index to positive index
            stop = total_number_of_items + stop if stop < 0 else stop

            step = i.step or 1

            if step < 0:
                # If step is negative, we need to look at the list in reverse
                start, stop = stop, start
                step = -step

            # Determine the number of items to query
            # If start is still negative, we don't need to query for the range start -> 0
            len_ = stop - max(0, start)

            # If length to query <= 0 or stop of the slice is <= 0 no need to query
            if len_ <= 0 or stop <= 0:
                return []

            # Offset cannot be negative
            offset = max(0, start)
            # Create a new slice with shifted indices
            new_i = slice(0, len_, step)

        return list(self._paginate(offset=offset, len=len_))[new_i]

    def _get_all_results_from_api(self, **kwargs):
        """Used to get multiple (all) results from api.

        Args:
            Optional arguments to be passed to filter the results.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of inherited instances of
                :py:class:`streamsets.sdk.sch_models.BaseModel` and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of inherited instances of :py:class:`streamsets.sdk.sch_models.BaseModel`
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Deployment`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's __init__
        """
        pass

    def contains(self, **kwargs):
        """
        Args:
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :py:obj:`boolean` object.
        """
        try:
            self.get(**kwargs)
        except ValueError:
            return False
        return True

    def get_all(self, **kwargs):
        """
        Args:
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of inherited instances of
            :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        return SeekableList(self._paginate(**kwargs))

    def get(self, **kwargs):
        """
        Args:
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        # This will avoid querying all the items after finding the required item at some point.
        for item in self._paginate(**kwargs):
            return item
        # Raise instance doesn't exist if not found at the end
        raise ValueError('Instance ({}) is not in list'.format(', '.join('{}={}'.format(k, v)
                                                                         for k, v in kwargs.items())))


class ACL(BaseModel):
    """Represents an ACL.

    Args:
        acl (:obj:`dict`): JSON representation of an ACL.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.

    Attributes:
        permissions (:py:class:`streamsets.sdk.sch_models.Permissions`): A Collection of Permissions.
    """
    _ATTRIBUTES_TO_REMAP = {'resource_id': 'resourceId',
                            'resource_owner': 'resourceOwner',
                            'resource_created_time': 'resourceCreatedTime',
                            'resource_type': 'resourceType',
                            'last_modified_by': 'lastModifiedBy',
                            'last_modified_on': 'lastModifiedOn'}
    _ATTRIBUTES_TO_IGNORE = ['permissions']
    _REPR_METADATA = ['resource_id', 'resource_type']

    def __init__(self, acl, control_hub):
        super().__init__(acl,
                         attributes_to_remap=ACL._ATTRIBUTES_TO_REMAP,
                         attributes_to_ignore=ACL._ATTRIBUTES_TO_IGNORE,
                         repr_metadata=ACL._REPR_METADATA)
        self.permissions = SeekableList(Permission(permission,
                                                   self.resource_type,
                                                   control_hub.api_client) for permission in self._data['permissions'])
        self._control_hub = control_hub

    def __getitem__(self, key):
        return getattr(self, key)

    def __len__(self):
        return len(self._data)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in {'resource_owner'}:
            set_acl(self._control_hub.api_client, self.resource_type, self.resource_id, self._data)

    @property
    def permission_builder(self):
        """Get a permission builder instance with which a pipeline can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACLPermissionBuilder`.
        """
        permission = {property: None
                      for property in self._control_hub._job_api['definitions']['PermissionJson']['properties']}

        return ACLPermissionBuilder(permission=permission, acl=self)

    def add_permission(self, permission):
        """Add new permission to the ACL.

        Args:
            permission (:py:class:`streamsets.sdk.sch_models.Permission`): A permission object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        self._data['permissions'].append(permission._data)
        return set_acl(self._control_hub.api_client, self.resource_type, self.resource_id, self._data)

    def remove_permission(self, permission):
        """Remove a permission from ACL.

        Args:
            permission (:py:class:`streamsets.sdk.sch_models.Permission`): A permission object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        permissions = self._data['permissions']
        self._data['permissions'] = [perm for perm in permissions if perm['subjectId'] != permission.subject_id]
        return set_acl(self._control_hub.api_client, self.resource_type, self.resource_id, self._data)


class ACLPermissionBuilder():
    """Class to help build the ACL permission.

    Args:
        permission (:py:class:`streamsets.sdk.sch_models.Permission`): A permission object.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): An ACL object.
    """

    def __init__(self, permission, acl):
        self._permission = permission
        self._acl = acl

    def build(self, subject_id, subject_type, actions):
        """Method to help build the ACL permission.

        Args:
            subject_id (:obj:`str`): Id of the subject e.g. 'test@test'.
            subject_type (:obj:`str`): Type of the subject e.g. 'USER'.
            actions (:obj:`list`): A list of actions of type :obj:`str` e.g. ['READ', 'WRITE', 'EXECUTE'].

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Permission`.
        """
        self._permission.update({'resourceId': self._acl.resource_id,
                                 'subjectId': subject_id,
                                 'subjectType': subject_type,
                                 'actions': actions})
        return Permission(self._permission, self._acl.resource_type, self._acl._control_hub.api_client)


class AdminTool:
    """SCH Admin tool model.

    Args:
        base_url (:obj:`str`): Base url of the admin tool.
        username (:obj:`str`): Username for the admin tool.
        password (:obj:`str`): Password for the admin tool.
    """
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.api_client = sch_api.AdminToolApiClient(base_url, username, password)
        self.api_client.login()

    @property
    def logs(self):
        """Gather system logs from admin app."""
        log_parts = []
        # As per 'https://git.io/JexPa', the streamer uses a buffer of size 50 Kb
        offset_constant = 50*1024
        ending_offset = offset_constant
        # Retreive all parts of the text file and combine them
        log_part = self.api_client.get_system_logs(component_url=self.base_url,
                                                   ending_offset=ending_offset).response.text
        while log_part:
            log_parts.append(log_part)
            ending_offset += offset_constant
            log_part = self.api_client.get_system_logs(component_url=self.base_url,
                                                       ending_offset=ending_offset).response.text
        return Logs(''.join(log_parts).split('\n'))



class Permission(BaseModel):
    """A container for a permission.

    Args:
        permission (:obj:`dict`): A Python object representation of a permission.
        resource_type (:obj:`str`): String representing the type of resource e.g. 'JOB', 'PIPELINE'.
        api_client (:py:class:`streamsets.sdk.sch_api.ApiClient`): An instance of ApiClient.

    Attributes:
        resource_id (:obj:`str`): Id of the resource e.g. Pipeline or Job.
        subject_id (:obj:`str`): Id of the subject e.g. user id ``'admin@admin'``.
        subject_type (:obj:`str`): Type of the subject e.g. ``'USER'``.
        last_modified_by (:obj:`str`): User who last modified this permission e.g. ``'admin@admin'``.
        last_modified_on (:obj:`int`): Timestamp at which this permission was last modified e.g. ``1550785079811``.
    """
    _ATTRIBUTES_TO_REMAP = {'resource_id': 'resourceId',
                            'subject_id': 'subjectId',
                            'subject_type': 'subjectType',
                            'last_modified_by': 'lastModifiedBy',
                            'last_modified_on': 'lastModifiedOn'}
    _ATTRIBUTES_TO_IGNORE = ['resource_type', 'api_client']
    _REPR_METADATA = ['resource_id', 'subject_type', 'subject_id']

    def __init__(self, permission, resource_type, api_client):
        super().__init__(permission,
                         attributes_to_remap=Permission._ATTRIBUTES_TO_REMAP,
                         attributes_to_ignore=Permission._ATTRIBUTES_TO_IGNORE,
                         repr_metadata=Permission._REPR_METADATA)
        self._resource_type = resource_type
        self._api_client = api_client

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in {'actions', 'subject_id', 'subject_type'}:
            update_acl_permissions(self._api_client, self._resource_type, self._data)


class UserBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.User`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_user_builder`.

    Args:
        user (:obj:`dict`): Python object built from our Swagger UserJson definition.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`. Default: ``None``.
    """

    def __init__(self, user, roles, control_hub=None):
        self._user = user
        self._roles = roles
        self._control_hub = control_hub

    def build(self, id, display_name, email_address, saml_user_name=None, ldap_user_name=None):
        """Build the user.

        Args:
            id (:obj:`str`): User Id.
            display_name (:obj:`str`): User display name.
            email_address (:obj:`str`): User Email Address.
            saml_user_name (:obj:`str`, optional): Default: ``None``.
            ldap_user_name (:obj:`str`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.User`.
        """
        user_prefix = id.split('@')[0]
        if saml_user_name and ldap_user_name:
            raise ValueError('Arguments saml_user_name and ldap_user_name cannot be specified at the same time')
        if not self._control_hub.ldap_enabled and ldap_user_name:
            raise ValueError('LDAP user name cannot be specified without enabling LDAP')
        # Following logic from https://git.io/JvRTf.
        organization = self._control_hub.organization
        if organization == 'admin' and saml_user_name:
            raise ValueError('SAML user name cannot be specified for admin organization user')

        name_in_org = None
        # Following logic from https://git.io/JvRUP.
        if not self._control_hub.ldap_enabled:
            if organization != 'admin':
                name_in_org = saml_user_name if saml_user_name else email_address
        else:
            name_in_org = ldap_user_name if ldap_user_name else user_prefix
        self._user.update({'id': id,
                           'name': display_name,
                           'email': email_address,
                           'nameInOrg': name_in_org})
        return User(user=self._user, roles=self._roles)


class User(BaseModel):
    """Model for User.

    Args:
        user (:obj:`dict`): JSON representation of User.
        roles (:obj:`dict`): A mapping of role IDs to role labels.

    Attributes:
        active (:obj:`bool`): Whether the user is active or not.
        created_by (:obj:`str`): Creator of this user.
        created_on (:obj:`str`): Creation time of this user.
        display_name (:obj:`str`): Display name of this user.
        email_address (:obj:`str`): Email address of this user.
        id (:obj:`str`): Id of this user.
        groups (:obj:`list`): Groups this user belongs to.
        last_modified_by (:obj:`str`): User last modified by.
        last_modified_on (:obj:`str`): User last modification time.
        password_expires_on (:obj:`str`): User's password expiration time.
        password_system_generated (:obj:`bool`): Whether User's password is system generated or not.
        roles (:obj:`set`): A set of role labels.
        saml_user_name (:obj:`str`): SAML username of user.
    """
    _ATTRIBUTES_TO_IGNORE = ['destroyer', 'organization', 'roles', 'userDeleted']
    _ATTRIBUTES_TO_REMAP = {'created_by': 'creator',
                            'email_address': 'email',
                            'display_name': 'name',
                            'saml_user_name': 'nameInOrg',
                            'password_expires_on': 'passwordExpiryTime',
                            'password_system_generated': 'passwordGenerated'}
    _REPR_METADATA = ['id', 'display_name']

    # Jetty requires ever SCH user to have the 'user' role, which is hidden in the UI. We'll do the same.
    _ROLES_TO_HIDE = ['user']

    def __init__(self, user, roles):
        super().__init__(user,
                         attributes_to_ignore=User._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=User._ATTRIBUTES_TO_REMAP,
                         repr_metadata=User._REPR_METADATA)
        self._roles = roles

    @property
    def roles(self):
        return {self._roles[role] for role in self._data.get('roles', []) if role not in User._ROLES_TO_HIDE}

    @roles.setter
    def roles(self, value):
        # We reverse the _roles dictionary to let this setter deal with role labels while still writing role ids.
        role_label_to_id = {role_label: role_id for role_id, role_label in self._roles.items()}

        value_ = value if isinstance(value, list) else [value]
        self._data['roles'] = list({role_label_to_id[role] for role in value_} | set(User._ROLES_TO_HIDE))


class Users(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.User` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, roles, organization):
        super().__init__(control_hub)
        self._roles = roles
        self._organization = organization

    def _get_all_results_from_api(self, organization=None, **kwargs):
        """
        Args:
            organization (:obj:`str`)
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.User` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.User`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        response = self._control_hub.api_client.get_all_users(org_id=organization,
                                                              offset=kwargs_unioned['offset'],
                                                              len=kwargs_unioned['len'],
                                                              with_wrapper=True).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, User, {'roles': self._roles})


class LoginAudit(BaseModel):
    """Model for LoginAudit.

    Args:
        login_audit (:obj:`dict`): JSON representation of LoginAudit.

    Attributes:
        details (:obj:`str`): Details of login audit.
        ip_address (:obj:`str`): IP address that tried logging in.
        login_time (:obj:`int`): Login time of this user.
        logout_time (:obj:`int`): Time of logout.
        logout_user_id (:obj:`str`): User that attempted logout.
        logout_reason (:obj:`str`): Reason for logout.
        organization (:obj:`str`): Organization ID.
        success (:obj:`bool`): If this login succeeded.
        user_agent (:obj:`str`): User that made login request. May differ from user_id
        user_id (:obj:`str`): ID of user account that login was attempted for.
    """
    _ATTRIBUTES_TO_REMAP = {'login_time': 'loginTimestamp',
                            'logout_time': 'logoutTimestamp',
                            'logout_user_id': 'logoutUser',
                            'organization': 'org_id'}
    _REPR_METADATA = ['user_id', 'ip_address', 'login_timestamp', 'logout_timestamp']

    def __init__(self, login_audit):
        super().__init__(login_audit,
                         attributes_to_remap=LoginAudit._ATTRIBUTES_TO_REMAP,
                         repr_metadata=LoginAudit._REPR_METADATA)


class LoginAudits(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.LoginAudit` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization
        self._id_attr = 'login_time'

    def _get_all_results_from_api(self, organization=None, **kwargs):
        """
        Args:
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.LoginAudit` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.LoginAudit`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None, 'sort_field': None, 'sort_order': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        response = self._control_hub.api_client.get_all_login_audits_for_org(org_id=organization,
                                                                             offset=kwargs_unioned['offset'],
                                                                             len=kwargs_unioned['len'],
                                                                             sort_field=kwargs_unioned['sort_field'],
                                                                             sort_order=kwargs_unioned['sort_order'],
                                                                             with_wrapper=True).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, LoginAudit, {})


class ActionAudit(BaseModel):
    """Model for ActionAudit.

    Args:
        action_audit (:obj:`dict`): JSON representation of ActionAudit.

    Attributes:
        action (:obj:`str`): Action performed.
        affected_user_id (:obj:`str`): User ID of the affected user.
        field_type (:obj:`str`): Type of field.
        id (:obj:`str`): ID of this action audit.
        ip_address (:obj:`str`): IP address that tried logging in.
        new_value (:obj:`str`): New value.
        old_value (:obj:`str`): Old Value.
        organization (:obj:`str`): Organization ID.
        requested_user_id (:obj:`str`): User ID of the requested user.
        time (:obj:`int`): Timestamp.
    """
    _ATTRIBUTES_TO_REMAP = {'affected_user_id': 'affectsUser',
                            'requested_user_id': 'requesterId',
                            'organization': 'org_id'}
    _REPR_METADATA = ['affected_user_id', 'action', 'time', 'ip_address']

    def __init__(self, action_audit):
        super().__init__(action_audit,
                         attributes_to_remap=ActionAudit._ATTRIBUTES_TO_REMAP,
                         repr_metadata=ActionAudit._REPR_METADATA)


class ActionAudits(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.ActionAudit` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, organization=None, **kwargs):
        """
        Args:
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.ActionAudit` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.ActionAudit`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None, 'sort_field': None, 'sort_order': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        response = self._control_hub.api_client.get_all_user_actions_for_org(org_id=organization,
                                                                             offset=kwargs_unioned['offset'],
                                                                             len=kwargs_unioned['len'],
                                                                             sort_field=kwargs_unioned['sort_field'],
                                                                             sort_order=kwargs_unioned['sort_order'],
                                                                             with_wrapper=True).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, ActionAudit, {})


class ConnectionAudit(BaseModel):
    """Model for ConnectionAudit.

    Args:
        connection_audit (:obj:`dict`): JSON representation of ConnectionAudit.

    Attributes:
        id (:obj:`str`): Connection audit ID.
        organization (:obj:`str`): Organization.
        user_id (:obj:`str`): User ID.
        connection_id (:obj:`str`): Connection ID.
        connection_name (:obj:`str`): Connection name.
        audit_time (:obj:`str`): Audit time.
        audit_action (:obj:`str`): Audit action
    """
    _REPR_METADATA = ['user_id', 'connection_name', 'audit_action', 'audit_time']

    def __init__(self, connection_audit):
        super().__init__(connection_audit,
                         repr_metadata=ConnectionAudit._REPR_METADATA)


class ConnectionAudits(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.ConnectionAudit` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, start_time=None, end_time=None, organization=None, connection=None, **kwargs):
        """
        Args:
            start_time (:obj:`float`, optional): Start time in milliseconds (will be rounded off to closest integer).
                                                 Default: ``None``. If both start_time and end_time are not specified,
                                                 we return the audits for last 30 days.
            end_time (:obj:`float`, optional): End time in milliseconds (will be rounded off to closest integer).
                                               Default: ``None``. If both start_time and end_time are not specified,
                                               we return the audits for last 30 days.
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            connection (:py:obj:`streamsets.sdk.sch_models.Connection`, optional): Connection object. Default: ``None``.
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.ConnectionAudit` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.ConnectionAudit`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None, 'sort_field': None, 'sort_order': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        if (start_time is None and end_time is not None) or (start_time is not None and end_time is None):
            raise ValueError('Either both or None of start_time and end_time should be specified')
        if start_time is not None and connection is not None:
            raise ValueError('start_time and end_time cannot be specified when connection argument is passed')
        if connection is not None:
            response = (self._control_hub.api_client.get_audits_for_connection(connection_id=connection.id
                                                                               ).response.json())
        elif start_time is None and end_time is None:
            response = self._control_hub.api_client.get_all_connection_audits_last_30_days(
                org_id=organization,
                offset=kwargs_unioned['offset'],
                len_=kwargs_unioned['len'],
                sort_field=kwargs_unioned['sort_field'],
                sort_order=kwargs_unioned['sort_order']
                ).response.json()
        else:
            response = self._control_hub.api_client.get_all_connection_audits(org_id=organization,
                                                                              offset=kwargs_unioned['offset'],
                                                                              len_=kwargs_unioned['len'],
                                                                              sort_field=kwargs_unioned['sort_field'],
                                                                              sort_order=kwargs_unioned['sort_order'],
                                                                              start_time=int(start_time),
                                                                              end_time=int(end_time)).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, ConnectionAudit, {})


class Roles(list):
    """Wrapper class over the list of Roles.

    Args:
        values (:obj:`list`): List of roles.
        entity (:py:class:`streamsets.sdk.sch_models.Group`) or
              (:py:class:`streamsets.sdk.sch_models.User`): Group or User object.
        role_label_to_id (:obj:`dict`): Role label to Role ID mapping.
    """
    def __init__(self, values, entity, role_label_to_id):
        super().__init__(values)
        self._entity = entity
        self._role_label_to_id = role_label_to_id

    def append(self, value):
        # Use super().append() to throw corresponding exceptions when necessary.
        super().append(value)
        self._entity._data['roles'].append(self._role_label_to_id[value])

    def remove(self, value):
        # Use super().remove() to throw corresponding exceptions when necessary.
        super().remove(value)
        self._entity._data['roles'].remove(self._role_label_to_id[value])


class GroupBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Group`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_group_builder`.

    Args:
        group (:obj:`dict`): Python object built from our Swagger GroupJson definition.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
    """

    def __init__(self, group, roles):
        self._group = group
        self._roles = roles

    def build(self, id, display_name, ldap_groups=None):
        """Build the group.

        Args:
            id (:obj:`str`): Group ID.
            display_name (:obj:`str`): Group display name.
            ldap_groups (:obj:`list`): List of LDAP groups (strings).

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Group`.
        """
        self._group.update({'id': id,
                            'name': display_name,
                            'externalGroupIds': ldap_groups})
        return Group(group=self._group, roles=self._roles)


class Group(BaseModel):
    """Model for Group.

    Args:
        group (:obj:`dict`): A Python object representation of Group.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
    """
    _REPR_METADATA = ['id', 'display_name']

    # Jetty requires every SCH group to have the 'user' role, which is hidden in the UI. We'll do the same.
    _ROLES_TO_HIDE = ['user']

    def __init__(self, group, roles):
        super().__init__(group,
                         attributes_to_ignore=User._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=User._ATTRIBUTES_TO_REMAP,
                         repr_metadata=User._REPR_METADATA)
        self._roles = roles

    @property
    def roles(self):
        return Roles([self._roles[role] for role in self._data.get('roles', []) if role not in Group._ROLES_TO_HIDE],
                     self,
                     reversed_dict(self._roles))

    @roles.setter
    def roles(self, value):
        # We reverse the _roles dictionary to let this setter deal with role labels while still writing role ids.
        role_label_to_id = reversed_dict(self._roles)

        value_ = value if isinstance(value, list) else [value]
        self._data['roles'] = list({role_label_to_id[role] for role in value_} | set(Group._ROLES_TO_HIDE))


class Groups(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Group` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, roles, organization):
        super().__init__(control_hub)
        self._roles = roles
        self._organization = organization

    def _get_all_results_from_api(self, id=None, organization=None, **kwargs):
        """
        Args:
            id (:obj:`str`)
            organization (:obj:`str`)
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Group` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Group`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        if id is not None:
            try:
                response = [self._control_hub.api_client.get_group(org_id=organization, group_id=id).response.json()]
                kwargs_unused = kwargs_instance.subtract()
                return CollectionModelResults(response, kwargs_unused, Group, {'roles': self._roles})
            except requests.exceptions.HTTPError:
                raise ValueError('Group (id={}) not found'.format(id))
        response = self._control_hub.api_client.get_all_groups(org_id=organization,
                                                               offset=kwargs_unioned['offset'],
                                                               len=kwargs_unioned['len'],
                                                               with_wrapper=True).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Group, {'roles': self._roles})


class OrganizationBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Organization`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_organization_builder`.

    Args:
        organization (:obj:`dict`): Python object built from our Swagger UserJson definition.
    """

    def __init__(self, organization, organization_admin_user):
        self._organization = organization
        self._organization_admin_user = organization_admin_user

    def build(self, id, name, admin_user_id, admin_user_display_name, admin_user_email_address,
              admin_user_ldap_user_name=None):
        """Build the organization.

        Args:
            id (:obj:`str`): Organization ID.
            name (:obj:`str`): Organization name.
            admin_user_id (:obj:`str`): User Id of the admin of this organization.
            admin_user_display_name (:obj:`str`): User display name of admin of this organization.
            admin_user_email_address (:obj:`str`): User email address of admin of this organization.
            admin_user_ldap_user_name (:obj:`str`, optional): LDAP username. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Organization`.
        """
        self._organization.update({'id': id,
                                   'name': name,
                                   'primaryAdminId': admin_user_id})
        self._organization_admin_user.update({'id': admin_user_id,
                                              'name': admin_user_display_name,
                                              'email': admin_user_email_address,
                                              'organization': id,
                                              'nameInOrg': admin_user_ldap_user_name})
        return Organization(self._organization, self._organization_admin_user)


class Organization(BaseModel):
    """Model for Organization.

    Args:
        organization (:obj:`str`): Organization Id.
        organization_admin_user (:obj:`str`, optional): Default: ``None``.
        api_client (:py:obj:`streamsets.sdk.sch_api.ApiClient`, optional): Default: ``None``.
    """
    _ATTRIBUTES_TO_IGNORE = ['configuration', 'passwordExpiryTimeInMillis', ]
    _ATTRIBUTES_TO_REMAP = {'admin_user_id': 'primaryAdminId',
                            'created_by': 'creator',
                            'saml_intergration_enabled': 'externalAuthEnabled'}
    _REPR_METADATA = ['id', 'name']

    def __init__(self, organization, organization_admin_user=None, api_client=None):
        super().__init__(organization,
                         attributes_to_ignore=Organization._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=Organization._ATTRIBUTES_TO_REMAP,
                         repr_metadata=Organization._REPR_METADATA)
        self._organization_admin_user = organization_admin_user
        self._api_client = api_client

    @property
    def default_user_password_expiry_time_in_days(self):
        return self._data['passwordExpiryTimeInMillis'] / 86400000  # 1 d => ms

    @default_user_password_expiry_time_in_days.setter
    def default_user_password_expiry_time_in_days(self, value):
        self._data['passwordExpiryTimeInMillis'] = value * 86400000

    @property
    def configuration(self):
        configuration = self._api_client.get_organization_configuration(self.id).response.json()

        # Some of the config names are a bit long, so shorten them slightly...
        ID_TO_REMAP = {'accountType': 'Organization account type',
                       'contractExpirationTime': 'Timestamp of the contract expiration',
                       'trialExpirationTime': 'Timestamp of the trial expiration'}
        return Configuration(configuration=configuration,
                             update_callable=self._api_client.update_organization_configuration,
                             update_callable_kwargs=dict(org_id=self.id, body=configuration),
                             id_to_remap=ID_TO_REMAP)

    @configuration.setter
    def configuration(self, value):
        self._api_client.update_organization_configuration(self.id, value._data)


class Organizations(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Organization` instances."""

    def _get_all_results_from_api(self, **kwargs):
        """
        Args:
            kwargs: optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Organization` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Organization`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.get_all_organizations(offset=kwargs_unioned['offset'],
                                                                      len=kwargs_unioned['len'],
                                                                      with_wrapper=True
                                                                      ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Organization,
                                      {'api_client': self._control_hub.api_client})


class Configuration:
    """A dictionary-like container for getting and setting configuration values.

    Args:
        configuration (:obj:`dict`): JSON object representation of configuration.
        update_callable (optional): A callable to which ``self._data`` will be passed as part of ``__setitem__``.
        update_callable_kwargs (:obj:`dict`, optional): A dictionary of kwargs to pass (along with a body)
            to the callable.
        id_to_remap (:obj:`dict`, optional): A dictionary mapping configuration IDs to human-readable container keys.
    """

    def __init__(self, configuration, update_callable=None, update_callable_kwargs=None, id_to_remap=None):
        self._data = configuration
        self._update_callable = update_callable
        self._update_callable_kwargs = update_callable_kwargs or {}
        self._id_to_remap = id_to_remap or {}

    def __getitem__(self, key):
        for config in self._data:
            if config['name'] == key or self._id_to_remap.get(config.get('id')) == key:
                break
        else:
            raise KeyError(key)
        if 'type' not in config:
            return config['value']
        if config['type'] == 'boolean':
            return json.loads(config['value'])
        elif config['type'] == 'integer':
            return int(config['value'])
        else:
            return config['value']

    def __setitem__(self, key, value):
        for config in self._data:
            if config['name'] == key or self._id_to_remap.get(config.get('id')) == key:
                break
        else:
            raise KeyError(key)
        config['value'] = value
        if self._update_callable:
            kwargs = dict(body=[config])
            kwargs.update(self._update_callable_kwargs)
            self._update_callable(**kwargs)

    def __repr__(self):
        configs = {}
        for config in self._data:
            key = self._id_to_remap.get(config.get('id')) or config['name']
            if 'type' not in config:
                value = config['value']
            elif config['type'] == 'boolean':
                value = json.loads(config['value'])
            elif config['type'] == 'integer':
                value = int(config['value'])
            else:
                value = config['value']
            configs[key] = value
        return '{{{}}}'.format(', '.join("'{}': {}".format(k, v) for k, v in configs.items()))

    def get(self, key, default=None):
        """Return the value of key or, if not in the configuration, the default value."""
        try:
            return self[key]
        except KeyError:
            return default


class DataCollector(BaseModel):
    """Model for Data Collector.

    Attributes:
        execution_mode (:obj:`bool`): ``True`` for Edge and ``False`` for SDC.
        id (:obj:`str`): Data Collectort id.
        labels (:obj:`list`): Labels for Data Collector.
        last_validated_on (:obj:`str`): Last validated time for Data Collector.
        reported_labels (:obj:`list`): Reported labels for Data Collector.
        url (:obj:`str`): Data Collector's url.
        version (:obj:`str`): Data Collector's version.
    """
    _ATTRIBUTES_TO_IGNORE = ['offsetProtocolVersion', 'edge']
    _ATTRIBUTES_TO_REMAP = {'execution_mode': 'edge',
                            'last_validated_on': 'lastReportedTime',
                            'url': 'httpUrl'}
    _REPR_METADATA = ['id', 'url']

    def __init__(self, data_collector, control_hub):
        super().__init__(data_collector,
                         attributes_to_ignore=DataCollector._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=DataCollector._ATTRIBUTES_TO_REMAP,
                         repr_metadata=DataCollector._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def accessible(self):
        """Returns a :obj:`bool` for whether the Data Collector instance is accessible."""
        try:
            # We disable InsecureRequestWarning and disable SSL certificate verification to enable self-signed certs.
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            requests.get(self.http_url, verify=False, timeout=5)
            return True
        except requests.exceptions.ConnectionError:
            return False

    @property
    def responding(self):
        """Returns a :obj:`bool` for whether the Data Collector instance is responding."""
        self._refresh()
        return self._data['responding']

    @property
    def attributes(self):
        """Returns a :obj:`dict` of Data Collector attributes."""
        return self._component['attributes']

    @property
    def attributes_updated_on(self):
        return self._component['attributesUpdatedOn']

    @property
    def authentication_token_generated_on(self):
        return self._component['authTokenGeneratedOn']

    @property
    def instance(self):
        # Disable SSL cert verification to enable use of self-signed certs.
        SdcDataCollector.VERIFY_SSL_CERTIFICATES = False
        return SdcDataCollector(self.url, control_hub=self._control_hub)

    @property
    def jobs(self):
        return SeekableList(self._control_hub.jobs.get(id=job_id) for job_id in self.job_ids)

    @property
    def job_ids(self):
        # Separated this out, to help make stuff more performant since, DataCollector.jobs would make one api call for
        # every job id. People can choose to use this method if they need just the ids and they have lot of jobs.
        return [item['jobId'] for item in
                self._control_hub.api_client.get_pipelines_running_in_sdc(self.id).response.json()]

    @property
    def registered_by(self):
        return self._component['registeredBy']

    @property
    def pipelines_committed(self):
        """Control Hub Job IDs that are about to be started but have no corresponding pipeline status yet.

        Returns:
            A :obj:`list` of Job IDs (:obj:`str` objects).
        """
        self._refresh()
        return self._data['pipelinesCommitted']

    @property
    def acl(self):
        """Get DataCollector ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_executor_acl(executor_id=self.id).response.json(),
                   self._control_hub)

    @acl.setter
    def acl(self, sdc_acl):
        """Update DataCollector ACL.

        Args:
            sdc_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The sdc ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.set_executor_acl(executor_id=self.id, executor_acl_json=sdc_acl._data)

    def _refresh(self):
        self._data = self._control_hub.api_client.get_sdc(data_collector_id=self.id).response.json()


class Transformer(BaseModel):
    """Model for Transformer.

    Attributes:
        execution_mode (:obj:`str`):
        id (:obj:`str`): Transformer id.
        labels (:obj:`list`): Labels for Transformer.
        last_validated_on (:obj:`str`): Last validated time for Transformer.
        reported_labels (:obj:`list`): Reported labels for Transformer.
        url (:obj:`str`): Transformer's url.
        version (:obj:`str`): Transformer's version.
    """
    _ATTRIBUTES_TO_IGNORE = ['offsetProtocolVersion', 'edge']
    _ATTRIBUTES_TO_REMAP = {'execution_mode': 'edge',
                            'last_validated_on': 'lastReportedTime',
                            'url': 'httpUrl'}
    _REPR_METADATA = ['id', 'url']

    def __init__(self, transformer, control_hub):
        super().__init__(transformer,
                         attributes_to_ignore=Transformer._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=Transformer._ATTRIBUTES_TO_REMAP,
                         repr_metadata=Transformer._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def accessible(self):
        """Returns a :obj:`bool` for whether the Transformer instance is accessible."""
        try:
            # We disable InsecureRequestWarning and disable SSL certificate verification to enable self-signed certs.
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            requests.get(self.http_url, verify=False, timeout=5)
            return True
        except requests.exceptions.ConnectionError:
            return False

    @property
    def attributes(self):
        """Returns a :obj:`dict` of Transformer attributes."""
        return self._component['attributes']

    @property
    def attributes_updated_on(self):
        return self._component['attributesUpdatedOn']

    @property
    def authentication_token_generated_on(self):
        return self._component['authTokenGeneratedOn']

    @property
    def instance(self):
        # Disable SSL cert verification to enable use of self-signed certs.
        StTransformer.VERIFY_SSL_CERTIFICATES = False
        return StTransformer(server_url=self.url, control_hub=self._control_hub)

    @property
    def registered_by(self):
        return self._component['registeredBy']

    @property
    def acl(self):
        """Get Transformer ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_executor_acl(executor_id=self.id).response.json(),
                   self._control_hub)

    @acl.setter
    def acl(self, transformer_acl):
        """Update Transformer ACL.

        Args:
            transformer_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The transformer ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.set_executor_acl(executor_id=self.id,
                                                             executor_acl_json=transformer_acl._data)


class ProvisioningAgent(BaseModel):
    """Model for Provisioning Agent.

    Args:
        provisioning_agent (:obj:`dict`): A Python object representation of Provisioning Agent.
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
    """
    _REPR_METADATA = ['id', 'name', 'type', 'version']

    def __init__(self, provisioning_agent, control_hub):
        # This is hardcoded in domainserver https://git.io/JecVj
        provisioning_agent['type'] = 'Kubernetes'
        super().__init__(provisioning_agent,
                         repr_metadata=ProvisioningAgent._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def deployments(self):
        """Get the deployments associated with the Provisioning Agent.

        Returns:
              A :obj:`list` of :py:class:`streamsets.sdk.sch_models.Deployment` instances.
        """
        return self._control_hub.deployments.get_all(dpm_agent_id=self.id)

    @property
    def acl(self):
        """Get the ACL of a Provisioning Agent.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_provisioning_agent_acl(dpm_agent_id=self.id).response.json(),
                   self._control_hub)

    @acl.setter
    def acl(self, dpm_agent_acl):
        self._control_hub.api_client.set_provisioning_agent_acl(dpm_agent_id=self.id,
                                                                dpm_agent_acl_json=dpm_agent_acl._data)


class ProvisioningAgents(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.ProvisioningAgent` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """
    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, id=None, organization=None, **kwargs):
        """
        Args:
            id (:obj:`str`, optional): Default: ``None``.
            organization (:obj:`str`, optional): Default: ``None``.
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.ProvisioningAgent` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.ProvisioningAgent`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order_by': 'LAST_REPORTED_TIME', 'order': 'DESC', 'version': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        if id is not None:
            try:
                response = [self._control_hub.api_client.get_provisioning_agent(agent_id=id).response.json()]
            except requests.exceptions.HTTPError:
                raise ValueError('Provisioning Agent (id={}) not found'.format(id))
        else:
            response = self._control_hub.api_client.return_all_provisioning_agents(organization=organization,
                                                                                   offset=kwargs_unioned['offset'],
                                                                                   len=kwargs_unioned['len'],
                                                                                   order_by=kwargs_unioned['order_by'],
                                                                                   order=kwargs_unioned['order'],
                                                                                   version=kwargs_unioned['version'],
                                                                                   with_wrapper=True
                                                                                   ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, ProvisioningAgent, {'control_hub': self._control_hub})


class DeploymentBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Deployment`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_deployment_builder`.

    Args:
        deployment (:obj:`dict`): Python object that represents Deployment JSON.
    """

    def __init__(self, deployment):
        self._deployment = deployment

    def build(self, name, provisioning_agent, number_of_data_collector_instances, spec=None, description=None,
              data_collector_labels=None):
        """Build the deployment.

        Args:
            name (:obj:`str`): Deployment Name.
            provisioning_agent (:py:obj:`streamsets.sdk.sch_models.ProvisioningAgent`): Agent to use.
            number_of_data_collector_instances (obj:`int`): Number of sdc instances.
            spec (:obj:`dict`, optional): Deployment yaml in dictionary format. Will use default yaml used by ui if
                                          left out.
            description (:obj:`str`, optional): Default: ``None``.
            data_collector_labels (:obj:`list`, optional): Default: ``['all']``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Deployment`.
        """
        current_deployment = dict(self._deployment)
        if spec:
            spec = yaml.dump(spec, default_flow_style=False)
        current_deployment.update({'name': name,
                                   'description': description,
                                   'labels': data_collector_labels or [],
                                   'numInstances': number_of_data_collector_instances,
                                   'spec': spec or DEFAULT_PROVISIONING_SPEC,
                                   'agentId': provisioning_agent.id})
        return Deployment(deployment=current_deployment)


class Deployment(BaseModel):
    """Model for Deployment.

    Args:
        deployment (:obj:`dict`): A Python object representation of Deployment.
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
    """
    _ATTRIBUTES_TO_REMAP = {'number_of_data_collector_instances': 'numInstances'}
    _REPR_METADATA = ['id', 'name', 'number_of_data_collector_instances', 'status']

    def __init__(self, deployment, control_hub=None):
        super().__init__(deployment,
                         attributes_to_remap=Deployment._ATTRIBUTES_TO_REMAP,
                         repr_metadata=Deployment._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def status(self):
        return self._data['currentDeploymentStatus']['status']

    @property
    def provisioning_agent(self):
        return self._control_hub.provisioning_agents.get(id=self._data['currentDeploymentStatus']['dpmAgent']['id'])

    @property
    def acl(self):
        """Get the ACL of a Deployment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_deployment_acl(deployment_id=self.id).response.json(),
                   self._control_hub)

    @acl.setter
    def acl(self, deployment_acl):
        self._control_hub.api_client.set_deployment_acl(deployment_id=self.id,
                                                        deployment_acl_json=deployment_acl._data)


class Deployments(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Deployment` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """
    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, id=None, organization=None, **kwargs):
        """
        Args:
            id (:obj:`str`, optional): Default: ``None``.
            organization (:obj:`str`, optional): Default: ``None``.
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Deployment` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Deployment`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order_by': 'LAST_MODIFIED_ON', 'order': 'DESC',
                           'dpm_agent_id': None, 'deployment_status': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        if id is not None:
            try:
                response = [self._control_hub.api_client.get_deployment(deployment_id=id).response.json()]
            except requests.exceptions.HTTPError:
                raise ValueError('Deployment (id={}) not found'.format(id))
        else:
            deployment_ids = [deployment['id'] for deployment in self._control_hub.api_client
                .return_all_deployments(organization=organization,
                                        offset=kwargs_unioned['offset'],
                                        len=kwargs_unioned['len'],
                                        order_by=kwargs_unioned['order_by'],
                                        order=kwargs_unioned['order'],
                                        dpm_agent_id=kwargs_unioned['dpm_agent_id'],
                                        deployment_status=kwargs_unioned['deployment_status'],
                                        with_wrapper=True
                                        ).response.json()]
            # TODO: Because return_all_deployments does not include the yaml spec, we have to request them one at a
            #  time. We should see if yaml spec can be returned with the API referenced by return_all_deployments.
            response = [self._control_hub.api_client.get_deployment(deployment_id=deployment_id).response.json()
                        for deployment_id in deployment_ids]
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Deployment, {'control_hub': self._control_hub})


class SchSdcStage(SdcStage):
    def use_connection(self, *connections):
        if not hasattr(self, 'connection'):
            raise ValueError('Connections for stage {} are not supported yet'.format(self.stage_name))
        # For the foreseeable future, only one connection per stage is possible
        connection = connections[0]
        # Based on the label 'Connection' of the config field connectionSelection
        self.set_attributes(connection=connection.id)


class SchStStage(StStage):
    def use_connection(self, *connections):
        if not hasattr(self, 'connection'):
            raise ValueError('Connections for stage {} are not supported yet'.format(self.stage_name))
        # For the foreseeable future, only one connection per stage is possible
        connection = connections[0]
        # Based on the label 'Connection' of the config field connectionSelection
        self.set_attributes(connection=connection.id)


class PipelineBuilder(SdcPipelineBuilder):
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Pipeline`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_pipeline_builder`.

    Args:
        pipeline (:obj:`dict`): Python object built from our Swagger PipelineJson definition.
        data_collector_pipeline_builder (:py:class:`streamsets.sdk.sdc_models.PipelineBuilder`): Data Collector Pipeline
                                                                                                 Builder object.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Default: ``None``.
        fragment (:obj:`boolean`, optional): Specify if a fragment builder. Default: ``False``.
    """
    def __init__(self, pipeline, data_collector_pipeline_builder, control_hub=None, fragment=False):
        super().__init__(data_collector_pipeline_builder._pipeline,
                         data_collector_pipeline_builder._definitions,
                         fragment=fragment)
        self._data_collector_pipeline_builder = data_collector_pipeline_builder
        self._sch_pipeline = pipeline
        self._control_hub = control_hub
        self._fragment = fragment
        self._config_key = 'pipelineFragmentConfig' if 'pipelineFragmentConfig' in self._pipeline else 'pipelineConfig'
        self._sch_pipeline['fragment'] = self._fragment
        # Convert SDC stage to SCH stage object
        self._all_stages = {stage_name: type(stage_name,
                                             (_SchSdcStage, ),
                                             {'_attributes': stage_type._attributes})
                            for stage_name, stage_type in self._all_stages.items()}

    def add_stage(self, label=None, name=None, type=None, library=None):
        """Add a stage to the pipeline.

        When specifying a stage, either ``label`` or ``name`` must be used. ``type`` and ``library``
        may also be used to select a particular stage if ambiguities exist. If ``type`` and/or ``library``
        are omitted, the first stage definition matching the given ``label`` or ``name`` will be
        used.

        Args:
            label (:obj:`str`, optional): Stage label to use when selecting stage from
                definitions. Default: ``None``.
            name (:obj:`str`, optional): Stage name to use when selecting stage from
                definitions. Default: ``None``.
            type (:obj:`str`, optional): Stage type to use when selecting stage from
                definitions (e.g. `origin`, `destination`, `processor`, `executor`). Default: ``None``.
            library (:obj:`str`, optional): Stage library to use when selecting stage from
                definitions. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.SchSdcStage`.
        """
        stage_instance, stage_label = next((stage.instance, stage.definition.get('label'))
                                           for stage in self._get_stage_data(label=label, name=name,
                                                                             type=type, library=library)
                                           if stage.definition.get('errorStage') is False)
        self._pipeline[self._config_key]['stages'].append(stage_instance)
        return self._all_stages.get(stage_instance['stageName'], SchSdcStage)(stage=stage_instance,
                                                                              label=stage_label)

    def build(self, title='Pipeline', labels=None, **kwargs):
        """Build the pipeline.

        Args:
            title (:obj:`str`): title of the pipeline.
            labels (:obj:`list`, optional): List of pipeline labels of type :obj:`str`. Default: ``None``.

        Returns:
            An instance of :py:class`streamsets.sdk.sch_models.Pipeline`.
        """
        if kwargs.get('build_from_imported'):
            return Pipeline(pipeline=self._sch_pipeline,
                            builder=self,
                            pipeline_definition=json.loads(self._sch_pipeline['pipelineDefinition']),
                            rules_definition=json.loads(self._sch_pipeline['currentRules']['rulesDefinition']),
                            control_hub=self._control_hub,
                            library_definitions=self._definitions)
        sdc_pipeline = super().build(title=title)
        sch_pipeline = (_Pipeline)(pipeline=self._sch_pipeline,
                                   builder=self,
                                   pipeline_definition=sdc_pipeline._data[self._config_key],
                                   rules_definition=sdc_pipeline._data['pipelineRules'],
                                   control_hub=self._control_hub,
                                   library_definitions=self._definitions)
        if 'metadata' not in sch_pipeline._pipeline_definition:
            sch_pipeline._pipeline_definition['metadata'] = {}
        if kwargs.get('preserve_id'):
            sch_pipeline.pipeline_id = sch_pipeline._pipeline_definition['metadata']['dpm.pipeline.id']
            sch_pipeline.commit_id = sch_pipeline._pipeline_definition['metadata']['dpm.pipeline.commit.id']
            # Also preserving pipeline name, assuming people will do another separate commit to update it.
            sch_pipeline.name = sch_pipeline._pipeline_definition['info']['title']
            sch_pipeline._pipeline_definition['title'] = sch_pipeline._pipeline_definition['info']['title']
        else:
            sch_pipeline.name = title
        fragment_commit_ids = sdc_pipeline._data.get('fragmentCommitIds')
        sch_pipeline._data['fragmentCommitIds'] = fragment_commit_ids
        if labels:
            sch_pipeline.add_label(*labels)
        # Logic as seen at https://git.io/JUWpZ
        connection_ids = [stage.connection for stage in sch_pipeline.stages if hasattr(stage, 'connection')]
        if connection_ids:
            sch_pipeline._pipeline_definition['metadata']['dpm.pipeline.connections'] = ''.join(connection_ids)
        return sch_pipeline


class StPipelineBuilder(StPipelineBuilder):
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Pipeline`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_pipeline_builder`.

    Args:
        pipeline (:obj:`dict`): Python object built from our Swagger PipelineJson definition.
        transformer_pipeline_builder (:py:class:`streamsets.sdk.sdc_models.PipelineBuilder`): Transformer Pipeline
                                                                                              Builder object.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Default: ``None``.
        fragment (:obj:`boolean`, optional): Specify if a fragment builder. Default: ``False``.
    """
    def __init__(self, pipeline, transformer_pipeline_builder, control_hub=None, fragment=False):
        super().__init__(transformer_pipeline_builder._pipeline,
                         transformer_pipeline_builder._definitions)
                         # TODO: fragment=fragment)
        self._transformer_pipeline_builder = transformer_pipeline_builder
        self._sch_pipeline = pipeline
        self._control_hub = control_hub
        self._fragment = fragment
        self._config_key = 'pipelineFragmentConfig' if 'pipelineFragmentConfig' in self._pipeline else 'pipelineConfig'
        self._sch_pipeline['fragment'] = self._fragment
        # Convert Transformer stage to SCH stage object
        self._all_stages = {stage_name: type(stage_name,
                                             (_SchStStage, ),
                                             {'_attributes': stage_type._attributes})
                            for stage_name, stage_type in self._all_stages.items()}

    def add_stage(self, label=None, name=None, type=None, library=None):
        """Add a stage to the pipeline.

        When specifying a stage, either ``label`` or ``name`` must be used. ``type`` and ``library``
        may also be used to select a particular stage if ambiguities exist. If ``type`` and/or ``library``
        are omitted, the first stage definition matching the given ``label`` or ``name`` will be
        used.

        Args:
            label (:obj:`str`, optional): Transformer stage label to use when selecting stage from
                definitions. Default: ``None``.
            name (:obj:`str`, optional): Transformer stage name to use when selecting stage from
                definitions. Default: ``None``.
            type (:obj:`str`, optional): Transformer stage type to use when selecting stage from
                definitions (e.g. `origin`, `destination`, `processor`, `executor`). Default: ``None``.
            library (:obj:`str`, optional): Transformer stage library to use when selecting stage from
                definitions. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.SchStStage`.
        """
        stage_instance, stage_label = next((stage.instance, stage.definition.get('label'))
                                           for stage in self._get_stage_data(label=label, name=name,
                                                                             type=type, library=library)
                                           if stage.definition.get('errorStage') is False)
        self._pipeline['pipelineConfig']['stages'].append(stage_instance)
        return self._all_stages.get(stage_instance['stageName'], SchStStage)(stage=stage_instance,
                                                                             label=stage_label)

    def build(self, title='Pipeline', **kwargs):
        """Build the pipeline.

        Args:
            title (:obj:`str`): title of the pipeline.

        Returns:
            An instance of :py:class`streamsets.sdk.sch_models.Pipeline`.
        """
        if kwargs.get('build_from_imported'):
            return Pipeline(pipeline=self._sch_pipeline,
                            builder=self,
                            pipeline_definition=json.loads(self._sch_pipeline['pipelineDefinition']),
                            rules_definition=json.loads(self._sch_pipeline['currentRules']['rulesDefinition']),
                            control_hub=self._control_hub)
        st_pipeline = super().build(title=title)
        sch_pipeline = (_Pipeline)(pipeline=self._sch_pipeline,
                                   builder=self,
                                   pipeline_definition=st_pipeline._data[self._config_key],
                                   rules_definition=st_pipeline._data['pipelineRules'],
                                   control_hub=self._control_hub)
        sch_pipeline.name = title
        fragment_commit_ids = st_pipeline._data.get('fragmentCommitIds')
        sch_pipeline._data['fragmentCommitIds'] = fragment_commit_ids
        execution_mode = kwargs.get('execution_mode', TRANSFORMER_DEFAULT_EXECUTION_MODE)
        sch_pipeline._pipeline_definition['executorType'] = 'TRANSFORMER'
        sch_pipeline.configuration['executionMode'] = execution_mode
        return sch_pipeline


class Pipeline(BaseModel):
    """Model for Pipeline.

    Args:
        pipeline (:obj:`dict`): Pipeline in JSON format.
        builder (:py:class:`streamsets.sdk.sch_models.PipelineBuilder`): Pipeline Builder object.
        pipeline_definition (:obj:`dict`): Pipeline Definition in JSON format.
        rules_definition (:obj:`dict`): Rules Definition in JSON format.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`, optional): ControlHub object. Default: ``None``.
        library_definitions (:obj:`dict`, optional): Library Definition in JSON format. Default: ``None``.
    """
    _REPR_METADATA = ['pipeline_id', 'commit_id', 'name', 'version']

    def __init__(self, pipeline, builder, pipeline_definition, rules_definition, control_hub=None,
                 library_definitions=None):
        super().__init__(pipeline,
                         repr_metadata=Pipeline._REPR_METADATA)
        self._builder = builder
        self.__pipeline_definition = pipeline_definition
        self._rules_definition = rules_definition
        self._control_hub = control_hub
        self._parameters = None
        self._library_definitions = library_definitions

    @property
    def _pipeline_definition(self):
        # Load data if not exists whenever this attribute is acccessed
        self._load_data()
        return self.__pipeline_definition

    @_pipeline_definition.setter
    def _pipeline_definition(self, pipeline_definition):
        self.__pipeline_definition = pipeline_definition

    @property
    def _data(self):
        # Load data if not exists whenever this attribute is acccessed
        self._load_data()
        return self._data_internal

    @_data.setter
    def _data(self, data):
        self._data_internal = data

    def _load_data(self):
        # Load data if not exists whenever this function is called
        if not self.__pipeline_definition:
            data = self._control_hub.api_client.get_pipeline_commit(self.commit_id).response.json()
            self._data_internal['libraryDefinitions'] = data['libraryDefinitions']
            self._data_internal['pipelineDefinition'] = data['pipelineDefinition']
            self._data_internal['currentRules'] = data['currentRules']
            self.__pipeline_definition = json.loads(data['pipelineDefinition'])
            self._rules_definition = json.loads(data['currentRules']['rulesDefinition'])

    @property
    def commits(self):
        """Get commits for this pipeline.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of instances of
            :py:class:`streamsets.sdk.sch_models.PipelineCommit`.
        """
        return SeekableList(PipelineCommit(commit, control_hub=self._control_hub)
                            for commit in
                            self._control_hub.api_client
                            .get_pipeline_commits(pipeline_id=self.pipeline_id).response.json())

    @property
    def tags(self):
        """Get tags for this pipeline.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of instances of
            :py:class:`streamsets.sdk.sch_models.PipelineTag`.
        """
        return SeekableList(PipelineTag(tag, control_hub=self._control_hub)
                            for tag in
                            self._control_hub.api_client
                            .get_pipeline_tags(pipeline_id=self.pipeline_id).response.json())

    @property
    def configuration(self):
        """Get pipeline's configuration.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Configuration`.
        """
        return Configuration(configuration=self._pipeline_definition['configuration'])

    @property
    def acl(self):
        """Get pipeline ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_pipeline_acl(pipeline_id=self.pipeline_id).response.json(),
                   self._control_hub)

    @acl.setter
    def acl(self, pipeline_acl):
        """Update pipeline ACL.

        Args:
            pipeline_acl (:py:class:`streamsets.sdk.sch_models.ACL`): Pipeline ACL in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sch_api.Command`.
        """
        return self._control_hub.api_client.set_pipeline_acl(pipeline_id=self.pipeline_id,
                                                             pipeline_acl_json=pipeline_acl._data)

    @property
    def stages(self):
        executor_type = getattr(self, 'executor_type', 'COLLECTOR') or 'COLLECTOR'
        stage_class = _SchSdcStage if executor_type == 'COLLECTOR' else _SchStStage
        pipeline_builder = SdcPipelineBuilder if executor_type == 'COLLECTOR' else StPipelineBuilder
        all_stages = {}
        if ('libraryDefinitions' in self._data and self._data['libraryDefinitions']) or self._library_definitions:
            library_definitions = (json.loads(self._data['libraryDefinitions']) if self._data['libraryDefinitions']
                                       else self._library_definitions)
            all_stages = pipeline_builder._generate_all_stages(library_definitions)
            all_stages = {stage_name: type(stage_name,
                                           (stage_class, ),
                                           {'_attributes': stage_type._attributes})
                                for stage_name, stage_type in all_stages.items()}
        return SeekableList(all_stages.get(stage['stageName'],
                                           stage_class)(stage=stage, label=stage['stageName'])
                            for stage in self._pipeline_definition['stages']
                            if 'instanceName' in stage and 'stageName' in stage)

    @property
    def error_stage(self):
        executor_type = getattr(self, 'executor_type', 'COLLECTOR') or 'COLLECTOR'
        stage_class = _SchSdcStage if executor_type == 'COLLECTOR' else _SchStStage
        pipeline_builder = SdcPipelineBuilder if executor_type == 'COLLECTOR' else StPipelineBuilder
        all_stages = {}
        if ('libraryDefinitions' in self._data and self._data['libraryDefinitions']) or self._library_definitions:
            library_definitions = (json.loads(self._data['libraryDefinitions']) if self._data['libraryDefinitions']
                                       else self._library_definitions)
            all_stages = pipeline_builder._generate_all_stages(library_definitions)
            all_stages = {stage_name: type(stage_name,
                                           (stage_class, ),
                                           {'_attributes': stage_type._attributes})
                                for stage_name, stage_type in all_stages.items()}
        error_stage = self._pipeline_definition['errorStage']
        return (all_stages.get(error_stage['stageName'],
                               stage_class)(stage=error_stage, label=error_stage['stageName'])
                if error_stage else None)

    @property
    def parameters(self):
        """Get the pipeline parameters.

        Returns:
            A dict like, :py:obj:`streamsets.sdk.sch_models.PipelineParameters` object of parameter key-value pairs.
        """
        if self._parameters is None:
            self._parameters = PipelineParameters(self)
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Create new set of pipeline parameters by replacing existing ones if any.

        Args:
            parameters (:obj:`dict`): A dictionary of key-value parameters to set.
        """
        self.parameters._create(parameters)

    @property
    def stats_aggregator_stage(self):
        executor_type = getattr(self, 'executor_type', 'COLLECTOR') or 'COLLECTOR'
        stage_class = _SchSdcStage if executor_type == 'COLLECTOR' else _SchStStage
        pipeline_builder = SdcPipelineBuilder if executor_type == 'COLLECTOR' else StPipelineBuilder
        all_stages = {}
        if ('libraryDefinitions' in self._data and self._data['libraryDefinitions']) or self._library_definitions:
            library_definitions = (json.loads(self._data['libraryDefinitions']) if self._data['libraryDefinitions']
                                       else self._library_definitions)
            all_stages = pipeline_builder._generate_all_stages(library_definitions)
            all_stages = {stage_name: type(stage_name,
                                           (stage_class, ),
                                           {'_attributes': stage_type._attributes})
                                for stage_name, stage_type in all_stages.items()}
        stats_aggregator_stage = self._pipeline_definition.get('statsAggregatorStage')
        return (all_stages.get(stats_aggregator_stage['stageName'],
                               stage_class)(stage=stats_aggregator_stage, label=stats_aggregator_stage['stageName'])
                if stats_aggregator_stage else None)

    @property
    def labels(self):
        """Get the pipeline labels.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of instances of
            :py:class:`streamsets.sdk.sch_models.PipelineLabel`.
        """
        if self._data['pipelineLabels'] is not None:
            return SeekableList(PipelineLabel(label) for label in self._data['pipelineLabels'])
        else:
            return SeekableList()

    def add_label(self, *labels):
        """Add a label

        Args:
            *labels: One or more instances of :obj:`str`
        """
        if 'labels' not in self._pipeline_definition['metadata']:
            self._pipeline_definition['metadata']['labels'] = []
        if self._data['pipelineLabels'] is None:
            self._data['pipelineLabels'] = []
        for label in labels:
            self._pipeline_definition['metadata']['labels'].append(label)
            # Logic as seen at https://git.io/JfPhk
            parent_id = ('{}:{}'.format('/'.join(label.split('/')[:-1]), self._control_hub.organization) if
                         label.split('/')[0:-1] else None)
            self._data['pipelineLabels'].append({'id': '{}:{}'.format(label, self._control_hub.organization),
                                                 'label': label.split('/')[-1],
                                                 'parentId': parent_id,
                                                 'organization': self._control_hub.organization})

    def remove_label(self, *labels):
        """Remove a label

        Args:
            *labels: One or more instances of :obj:`str`
        """
        for label in labels:
            if label in self._pipeline_definition['metadata']['labels']:
                self._pipeline_definition['metadata']['labels'].remove(label)
                item = self.labels.get(label=label)
                self._data['pipelineLabels'].remove(item._data)
            else:
                logger.warning('Label %s is not an assigned label for this pipeline. Ignoring this label.', label)

    @property
    def Labels(self):
        """Get the pipeline labels. This attribute will be deprecated in a future release. Please use labels instead.

        Returns:
            A :obj:`list` of :obj:`dict`
        """
        warnings.warn('The attribute Labels of streamsets.sdk.sch_models.Pipeline will be removed in a '
                      'future release. Please use labels instead.',
                      DeprecationWarning)
        return self._data['pipelineLabels']


class PipelineLabel(BaseModel):
    """Model for pipeline label.

    Args:
        pipeline_label (:obj:`dict`): Pipeline label in JSON format.
    """
    _REPR_METADATA = ['label']
    _ATTRIBUTES_TO_REMAP = {'youngest_child_label': 'label'}

    def __init__(self, pipeline_label):
        super().__init__(pipeline_label,
                         repr_metadata=PipelineLabel._REPR_METADATA,
                         attributes_to_remap=PipelineLabel._ATTRIBUTES_TO_REMAP)

    @property
    def label(self):
        return self.id.split(':')[0]


class PipelineLabels(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.PipelineLabel` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, organization=None, parent_id=None, **kwargs):
        """Args offset, len, order are not exposed directly as arguments because of their limited use by normal users
        but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`, optional): Organization id of pipeline. Default: ``None``.
            parent_id (:obj:`str`, optional): ID of the parent pipeline label. Default: ``None``.
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.PipelineLabel` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.PipelineLabel`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order': 'DESC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        response = self._control_hub.api_client.get_all_pipeline_labels(organization=organization,
                                                                        parent_id=parent_id,
                                                                        offset=kwargs_unioned['offset'],
                                                                        len=kwargs_unioned['len'],
                                                                        order=kwargs_unioned['order']).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, PipelineLabel, {})


class PipelineCommit(BaseModel):
    """Model for pipeline commit.

    Args:
        pipeline_commit (:obj:`dict`): Pipeline commit in JSON format.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """
    _REPR_METADATA = ['commit_id', 'version', 'commit_message']

    def __init__(self, pipeline_commit, control_hub=None):
        super().__init__(pipeline_commit,
                         repr_metadata=PipelineCommit._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def pipeline(self):
        return self._control_hub.pipelines.get(commit_id=self.commit_id)


class PipelineTag(BaseModel):
    """Model for pipeline tag.

    Args:
        pipeline_tag (:obj:`dict`): Pipeline tag in JSON format.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """
    _REPR_METADATA = ['id', 'commit_id', 'name', 'message']

    def __init__(self, pipeline_tag, control_hub=None):
        super().__init__(pipeline_tag,
                         repr_metadata=PipelineTag._REPR_METADATA)
        self._control_hub = control_hub


class PipelineParameters(collections.Mapping):
    """Parameters for pipelines.

    Args:
        pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline Instance.
    """
    def __init__(self, pipeline):
        self._store = {parameter['key']: parameter['value'] for parameter in pipeline.configuration['constants']}
        self._pipeline = pipeline

    def update(self, parameters_dict):
        """Update existing parameters. Works similar to Python dictionary update.

        Args:
            parameters_dict (:obj:`dict`): Dictionary of key-value pairs to be used as parameters.
        """
        self._store.update(parameters_dict)
        self._create(self._store)

    def _create(self, parameters_dict):
        """Create a new set of parameters discarding existing ones.

        Args:
            parameters_dict (:obj:`dict`): Dictionary of key-value pairs to be used as parameters.
        """
        self._pipeline.configuration['constants'] = []
        self._store = parameters_dict.copy()
        for key, value in parameters_dict.items():
            self._pipeline.configuration['constants'].append({'key': key, 'value': value})
        config_key = 'pipelineFragmentConfig' if 'pipelineFragmentConfig' in self._pipeline._data else 'pipelineConfig'
        self._pipeline._data[config_key] = json.dumps(self._pipeline.pipeline_definition)

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return str(self._store)


class Pipelines(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Pipeline` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """
    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization
        self._id_attr = 'pipeline_id'

    def __len__(self):
        return self._control_hub.api_client.get_pipelines_count(organization=None,
                                                                system=False).response.json()['count']

    def _get_all_results_from_api(self, commit_id=None, organization=None, label=None, template=False, fragment=False,
                                  using_fragment=None, draft=None, **kwargs):
        """Args offset, len, order_by, order, system, filter_text, only_published, execution_modes, start_time, end_time
         and user_ids are not exposed directly as arguments because of their limited use by normal users but, could
        still be specified just like any other args with the help of kwargs.

        Args:
            commit_id (:obj:`str`, optional): Pipeline commit id. Default: ``None``.
            organization (:obj:`str`, optional): Organization id of pipeline. Default: ``None``.
            label (:obj:`str`, optional): Label of pipeline. Default: ``None``.
            template (:obj:`boolean`, optional): Indicate if requesting pipeline templates or pipelines.
                                                 Default: ``False``.
            fragment (:obj:`boolean`, optional): Specify if querying for fragments. Default: ``False``.
            using_fragment (:py:obj:`streamsets.sdk.sch_models.Pipeline`, optional): Pipelines using this fragment.
                                                                                     Default: ``None``.
            draft (:py:obj:`boolean`, optional): Indicate if requesting draft pipelines. Default: ``None``.
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Pipeline` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Pipeline`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        if draft is not None and Version(self._control_hub.version) < Version('3.18.0'):
            raise ValueError('Argument draft cannot be specified for this version of Control Hub')
        kwargs_defaults = {'offset': None, 'len': None, 'order_by': None, 'order': None, 'system': None,
                           'filter_text': None, 'only_published': False, 'execution_modes': None, 'start_time': -1,
                           'end_time': -1, 'user_ids': None}
        pipeline_id = kwargs.pop('pipeline_id', None)
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if label is not None:
            label_id_org = self._organization if organization is None else organization
            pipeline_label_id = '{}:{}'.format(label, label_id_org)
        else:
            pipeline_label_id = None
        if pipeline_id:
            pipeline_commit_json = self._control_hub.api_client.get_latest_pipeline_commit(pipeline_id=pipeline_id
                                                                                           ).response.json()
            response = [] if not pipeline_commit_json['commitId'] else [pipeline_commit_json]
        elif commit_id:
            response = [self._control_hub.api_client.get_pipeline_commit(commit_id=commit_id
                                                                         ).response.json()]
        elif using_fragment:
            fragment_commit_id = using_fragment.commit_id
            response = self._control_hub.api_client.get_pipelines_using_fragment(fragment_commit_id=fragment_commit_id,
                                                                                 offset=kwargs_unioned['offset'],
                                                                                 len=kwargs_unioned['len'],
                                                                                 order_by=kwargs_unioned['order_by'],
                                                                                 order=kwargs_unioned['order']
                                                                                 ).response.json()
        elif template:
            response = self._control_hub.api_client.return_all_pipeline_templates(
                 pipeline_label_id=pipeline_label_id,
                 offset=kwargs_unioned['offset'],
                 len=kwargs_unioned['len'],
                 order_by=kwargs_unioned['order_by'],
                 order=kwargs_unioned['order'],
                 system=kwargs_unioned['system'],
                 filter_text=kwargs_unioned['filter_text'],
                 execution_modes=kwargs_unioned['execution_modes'],
                 start_time=kwargs_unioned['start_time'],
                 end_time=kwargs_unioned['end_time'],
                 user_ids=kwargs_unioned['user_ids']
                 ).response.json()
        elif fragment:
            response = self._control_hub.api_client.return_all_pipeline_fragments(
                 organization=organization,
                 pipeline_label_id=pipeline_label_id,
                 offset=kwargs_unioned['offset'],
                 len=kwargs_unioned['len'],
                 order_by=kwargs_unioned['order_by'],
                 order=kwargs_unioned['order'],
                 system=kwargs_unioned['system'],
                 filter_text=kwargs_unioned['filter_text'],
                 only_published=kwargs_unioned['only_published'],
                 execution_modes=kwargs_unioned['execution_modes'],
                 start_time=kwargs_unioned['start_time'],
                 end_time=kwargs_unioned['end_time'],
                 user_ids=kwargs_unioned['user_ids'],
                 draft=draft
                 ).response.json()
        else:
            response = self._control_hub.api_client.return_all_pipelines(
                 organization=organization,
                 pipeline_label_id=pipeline_label_id,
                 offset=kwargs_unioned['offset'],
                 len=kwargs_unioned['len'],
                 order_by=kwargs_unioned['order_by'],
                 order=kwargs_unioned['order'],
                 system=kwargs_unioned['system'],
                 filter_text=kwargs_unioned['filter_text'],
                 only_published=kwargs_unioned['only_published'],
                 execution_modes=kwargs_unioned['execution_modes'],
                 start_time=kwargs_unioned['start_time'],
                 end_time=kwargs_unioned['end_time'],
                 user_ids=kwargs_unioned['user_ids'],
                 draft=draft
                 ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Pipeline, {'builder': None,
                                                                          'pipeline_definition': None,
                                                                          'rules_definition': None,
                                                                          'control_hub': self._control_hub})


class JobBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Job`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_job_builder`.

    Args:
        job (:obj:`dict`): Python object built from our Swagger JobJson definition.
    """

    def __init__(self, job, control_hub):
        self._job = job
        self._control_hub = control_hub

    def build(self, job_name, pipeline, job_template=False, runtime_parameters=None, pipeline_commit=None,
              pipeline_tag=None, pipeline_commit_or_tag=None, tags=None):
        """Build the job.

        Args:
            job_name (:obj:`str`): Name of the job.
            pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline object.
            job_template (:obj:`boolean`, optional): Indicate if it is a Job Template. Default: ``False``.
            runtime_parameters (:obj:`dict`, optional): Runtime Parameters for the Job or Job Template.
                                                        Default: ``None``.
            pipeline_commit (:py:obj:`streamsets.sdk.sch_models.PipelineCommit`): Default: ``None`, which resolves to
                                                                                  the latest pipeline commit.
            pipeline_tag (:py:obj:`streamsets.sdk.sch_models.PipelineTag`): Default: ``None`, which resolves to
                                                                            the latest pipeline tag.
            pipeline_commit_or_tag (:obj:`str`, optional): Default: ``None``, which resolves to the latest pipeline
                                                           commit.
            tags (:obj:`list`, optional): Job tags. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        if pipeline_commit and pipeline_tag:
            raise ValueError('Cannot specify both the arguments pipeline_commit and pipeline_tag at the same time.')

        if pipeline_commit_or_tag:
            logger.warning('pipeline_commit_or_tag argument will be removed in a future release. Please use '
                           'pipeline_commit, pipeline_tag arguments instead.')
            if pipeline_commit or pipeline_tag:
                raise ValueError('Cannot specify both the arguments pipeline_commit_or_tag and '
                                 '{} at the same time'.format('pipeline_commit' if pipeline_commit else 'pipeline_tag'))

        executor_type = pipeline._data['executorType'] if 'executorType' in pipeline._data else None
        if job_template: assert runtime_parameters is not None, "Please specify atleast one runtime parameter."
        if pipeline_tag:
            pipeline_version = pipeline.commits.get(commit_id=pipeline_tag.commit_id).version
        else:
            pipeline_version = pipeline.version
        self._job.update({'name': job_name,
                          'pipelineCommitId': (pipeline_commit_or_tag or getattr(pipeline_commit, 'commit_id', None) or
                                               getattr(pipeline_tag, 'commit_id', None) or pipeline.commit_id),
                          'pipelineCommitLabel': 'v{}'.format(getattr(pipeline_commit, 'version', None) or
                                                              pipeline_version),
                          'pipelineId': pipeline.pipeline_id,
                          'pipelineName': pipeline.name,
                          'rulesId': pipeline.current_rules['id'],
                          'jobTemplate': job_template,
                          'runtimeParameters': None if runtime_parameters is None else json.dumps(runtime_parameters),
                          'executorType': executor_type})
        job = Job(job=self._job, control_hub=self._control_hub)
        if tags:
            job.add_tag(*tags)
        return job


class JobCommittedOffset(BaseModel):
    """Model for committedOffsets for an instance of :py:class:`streamsets.sdk.sch_models.Job`.

    Args:
        committed_offset (:obj:`dict`): Committed offset in JSON format
    """

    _REPR_METADATA = ['version', 'offsets']

    def __init__(self, committed_offset):
        super().__init__(committed_offset, repr_metadata=JobCommittedOffset._REPR_METADATA)


class JobOffset(BaseModel):
    """Model for offset.

    Args:
        offset (:obj:`dict`): Offset in JSON format.
    """
    _REPR_METADATA = ['sdc_id', 'pipeline_id']
    def __init__(self, offset):
        super().__init__(offset,
                         repr_metadata=JobOffset._REPR_METADATA)


class JobRunEvent(BaseModel):
    """Model for an event in a Job Run.

    Args:
        event (:obj:`dict`): Job Run Event in JSON format.
    """
    _REPR_METADATA = ['user', 'time', 'status']
    def __init__(self, event):
        super().__init__(event,
                         repr_metadata=JobRunEvent._REPR_METADATA)


class JobStatus(BaseModel):
    """Model for Job Status.

    Attributes:
        run_history (:py:class:`streamsets.sdk.utils.SeekableList`) of
                    (:py:class:`streamsets.sdk.utils.JobRunHistoryEvent`): History of a particular job run.
        offsets (:py:class:`streamsets.sdk.utils.SeekableList`) of
                (:py:class:`streamsets.sdk.utils.JobPipelineOffset`): Offsets after the job run.

    Args:
        status (:obj:`dict`): Job status in JSON format.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.
    """
    _ATTRIBUTES_TO_IGNORE = ['pipeline_offsets']
    _REPR_METADATA = ['status', 'color']
    # We generate different canonical string representation of the class instance if it's created in the context
    # of a job history view.
    _JOB_HISTORY_VIEW_REPR_METADATA = ['status', 'start_time', 'finish_time', 'run_count']

    def __init__(self, status, control_hub, **kwargs):
        super().__init__(status,
                         repr_metadata=(JobStatus._REPR_METADATA
                                        if not kwargs.get('job_history_view')
                                        else JobStatus._JOB_HISTORY_VIEW_REPR_METADATA))
        self._control_hub = control_hub

    @property
    def color(self):
        return self._data.get('color')

    @property
    def run_history(self):
        return SeekableList(JobRunEvent(event)
                            for event in self._control_hub.api_client
                                                          .get_job_status_history_for_run(job_status_id=self.id,
                                                                                          offset=0,
                                                                                          len=-1).response.json())

    @property
    def offsets(self):
        if 'pipelineOffsets' not in self._data or not self._data['pipelineOffsets']:
            return None
        return SeekableList(JobOffset(pipeline_offset) for pipeline_offset in self._data['pipelineOffsets'])

    def __eq__(self, other):
        # Handle the case of a JobStatus being compared to a str (e.g. 'ACTIVE').
        return self.status == other if isinstance(other, str) else super().__eq__(other)


class JobMetrics(BaseModel):
    """Model for job metrics.

    Attributes:
        error_count (:obj:`int`): The number of error records generated by this run of the Job.
        error_records_per_sec (:obj:`float`): The number of error records per second generated by this run of the Job.
        input_count (:obj:`int`): The number of records ingested by this run of the Job.
        input_records_per_sec (:obj:`float`): The number of records per second ingested by this run of the Job.
        output_count (:obj:`int`): The number of records output by this run of the Job.
        output_records_per_sec (:obj:`float`): The number of records output per second by the run of the Job.
        pipeline_version (:obj:`str`): The version of the pipeline that was used in this Job run.
        run_count (:obj:`int`): The count corresponding to this Job run.
        sdc_id (:obj:`str`): The ID of the SDC instance on which this Job run was executed.
        stage_errors_count (:obj:`int`): The number of stage error records generated by this run of the Job.
        stage_error_records_per_sec (:obj:`float`): The number of stage error records generated per second by this run
                                                    of the job.
        total_error_count (:obj:`int`): The total number of both error records and stage errors generated by this run
                                        of the job.

    Args:
        metrics (:obj:`dict`): Metrics counts in JSON format.
    """
    _ATTRIBUTES_TO_REMAP = {'error_records_per_sec': 'errorM1Rate',
                            'input_records_per_sec': 'inputM1Rate',
                            'output_records_per_sec': 'outputM1Rate',
                            'stage_error_records_per_sec': 'stageErrorsM1Rate'}
    _ATTRIBUTES_TO_IGNORE = ['jobId', 'lastUpdatedOn', 'organization', 'stageId']
    _REPR_METADATA = ['run_count', 'input_count', 'output_count', 'total_error_count']

    def __init__(self, metrics):
        super().__init__(metrics,
                         attributes_to_ignore=JobMetrics._ATTRIBUTES_TO_IGNORE,
                         repr_metadata=JobMetrics._REPR_METADATA,
                         attributes_to_remap=JobMetrics._ATTRIBUTES_TO_REMAP)
        # Aggregating error counts as done in the UI: https://git.io/JYNdT
        self.total_error_count = self._data['errorCount'] + self._data['stageErrorsCount']


class JobTimeSeriesMetrics(BaseModel):
    """Model for job metrics.

    Attributes:
        input_records (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                   'Record Count Time Series' or
                                                                                   'Record Throughput Time Series'.
        output_records (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                    'Record Count Time Series' or
                                                                                    'Record Throughput Time Series'.
        error_records (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                   'Record Count Time Series' or
                                                                                   'Record Throughput Time Series'.
        batch_counter (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                   'Batch Throughput Time Series'.
        batch_processing_timer (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                            'Batch Processing Timer
                                                                                            seconds'.

    Args:
        metrics (:obj:`dict`): Metrics in JSON format.
    """
    _ATTRIBUTES_TO_REMAP = {'input_records': 'pipeline_batchInputRecords_meter',
                            'output_records': 'pipeline_batchOutputRecords_meter',
                            'error_records': 'pipeline_batchErrorRecords_meter',
                            'batch_counter': 'pipeline_batchCount_meter',
                            'batch_processing_timer': 'stage_batchProcessing_timer'}
    _METRIC_TYPE_ATTRS = {'Record Count Time Series': ['input_records', 'output_records', 'error_records'],
                          'Record Throughput Time Series': ['input_records', 'output_records', 'error_records'],
                          'Batch Throughput Time Series': ['batch_counter'],
                          'Stage Batch Processing Timer seconds': ['batch_processing_timer']}

    def __init__(self, metrics, metric_type):
        data = {}
        repr_metadata = []
        attributes_map_inverted = {v: k for k, v in JobTimeSeriesMetrics._ATTRIBUTES_TO_REMAP.items()}
        for metric in metrics:
            series = metric['series']
            if series:
                name = metric['series'][0]['name']
                remapped_name = attributes_map_inverted[name]
                data[name] = JobTimeSeriesMetric(metric, remapped_name)
                repr_metadata.append(remapped_name)
            else:
                data = {JobTimeSeriesMetrics._ATTRIBUTES_TO_REMAP[attr]: None
                        for attr in JobTimeSeriesMetrics._METRIC_TYPE_ATTRS[metric_type]}
        super().__init__(data,
                         attributes_to_remap=JobTimeSeriesMetrics._ATTRIBUTES_TO_REMAP,
                         repr_metadata=repr_metadata)


class JobTimeSeriesMetric(BaseModel):
    """Model for job metrics.

    Attributes:
        name (:obj:`str`): Name of measurement.
        values (:obj:`list`): Timeseries data.
        time_series (:obj:`dict`): Timeseries data with timestamp as key and metric value as value.

    Args:
        metric (:obj:`dict`): Metrics in JSON format.
    """
    _REPR_METADATA = ['name', 'time_series']
    _ATTRIBUTES_TO_IGNORE = ['columns', 'tags']

    def __init__(self, metric, metric_type):
        if metric.get('error'):
            # Not throwing an exception because if one metric fails, every other metric won't be displayed because of
            # __repr__ of JobTimeSeriesMetrics.
            logger.warning('Fetching metrics for %s failed with error %s', metric_type, metric.get('error'))
        super().__init__(metric['series'][0],
                         repr_metadata=JobTimeSeriesMetric._REPR_METADATA,
                         attributes_to_ignore=JobTimeSeriesMetric._ATTRIBUTES_TO_IGNORE)

    @property
    def time_series(self):
        time_series = {}
        for k, v in self.values:
            time_series[k] = v
        return time_series


class JobDataCollector(DataCollector):
    def __init__(self, data_collector, pipeline_name):
        super().__init__(data_collector._data, data_collector._control_hub)
        self._pipeline_name = pipeline_name

    @property
    def pipeline(self):
        id_separator = getattr(self, 'id_separator', '__')
        pipeline_id = self._pipeline_name.replace(':', '__') if id_separator == '__' else self._pipeline_name
        return self.instance.pipelines.get(id=pipeline_id)


class JobTransformer(Transformer):
    def __init__(self, transformer, pipeline_name):
        super().__init__(transformer._data, transformer._control_hub)
        self._pipeline_name = pipeline_name

    @property
    def pipeline(self):
        id_separator = getattr(self, 'id_separator', '__')
        pipeline_id = self._pipeline_name.replace(':', '__') if id_separator == '__' else self._pipeline_name
        return self.instance.pipelines.get(id=pipeline_id)


class Tag(BaseModel):
    """Model for tag.

    Args:
        tag (:obj:`dict`): tag in JSON format.
    """
    _REPR_METADATA = ['tag']
    _ATTRIBUTES_TO_REMAP = {'youngest_child_label': 'tag'}

    def __init__(self, tag):
        super().__init__(tag,
                         repr_metadata=Tag._REPR_METADATA,
                         attributes_to_remap=Tag._ATTRIBUTES_TO_REMAP)

    @property
    def tag(self):
        return self.id.split(':')[0]


class JobTags(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Tag` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, organization=None, parent_id=None, **kwargs):
        """Args offset, len, order are not exposed directly as arguments because of their limited use by normal users
        but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`, optional): Organization id of job. Default: ``None``.
            parent_id (:obj:`str`, optional): ID of the parent job tag. Default: ``None``.
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Tag` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Tag`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order': 'DESC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        response = self._control_hub.api_client.get_all_job_tags(organization=organization,
                                                                 parent_id=parent_id,
                                                                 offset=kwargs_unioned['offset'],
                                                                 len=kwargs_unioned['len'],
                                                                 order=kwargs_unioned['order']).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Tag, {})


class Job(BaseModel):
    """Model for Job.

    Attributes:
        commit_id (:obj:`str`): Pipeline commit id.
        commit_label (:obj:`str`): Pipeline commit label.
        created_by (:obj:`str`): User that created this job.
        created_on (:obj:`int`): Time at which this job was created.
        data_collector_labels (:obj:`list`): Labels of the data collectors.
        description (:obj:`str`): Job description.
        destroyer (:obj:`str`): Job destroyer.
        enable_failover (:obj:`bool`): Flag that indicates if failover is enabled.
        enable_time_series_analysis (:obj:`bool`): Flag that indicates if time series is enabled.
        execution_mode (:obj:`bool`): True for Edge and False for SDC.
        job_deleted (:obj:`bool`): Flag that indicates if this job is deleted.
        job_id (:obj:`str`): Id of the job.
        job_name (:obj:`str`): Name of the job.
        last_modified_by (:obj:`str`): User that last modified this job.
        last_modified_on (:obj:`int`): Time at which this job was last modified.
        number_of_instances (:obj:`int`): Number of instances.
        pipeline_force_stop_timeout (:obj:`int`): Timeout for Pipeline force stop.
        pipeline_id (:obj:`str`): Id of the pipeline that is running the job.
        pipeline_name (:obj:`str`): Name of the pipeline that is running the job.
        pipeline_rule_id (:obj:`str`): Rule Id of the pipeline that is running the job.
        read_policy (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Read Policy of the job.
        require_job_error_acknowledgement (:obj:`bool``) Flag that indicates if job requires manual error
            acknowledgement.
        runtime_parameters (:obj:`str`): Run-time parameters of the job.
        statistics_refresh_interval_in_millisecs (:obj:`int`): Refresh interval for statistics in milliseconds.
        status (:obj:`string`): Status of the job.
        write_policy (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Write Policy of the job.
    """
    _ATTRIBUTES_TO_IGNORE = ['current_job_status', 'delete_time', 'destroyer', 'organization', 'parent_job_id',
                             'provenance_meta_data', 'runtime_parameters', 'system_job_id']
    _ATTRIBUTES_TO_REMAP = {'commit_id': 'pipelineCommitId',
                            'commit_label': 'pipelineCommitLabel',
                            'created_by': 'creator',
                            'created_on': 'createTime',
                            'data_collector_labels': 'labels',
                            'enable_failover': 'migrateOffsets',
                            'enable_time_series_analysis': 'timeSeries',
                            'execution_mode': 'edge',
                            'job_id': 'id',
                            'job_name': 'name',
                            'number_of_instances': 'numInstances',
                            'pipeline_rule_id': 'rulesId',
                            'pipeline_force_stop_timeout': 'forceStopTimeout',
                            'require_job_error_acknowledgement': 'needsManualAck',
                            'statistics_refresh_interval_in_millisecs': 'statsRefreshInterval',
                            'system_job_id': 'systemJobId'}
    _REPR_METADATA = ['job_id', 'job_name']

    def __init__(self, job, control_hub=None):
        super().__init__(job,
                         attributes_to_ignore=Job._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=Job._ATTRIBUTES_TO_REMAP,
                         repr_metadata=Job._REPR_METADATA)
        self._control_hub = control_hub
        self.read_policy = None
        self.write_policy = None

    def refresh(self):
        self._data = self._control_hub.api_client.get_job(self.job_id).response.json()

    @property
    def data_collectors(self):
        data_collectors = SeekableList()
        for pipeline_status in self.pipeline_status:
            data_collector = self._control_hub.data_collectors.get(id=pipeline_status.sdc_id)
            pipeline_name = pipeline_status.name
            data_collectors.append(JobDataCollector(data_collector=data_collector,
                                                    pipeline_name=pipeline_name))
        return data_collectors

    @property
    def transformers(self):
        transformers = SeekableList()
        for pipeline_status in self.pipeline_status:
            transformer = self._control_hub.transformers.get(id=pipeline_status.sdc_id)
            pipeline_name = pipeline_status.name
            transformers.append(JobTransformer(transformer=transformer,
                                               pipeline_name=pipeline_name))
        return transformers

    @property
    def status(self):
        current_job_status = self._data['currentJobStatus']
        # Newly added jobs have a currentJobStatus of None, so need to be handled accordingly.
        return JobStatus(current_job_status, self._control_hub) if current_job_status is not None else None

    @property
    def current_status(self):
        logger.debug('Job.current_status will be removed in a future release. Please use Job.status instead.')
        current_job_status = self._data['currentJobStatus']
        return JobStatus(current_job_status, self._control_hub) if current_job_status is not None else None

    @property
    def history(self):
        job_statuses = self._control_hub.api_client.get_job_status_history(job_id=self.job_id,
                                                                           offset=0,
                                                                           len=-1)
        return SeekableList(JobStatus(job_status, self._control_hub, job_history_view=True)
                            for job_status in job_statuses.response.json())

    @property
    def start_time(self):
        return datetime.fromtimestamp(self._data['currentJobStatus']['startTime']/1000)

    @property
    def pipeline_status(self):
        # We use type to create a trivial class as a container for the dictionaries we get from
        # SCH containing pipeline status.
        PipelineStatus = type('PipelineStatus', (BaseModel,), {})
        if not self._data.get('currentJobStatus', None) or not self._data['currentJobStatus'].get('pipelineStatus', []):
            return SeekableList([])
        return SeekableList(PipelineStatus(pipeline_status, repr_metadata=['sdc_id', 'name'])
                            for pipeline_status in self._data['currentJobStatus']['pipelineStatus'])

    @property
    def runtime_parameters(self):
        return RuntimeParameters(self._data['runtimeParameters'], self)

    @runtime_parameters.setter
    def runtime_parameters(self, value):
        self._data['runtimeParameters'] = json.dumps(value)

    @property
    def acl(self):
        """Get job ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_job_acl(job_id=self.job_id).response.json(), self._control_hub)

    @acl.setter
    def acl(self, job_acl):
        """Update job ACL.

        Args:
            job_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The job ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.set_job_acl(job_id=self.job_id, job_acl_json=job_acl._data)

    @property
    def commit(self):
        """Get pipeline commit of the job.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.PipelineCommit`.
        """
        return self.pipeline.commits.get(commit_id=self._data['pipelineCommitId'])

    @commit.setter
    def commit(self, pipeline_commit):
        """Update pipeline commit of the job.

        Args:
            pipeline_commit (:py:class:`streamsets.sdk.sch_models.PipelineCommit`): Pipeline commit instance.
        """
        self._data['pipelineCommitId'] = pipeline_commit.commit_id
        self._data['pipelineCommitLabel'] = 'v{}'.format(pipeline_commit.version)

    @property
    def tag(self):
        """Get pipeline tag of the job.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.PipelineTag`.
        """
        try:
            return self.pipeline.tags.get(commit_id=self._data['pipelineCommitId'])
        except ValueError:
            return None

    @tag.setter
    def tag(self, pipeline_tag):
        """Update pipeline tag of the job.

        Args:
            pipeline_tag (:py:class:`streamsets.sdk.sch_models.PipelineTag`): Pipeline tag instance.
        """
        self._data['pipelineCommitId'] = pipeline_tag.commit_id
        pipeline_commit = self.pipeline.commits.get(commit_id=pipeline_tag.commit_id)
        self._data['pipelineCommitLabel'] = 'v{}'.format(pipeline_commit.version)

    @property
    def system_job(self):
        """Get the sytem Job for this job if exists.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        system_job_id = self._control_hub.jobs.get(job_id=self.job_id).system_job_id
        if system_job_id is not None:
            return self._control_hub.jobs.get(job_id=system_job_id, system=True)

    @property
    def pipeline(self):
        """Get the pipeline object corresponding to this job."""
        return self._control_hub.pipelines.get(commit_id=self._data['pipelineCommitId'])

    @property
    def _pipeline_version(self):
        """Get the version of the pipeline.

        Returns:
            An instance of :obj:`int`.
        """
        return self.pipeline_commit_label.replace('v', '')

    @property
    def tags(self):
        """Get the job tags.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of instances of
            :py:class:`streamsets.sdk.sch_models.Tag`.
        """
        job_tags = self._data.get('jobTags', []) or []
        if not job_tags:
            raw_job_tags = self._data.get('rawJobTags', []) or []
            if raw_job_tags:
                organization = self._control_hub.organization
                job_tags = [build_tag_from_raw_tag(raw_tag, organization) for raw_tag in raw_job_tags]
                self._data['jobTags'] = job_tags
        return SeekableList(Tag(tag) for tag in job_tags)

    def add_tag(self, *tags):
        """Add a tag

        Args:
            *tags: One or more instances of :obj:`str`
        """
        current_tags = [tag.tag for tag in self.tags]
        if not self._data.get('jobTags', None):
            self._data['jobTags'] = []
        if not self._data.get('rawJobTags', None):
            self._data['rawJobTags'] = current_tags
        for tag in tags:
            self._data['rawJobTags'].append(tag)
            tag_json = build_tag_from_raw_tag(tag, self._control_hub.organization)
            self._data['jobTags'].append(tag_json)

    def remove_tag(self, *tags):
        """Remove a tag

        Args:
            *tags: One or more instances of :obj:`str`
        """
        current_tags = [tag.tag for tag in self.tags]
        for tag in tags:
            if tag in current_tags:
                current_tags.remove(tag)
                item = self.tags.get(tag=tag)
                self._data['jobTags'].remove(item._data)
            else:
                logger.warning('Tag %s is not an assigned tag for this pipeline. Ignoring this tag.', tag)
        self._data['rawJobTags'] = current_tags

    @property
    def metrics(self):
        """The metrics from all runs of a Job.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.JobMetrics` instances.

        """
        metrics = self._control_hub.api_client.get_job_record_count_for_all_runs(job_id=self.job_id).response.json()
        # Manually set the run count because the Metrics API doesn't return a 'runCount' value for the last job run.
        # See the UI implementation here: https://git.io/JYNdT
        metrics['0']['runCount'] = len(metrics)
        return SeekableList(sorted((JobMetrics(metrics[metric]) for metric in metrics), key=lambda x: x.run_count,
                                   reverse=True))

    def time_series_metrics(self, metric_type, time_filter_condition='LAST_5M', **kwargs):
        """Get historic time series metrics for the job.

        Args:
            metric_type (:obj:`str`): metric type in {'Record Count Time Series', 'Record Throughput Time Series',
                                                      'Batch Throughput Time Series',
                                                      'Stage Batch Processing Timer seconds'}.
            time_filter_condition (:obj:`str`, optional): Default: ``'LAST_5M'``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetrics`.
        """
        def generate_body(column, measurements, self):
            body = []
            for measurement in measurements:
                time_series_query_json = self._time_series_query_json.copy()
                time_series_query_json.update({'columns': [column],
                                               'jobId': self.job_id,
                                               'measurement': measurement,
                                               'pipelineVersion': self._pipeline_version,
                                               'sdcId': self._data['currentJobStatus']['sdcIds'][0]})
                body.append(time_series_query_json)
            return body

        # Swagger for time series does not exist yet (DPM-6328). So, using a static json here.
        self._time_series_query_json = {'columns': None,
                                        'jobId': None,
                                        'measurement': None,
                                        'pipelineVersion': None,
                                        'sdcId': None}
        record_meter_types = ['PIPELINE_BATCH_INPUT_RECORDS_METER', 'PIPELINE_BATCH_OUTPUT_RECORDS_METER',
                              'PIPELINE_BATCH_ERROR_RECORDS_METER']
        metric_type_to_body_params = {'Record Count Time Series': generate_body('count',
                                                                                record_meter_types,
                                                                                self),
                                      'Record Throughput Time Series': generate_body('m1_rate',
                                                                                     record_meter_types,
                                                                                     self),
                                      'Batch Throughput Time Series': generate_body('m1_rate',
                                                                                    ['PIPELINE_BATCH_COUNT_METER'],
                                                                                    self),
                                      'Stage Batch Processing Timer seconds': generate_body(
                                                                                       'mean',
                                                                                       ['STAGE_BATCH_PROCESSING_TIMER'],
                                                                                       self)}
        return JobTimeSeriesMetrics(self._control_hub
                                              .api_client
                                              .get_job_time_series_metrics(metric_type_to_body_params[metric_type],
                                                                          time_filter_condition,
                                                                          **kwargs).response.json(),
                                    metric_type)

    @property
    def committed_offsets(self):
        """Get the committed offsets for a given job id.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.JobCommittedOffset`.
        """
        committed_offsets = self._control_hub.api_client.get_job_committed_offsets(job_id=self.job_id)

        return JobCommittedOffset(committed_offsets.response.json()) if committed_offsets.response.text else None


class Jobs(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Job` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.
    """

    def __init__(self, control_hub):
        self._control_hub = control_hub
        self._id_attr = 'job_id'

    def __len__(self):
        return self._control_hub.api_client.get_jobs_count(organization=None,
                                                           removed=False,
                                                           system=False).response.json()['count']

    def count(self, status):
        """Get job counts by status.

        Args:
            status (:obj:`str`): Status of the jobs in {'ACTIVE', 'INACTIVE', 'ACTIVATING', 'DEACTIVATING',
                                                        'INACTIVE_ERROR', 'ACTIVE_GREEN', 'ACTIVE_RED', ''}

        Returns:
            An instance of :obj:`int` indicating the count of jobs with specified status.
        """
        counts = {item['status']: item['count']
                  for item in self._control_hub.api_client.get_job_count_by_status().response.json()['data']}
        if status not in counts:
            raise ValueError('Specified status {} is invalid'.format(status))
        return counts[status]

    def _get_all_results_from_api(self, id=None, organization=None, **kwargs):
        """Args order_by, order, removed, system, filter_text, job_status, job_label, edge, len, offset are not exposed
        directly as arguments because of their limited use by normal users but, could still be specified just like any
        other args with the help of kwargs.

        Args:
            id (:obj:`str`).
            organization (:obj:`str`): Organization ID.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Job` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Job`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'order_by': 'NAME', 'order': 'ASC', 'removed': False, 'system': False, 'filter_text': None,
                           'job_status': None, 'job_label': None, 'edge': None, 'offset': 0, 'len': None,
                           'executor_type': None, 'job_tag': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if id is not None:
            try:
                response = [self._control_hub.api_client.get_job(id).response.json()]
            except requests.exceptions.HTTPError:
                raise ValueError('Job (id={}) not found'.format(id))
        else:
            response = self._control_hub.api_client.return_all_jobs(organization=organization,
                                                                    order_by=kwargs_unioned['order_by'],
                                                                    order=kwargs_unioned['order'],
                                                                    removed=kwargs_unioned['removed'],
                                                                    system=kwargs_unioned['system'],
                                                                    filter_text=kwargs_unioned['filter_text'],
                                                                    job_status=kwargs_unioned['job_status'],
                                                                    job_label=kwargs_unioned['job_label'],
                                                                    edge=kwargs_unioned['edge'],
                                                                    offset=kwargs_unioned['offset'],
                                                                    len=kwargs_unioned['len'],
                                                                    executor_type=kwargs_unioned['executor_type'],
                                                                    with_wrapper=True,
                                                                    job_tag=kwargs_unioned['job_tag']).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Job, {'control_hub': self._control_hub})


class RuntimeParameters:
    """Wrapper for Control Hub job runtime parameters.

    Args:
        runtime_parameters (:obj:`str`): Runtime parameter.
        job (:py:obj:`streamsets.sdk.sch_models.Job`): Job object.
    """

    def __init__(self, runtime_parameters, job):
        self._data = json.loads(runtime_parameters) if runtime_parameters else {}
        self._job = job

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._propagate()

    def update(self, runtime_parameters):
        self._data.update(runtime_parameters)
        self._propagate()

    def _propagate(self):
        self._job._data['runtimeParameters'] = json.dumps(self._data)

    def __repr__(self):
        return str(self._data)

    def __bool__(self):
        return bool(self._data)


class TopologyBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Topology`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_topology_builder`.

    Args:
        topology (:obj:`dict`): Python object built from our Swagger TopologyJson definition.
        control_hub (:py:class:`streamsets.sdk.ControlHub`, optional): Control Hub instance. Default: ``None``
    """

    def __init__(self, topology, control_hub=None):
        self._topology = topology
        self._default_topology = topology
        self._control_hub = control_hub

    @property
    def topology_nodes(self):
        """Get all of the nodes currently part of the topology held by the TopologyBuilder.

        Returns:
            A :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.TopologyNode`
                instances.
        """
        if isinstance(self._topology['topologyDefinition'], str):
            return SeekableList(TopologyNode(node) for node in
                                json.loads(self._topology['topologyDefinition']['topologyNodes']))
        else:
            return SeekableList(TopologyNode(node) for node in self._topology['topologyDefinition']['topologyNodes'])

    def build(self, topology_name=None, description=None):
        """Build the topology.

        Args:
            topology_name (:obj:`str`, optional): Name of the topology. This parameter is required when building a new
                topology.
            description (:obj:`str`, optional): Description of the topology. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Topology`.
        """

        if topology_name is None and self._topology['name'] is None:
            raise TopologyIssuesError("The Topology's 'name' attribute is empty, and no topology_name was supplied to"
                                      "build(). Please provide a topology_name.")
        if topology_name is not None:
            self._topology.update({'name': topology_name})
        self._topology.update({'description': description})
        # Convert topologyDefinition from dict to str for consistency with Topology class
        self._topology['topologyDefinition'] = json.dumps(self._topology['topologyDefinition'])
        return Topology(topology=self._topology, control_hub=self._control_hub)

    def import_topology(self, topology):
        """Import an existing topology to be used in the builder.

        Args:
            topology (:py:class:`streamsets.sdk.sch_models.Topology`): An existing Topology instance to modify.
        """
        if not topology.commit_id:
            raise TopologyIssuesError('Cannot call import_topology using an unpublished topology.')
        self._topology.update(topology._data)
        # Convert topologyDefinition from str to dict for processing
        self._topology['topologyDefinition'] = json.loads(self._topology['topologyDefinition'])

    def add_job(self, job):
        """Add a job node to the Topology being built.

        Args:
            job (:py:class:`streamsets.sdk.sch_models.Job`): An instance of a job to be added.
        """
        pipeline_json = self._control_hub.api_client.get_pipeline_commit(commit_id=
                                                                         job.pipeline.commit_id).response.json()
        pipeline_definition = json.loads(pipeline_json['pipelineDefinition'])
        library_definitions = json.loads(pipeline_json['libraryDefinitions'])
        topology_nodes = (self._topology['topologyDefinition']['topologyNodes']
                          if 'topologyDefinition' in self._topology else {})
        x_pos = 100
        y_pos = 50

        for topology_node in topology_nodes:
            if topology_node['uiInfo']['xPos'] >= x_pos:
                x_pos = topology_node['uiInfo']['xPos'] + 250
        nodes = get_topology_nodes([job], pipeline_json, pipeline_definition, x_pos, y_pos)

        for node in nodes:
            icon_key = '{}:{}'.format(node['library'], node['stageName'])
            if 'stageIcons' in library_definitions and icon_key in library_definitions['stageIcons']:
                self._topology['topologyDefinition']['stageIcons'][icon_key] = (library_definitions['stageIcons']
                                                                                [icon_key])

        topology_nodes.extend(nodes)

    def add_system(self, name):
        """Add a system node to the Topology being built.

        Args:
            name (:obj:`str`): The name of the system to add to the topology.
        """
        topology_node_json = {'nodeType': None, 'instanceName': None, 'library': None, 'stageName': None,
                              'stageVersion': None, 'jobId': None, 'pipelineId': None, 'pipelineCommitId': None,
                              'pipelineVersion': None, 'inputLanes': [], 'outputLanes': [], 'uiInfo': {}}
        try:
            system = next(system for system in ALL_TOPOLOGY_SYSTEMS if system['label'] == name)
        except StopIteration:
            raise TopologyIssuesError(f'No system found with the name "{name}".')
        topology_nodes = (self._topology['topologyDefinition']['topologyNodes']
                          if 'topologyDefinition' in self._topology else {})
        x_pos = 100
        y_pos = 50

        for topology_node in topology_nodes:
            if topology_node['uiInfo']['xPos'] >= x_pos:
                x_pos = topology_node['uiInfo']['xPos'] + 250

        system_node = copy.deepcopy(topology_node_json)
        system_node['nodeType'] = 'SYSTEM'
        system_node['instanceName'] = 'ADDED_SEPARATELY:SYSTEM:{}'.format(int(datetime.utcnow().timestamp() * 1000))
        system_node['outputLanes'] = ['{}OutputLane1'.format(system_node['instanceName'])]
        system_node['uiInfo']['label'] = system['label']
        system_node['uiInfo']['xPos'] = x_pos
        system_node['uiInfo']['yPos'] = y_pos
        system_node['uiInfo']['icon'] = system['icon']
        system_node['uiInfo']['colorIcon'] = system['colorIcon']

        topology_nodes.append(system_node)

    def delete_node(self, topology_node):
        """Delete a system or job node from the topology.

        Args:
            topology_node (:py:class:`streamsets.sdk.sch_models.TopologyNode`): An instance of a TopologyNode to delete
                from the topology.

        """
        # Based off of https://git.io/JRoAC
        try:
            node_index, selected_node = next((index, node) for index, node in enumerate(self.topology_nodes)
                                             if node.instance_name == topology_node.instance_name)
        except ValueError as ex:
            ex.message = 'The specified node does not exist within this topology.'
            raise
        if isinstance(self._topology, dict):
            del self._topology['topologyDefinition']['topologyNodes'][node_index]
        else:
            del json.loads(self._topology['topologyDefinition'])['topologyNodes'][node_index]

        # Remove the inputLanes that reference the deleted node's outputLane
        for topology_node in self.topology_nodes:
            for lane_index, input_lane in enumerate(topology_node.input_lanes):
                if input_lane in selected_node.output_lanes:
                    del topology_node.input_lanes[lane_index]


class TopologyNode(BaseModel):
    """Model for a node within a Topology.

    Args:
        topology_node_json (:obj:`dict`): JSON representation of a Topology Node.

    Attributes:
        node_type (:obj:`str`): The type of this node, i.e. SYSTEM, JOB, etc.
        instance_name (:obj:`str`): The name of this node instance.
        stage_name (:obj:`str`): The name of the stage in this node.
        stage_version (:obj:`str`): The version of the stage in this node.
        job_id (:obj:`str`): The ID of the job in this node.
        pipeline_id (:obj:`str`): The pipeline ID associated with the job in this node.
        pipeline_commit_id (:obj:`str`): The commit ID of the pipeline.
        pipeline_version (:obj:`str`): The version of the pipeline.
        input_lanes (:obj:`list`): A list of :obj:`str` representing the input lanes for this node.
        output_lanes (:obj:`list`): A list of :obj:`str` representing the output lanes for this node.
    """
    _REPR_METADATA = ['name', 'node_type']
    _ATTRIBUTES_TO_IGNORE = ['uiInfo', 'library']

    def __init__(self, topology_node_json):
        super().__init__(topology_node_json,
                         attributes_to_ignore=TopologyNode._ATTRIBUTES_TO_IGNORE,
                         repr_metadata=TopologyNode._REPR_METADATA)

    @property
    def name(self):
        return self._data['uiInfo']['label']


class Topology(BaseModel):
    """Model for Topology.

    Args:
        topology (:obj:`dict`): JSON representation of Topology.

    Attributes:
        commit_id (:obj:`str`): Pipeline commit id.
        commit_message (:obj:`str`): Commit Message.
        commit_time (:obj:`int`): Time at which commit was made.
        committed_by (:obj:`str`): User that made the commit.
        default_topology (:obj:`bool`): Default Topology.
        description (:obj:`str`): Topology description.
        draft (:obj:`bool`): Indicates whether this topology is a draft.
        last_modified_by (:obj:`str`): User that last modified this topology.
        last_modified_on (:obj:`int`): Time at which this topology was last modified.
        new_pipeline_version_available (:obj:`bool`): Whether any job in the topology has a new pipeline version to be
            updated to.
        organization (:obj:`str`): Id of the organization.
        parent_version (:obj:`str`): Version of the parent topology.
        topology_definition (:obj:`str`): Definition of the topology.
        topology_id (:obj:`str`): Id of the topology.
        topology_name (:obj:`str`): Name of the topology.
        validation_issues (:obj:`dict`): Any validation issues that exist for this Topology.
        version (:obj:`str`): Version of this topology.
    """
    _ATTRIBUTES_TO_IGNORE = ['provenanceMetaData']
    _ATTRIBUTES_TO_REMAP = {'committed_by': 'committer',
                            'topology_name': 'name'}
    _REPR_METADATA = ['topology_id', 'topology_name']

    def __init__(self, topology, control_hub=None):
        super().__init__(topology,
                         attributes_to_ignore=Topology._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=Topology._ATTRIBUTES_TO_REMAP,
                         repr_metadata=Topology._REPR_METADATA)
        self._control_hub = control_hub
        self._topology_definition_internal = (json.loads(topology['topologyDefinition'])
                                              if isinstance(topology['topologyDefinition'], str)
                                              else topology['topologyDefinition'])
        self._validation_issues = []
        self._new_pipeline_version_map = {}
        self._new_pipeline_version_available = False

    @property
    def _data(self):
        # Check if data exists, otherwise load it
        if not self._topology_definition_internal:
            self._load_data()
        return self._data_internal

    @_data.setter
    def _data(self, data):
        self._data_internal = data

    @property
    def _topology_definition(self):
        # Check if data exists, otherwise load it
        if not self._topology_definition_internal:
            self._load_data()
        return self._topology_definition_internal

    @_topology_definition.setter
    def _topology_definition(self, topology_definition):
        self._topology_definition_internal = topology_definition

    @property
    def topology_definition(self):
        # Check if data exists, otherwise load it
        if not self._topology_definition_internal:
            self._load_data()
        return self._data_internal['topologyDefinition']

    @topology_definition.setter
    def topology_definition(self, topology_definition):
        self._topology_definition_internal = topology_definition

    def _load_data(self):
        data = self._control_hub.api_client.get_topology_for_commit_id(commit_id=self._data_internal['commitId'],
                                                                       validate=True).response.json()
        self._data_internal['topologyDefinition'] = data['topology']['topologyDefinition']
        self._topology_definition_internal = json.loads(data['topology']['topologyDefinition'])

    @property
    def nodes(self):
        """Get the job and system nodes that make up the Topology.

        Returns:
            A :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.TopologyNode`
                instances.
        """
        return SeekableList(TopologyNode(topology_node) for topology_node in self._topology_definition['topologyNodes'])

    @property
    def jobs(self):
        """Get the jobs that are contained within the Topology.

        Returns:
            A :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Job` instances.
        """
        job_ids = list({job_node['jobId'] for job_node in self._get_topology_job_nodes()})
        return SeekableList(self._control_hub.jobs.get(job_id=job_id) for job_id in job_ids)

    @property
    def acl(self):
        """Get the ACL of a Topology.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_topology_acl(topology_id=self.topology_id).response.json(),
                   self._control_hub)

    @acl.setter
    def acl(self, topology_acl):
        self._control_hub.api_client.set_topology_acl(topology_id=self.topology_id,
                                                      topology_acl_json=topology_acl._data)

    @property
    def data_slas(self):
        return SeekableList([DataSla(sla, self._control_hub)
                             for sla in self._control_hub
                                            .api_client
                                            .get_data_sla(organization=self._control_hub.organization,
                                                          topology_commit_id=self.commit_id).response.json()])

    @property
    def validation_issues(self):
        """Get any validation issues that are detected for the Topology.

        Returns:
            A (:obj:`list`) of validation issues in JSON format.
        """
        self._validation_issues = (self._control_hub.api_client.get_topology_for_commit_id(commit_id=self.commit_id,
                                                                                           validate=True)
                                   .response.json()['issues'] if self.commit_id is not None else [])
        return self._validation_issues

    @property
    def new_pipeline_version_available(self):
        """Determine if a new pipeline version is available for any jobs in the Topology.

        Returns:
            A (:obj:`bool`) value.
        """
        self._update_new_pipeline_version_map()
        return self._new_pipeline_version_available

    def _auto_fix_topology(self, topology, topology_definition):
        # Auto fix a topology - based off of https://git.io/J4AuC
        if self._validation_issues and len(self._validation_issues):
            for issue in self._validation_issues:
                removed_output_lanes = []
                if issue['code'] == 'TOPOLOGY_08' and issue['additionalInfo'] and issue['additionalInfo']['jobId']:
                    # The job has been updated with a new version of the pipeline
                    job_id = issue['additionalInfo']['jobId']
                    pipeline_commit_id = issue['additionalInfo']['pipelineCommitId']
                    job_node = next(node for node in topology_definition['topologyNodes']
                                    if node['nodeType'] == 'JOB' and node['jobId'] == job_id)
                    updated_pipeline = (self._control_hub.api_client.get_pipeline_commit(commit_id=pipeline_commit_id)
                                        .response.json())
                    job_node['pipelineCommitId'] = pipeline_commit_id
                    job_node['pipelineVersion'] = updated_pipeline['version']
                    pipeline_definition = json.loads(updated_pipeline['pipelineDefinition'])
                    stage_instances = pipeline_definition['stages']
                    source_stage_instance = next(stage for stage in stage_instances
                                                 if stage['uiInfo']['stageType'] == 'SOURCE')
                    target_stage_instances = [stage for stage in stage_instances
                                              if stage['uiInfo']['stageType'] == 'TARGET'
                                              or stage['uiInfo']['stageType'] == 'EXECUTOR']

                    new_output_lanes = []
                    output_stream_labels = []
                    output_stream_texts = []

                    for count, target_stage_instance in enumerate(target_stage_instances):
                        lane_prefix = '{}:LANE:'.format(target_stage_instance['instanceName'])
                        existing_lane = next((lane for lane in job_node['outputLanes'] if lane_prefix in lane), None)
                        if existing_lane:
                            new_output_lanes.append(existing_lane)
                        else:
                            new_output_lanes.append('{}:LANE:{}{}'.format(target_stage_instance['instanceName'],
                                                                          int(datetime.utcnow().timestamp() * 1000),
                                                                          count+1))
                        output_stream_labels.append(target_stage_instance['uiInfo']['label'])
                        output_stream_texts.append(target_stage_instance['uiInfo']['label'][0:1])

                    if 'errorStage' in pipeline_definition:
                        error_stage_instance = pipeline_definition['errorStage']
                        lane_prefix = '{}:LANE:'.format(error_stage_instance['instanceName'])
                        existing_lane = next((lane for lane in job_node['outputLanes'] if lane_prefix in lane), None)
                        if existing_lane:
                            new_output_lanes.append(existing_lane)
                        else:
                            new_output_lanes.append('{}:LANE:{}{}'.format(error_stage_instance['instanceName'],
                                                                          int(datetime.utcnow().timestamp() * 1000),
                                                                          len(target_stage_instances) + 1))
                        output_stream_labels.append(error_stage_instance['uiInfo']['label'])
                        output_stream_texts.append(error_stage_instance['uiInfo']['label'][0:1])

                    for output_lane in job_node['outputLanes']:
                        if output_lane not in new_output_lanes:
                            removed_output_lanes.append(output_lane)

                    job_node['outputLanes'] = new_output_lanes
                    job_node['uiInfo']['outputStreamLabels'] = output_stream_labels
                    job_node['uiInfo']['outputStreamTexts'] = output_stream_texts
                elif issue['code'] == 'TOPOLOGY_06' and issue['additionalInfo'] and issue['additionalInfo']['jobId']:
                    # The job has been removed, so remove the node
                    job_id = issue['additionalInfo']['jobId']
                    node_index = next((index for index, node in enumerate(topology_definition['topologyNodes'])
                                       if node['nodeType'] == 'JOB' and node['jobId'] == job_id), None)
                    if node_index is not None:
                        deleted_job_node = topology_definition['topologyNodes'][node_index]
                        del topology_definition['topologyNodes'][node_index]
                        removed_output_lanes.extend(deleted_job_node['outputLanes'])

                # Remove lanes in removed_output_lanes from all nodes that had them as input_lanes
                if len(removed_output_lanes):
                    for node in topology_definition['topologyNodes']:
                        new_input_lanes = [input_lane for input_lane in node['inputLanes']
                                           if input_lane not in removed_output_lanes]
                        node['inputLanes'] = new_input_lanes
                # Save the topology
                topology['topologyDefinition'] = json.dumps(topology_definition)
                job_nodes = [topology_node for topology_node in topology_definition['topologyNodes']
                             if topology_node['nodeType'] == 'JOB']
                if len(job_nodes) > 0:
                    self._update_new_pipeline_version_map()
                return self._control_hub.api_client.update_topology(commit_id=topology['commitId'],
                                                                    topology_json=topology)

    def _different_job_nodes(self, jobs, pipelines_map):
        # Treat nodes as standalone entities, ignoring connections - Based off of https://git.io/JR9Xz
        nodes = []
        stage_icons = {}
        x_pos = 100
        max_y_pos = y_pos = 50
        prefix = 0

        for job in jobs:
            pipeline = pipelines_map[job.pipeline_commit_id]
            pipeline_definition = pipeline['pipelineDefinition']
            library_definitions = pipeline['libraryDefinitions']
            prefix += 1
            job_nodes = get_topology_nodes([job], pipeline, pipeline_definition, x_pos, y_pos, postfix=prefix)
            for node in job_nodes:
                nodes.append(node)
                max_y_pos = node['uiInfo']['yPos'] if node['uiInfo']['yPos'] >= max_y_pos else max_y_pos
            y_pos = max_y_pos + 150 if max_y_pos > 50 else 50
        return nodes, stage_icons if len(stage_icons) else self._topology_definition['stageIcons']

    def _get_topology_job_nodes(self):
        # Get the Job nodes in a Topology - based off of https://bit.ly/2M6sPLv
        if self._topology_definition is not None:
            return [topology_node for topology_node in self._topology_definition['topologyNodes']
                    if topology_node['nodeType'] == 'JOB']
        else:
            return []

    def _on_update_to_latest(self):
        # Upgrade a topology's jobs to the latest pipeline change - based off of https://git.io/JBuUc
        jobs_to_update = []
        for topology_node in self._topology_definition['topologyNodes']:
            if topology_node['nodeType'] == 'JOB':
                latest_pipeline = self._new_pipeline_version_map[topology_node['pipelineId']]
                if latest_pipeline and latest_pipeline['commitId'] != topology_node['pipelineCommitId']:
                    jobs_to_update.append(topology_node['jobId'])
        self._control_hub.api_client.upgrade_jobs(jobs_to_update)

    def _refresh(self):
        # Refresh a topology's data representation with the most current
        self._data = self._control_hub.api_client.get_topology_for_commit_id(commit_id=self.commit_id).response.json()
        self._topology_definition = (json.loads(self._data['topologyDefinition'])
                                     if isinstance(self._data['topologyDefinition'], str)
                                     else self._data['topologyDefinition'])

    def _update_new_pipeline_version_map(self):
        # Map new pipeline versions to job nodes - based off of https://git.io/JBuJI
        pipelines = []
        pipeline_version_map = {}
        job_nodes = self._get_topology_job_nodes()
        if len(job_nodes):
            for node in job_nodes:
                pipelines.append(self._control_hub.api_client.get_latest_pipeline_commit(pipeline_id=node['pipelineId'])
                                 .response.json())
            if len(pipelines):
                for pipeline in pipelines:
                    pipeline_version_map[pipeline['pipelineId']] = pipeline
                for node in job_nodes:
                    new_version_pipeline = pipeline_version_map[node['pipelineId']]
                    self._new_pipeline_version_available = (self._new_pipeline_version_available or
                                                            (new_version_pipeline and new_version_pipeline['commitId']
                                                             != node['pipelineCommitId']))
        self._new_pipeline_version_map = pipeline_version_map

    def add_data_sla(self, data_sla):
        """Add SLA.

        Args:
            data_sla (:py:class:`streamsets.sdk.sch_models.DataSla`): Data SLA object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        cmd = self._control_hub.api_client.add_data_sla(data_sla._data)
        data_sla._data = cmd.response.json()
        return cmd

    def activate_data_sla(self, *data_slas):
        """Activate Data SLAs.

        Args:
            *data_slas: One or more instances of :py:class:`streamsets.sdk.sch_models.DataSla`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        cmd = self._control_hub.api_client.activate_data_sla([data_sla.id for data_sla in data_slas])
        for data_sla in data_slas:
            data_sla._refresh()
        return cmd

    def deactivate_data_sla(self, *data_slas):
        """Deactivate Data SLAs.

        Args:
            *data_slas: One or more instances of :py:class:`streamsets.sdk.sch_models.DataSla`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        cmd = self._control_hub.api_client.deactivate_data_sla([data_sla.id for data_sla in data_slas])
        for data_sla in data_slas:
            data_sla._refresh()
        return cmd

    def delete_data_sla(self, *data_slas):
        """Delete Data SLAs.

        Args:
            *data_slas: One or more instances of :py:class:`streamsets.sdk.sch_models.DataSla`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.delete_data_sla([data_sla.id for data_sla in data_slas])

    def acknowledge_job_errors(self):
        """Acknowledge all errors for the jobs in a topology.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        job_ids = list({job_node['jobId'] for job_node in self._get_topology_job_nodes()})
        return self._control_hub.api_client.jobs_acknowledge_errors(job_ids)

    def start_all_jobs(self):
        """Start all jobs of a topology.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        job_ids = list({job_node['jobId'] for job_node in self._get_topology_job_nodes()})
        response = self._control_hub.api_client.start_jobs(job_ids)
        for job_id in job_ids:
            self._control_hub.api_client.wait_for_job_status(job_id=job_id, status='ACTIVE')
        return response

    def stop_all_jobs(self, force=False):
        """Stop all jobs of a topology.

        Args:
            force (:obj:`bool`, optional): Force topology jobs to stop. Default: ``False``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        job_ids = list({job_node['jobId'] for job_node in self._get_topology_job_nodes()})
        if force:
            response = self._control_hub.api_client.force_stop_jobs(job_ids)
        else:
            response = self._control_hub.api_client.stop_jobs(job_ids)
        for job_id in job_ids:
            self._control_hub.api_client.wait_for_job_status(job_id=job_id, status='INACTIVE')
        return response

    def update_jobs_to_latest_change(self):
        """Upgrade a topology's job(s) to the latest corresponding pipeline change.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        # Based off of https://git.io/J4AtD
        if self.commit_id:
            self._update_new_pipeline_version_map()
            if self._new_pipeline_version_available:
                self._on_update_to_latest()
                return self.auto_fix()

    def auto_fix(self):
        """Auto-fix a topology by rectifying invalid or removed jobs, outdated jobs, etc.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        # Based off of https://git.io/J4AGv
        if self.commit_id:
            validated_topology = self._control_hub.api_client.get_topology_for_commit_id(commit_id=self.commit_id,
                                                                                         validate=True).response.json()
            self._data = validated_topology['topology'] if validated_topology['topology'] is not None else self._data
            self._validation_issues = validated_topology['issues']
            self._new_pipeline_version_available = False
            if self._validation_issues:
                if not self.draft:
                    self._data = self._control_hub.api_client.create_topology_draft(commit_id=
                                                                                    self.commit_id).response.json()
                response = self._auto_fix_topology(self._data, self._topology_definition)
                self._refresh()
                return response

    def auto_discover_connections(self):
        """Auto discover connecting systems between nodes in a Topology.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        # Based off of https://git.io/JRKmU
        pipelines_map = {}
        pipeline_commit_id_list = []
        job_id_list = []
        jobs = self.jobs

        for job in jobs:
            if job.job_id not in job_id_list:
                job_id_list.append(job.job_id)
                if job.pipeline_commit_id not in pipeline_commit_id_list:
                    pipeline_commit_id_list.append(job.pipeline_commit_id)
        pipelines = self._control_hub.api_client.get_pipelines_commit(body=pipeline_commit_id_list).response.json()
        for pipeline in pipelines:
            pipeline['pipelineDefinition'] = json.loads(pipeline['pipelineDefinition'])
            pipeline['libraryDefinitions'] = json.loads(pipeline['libraryDefinitions'])
            pipelines_map[pipeline['commitId']] = pipeline

        new_topology_nodes, new_stage_icons = self._different_job_nodes(jobs, pipelines_map)
        if not self.draft:
            self._data = self._control_hub.api_client.create_topology_draft(commit_id=self.commit_id).response.json()
        # Based off of https://git.io/JR9SI
        new_topology_definition = json.loads(self._data['topologyDefinition'])
        new_topology_definition['topologyNodes'] = new_topology_nodes
        new_topology_definition['stageIcons'] = new_stage_icons
        self._data['topologyDefinition'] = json.dumps(new_topology_definition)
        response = self._control_hub.api_client.update_topology(commit_id=self._data['commitId'],
                                                                topology_json=self._data)
        self._refresh()
        return response


class Topologies(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Topology` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): An instance of the Control Hub.
    """

    def __init__(self, control_hub):
        super().__init__(control_hub)
        self._id_attr = 'topology_id'

    def _get_all_results_from_api(self, commit_id=None, organization=None, **kwargs):
        """Args offset, len_, order_by, order are not exposed directly as arguments because of their limited use by
        normal users but, could still be specified just like any other args with the help of kwargs.

        Args:
            commit_id (:obj:`str`)
            organization (:obj:`str`, optional): Default: ``None``.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Topology` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Topology`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order_by': 'NAME', 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = [topology for topology in self._control_hub.api_client
                                                 .return_all_topologies(organization=organization,
                                                                        offset=kwargs_unioned['offset'],
                                                                        len=kwargs_unioned['len'],
                                                                        order_by=kwargs_unioned['order_by'],
                                                                        order=kwargs_unioned['order'],
                                                                        with_wrapper=True
                                                                        ).response.json()['data']]
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Topology, {'control_hub': self._control_hub})


class DataSla(BaseModel):
    """Model for DataSla.

    Args:
        data_sla (:obj:`dict`): JSON representation of SLA.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): An instance of the Control Hub.
    """
    _ATTRIBUTES_TO_REMAP = {'status': 'slaStatus'}
    _REPR_METADATA = ['label', 'last_modified_on', 'status']

    def __init__(self, data_sla, control_hub):
        super().__init__(data_sla,
                         attributes_to_remap=DataSla._ATTRIBUTES_TO_REMAP,
                         repr_metadata=DataSla._REPR_METADATA)
        self._control_hub = control_hub

    def _refresh(self):
        topology = self._control_hub.topologies.get(commit_id=self.topology_commit_id)
        self._data = topology.data_slas.get(id=self.id)._data


class DataSlaBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.DataSla`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_data_sla_builder`.

    Args:
        data_sla (:obj:`dict`): Python object built from our Swagger DataSlaJson definition.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): An instance of the Control Hub.
    """

    def __init__(self, data_sla, control_hub):
        self._data_sla = data_sla
        self._control_hub = control_hub

    def build(self, topology, label, job, alert_text, qos_parameter='THROUGHPUT_RATE', function_type='Max',
              min_max_value=100, enabled=True):
        """Build the Data Sla.

        Args:
            topology (:py:class:`streamsets.sdk.sch_models.Topology`): Topology object.
            label (:obj:`str`): Label for the SLA.
            job (:obj:`list`): List of :py:class:`streamsets.sdk.sch_models.Job` objects.
            alert_text (:obj:`str`): Alert text.
            qos_parameter (:obj:`str`, optional): paramter in {'THROUGHPUT_RATE', 'ERROR_RATE'}.
                Default: ``'THROUGHPUT_RATE'``.
            function_type (:obj:`str`, optional): paramter in {'Max', 'Min'}. Default: ``'Max'``.
            min_max_value (:obj:`str`, optional): Default: ``100``.
            enabled (:obj:`boolean`, optional): Default: ``True``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.DataSla`.
        """
        sla_definition = json.dumps({'enabled': enabled,
                                     'qosParameter': qos_parameter,
                                     'slaConditions': [{'slaFunctionType': function_type.upper(),
                                                        'value': min_max_value}],
                                     'jobIds': [job.job_id],
                                     'alertText': alert_text})
        self._data_sla.update({'label': label,
                               'topologyCommitId': topology.commit_id,
                               'topologyId': topology.topology_id,
                               'slaDefinition': sla_definition})
        return DataSla(data_sla=self._data_sla, control_hub=self._control_hub)


class ClassificationRule(UiMetadataBaseModel):
    """Classification Rule Model.

    Args:
        classification_rule (:obj:`dict`): A Python dict representation of classification rule.
        classifiers (:obj:`list`): A list of :py:class:`streamsets.sdk.sch_models.Classifier` instances.
    """
    _ATTRIBUTES_TO_IGNORE = ['classifiers']
    _ATTRIBUTES_TO_REMAP = {}

    def __init__(self, classification_rule, classifiers):
        super().__init__(classification_rule,
                         attributes_to_ignore=ClassificationRule._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=ClassificationRule._ATTRIBUTES_TO_REMAP)
        self.classifiers = classifiers


class Classifier(UiMetadataBaseModel):
    """Classifier model.

    Args:
        classifier (:obj:`dict`): A Python dict representation of classifier.
    """
    _ATTRIBUTES_TO_IGNORE = ['patterns']
    _ATTRIBUTES_TO_REMAP = {'case_sensitive': 'sensitive',
                            'match_with': 'type',
                            'regular_expression_type': 'implementationClassValue', }

    # From https://git.io/fA0w2.
    MATCH_WITH_ENUM = {'Field Path': 'FIELD_PATH',
                       'Field Value': 'FIELD_VALUE'}

    # From https://git.io/fA0w4.
    REGULAR_EXPRESSION_TYPE_ENUM = {'RE2/J': 'RE2J_MATCHER',
                                    'Java Regular Expression': 'REGEX_MATCHER'}

    def __init__(self, classifier):
        super().__init__(classifier,
                         attributes_to_ignore=Classifier._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=Classifier._ATTRIBUTES_TO_REMAP)

    @property
    def patterns(self):
        return [pattern['value'] for pattern in self._data['patterns']]

    @patterns.setter
    def patterns(self, values):
        self._data['patterns'] = [{'messages': [],
                                   'type': 'RSTRING',
                                   'value': value,
                                   'scrubbed': False}
                                  for value in values]

    @property
    def _id(self):
        return self._data['id']

    @_id.setter
    def _id(self, value):
        self._data['id'] = value

    @property
    def _rule_uuid(self):
        return self._data['ruleUuid']

    @_rule_uuid.setter
    def _rule_uuid(self, value):
        self._data['ruleUuid'] = value

    @property
    def _uuid(self):
        return self._data['uuid']

    @_uuid.setter
    def _uuid(self, value):
        self._data['uuid'] = value


class ClassificationRuleBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ClassificationRule`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_classification_rule_builder`.

    Args:
        classification_rule (:obj:`dict`): Python object defining a classification rule.
        classifier (:obj:`dict`): Python object defining a classifier.
    """

    def __init__(self, classification_rule, classifier):
        self._classification_rule = classification_rule
        self._classifier = classifier
        self.classifiers = []

    def add_classifier(self, patterns=None, match_with=None,
                       regular_expression_type='RE2/J', case_sensitive=False):
        """Add classifier to the classification rule.

        Args:
            patterns (:obj:`list`, optional): List of strings of patterns. Default: ``None``.
            match_with (:obj:`str`, optional): Default: ``None``.
            regular_expression_type (:obj:`str`, optional): Default: ``'RE2/J'``.
            case_sensitive (:obj:`bool`, optional): Default: ``False``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Classifier`.
        """
        classifier = Classifier(classifier=copy.deepcopy(self._classifier))
        classifier.patterns = patterns or ['.*']
        classifier.match_with = Classifier.MATCH_WITH_ENUM.get(match_with) or 'FIELD_PATH'
        classifier.regular_expression_type = Classifier.REGULAR_EXPRESSION_TYPE_ENUM.get(regular_expression_type)
        classifier.case_sensitive = case_sensitive

        classifier._uuid = str(uuid.uuid4())
        classifier._id = '{}:1'.format(classifier._uuid)
        classifier._rule_uuid = self._classification_rule['uuid']
        self.classifiers.append(classifier)
        return classifier

    def build(self, name, category, score):
        """Build the classification rule.

        Args:
            name (:obj:`str`): Classification Rule name.
            category (:obj:`str`): Classification Rule category.
            score (:obj:`float`): Classification Rule score.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ClassificationRule`.
        """
        classification_rule = ClassificationRule(classification_rule=self._classification_rule,
                                                 classifiers=self.classifiers)
        classification_rule.name = name
        classification_rule.category = category
        classification_rule.score = score
        return classification_rule


class ProtectionPolicy(UiMetadataBaseModel):
    """Model for Protection Policy.

    Args:
        protection_policy (:obj:`dict`): JSON representation of Protection Policy.
        procedures (:obj:`list`): A list of :py:class:`streamsets.sdk.sch_models.PolicyProcedure` instances,
                    Default: ``None``.
    """
    _ATTRIBUTES_TO_IGNORE = ['enactment', 'defaultSetting', 'procedures']
    _ATTRIBUTES_TO_REMAP = {}
    _REPR_METADATA = ['name']

    # The DEFAULT_POLICY_ENUM supportes mapping for both the 'enactment'
    # property (used prior to SCH/SDP 3.14) and the new defaultSetting property
    # that has been introducted starting SCH/SDP 3.14
    DEFAULT_POLICY_ENUM = {'No': 'NO',
                           'Read': 'READ',
                           'Write': 'WRITE',
                           'Both': 'BOTH'}

    SAMPLING_ENUM = {'Only new Field Paths': 'NEW_PATHS',
                     'First Record of Every Batch': 'FIRST_BATCH_RECORD',
                     'Random Sample of Records': 'RANDOM_SAMPLE',
                     'All records': 'ALL_RECORDS',
                     'No records': 'NONE'}

    def __init__(self, protection_policy, procedures=None):
        super().__init__(protection_policy,
                         attributes_to_ignore=ProtectionPolicy._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=ProtectionPolicy._ATTRIBUTES_TO_REMAP,
                         repr_metadata=ProtectionPolicy._REPR_METADATA)
        self._procedures = procedures

    @property
    def procedures(self):
        if self._procedures is not None:
            return self._procedures
        if self._data['procedures']:
            return [PolicyProcedure(procedure) for procedure in self._data['procedures']]
        return None

    @property
    def _id(self):
        return self._data['id']

    @_id.setter
    def _id(self, value):
        self._data['id'] = value

    @property
    def default_setting(self):
        # The defaultSetting property only existed in the SCH/SDP version 3.14
        # or later.  The SDK supports versions prior to that as well.  So first
        # check and see if the defaultSetting property exists before attempting
        # to return it.
        if 'defaultSetting' in self._data:
            return next((k for k, v in ProtectionPolicy.DEFAULT_POLICY_ENUM.items()
                         if v == self._data['defaultSetting']['value']), None)
    @property
    def enactment(self):
        # The enactment property only existed in the SCH/SDP versions prior to 3.14
        # The SDK supports older and newer versions. So first check and see if the
        # enactment property exists before attempting to return it.
        if 'enactment' in self._data:
            return next((k for k, v in ProtectionPolicy.DEFAULT_POLICY_ENUM.items()
                         if v == self._data['enactment']['value']), None)

    @enactment.setter
    def enactment(self, value):
        self._data['enactment']['value'] = value

    @property
    def sampling(self):
        if 'sampling' in self._data:
            return next((k for k, v in ProtectionPolicy.SAMPLING_ENUM.items()
                         if v == self._data['sampling']['value']), None)

    @sampling.setter
    def sampling(self, value):
        if value in ProtectionPolicy.SAMPLING_ENUM:
            self._data['sampling'] = ProtectionPolicy.SAMPLING_ENUM.get(value)
        else:
            raise ValueError('Unknown sampling type ({})'.format(value))


class ProtectionPolicies(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.ProtectionPolicy` instances."""

    def _get_all_results_from_api(self, **kwargs):
        """
        Args:
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.ProtectionPolicy` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        protection_policies = []
        response = self._control_hub.api_client.get_protection_policy_list().response.json()['response']
        for protection_policy in response:
            protection_policy['data'].pop('messages', None)
            protection_policies.append(ProtectionPolicy(protection_policy['data']))
        return ModelCollectionResults(SeekableList(protection_policies), kwargs)


class ProtectionPolicyBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ProtectionPolicy`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_protection_policy_builder`.

    Args:
        protection_policy (:obj:`dict`): Python object defining a protection policy.
        policy_procedure (:obj:`dict`): Python object defining a policy procedure.
    """

    def __init__(self, control_hub, protection_policy, policy_procedure):
        self._control_hub = control_hub
        self._protection_policy = protection_policy
        self._policy_procedure = policy_procedure
        self.procedures = []

    def add_procedure(self, classification_score_threshold=0.5, procedure_basis='Category Pattern',
                      classification_category_pattern=None, field_path=None, protection_method=None):
        procedure = PolicyProcedure(policy_procedure=copy.deepcopy(self._policy_procedure))
        procedure.classification_score_threshold = classification_score_threshold
        if PolicyProcedure._ATTRIBUTES_TO_REMAP['procedure_basis'] in procedure._data:
            procedure.procedure_basis = PolicyProcedure.PROCEDURE_BASIS_ENUM.get(procedure_basis)
        if procedure_basis == 'Category Pattern':
            procedure.classification_category_pattern = classification_category_pattern
        elif procedure_basis == 'Field Path':
            procedure.field_path = field_path
        # https://git.io/fAE0K
        procedure.protection_method = json.dumps({'issues': None,
                                                  'schemaVersion': 1,
                                                  'stageConfiguration': protection_method._data})

        self.procedures.append(procedure)

    def build(self, name, enactment=None, sampling='All records'):
        protection_policy = ProtectionPolicy(self._protection_policy, self.procedures)
        protection_policy.name = name
        protection_policy.sampling = ProtectionPolicy.SAMPLING_ENUM.get(sampling)
        # The enactment property is only valid for versions before 3.14.  Check
        # if the SCH/SDP version if below 3.14 before setting the enactment
        # property.
        if (Version(self._control_hub.version) < Version('3.14.0') and
                enactment is not None):
            protection_policy.enactment = ProtectionPolicy.DEFAULT_POLICY_ENUM.get(enactment)

        return protection_policy


class PolicyProcedure(UiMetadataBaseModel):
    """Model for Policy Procedure.

    Args:
        policy_procedure (:obj:`dict`): JSON representation of Policy Procedure.
    """
    PROCEDURE_BASIS_ENUM = {'Category Pattern': 'CATEGORY_PATTERN',
                            'Field Path': 'FIELD_PATH'}

    _ATTRIBUTES_TO_IGNORE = ['id', 'optimisticLockVersion', 'version']
    _ATTRIBUTES_TO_REMAP = {'classification_category_pattern': 'classificationCategory',
                            'classification_score_threshold': 'threshold',
                            'procedure_basis': 'subjectType',
                            'protection_method': 'transformerConfig'}

    def __init__(self, policy_procedure):
        super().__init__(policy_procedure,
                         attributes_to_ignore=PolicyProcedure._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=PolicyProcedure._ATTRIBUTES_TO_REMAP)

    @property
    def _id(self):
        return self._data['id']

    @_id.setter
    def _id(self, value):
        self._data['id'] = value

    @property
    def _policy_id(self):
        return self._data['policyId']

    @_policy_id.setter
    def _policy_id(self, value):
        self._data['policyId'] = value


class ProtectionMethod(SchSdcStage):
    """Protection Method Model.

    Args:
        stage (:obj:`dict`): JSON representation of a stage.
    """
    STAGE_LIBRARY = 'streamsets-datacollector-dataprotector-lib'
    CRYPTO_STAGE_LIBRARY = 'streamsets-datacollector-crypto-lib'

    def __init__(self, stage):
        super().__init__(stage, label=stage['uiInfo']['label'])


class ProtectionMethodBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ProtectionMethod`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_protection_method_builder`.

    Args:
        pipeline_builder (:py:class:`streamsets.sdk.sch_models.PipelineBuilder`): Pipeline Builder object.
    """

    def __init__(self, pipeline_builder):
        self._pipeline_builder = pipeline_builder

    def build(self, method, library=ProtectionMethod.STAGE_LIBRARY):
        method_stage = self._pipeline_builder.add_stage(label=method, library=library)
        # We generate a single output lane to conform to SDP's expectations for detached stages.
        method_stage.add_output()
        protection_method = type(method_stage.stage_name,
                                 (ProtectionMethod,),
                                 {'_attributes': method_stage._attributes})
        return protection_method(method_stage._data)


class ReportDefinitions(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.ReportDefinition` instances."""

    def _get_all_results_from_api(self, organization=None, **kwargs):
        """Args order_by, order, filter_text, len, offset are not exposed directly as arguments because of their limited
        use by normal users but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`): Organization Id.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.ReportDefinition` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'order_by': 'NAME', 'order': 'ASC', 'filter_text': None, 'offset': 0, 'len': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.return_all_report_definitions(organization=organization,
                                                                              offset=kwargs_unioned['offset'],
                                                                              len=kwargs_unioned['len'],
                                                                              order_by=kwargs_unioned['order_by'],
                                                                              order=kwargs_unioned['order'],
                                                                              filter_text=kwargs_unioned['filter_text']
                                                                              ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, ReportDefinition, {'control_hub': self._control_hub})


class ReportDefinition(BaseModel):
    """Model for Report Definition.

    Args:
        report_definition (:obj:`dict`): JSON representation of Report Definition.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """
    _REPR_METADATA = ['id', 'name']

    def __init__(self, report_definition, control_hub):
        super().__init__(report_definition, repr_metadata=ReportDefinition._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def reports(self):
        """Get Reports of the Report Definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Reports`.
        """
        return Reports(self._control_hub, self.id)

    @property
    def report_resources(self):
        """Get Report Resources of the Report Definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ReportResources`.
        """
        return ReportResources(self._data['reportArtifacts'], self)

    def generate_report(self):
        """Generate a Report for Report Definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Report`.
        """
        trigger_time = int(round(time.time() * 1000))
        return GenerateReportCommand(self._control_hub,
                                     self,
                                     self._control_hub.api_client
                                     .generate_report_for_report_definition(self.id, trigger_time).response.json())

    @property
    def acl(self):
        """Get Report Definition ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client
                       .get_report_definition_acl(report_definition_id=self.id).response.json(), self._control_hub)

    @acl.setter
    def acl(self, report_definition_acl):
        """Update Report Definition ACL.

        Args:
            report_definition_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The Report Definition ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return (self._control_hub.api_client
                    .set_report_definition_acl(report_definition_id=self.id,
                                               report_definition_acl_json=report_definition_acl._data))


class GenerateReportCommand:
    """Command to interact with the response from generate_report.

    Args:
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
        report_definition (:obj:`dict`): JSON representation of Report Definition.
        response (:obj:`dict`): Api response from generating the report.
    """
    def __init__(self, control_hub, report_defintion, response):
        self._control_hub = control_hub
        self._report_defintion = report_defintion
        self.response = response

    @property
    def report(self):
        report = self._report_defintion.reports.get(id=self.response['id'])
        self.response = report._data
        if report.report_status == 'REPORT_TO_BE_GENERATED':
            logger.warning('Report is still being generated...')
        elif report.report_status == 'REPORT_SUCCESS':
            return Report(report, self._control_hub, self._report_defintion.id)
        else:
            raise Exception('Report generation failed with status {}'.format(report.report_status))


class ReportResources:
    """Model for the collection of Report Resources.

    Args:
        report_resources (:obj:`list`): List of Report Resources.
        report_definition (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Report Definition object.
    """
    def __init__(self, report_resources, report_definition):
        self._report_resources = SeekableList(ReportResource(report_resource) for report_resource in report_resources)
        self._report_definition = report_definition

    def get(self, **kwargs):
        return self._report_resources.get(**kwargs)

    def get_all(self, **kwargs):
        return self._report_resources.get_all(**kwargs)

    def __iter__(self):
        for report_resource in self._report_resources:
            yield report_resource

    def __len__(self):
        return len(self._report_resources)

    def __getitem__(self, i):
        return self._report_resources[i]

    def __contains__(self, resource):
        """Check if given resource is in Report Definition resources.

        Args:
            resource (:py:class:streamsets.sdk.sch_models.Job) or (:py:class:streamsets.sdk.sch_models.Topology)

        Returns:
            A :obj:`boolean` indicating if the resource exists.
        """
        assert isinstance(resource, Job) or isinstance(resource, Topology), "Only Job and Topology are supported"
        if isinstance(resource, Job):
            resource_id = resource.job_id
            resource_type = 'JOB'
        else:
            resource_id = resource.commit_id
            resource_type = 'TOPOLOGY'
        for resource in self._report_resources:
            if resource.resource_id == resource_id and resource.resource_type == resource_type:
                return True
        return False

    def __repr__(self):
        return str(self._report_resources)


class ReportResource(BaseModel):
    """Model for Report Resource.

    Args:
        report_resource (:obj:`dict`): JSON representation of Report Resource.
    """
    _REPR_METADATA = ['resource_type', 'resource_id']

    def __init__(self, report_resource):
        super().__init__(report_resource, repr_metadata=ReportResource._REPR_METADATA)


class ReportDefinitionBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ReportDefinition`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_report_definition_builder`.

    Args:
        report_definition (:obj:`dict`): JSON representation of Report Definition.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """

    def __init__(self, report_definition, control_hub):
        self._report_definition = report_definition
        self._report_resources = SeekableList()
        self._control_hub = control_hub

    def import_report_definition(self, report_definition):
        """Import an existing Report Definition to update it.

        Args:
            report_definition (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Report Definition object.
        """
        self._report_definition = report_definition._data
        self._report_resources = SeekableList(ReportResource(report_resource)
                                              for report_resource in report_definition._data['reportArtifacts'])

    def set_data_retrieval_period(self, start_time, end_time):
        """Set Time range over which the report will be generated.

        Args:
            start_time (:obj:`str`) or (:obj:`int`): Absolute or relative start time for the Report.
            end_time (:obj:`str`) or (:obj:`int`): Absolute or relative end time for the Report.
        """
        self._report_definition.update({'startTime': start_time,
                                        'endTime': end_time})

    def add_report_resource(self, resource):
        """Add a given resource to Report Definition resources.

        Args:
            resource (:py:class:`streamsets.sdk.sch_models.Job`) or (:py:class:`streamsets.sdk.sch_models.Topology`)
        """
        if isinstance(resource, Job):
            self._report_resources.append(ReportResource({'resourceId': resource.job_id,
                                                          'resourceType': 'JOB'}))
        elif isinstance(resource, Topology):
            self._report_resources.append(ReportResource({'resourceId': resource.commit_id,
                                                          'resourceType': 'TOPOLOGY'}))
        if self._report_definition is not None:
            self._report_definition['reportArtifacts'] = SeekableList(report_resource._data
                                                                            for report_resource in
                                                                            self._report_resources)

    def remove_report_resource(self, resource):
        """Remove a resource from Report Definition Resources.

        Args:
            resource (:py:class:`streamsets.sdk.sch_models.Job`) or (:py:class:`streamsets.sdk.sch_models.Topology`)

        Returns:
            A resource of type :py:obj:`dict` that is removed from Report Definition Resources.
        """
        if isinstance(resource, Job):
            resource_type = 'JOB'
            resource_id = resource.job_id
        elif isinstance(resource, Topology):
            resource_type = 'TOPOLOGY'
            resource_id = resource.commit_id

        popped = self._report_resources.get(resource_type=resource_type,
                                            resource_id=resource_id)
        self._report_resources = SeekableList(i for i in self._report_resources if any(getattr(i, k) != v
                                              for k, v in popped._data.items()))
        if self._report_definition is not None:
            self._report_definition['reportArtifacts'] = SeekableList(report_resource._data
                                                                            for report_resource in
                                                                            self._report_resources)
        return popped

    def build(self, name, description=None):
        """Build the report definition.

        Args:
            name (:obj:`str`): Name of the Report Definition.
            description (:obj:`str`, optional): Description of the Report Definition. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ReportDefinition`.
        """
        self._report_definition.update({'name': name,
                                        'description': description})
        return ReportDefinition(self._report_definition, self._control_hub)


class Reports(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Report` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.
        report_definition_id (:obj:`str`): Report Definition Id.
    """

    def __init__(self, control_hub, report_definition_id):
        super().__init__(control_hub)
        self._report_definition_id = report_definition_id

    def _get_all_results_from_api(self, id=None, **kwargs):
        """Get Reports belonging to a Report Definition. Args offset, len are not exposed directly as arguments because
        of their limited use by normal users but, could still be specified just like any other args with the help of
        kwargs.

        Args:
            id (:obj:`str`, optional): Report Id. Default: ``None``. If specified, only that particular report is
                                       fetched from control hub. If not, all reports belonging to this Report Definition
                                       will be fetched and other filters will be applied later.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Report` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Report`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if self._report_definition_id is not None:
            if id is None:
                report_ids = [report['id']
                              for report in
                              self._control_hub.api_client
                              .return_all_reports_from_definition(report_definition_id=self._report_definition_id,
                                                                  offset=kwargs_unioned['offset'],
                                                                  len=kwargs_unioned['len']).response.json()['data']]
            else:
                report_ids = [id]
            response = [self._control_hub.api_client.get_report_for_given_report_id(self._report_definition_id,
                                                                                    report_id).response.json()
                        for report_id in report_ids]
        else:
            response = []
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Report,
                                      {'control_hub': self._control_hub,
                                       'report_definition_id': self._report_definition_id})


class Report(BaseModel):
    """Model for Report.

    Args:
        report (:obj:`dict`): JSON representation of Report.
    """
    _REPR_METADATA = ['id', 'name']

    def __init__(self, report, control_hub, report_definition_id):
        super().__init__(report, repr_metadata=Report._REPR_METADATA)
        self._control_hub = control_hub
        self._report_definition_id = report_definition_id

    def download(self):
        """Download the Report in PDF format

        Returns:
            An instance of :obj:`bytes`.
        """
        return self._control_hub.api_client.download_report(self._report_definition_id, self.id, 'PDF').response.content


class ScheduledTaskBaseModel(BaseModel):
    """Base Model for Scheduled Task related classes."""

    def __getattr__(self, name):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            return (self._data[remapped_name]['value']
                   if 'value' in self._data[remapped_name] else self._data[remapped_name])
        elif (name_ in self._data and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            return self._data[name_]['value'] if 'value' in self._data[name_] else self._data[name_]
        raise AttributeError('Could not find attribute {}.'.format(name_))

    def __setattr__(self, name, value):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            if 'value' in self._data[remapped_name]:
                self._data[remapped_name]['value'] = value
            else:
                self._data[remapped_name] = value
        elif (name_ in self._data and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            if 'value' in self._data[name_]:
                self._data[name_]['value'] = value
            else:
                self._data[name_] = value
        else:
            super().__setattr__(name, value)


class ScheduledTaskBuilder:
    """Builder for Scheduled Task.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_scheduled_task_builder`.

    Args:
        job_selection_types (:py:obj:`dict`): JSON representation of job selection types.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """

    def __init__(self, job_selection_types, control_hub):
        self._job_selection_types = job_selection_types
        self._control_hub = control_hub

    def build(self, task_object, action='START', name=None, description=None, cron_expression='0 0 1/1 * ? *',
              time_zone='UTC', status='RUNNING', start_time=None, end_time=None, missed_execution_handling='IGNORE'):
        """Builder for Scheduled Task.

        Args:
            task_object (:py:class:`streamsets.sdk.sch_models.Job`) or
                        (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Job or ReportDefinition object.
            action (:obj:`str`, optional): One of the {'START', 'STOP', 'UPGRADE'} actions. Default: ``START``.
            name (:obj:`str`, optional): Name of the task. Default: ``None``.
            description (:obj:`str`, optional): Description of the task. Default: ``None``.
            crontab_mask (:obj:`str`, optional): Schedule in cron syntax. Default: ``"0 0 1/1 * ? *"``. (Daily at 12).
            time_zone (:obj:`str`, optional): Time zone. Default: ``"UTC"``.
            status (:obj:`str`, optional): One of the {'RUNNING', 'PAUSED'} statuses. Default: ``RUNNING``.
            start_time (:obj:`str`, optional): Start time of task. Default: ``None``.
            end_time (:obj:`str`, optional): End time of task. Default: ``None``.
            missed_trigger_handling (:obj:`str`, optional): One of {'IGNORE', 'RUN ALL', 'RUN ONCE'}.
                                                            Default: ``IGNORE``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ScheduledTask`.
        """
        assert isinstance(task_object, Job) or isinstance(task_object, ReportDefinition), \
               "Only Job and ReportDefinition are supported"
        params = get_params(parameters=locals(), exclusions=('self', 'task_object'))

        if isinstance(task_object, Job):
            self._job_selection_types['jobId']['value'] = task_object.job_id
            self._job_selection_types['jobName']['value'] = task_object.job_name
            self._job_selection_types['type']['value'] = 'PIPELINE_JOB'
        else:
            self._job_selection_types['reportId']['value'] = task_object.id
            self._job_selection_types['reportName']['value'] = task_object.name
            self._job_selection_types['type']['value'] = 'REPORT_JOB'
        _response = self._control_hub.api_client.trigger_selection_info(data={'data': self._job_selection_types},
                                                                        api_version=2)
        task = _response.response.json()['response']['data']

        for key, value in params.items():
            if json_to_python_style(key) in ScheduledTask._ATTRIBUTES_TO_REMAP:
                key = ScheduledTask._ATTRIBUTES_TO_REMAP[json_to_python_style(key)]
            if key == 'action':
                task['executionInfo'][key]['value'] = value
            else:
                task[key]['value'] = value

        return ScheduledTask(task, self._control_hub)


class ScheduledTask(ScheduledTaskBaseModel):
    """Model for Scheduled Task.

    Args:
        task (:py:obj:`dict`): JSON representation of task.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """
    _REPR_METADATA = ['id', 'name', 'status']
    _ATTRIBUTES_TO_REMAP = {'cron_expression': 'crontabMask',
                            'missed_execution_handling': 'missedTriggerHandling'}

    def __init__(self, task, control_hub=None):
        super().__init__(task,
                         repr_metadata=ScheduledTask._REPR_METADATA,
                         attributes_to_remap=ScheduledTask._ATTRIBUTES_TO_REMAP)
        self._control_hub = control_hub
        self._allowed_actions = {'PAUSE', 'RESUME', 'KILL', 'DELETE'}
        # With this we would be able to call actions like task.pause(), task.kill(), task.resume() and task.delete()
        for action in self._allowed_actions:
            setattr(self, action.lower(), partial(self._perform_action, action=action))

    @property
    def runs(self):
        """Get Scheduled Task Runs.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of inherited instances of
            :py:class:`streamsets.sdk.sch_models.ScheduledTaskRun`.
        """
        _repsonse = self._control_hub.api_client.get_scheduled_task(id=self.id,
                                                                    run_info=True,
                                                                    audit_info=False,
                                                                    api_version=2)
        runs = _repsonse.response.json()['response']['data']['runs']
        return SeekableList(ScheduledTaskRun(run) for run in runs)

    @property
    def audits(self):
        """Get Scheduled Task Audits.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of inherited instances of
            :py:class:`streamsets.sdk.sch_models.ScheduledTaskAudit`.
        """
        _response = self._control_hub.api_client.get_scheduled_task(id=self.id,
                                                                    run_info=False,
                                                                    audit_info=True,
                                                                    api_version=2)
        audits = _response.response.json()['response']['data']['audits']
        return SeekableList(ScheduledTaskAudit(audit) for audit in audits)

    def _perform_action(self, action):
        """Perform a specified action on this scheduled task.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ScheduledTask`.
        """
        assert action in self._allowed_actions
        response = self._control_hub.api_client.perform_action_on_scheduled_task(self.id,
                                                                                 action,
                                                                                 api_version=2).response.json()
        updated_task = response['response']['data']
        self._data = updated_task
        return self

    @property
    def acl(self):
        """Get the ACL of a Scheduled Task.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_scheduled_task_acl(scheduled_task_id=self.id).response.json(),
                   self._control_hub)

    @acl.setter
    def acl(self, scheduled_task_acl):
        self._control_hub.api_client.set_scheduled_task_acl(scheduled_task_id=self.id,
                                                            scheduled_task_acl_json=scheduled_task_acl._data)


class ScheduledTasks(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.ScheduledTask` instances."""

    def _get_all_results_from_api(self, **kwargs):
        """Args order_by, offset, len are not exposed directly as arguments because of their limited use by normal
        users but, could still be specified just like any other args with the help of kwargs.

        Args:
            **kwargs: Optional other arguments to be passed to filter the results.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.ScheduledTask` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.ScheduledTask`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': -1, 'order_by': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        tasks = self._control_hub.api_client.get_scheduled_tasks(kwargs_unioned['order_by'],
                                                                 kwargs_unioned['offset'],
                                                                 kwargs_unioned['len'],
                                                                 api_version=2).response.json()['response']
        response = [task['data'] for task in tasks]
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, ScheduledTask, {'control_hub': self._control_hub})


class ScheduledTaskRun(ScheduledTaskBaseModel):
    """Scheduled Task Run.

    Args:
        run (:py:obj:`dict`): JSON representation if scheduled task run.
    """
    _REPR_METADATA = ['id', 'scheduledTime']

    def __init__(self, run):
        super().__init__(run,
                         repr_metadata=ScheduledTaskRun._REPR_METADATA)


class ScheduledTaskAudit(ScheduledTaskBaseModel):
    """Scheduled Task Audit.

    Args:
        run (:py:obj:`dict`): JSON representation of scheduled task audit.
    """
    _REPR_METADATA = ['id', 'action']

    def __init__(self, audit):
        super().__init__(audit,
                         repr_metadata=ScheduledTaskAudit._REPR_METADATA)


class Subscription(BaseModel):
    """Subscription.

    Args:
        subscription (:obj:`dict`): JSON representation of Subscription.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """
    _REPR_METADATA = ['id', 'name']

    def __init__(self, subscription, control_hub):
        super().__init__(subscription,
                         repr_metadata=Subscription._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def events(self):
        """Events of the Subscription."""

        return SeekableList(SubscriptionEvent(event, self._control_hub) for event in self._data['events'])

    @property
    def action(self):
        """Action of the Subscription."""
        return SubscriptionAction(self._data['externalActions'][0])

    @property
    def acl(self):
        """Get the ACL of an Event Subscription.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client
                   .get_subscription_acl(subscription_id=self.id).response.json(), self._control_hub)

    @acl.setter
    def acl(self, subscription_acl):
        self._control_hub.api_client.set_subscription_acl(subscription_id=self.id,
                                                          subscription_acl_json=subscription_acl._data)


class SubscriptionAction(BaseModel):
    """Action to take when the Subscription is triggered.

    Args:
        action (:obj:`dict`): JSON representation of an Action for a Subscription.
    """
    _REPR_METADATA = ['event_type']

    def __init__(self, action):
        super().__init__(action,
                         repr_metadata=SubscriptionAction._REPR_METADATA)
        self.config = json.loads(self.config) if isinstance(self.config, str) else self.config


class SubscriptionEvent(BaseModel):
    """An Event of a Subscription.

    Args:
        event (:obj:`dict`): JSON representation of Events of a Subscription.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """
    _REPR_METADATA = ['event_type', 'filter']

    def __init__(self, event, control_hub):
        event_types = control_hub._en_translations['notifications']['subscriptions']['events']
        if event['eventType'] in event_types:
            event['eventType'] = event_types[event['eventType']]
        super().__init__(event,
                         repr_metadata=SubscriptionEvent._REPR_METADATA)


class SubscriptionAudit(BaseModel):
    """Model for subscription audit.

    Args:
        audit (:obj:`dict`): JSON representation of a subscription audit.
    """
    _REPR_METADATA = ['subscription_name', 'event_name', 'external_action_type', 'created_time']

    def __init__(self, audit):
        super().__init__(audit,
                         repr_metadata=SubscriptionAudit._REPR_METADATA)


class Subscriptions(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Subscription` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.
    """

    def _get_all_results_from_api(self, organization=None, **kwargs):
        """Args offset, len, orderBy, order are not exposed directly as arguments because of their limited use by normal
        users but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`): Organization ID.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Subscription` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Subscription`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': 0, 'len': None, 'order_by': 'NAME', 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        response = self._control_hub.api_client.get_all_event_subscriptions(organization=organization,
                                                                            offset=kwargs_unioned['offset'],
                                                                            len=kwargs_unioned['len'],
                                                                            order_by=kwargs_unioned['order_by'],
                                                                            order=kwargs_unioned['order'],
                                                                            with_wrapper=True
                                                                            ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Subscription, {'control_hub': self._control_hub})


class SubscriptionBuilder:
    """Builder for Subscription.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_subscription_builder`.

    Args:
        subscription (:py:obj:`dict`): JSON representation of event subscription.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """

    def __init__(self, subscription, control_hub):
        self._subscription = subscription
        self._events = SeekableList()
        self._action = {}
        self._control_hub = control_hub

    def add_event(self, event_type, filter=None):
        """Add event to the Subscription.

        Args:
            event_type (:obj:`str`): Type of event in {'Job Status Change', 'Data SLA Triggered', 'Pipeline Committed',
                                                       'Pipeline Status Change', 'Report Generated',
                                                       'Data Collector not Responding'}.
            filter (:obj:`str`, optional): Filter to be applied on event. Default: ``None``.
        """
        event = {'eventType': event_type, 'filter': filter}
        if self._subscription is not None: self._subscription['events'].append(event)
        self._events.append(SubscriptionEvent(event, self._control_hub))

    def remove_event(self, event_type):
        """Remove event from the subscription.

        Args:
            event_type (:obj:`str`): Type of event in {'Job Status Change', 'Data SLA Triggered', 'Pipeline Committed',
                                                       'Pipeline Status Change', 'Report Generated',
                                                       'Data Collector not Responding'}.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.SubscriptionEvent`.
        """
        popped = self._events.get(event_type=event_type)
        self._events = SeekableList(i for i in self._events if getattr(i, 'event_type') != event_type)
        if self._subscription is not None:
            self._subscription['events'] = [i for i in self._subscription['events'] if i.get(event_type) != event_type]
        return popped

    def import_subscription(self, subscription):
        """Import an existing Subscription into the builder to update it.

        Args:
            subscription (:py:class:`streamsets.sdk.sch_models.Subscription`): Subscription instance.
        """
        self._subscription = subscription._data
        self._events = SeekableList(SubscriptionEvent(event,
                                                      self._control_hub) for event in subscription._data['events'])
        self._action = subscription._data['externalActions'][0]

    def set_email_action(self, recipients, subject=None, body=None):
        """Set the Email action.

        Args:
            recipients (:obj:`list`): List of email addresses.
            subject (:obj:`str`, optional): Subject of the email. Default: ``None``.
            body (:obj:`str`, optional): Body of the email. Default: ``None``.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        self._action.update({'eventType': 'EMAIL',
                             'config': params})

    def set_webhook_action(self, uri, method='GET', content_type=None, payload=None, auth_type=None, username=None,
                           password=None, timeout=30000, headers=None):
        """Set the Webhook action.

        Args:
            uri (:obj:`str`): URI for the Webhook.
            method (:obj:`str`, optional): HTTP method to use. Default: ``'GET'``.
            content_type (:obj:`str`, optional): Content Type of the request. Default:  ``None``.
            payload (:obj:`str`, optional): Payload of the request. Default:  ``None``.
            auth_type (:obj:`str`, optional): ``'basic'`` or ``None``. Default: ``None``.
            username (:obj:`str`, optional): username for the authentication. Default: ``None``.
            password (:obj:`str`, optional): password for the authentication. Default: ``None``.
            timeout (:obj:`int`, optional): timeout for the Webhook action. Default: ``30000``.
            headers (:obj:`dict`, optional): Headers to be sent to the Webhook call. Default: ``None``.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        if auth_type is None:
            params['authType'] = "none"
        self._action.update({'eventType': 'WEBHOOKV1',
                             'config': params})

    def build(self, name, description=None):
        """Builder for Scheduled Task.

        Args:
            name (:py:obj:`str`): Name of Subscription.
            description (:py:obj:`str`, optional): Description of subscription. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Subscription`.
        """
        self._subscription['events'] = [event._data for event in self._events]
        self._subscription['externalActions'] = [self._action]
        self._subscription['name'] = name
        self._subscription['description'] = description
        return Subscription(self._subscription, self._control_hub)


class Alert(BaseModel):
    """Model for Alerts.

    Attributes:
        message (:obj:`str`): The Alert's message text.
        alert_status (:obj:`str`): The status of the Alert.

    Args:
        alert (:obj:`dict`): JSON representation of an Alert.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """

    _ATTRIBUTES_TO_REMAP = {'message': 'label'}

    _ATTRIBUTES_TO_IGNORE = ['ackedBy',
                             'ackedOn',
                             'additionalInfo',
                             'alertType',
                             'id',
                             'organization',
                             'resourceId',
                             'ruleId']

    _REPR_METADATA = ['message', 'alert_status', 'triggered_on']

    def __init__(self, alert, control_hub):
        super().__init__(alert,
                         attributes_to_ignore=Alert._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=Alert._ATTRIBUTES_TO_REMAP,
                         repr_metadata=Alert._REPR_METADATA)
        self._control_hub = control_hub

    def _refresh(self):
        """Refresh an Alert in-memory."""
        resource_alerts = self._control_hub.api_client.get_resource_alerts(resource_id=self._data['resourceId'],
                                                                           alert_status='ACKNOWLEDGED')
        self._data = next(alert for alert in resource_alerts.response.json() if alert['id'] == self._data['id'])

    def acknowledge(self):
        """Acknowledge an active Alert."""
        if 'ACTIVE' in self.alert_status:
            self._control_hub.api_client.acknowledge_alert(body=[self._data['id']])
            self._refresh()
        else:
            raise ValueError("Alert is not ACTIVE, and cannot be acknowledged. Current Status: {}"
                             .format(self.alert_status))

    def delete(self):
        """Delete an acknowledged Alert."""
        if 'ACKNOWLEDGED' in self.alert_status:
            self._control_hub.api_client.delete_alert(body=[self._data['id']])
        else:
            raise ValueError("Alert is not ACKNOWLEDGED, and cannot be deleted. Current Status: {}"
                             .format(self.alert_status))

class Logs:
    """Model for SCH logs.

    Args:
        log_lines (:obj:`list`, optional): A list of strings of the log. Default: ``None``.
        data (:py:class:`streamsets.sdk.utils.SeekableList`, optional): A seekable list of logs in json format.
                                                                        Default: ``None``.
    """
    def __init__(self, log_lines=None, data=None):
        self._regex_pattern = ('(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s\[requestId:(.+)?\]\s\[app:(.+)?\]\s'
                               '\[componentId:(.+)?\]\s\[user:(.+)?\]\s\[thread:(.+)?\]\s(\w+)\s(.+)')
        self._headers = ['timestamp', 'request_id', 'app', 'component_id', 'user', 'thread', 'exception_level',
                         'message']
        if data is None:
            self._data = self._process_logs_to_json(log_lines)
        else:
            self._data = data

    def _process_logs_to_json(self, log_lines):
        i = 0
        data = []
        while i < len(log_lines):
            if re.match(self._regex_pattern, log_lines[i]):
                items = re.match(self._regex_pattern, log_lines[i]).groups()
                log_json = {self._headers[i]: items[i] for i in range(len(items))}
                data.append(log_json)
                i += 1
            else:
                # Handle logs where the message is split across multiple lines
                while i < len(log_lines) and not re.match(self._regex_pattern, log_lines[i]):
                    data[-1]['message'] += '\n{}'.format(log_lines[i])
                    i += 1
        data.sort(key=lambda x: x['timestamp'])
        return SeekableList(data)

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return format_sch_log(self._data)

    def __iter__(self):
        for log in self._data:
            yield log

    def __getitem__(self, key):
        return self._data[key]

    def to_dict(self):
        return self._data

    def get_all(self, **kwargs):
        return Logs(data=SeekableList(i for i in self._data if all(i.get(k) == v for k, v in kwargs.items())))

    def time_filter(self, after_timestamp=None, before_timestamp=None):
        """Returns log happened during a specified time interval (open/closed interval).

        Args:
            after_timestamp (:obj:`str`, optional): Specify timestamp in the form of `'2017-04-10 17:53:55,244'` to get
                                                    logs after particular time. Default: ``None``.
            before_timestamp (:obj:`str`, optional): Specify timestamp in the form of `'2017-04-10 17:53:55,244'` to get
                                                    logs before particular time. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Logs`.
        """
        if not after_timestamp and not before_timestamp:
            condition = lambda x: True
        elif after_timestamp and not before_timestamp:
            condition = lambda x: x.get('timestamp') and x.get('timestamp') > after_timestamp
        elif not after_timestamp and before_timestamp:
            condition = lambda x: x.get('timestamp') and x.get('timestamp') < before_timestamp
        else:
            condition = lambda x: (x.get('timestamp') and x.get('timestamp') > after_timestamp and
                                   x.get('timestamp') < before_timestamp)
        return Logs(data=SeekableList(filter(condition, self._data)))


class ConnectionBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Connection`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_connection_builder`.

    Args:
        connection (:obj:`dict`): Python object built from our Swagger ConnectionJson definition.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.
    """

    def __init__(self, connection, control_hub):
        self._connection = connection
        self._control_hub = control_hub

    def build(self, title, connection_type, authoring_data_collector, tags=None):
        """Define the connection.

        Args:
            title (:obj:`str`): Connection title.
            connecion_type (:obj:`str`): Type of connection.
            authoring_data_collector (:obj:`streamsets.sdk.ControlHub.DataCollector`): Authoring Data Collector.
            tags (:obj:`list`, optional): List of tags (strings). Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Connection`.
        """
        self._connection.update({'name': title,
                                 'connectionType': connection_type,
                                 'rawConnectionTags': [],
                                 'sdcId': authoring_data_collector.id,
                                 'sdcVersion': authoring_data_collector.version})
        self._connection_type = connection_type
        self._authoring_data_collector = authoring_data_collector
        connection_definition_json = self._get_connection_definition_json()
        connection_definition = self._setup_configuration(connection_definition_json)
        self._connection.update({'connectionDefinition': json.dumps(connection_definition._data),
                                 'libraryDefinition': json.dumps(connection_definition_json),
                                 'typeLabel': connection_definition.label})
        connection = Connection(connection=self._connection,
                                control_hub=self._control_hub)
        if tags:
            connection.add_tag(*tags)
        return connection

    def _get_connection_definition_json(self):
        """Fetch the connection definition.

        Returns:
            An instance of :py:obj:`dict`.
        """
        # Fetch connection definitions
        connection_definitions = (self._authoring_data_collector.instance.api_client
                                      .get_connection_definitions().response.json()['connections'])

        # Find the connection definition of required type
        for connection_definition in connection_definitions:
            if connection_definition['type'] == self._connection_type:
                return connection_definition
        else:
            raise ValueError('Provided authoring Data Collector does not have appropriate stage lib installed for '
                             'connection type {}'.format(self._connection_type))

    def _setup_configuration(self, connection_definition_json):
        """Setup the configuration of the connection.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ConnectionDefinition`.
        """

        # Create configuration json
        connection_definition_json['configuration'] = [{'name': config_def['name'],
                                                        'value': config_def['defaultValue']}
                                                       for config_def in
                                                       connection_definition_json['configDefinitions']]
        # Remove config definitons from dictionary as it is not needed in the final json
        del connection_definition_json['configDefinitions']

        connection_definition = ConnectionDefinition(connection_definition_json)
        return connection_definition


class ConnectionTags(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Tag` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, organization=None, parent_id=None, **kwargs):
        """Args offset, len_, order are not exposed directly as arguments because of their limited use by normal users
        but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            parent_id (:obj:`str`, optional): Parent tag ID to filter with. Default: ``None``.
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Tag` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Tag`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None, 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        response = self._control_hub.api_client.get_all_connection_tags(organization=organization,
                                                                        parent_id=parent_id,
                                                                        offset=kwargs_unioned['offset'],
                                                                        len_=kwargs_unioned['len'],
                                                                        order=kwargs_unioned['order']
                                                                        ).response.json()
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Tag, {})


class ConnectionDefinition(BaseModel):
    """Model for connection definition.

    Args:
        connection_definition (:obj:`dict`): A Python object representation of connection definition.
    """
    _REPR_METADATA = ['version']

    def __init__(self, connection_definition):
        super().__init__(connection_definition)
        self._configuration = Configuration(self._data['configuration'])

    @property
    def configuration(self):
        return self._configuration


class Connection(BaseModel):
    """Model for connection.

    Args:
        connection (:obj:`dict`): A Python object representation of Connection.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.
    """
    _REPR_METADATA = ['id', 'name', 'connection_type']

    def __init__(self, connection, control_hub):
        super().__init__(connection,
                         repr_metadata=Connection._REPR_METADATA)
        self._control_hub = control_hub
        self._connection_definition = (ConnectionDefinition(json.loads(self._data['connectionDefinition']))
                                       if self._data['connectionDefinition'] else None)

    @property
    def connection_definition(self):
        return self._connection_definition

    @property
    def pipeline_commits(self):
        """Get the pipeline commits using this connection.

        Returns:
            A :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.PipelineCommit`
                instances.
        """
        response = self._control_hub.api_client.get_pipeline_commits_using_connection(self.id).response.json()
        pipeline_commits = SeekableList()
        for commit_data in response:
            commit_data.update({'commitId': commit_data['pipelineCommitId'],
                                'version': commit_data['pipelineVersion'],
                                'commitMessage': None})
            pipeline_commits.append(PipelineCommit(pipeline_commit=commit_data, control_hub=self._control_hub))
        return pipeline_commits

    @property
    def acl(self):
        """Get Connection ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_connection_acl(connection_id=self.id).response.json(),
                   self._control_hub)

    @acl.setter
    def acl(self, connection_acl):
        """Update Connection ACL.

        Args:
            connection_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The Connection ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.update_connection_acl(connection_id=self.id,
                                                                  body=sdc_acl._data)

    @property
    def tags(self):
        """Get the connection tags.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of instances of
            :py:class:`streamsets.sdk.sch_models.Tag`.
        """
        connection_tags = self._data.get('tags', []) or []
        if not connection_tags:
            raw_connection_tags = self._data.get('rawConnectionTags', []) or []
            if raw_connection_tags:
                organization = self._control_hub.organization
                connection_tags = [build_tag_from_raw_tag(raw_tag, organization) for raw_tag in raw_connection_tags]
                self._data['tags'] = connection_tags
        return SeekableList(Tag(tag) for tag in connection_tags)

    def add_tag(self, *tags):
        """Add a tag

        Args:
            *tags: One or more instances of :obj:`str`
        """
        current_tags = [tag.tag for tag in self.tags]
        if not self._data.get('tags', None):
            self._data['tags'] = []
        if not self._data.get('rawConnectionTags', None):
            self._data['rawConnectionTags'] = current_tags
        for tag in tags:
            self._data['rawConnectionTags'].append(tag)
            tag_json = build_tag_from_raw_tag(tag, self._control_hub.organization)
            self._data['tags'].append(tag_json)

    def remove_tag(self, *tags):
        """Remove a tag

        Args:
            *tags: One or more instances of :obj:`str`
        """
        current_tags = [tag.tag for tag in self.tags]
        for tag in tags:
            if tag in current_tags:
                current_tags.remove(tag)
                item = self.tags.get(tag=tag)
                self._data['tags'].remove(item._data)
            else:
                logger.warning('Tag %s is not an assigned tag for this pipeline. Ignoring this tag.', tag)
        self._data['rawConnectionTags'] = current_tags


class Connections(CollectionModel):
    """Collection of :py:class:`streamsets.sdk.sch_models.Connection` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization

    def _get_all_results_from_api(self, id=None, organization=None, connection_type=None, **kwargs):
        """Args offset, len, order_by, order, filter_text, with_total_count are not exposed
        directly as arguments because of their limited use by normal users but, could still be specified just like any
        other args with the help of kwargs.

        Args:
            id (:obj:`str`)
            organization (:obj:`str`, optional): Organization ID. Default: ``None``.
            connection_type (:obj:`str`, optional): Type of connection. Default: ``None``.
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                response (:obj:`list`): a list of :py:class:`streamsets.sdk.sch_models.Connection` instances
                    in JSON format
                kwargs (:obj:`dict`): a dict of local variables not used in this function
                class_type (:py:class:`streamsets.sdk.sch_models.Connection`): the type of class to instantiate
                class_kwargs (:obj:`dict`): a dict of additional arguments required by the class_type's init
        """
        kwargs_defaults = {'offset': None, 'len': None, 'order_by': 'NAME', 'order': 'ASC', 'filter_text': None,
                           'with_total_count': False}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if organization is None:
            organization = self._organization
        if id is not None:
            response = [self._control_hub.api_client.get_connection(connection_id=id).response.json()]
        else:
            response = (self._control_hub.api_client
                        .get_all_connections(organization=organization,
                                             connection_type=connection_type,
                                             offset=kwargs_unioned['offset'],
                                             len=kwargs_unioned['len'],
                                             order_by=kwargs_unioned['order_by'],
                                             order=kwargs_unioned['order'],
                                             filter_text=kwargs_unioned['filter_text'],
                                             with_total_count=kwargs_unioned['with_total_count']
                                             ).response.json())
            connection_ids = [connection['id'] for connection in response['data']]
            response['data'] = [self._control_hub.api_client.get_connection(connection_id=connection_id).response.json()
                                for connection_id in connection_ids]
        kwargs_unused = kwargs_instance.subtract()
        return CollectionModelResults(response, kwargs_unused, Connection, {'control_hub': self._control_hub})


class ConnectionVerificationResult(BaseModel):
    """Model for connection verification result.

    Args:
        connection_preview_json (:obj:`dict`): dynamic preview API response JSON
    """
    _REPR_METADATA = ['status']

    def __init__(self, connection_preview_json):
        super().__init__(connection_preview_json,
                         repr_metadata=ConnectionVerificationResult._REPR_METADATA)

    @property
    def issue_count(self):
        """The count of the number of issues for the connection verification result.

        Returns:
              A :obj:`int` that represents the number of issues.
        """
        return self.issues['issueCount']

    @property
    def issue_message(self):
        """The message provided for the connection verification result.

        Returns:
              A :obj:`str` message detailing the response for the connection verification result.
        """
        return next(iter(self.issues['stageIssues'].values()))[0]['message']


# We define module-level attributes to allow users to extend certain
# SCH classes and have them used by other classes without the need to override
# their methods (e.g. allow the Pipeline class to be extended and be built using a
# non-extended PipelineBuilder class).
_Pipeline = Pipeline
_SchSdcStage = SchSdcStage
_SchStStage = SchStStage
