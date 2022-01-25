#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import enum
import warnings
import numpy as np
import pandas as pd
from datetime import datetime, date
from typing import Any, List, Dict, Type, Optional
from dateutil.parser import parse as python_date_parser

from .task import Task
from ..auth import Credentials
from ..error import DeepintBaseError
from ..util import handle_request, parse_date, parse_url


warnings.simplefilter(action='ignore', category=FutureWarning)


class FeatureType(enum.Enum):
    """Available feature types in the system.
    """
    text = 1
    date = 2
    logic = 3
    nominal = 4
    numeric = 5
    unknown = 6

    @classmethod
    def from_string(cls, _str: str) -> 'FeatureType':
        """Builds the :obj:`deepint.core.source.FeatureType` from a :obj:`str`.

        Args:
            _str: name of the feature type.

        Returns:
            the feature type converted to :obj:`deepint.core.source.FeatureType`.
        """
        return cls.unknown if _str not in [e.name for e in cls] else cls[_str]

    @classmethod
    def from_pandas_type(cls, column: pd.Series, min_text_size: int = 256) -> List['FeatureType']:
        """Builds a :obj:`deepint.core.source.FeatureType` from a :obj:`pandas.Series`.

        Checks the type of the elements stored in the column attribute, to detect the python native type
        or the :obj:`pandas` type, and build the corresponding :obj:`deepint.core.source.FeatureType`.

        Args:
            column: column of a :obj:`pd.DataFrame` to obtain the associated :obj:`deepint.core.source.FeatureType`
            min_text_size: the minimum length of an element to consider the type as text instead of nominal.

        Returns:
            The feature type associated to the given column
        """
        t = column.dtype
        # Cf. generic types in
        # https://numpy.org/doc/stable/reference/arrays.scalars.html
        if np.issubdtype(t, np.integer):
            return cls.nominal
        elif np.issubdtype(t, np.floating):
            return cls.numeric
        elif np.issubdtype(t, np.bool_):
            return cls.logic
        elif np.issubdtype(t, np.character):
            try:
                r = python_date_parser(column.iloc[0])
                is_date = True
            except:
                is_date = False
            if is_date:
                return cls.date
            elif column.str.len().max() >= min_text_size:
                return cls.text
            else:
                return cls.nominal
        elif np.issubdtype(t, np.datetime64) or np.issubdtype(t, np.timedelta64):
            return cls.date
        else:
            return cls.unknown


class SourceFeature:
    """ Stores the index, name, type and stats of a feature associated with a deepint.net source.
    
    Attributes:
        index: Feature index, starting with 0.
        name: Feature name (max 120 characters).
        feature_type: The type of the feature. Must be one of the values given in :obj:`deepint.core.source.FeatureType`.
        date_format: format used to parse the date if this feature is the type :obj:`deepint.core.source.FeatureType.date`.
        computed: True if the feature is computed (value based on operations over other features).
        null_count: Number of instances with value null.
        min_value: Min value.
        max_value: Max value..
        mean_value: Average value.
        deviation: Standard deviation.
        mapped_to: Index of the feature to map the existing data. You can specify -1 for no mapping.
    """

    def __init__(self, index: int, name: str, feature_type: FeatureType, indexed: bool,
                 date_format: str, computed: bool, null_count: int, min_value: int,
                 max_value: int, mean_value: int, deviation: int, mapped_to: int) -> None:

        self.index = index
        self.name = name
        self.feature_type = feature_type
        self.indexed = indexed
        self.date_format = date_format if not (
                date_format is None and feature_type == FeatureType.date) else 'YYYY-MM-DD'
        self.computed = computed
        self.null_count = null_count
        self.min_value = min_value
        self.max_value = max_value
        self.mean_value = mean_value
        self.deviation = deviation
        self.mapped_to = mapped_to if mapped_to is not None else index

    def __eq__(self, other):
        if not isinstance(other, SourceFeature):
            return False
        else:
            return self.name == other.name and (self.feature_type == other.feature_type or self.feature_type == FeatureType.unknown or other.feature_type == FeatureType.unknown)

    def __str__(self):
        return '<SourceFeature ' + ' '.join([f'{k}={v}' for k, v in self.to_dict().items()]) + '>'


    @staticmethod
    def from_dict(obj: Any) -> 'SourceFeature':
        """Builds a SourceFeature with a dictionary.

        Args:
            obj: :obj:`object` or :obj:`dict` containing the a serialized SourceFeature.

        Returns:
            SourceFeature containing the information stored in the given dictionary.
        """

        index = int(obj.get("index"))
        name = obj.get("name")
        feature_type = FeatureType.from_string(obj.get("type"))
        indexed = bool(obj.get("indexed"))
        date_format = obj.get("date_format")
        computed = bool(obj.get("computed"))
        null_count = int(obj.get("null_count")) if obj.get("null_count") is not None else None
        min_value = obj.get("min") if obj.get('min') is None or feature_type != FeatureType.date else parse_date(
            obj.get('min'))
        max_value = obj.get("max") if obj.get('max') is None or feature_type != FeatureType.date else parse_date(
            obj.get('max'))
        mean_value = obj.get("mean")
        deviation = obj.get("deviation")
        mapped_to = int(obj.get("mapped_to")) if obj.get("mapped_to") is not None else None
        return SourceFeature(index, name, feature_type, indexed, date_format,
                             computed, null_count, min_value, max_value, mean_value, deviation, mapped_to)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"index": self.index, "name": self.name, "type": self.feature_type.name, "indexed": self.indexed,
                "date_format": self.date_format, "computed": self.computed, "null_count": self.null_count,
                "min": self.min_value, "max": self.max_value, "mean": self.mean_value,
                "deviation": self.deviation, "mapped_to": self.mapped_to}

    def to_dict_minimized(self) -> Dict[str, Any]:
        """Builds a dictionary containing the minimal information stored in current object.

        The given resulting dictionary only contains fields for the name, type, indexed, date_format
        and mapped_to attributes.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"name": self.name, "type": self.feature_type.name, "indexed": self.indexed,
                "date_format": self.date_format, "mapped_to": self.mapped_to}

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, date_formats: Dict[str, str] = None, min_text_length: int = 1000) -> List[
        'SourceFeature']:
        """Given an :obj:`pandas.DataFrame` buils the list of :obj:`deepint.core.source.SourceFeature` associated with each of its columns.

        The given resulting ditionary only contains fields for the name, type, indexed, date_format 
        and mapped_to attributes.

        Note: The index values are assigned with the order of the columns in the given :obj:`pandas.DataFrame`

        Args:
            df: :obj:`pandas.DataFrame` from which the data types for each of its columns will be constructed. 
            date_formats: dicionary contianing the association between column name and date format like the ones specified 
                in [#/date_formats]. Is optional to provide value for any column, but if not provided will be considered as 
                null and the date format (in case of being a date type) will be the default one assigned by Deep Intelligence. 
            min_text_length: the minimun length of an element to consider the type as text instead of nominal.

        Returns:
            collection of features in the format of Deep Intellgience corresponding to the given DataFrame.
        """

        # prepare date formats
        date_formats = {} if date_formats is None else date_formats
        date_formats = {c: None if c not in date_formats else date_formats[c] for c in df.columns}

        # build features
        return [cls(i, c, FeatureType.from_pandas_type(df[c]), True, date_formats[c], False, None, None, None,
                              None, None, None) for i, c in enumerate(df.columns)]


class SourceInfo:
    """Stores the information of a Deep Intelligence source.
    
    Attributes:
        source_id: source's id in format uuid4.
        created: Creation date.
        last_modified: Last modified date.
        last_access: Last access date.
        name: source's name.
        description: source's description.
        source_type: type of source (mongodb, SQL, CSV, etc).
        instances: Number of instances.
        size_bytes: Source size in bytes.
    """

    def __init__(self, source_id: str, created: datetime,
                 last_modified: datetime, last_access: datetime, name: str,
                 description: str, source_type: str, instances: int,
                 size_bytes: int) -> None:
        self.source_id = source_id
        self.created = created
        self.last_modified = last_modified
        self.last_access = last_access
        self.name = name
        self.description = description
        self.source_type = source_type
        self.instances = instances
        self.size_bytes = size_bytes

    def __eq__(self, other):
        if not isinstance(other, SourceInfo):
            return False
        else:
            return self.source_id == other.source_id

    def __str__(self):
        return ' '.join([f'{k}={v}' for k, v in self.to_dict().items()])

    @staticmethod
    def from_dict(obj: Any) -> 'SourceInfo':
        """Builds a SourceInfo with a dictionary.

        Args:
            obj: :obj:`object` or :obj:`dict` containing the a serialized SourceInfo.

        Returns:
            SourceInfo containing the information stored in the given dictionary.
        """

        source_id = obj.get("id")
        created = parse_date(obj.get("created"))
        last_modified = parse_date(obj.get("last_modified"))
        last_access = parse_date(obj.get("last_access"))
        name = obj.get("name")
        description = obj.get("description")
        source_type = obj.get("type")
        instances = int(obj.get("instances"))
        size_bytes = int(obj.get("size_bytes"))
        return SourceInfo(source_id, created, last_modified, last_access, name,
                          description, source_type, instances,
                          size_bytes)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"id": self.source_id, "created": self.created.isoformat(),
                "last_modified": self.last_modified.isoformat(), "last_access": self.last_access.isoformat(),
                "name": self.name, "description": self.description, "source_type": self.source_type,
                "instances": int(self.instances), "size_bytes": int(self.size_bytes)}


class SourceInstances:
    """Operates over the instances of a concrete source.

    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.source.Source`
    
    Attributes:
        source: the source with which to operate with its instances
    """

    def __init__(self, source: 'Source') -> None:
        self.source = source

    def fetch(self,
              select: str = None,
              where: str = None,
              order_by: str = None,
              order_type: str = None,
              offset: int = None,
              limit: int = None) -> pd.DataFrame:
        """Retrieves a source's instances.

        Args:
            select: features to retrieve. Note: all features must belon to the source.
            where: query in Deepint Query Language.
            order_by: feature by which to sort instances during retrieval.
            order_type: must be asc or desc.
            offset: number of instances to ignore during the retrieval.
            limit: maximum number of instances to retrieve.

        Returns:
            :obj:`pd.DataFrame`: containing the retrieved data.
        """

        order_type = 'asc' if order_type is None else order_type
        order_by = f'{order_by},{order_type}' if order_by is not None else None

        path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}/instances'
        headers = {'x-deepint-organization': self.source.organization_id}
        parameters = {
            'select': select,
            'where': where,
            'order_by': order_by,
            'offset': offset,
            'limit': limit
        }
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.source.credentials, parameters=parameters)

        # format response
        result = [{
            feature['name']: instance[feature['index']]
            for feature in response['features']
        } for instance in response['instances']]

        df = pd.DataFrame(data=result)

        return df

    def update(self,
               data: pd.DataFrame,
               replace: bool = False,
               pk: str = None,
               date_format_feature: int = None,
               send_with_index: bool = False,
               **kwargs) -> Task:
        """Updates a source's instances.

        Args:
            data: data to update the instances. The column names must correspond to source's feature names.
            replace: if set to True the source's content is replaced by the new insertions.
            pk: feature used primary key during the instances insertion, to update the existing values and insert the not 
                existing ones. If is provided with the replace set to True, all the instances will be replaced.
            date_format_feature: the input pk for the request body.
            send_with_index: if set to False the data is send without the index as first field. Else index is send.

        Returns: 
            reference to task created to perform the source instances update operation.
        """

        # check arguments
        if not isinstance(data, pd.DataFrame):
            raise DeepintBaseError(code='TYPE_MISMATCH', message='The provided input is not a DataFrame.')
        elif data.empty or data is None:
            raise DeepintBaseError(code='EMPTY_DATA', message='The provided DataFrame is empty.')
        elif len(data.columns) != len([f for f in self.source.features.fetch_all() if not f.computed]):
            raise DeepintBaseError(code='INPUTS_MISMATCH',
                                   message='The provided DataFrame must have same number of columns as current source.')
        else:
            for c in data.columns:
                if self.source.features.fetch(name=c) is None:
                    raise DeepintBaseError(code='INPUTS_MISMATCH',
                                           message='The provided DataFrame columns must have same names as the soure\'s features.')

        # retrieve index of date_format
        date_format = None
        if date_format_feature is not None:
            f = self.source_id.features.fetch(index=date_format_feature)
            if f is not None:
                date_format = f.date_format

        # convert content to CSV
        try:
            column_order = [f.name for f in self.source.features.fetch_all() if not f.computed]
            streaming_values_data = data.to_csv(sep=',',
                                                index=send_with_index,
                                                columns=column_order)
        except:
            raise DeepintBaseError(code='CONVERSION_ERROR',
                                   message='Unable to convert DataFrame to CSV. Please, check the index, columns and the capability of serialization for the DataFrame fields.')

        # request
        path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}/instances'
        headers = {'x-deepint-organization': self.source.organization_id}
        files = [('file', ('file', streaming_values_data))]
        parameters = {
            'replace': replace,
            'pk': pk if not replace else None,
            'separator': ',',
            'quotes': '"',
            'csv_header': 'yes',
            'json_fields': '',
            'date_format': date_format
        }
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, files=files, credentials=self.source.credentials)

        # map response
        task = Task.build(task_id=response['task_id'], workspace_id=self.source.workspace_id,
                          organization_id=self.source.organization_id, credentials=self.source.credentials)

        return task

    def clean(self, where: str = None) -> Task:
        """ Removes a source's instances.

        Args:
            where: query in Deepint Query Language, to select which instances delete.

        Returns: 
            reference to task created to perform the source instances deletion operation.
        """

        path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}/instances'
        headers = {'x-deepint-organization': self.source.organization_id}
        parameters = {
            'where': where
        }
        response = handle_request(method='DELETE', path=path, headers=headers, credentials=self.source.credentials, parameters=parameters)

        # map response
        task = Task.build(task_id=response['task_id'], workspace_id=self.source.workspace_id,
                          organization_id=self.source.organization_id, credentials=self.source.credentials)

        return task


class SourceFeatures:
    """Operates over the features of a concrete source.
    
    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.source.Source`.
    
    Attributes:
        source: the source with which to operate with its features.
    """

    def __init__(self, source: 'Source', features: List[SourceFeature]) -> None:
        self.source = source
        self._features = features
        if self._features is not None:
            self._features.sort(key=lambda x: x.index)

    def __eq__(self, other) -> bool:
        if not isinstance(other, SourceFeatures):
            return False
        else:
            for f in self._features:
                other_f = other.fetch(name=f.name) 
                if (other_f is not None) and f != other_f:
                    return False
            return True

    def load(self):
        """Loads a source's features.

        If the features were already loaded, this ones are replace by the new ones after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}'
        headers = {'x-deepint-organization': self.source.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.source.credentials)

        # map results
        self._features = [SourceFeature.from_dict(f) for f in response['features']]

    def update(self, features: List[SourceFeature] = None) -> Task:
        """Updates a source's features.

        If the features were already loaded, this ones are replace by the new ones after retrieval.
        
        Args:
            features: the new eatures to update the source. If not provided the source's internal ones are used.
        
        Returns:
            reference to task created to perform the source features update operation.
        """

        # check parameters
        features = features if features is not None else self._features

        # request
        path = f'/api/v1/workspace/{self.source.workspace_id}/source/{self.source.info.source_id}/features'
        headers = {'x-deepint-organization': self.source.organization_id}
        parameters = {'features': [f.to_dict_minimized() for f in features]}
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.source.credentials)

        # update local state
        self._features = features

        # map response
        task = Task.build(task_id=response['task_id'], workspace_id=self.source.workspace_id,
                          organization_id=self.source.organization_id, credentials=self.source.credentials)

        return task

    def fetch(self, index: int = None, name: str = None, force_reload: bool = False) -> Optional[SourceFeature]:
        """Search for a feature in the source.
        
        Note: if no name or index is provided, the returned value is None.

        Args:
            index: feature's index to search by.
            name: feature's name to search by.
            force_reload: if set to True, features are reloaded before the search with the
                :obj:`deepint.core.source.SourceFeature.load` method.
        
        Returns:
            retrieved feature if found, and in other case None.
        """

        # if set to true reload
        if force_reload:
            self.load()

        # check parameters
        if index is None and name is None:
            return None

        # search
        for f in self._features:
            if f.index == index or f.name == name:
                return f
        return None

    def fetch_all(self, force_reload: bool = False) -> List[SourceFeature]:
        """Retrieves all source's features.
        
        Args:
            force_reload: if set to True, features are reloaded before the search with the
                :obj:`deepint.core.source.SourceFeature.load` method.
        
        Returns:
            the source's features.
        """

        # if set to true reload
        if force_reload:
            self.load()

        return self._features


class Source:
    """A Deep Intelligence source.
    
    Note: This class should not be instanced directly, and it's recommended to use the :obj:`deepint.core.source.Source.build`
    or :obj:`deepint.core.source.Source.from_url` methods. 
    
    Attributes:
        organization_id: organization where source is located.
        workspace_id: workspace where source is located.
        info: :obj:`deepint.core.source.SourceInfo` to operate with source's information.
        instances: :obj:`deepint.core.source.SourceInstances` to operate with source's instances.
        features: :obj:`deepint.core.source.SourceFeatures` to operate with source's features.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the source. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    def __init__(self, organization_id: str, workspace_id: str, credentials: Credentials,
                 info: SourceInfo, features: List[SourceFeature]) -> None:
        self.info = info
        self.credentials = credentials
        self.workspace_id = workspace_id
        self.organization_id = organization_id
        self.instances = SourceInstances(self)
        self.features = SourceFeatures(self, features)

    def __str__(self):
        return f'<Source organization_id={self.organization_id} workspace={self.workspace_id} {self.info} features={self.features.fetch_all()}>'

    def __eq__(self, other):
        if not isinstance(other, Source):
            return False
        else:
            return self.info == other.info

    @classmethod
    def build(cls, organization_id: str, workspace_id: str, source_id: str, credentials: Credentials = None) -> 'Source':
        """Builds a source.
        
        Note: when source is created, the source's information and features are retrieved from API.

        Args:
            organization_id: organization where source is located.
            workspace_id: workspace where source is located.
            source_id: source's id.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the source. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the source build with the given parameters and credentials.
        """

        credentials = credentials if credentials is not None else Credentials.build()
        src_info = SourceInfo(source_id=source_id, created=None, last_modified=None, last_access=None,
                              name=None, description=None, source_type=None, instances=None, size_bytes=None)
        src = cls(organization_id=organization_id, workspace_id=workspace_id, credentials=credentials, info=src_info, features=None)
        src.load()
        src.features.load()
        return src

    @classmethod
    def from_url(cls, url: str, organization_id: str = None, credentials: Credentials = None) -> 'Source':
        """Builds a source from it's API or web associated URL.

        The url must contain the workspace's id and the source's id as in the following examples:

        Example:
            - https://app.deepint.net/o/3a874c05-26d1-4b8c-894d-caf90e40078b/workspace?ws=f0e2095f-fe2b-479e-be4b-bbc77207f42d&s=source&i=db98f976-f4bb-43d5-830e-bc18a3a89641
            - https://app.deepint.net/api/v1/workspace/f0e2095f-fe2b-479e-be4b-bbc77207f42/source/db98f976-f4bb-43d5-830e-bc18a3a89641
        
        Note: when source is created, the source's information and features are retrieved from API.
            Also it is remmarkable that if the API URL is providen, the organization_id must be provided in the optional parameter, otherwise
            this ID won't be found on the URL and the Organization will not be created, raising a value error.

        Args:
            url: the source's API or web associated URL.
            organization_id: the id of the organziation. Must be providen if the API URL is used.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the source. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the source build with the URL and credentials.
        """

        url_info, hostname = parse_url(url)

        if 'organization_id' not in url_info and organization_id is None:
            raise ValueError('Fields organization_id must be in url to build the object. Or providen as optional parameter.')

        if 'workspace_id' not in url_info or 'source_id' not in url_info:
            raise ValueError('Fields workspace_id and source_id must be in url to build the object.')

        organization_id = url_info['organization_id'] if 'organization_id' in url_info else organization_id

        # create new credentials
        new_credentials = Credentials(token=credentials.token, instance=hostname)
        
        return cls.build(organization_id=organization_id, workspace_id=url_info['workspace_id'], source_id=url_info['source_id'],
                         credentials=new_credentials)

    def load(self):
        """Loads the source's information.

        If the source's information is already loaded, is replace by the new one after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.credentials)

        # map results
        self.info = SourceInfo.from_dict(response)

    def update(self, name: str = None, description: str = None):
        """Updates a source's name and description.

        Args:
            name: source's name. If not provided the source's name stored in the :obj:`deepint.core.source.Source.source_info` attribute is taken.
            descrpition: source's description. If not provided the source's description stored in the :obj:`deepint.core.source.Source.source_info` attribute is taken.
        """

        # check parameters
        name = name if name is not None else self.info.name
        description = description if description is not None else self.info.description

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}'
        headers = {'x-deepint-organization': self.organization_id}
        parameters = {'name': name, 'description': description}
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.credentials)

        # update local state
        self.info.name = name
        self.info.description = description

    def delete(self):
        """Deletes a source.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/source/{self.info.source_id}'
        headers = {'x-deepint-organization': self.organization_id}
        handle_request(method='DELETE', path=path, headers=headers, credentials=self.credentials)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary contining the information stored in the current object.
        """

        return {"info": self.info.to_dict(), "features": [x.to_dict() for x in self.features.fetch_all()]}
