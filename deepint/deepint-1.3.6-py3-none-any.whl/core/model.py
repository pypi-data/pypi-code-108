#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import enum
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Any, List, Dict

from ..auth import Credentials
from ..error import DeepintBaseError
from .source import Source, FeatureType, SourceFeature
from ..util import handle_request, handle_paginated_request, parse_date, parse_url


class ModelType(enum.Enum):
    """Available model types in the system.
    """

    classifier = 0
    regressor = 1
    unknown = 2

    @classmethod
    def from_string(cls, _str: str) -> 'ModelType':
        """Builds the :obj:`deepint.core.model.ModelType` from a :obj:`str`.

        Args:
            _str: name of the model type.

        Returns:
            the model type converted to :obj:`deepint.core.model.ModelType`.
        """
        return cls.unknown if _str not in [e.name for e in cls] else cls[_str]

    @classmethod
    def all(cls) -> List[str]:
        """ Returns all available model types serialized to :obj:`str`.

        Returns:
            all available model types.
        """
        return [e.name for e in cls]

class ModelMethod(enum.Enum):
    """Available model methods in the system.
    """

    bayes = 0
    forest = 1
    gradient = 2
    logistic = 3
    linear = 4
    mlp = 5
    neighbors = 6
    sv = 7
    tree = 8
    xgb = 9
    unknown = 10

    @classmethod
    def from_string(cls, _str: str) -> 'ModelMethod':
        """Builds the :obj:`deepint.core.model.ModelMethod` from a :obj:`str`.

        Args:
            _str: name of the model method.

        Returns:
            the model method converted to :obj:`deepint.core.model.ModelMethod`.
        """
        return cls.unknown if _str not in [e.name for e in cls] else cls[_str]

    @classmethod
    def all(cls) -> List[str]:
        """ Returns all available model methods serialized to :obj:`str`.

        Returns:
            all available model methods.
        """
        return [e.name for e in cls]

    @classmethod
    def allowed_methods_for_type(cls, model_type: ModelType) -> List['ModelMethod']:
        """Returns a list with the allowed model methods for a model type.

        Args:
            model_type: type of model to know about the allowed methods

        Returns:
            the model methods allowed for the given model type.
        """
        if model_type == ModelType.classifier:
            return [cls.bayes, cls.forest, cls.gradient, cls.logistic, cls.mlp, cls.neighbors, cls.sv, cls.tree,
                    cls.xgb]
        elif model_type == ModelType.regressor:
            return [cls.forest, cls.gradient, cls.linear, cls.mlp, cls.neighbors, cls.sv, cls.tree, cls.xgb]


class ModelFeature:
    """ Stores the index, name, type and stats of a model feature associated with a deepint.net model.
    
    Attributes:
        index: Feature index, starting with 0.
        name: Feature name (max 120 characters).
        input_type: The type of the feature. Must be one of the values given in :obj:`deepint.core.model.FeatureType`.
    """

    def __init__(self, name: str, input_type: FeatureType, index: int = None) -> None:
        self.name = name
        self.index = index
        self.input_type = input_type

    def __eq__(self, other):
        if not isinstance(other, SourceFeature):
            return False
        else:
            d1, d2, = self.to_dict(), other.to_dict()
            for k in d1:
                if d1[k] != d2[k]:
                    return False
            return True

    def __str__(self):
        return f'<ModelFeature ' + ' '.join([f'{k}={v}' for k, v in self.to_dict().items()]) + '>'

    @staticmethod
    def from_dict(obj: Any, index: int = None) -> 'ModelFeature':
        """Builds a ModelFeature with a dictionary.

        Args:
            obj: :obj:`object` or :obj:`dict` containing the a serialized ModelFeature.

        Returns:
            ModelFeature containing the information stored in the given dictionary.
        """

        if obj is None:
            name = None
            input_type = FeatureType.unknown
        else:
            name = obj.get("name")
            input_type = FeatureType.from_string(obj.get("type"))
        return ModelFeature(name, input_type, index=index)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"name": self.name, "type": self.input_type.name}


class ModelInfo:
    """Stores the information of a Deep Intelligence model.
    
    Attributes:
        model_id: model's id in format uuid4.
        name: model's name.
        description: model's description.
        model_type: type of model (classifier or regressor).
        method: method for prediction (bayes, logistic, forest, etc.).
        created: creation date.
        last_modified: last modified date.
        last_access: last access date.
        size_bytes: source size in bytes.
        source_train: source used to train the model.
        configuration: advanced model configuration
    """

    def __init__(self, model_id: str, name: str, description: str, model_type: ModelType, method: ModelMethod,
                 created: datetime, last_modified: datetime, last_access: datetime, source_train: str,
                 configuration: dict, size_bytes: int) -> None:
        self.model_id = model_id
        self.name = name
        self.description = description
        self.model_type = model_type
        self.method = method
        self.created = created
        self.last_modified = last_modified
        self.last_access = last_access
        self.source_train = source_train
        self.configuration = configuration
        self.size_bytes = size_bytes

    def __eq__(self, other):
        if not isinstance(other, ModelInfo):
            return False
        else:
            return self.model_id == other.model_id

    def __str__(self):
        return ' '.join([f'{k}={v}' for k, v in self.to_dict().items()])

    @staticmethod
    def from_dict(obj: Any) -> 'ModelInfo':
        """Builds a ModelInfo with a dictionary.

        Args:
            obj: :obj:`object` or :obj:`dict` containing the a serialized ModelInfo.

        Returns:
            ModelInfo containing the information stored in the given dictionary.
        """

        model_id = obj.get("id")
        name = obj.get("name")
        description = obj.get("description")
        model_type = ModelType.from_string(obj.get("type"))
        method = ModelMethod.from_string(obj.get("method"))
        created = parse_date(obj.get("created"))
        last_modified = parse_date(obj.get("last_modified"))
        last_access = parse_date(obj.get("last_access"))
        source_train = obj.get("source_train")
        configuration = obj.get("configuration")
        size_bytes = int(obj.get("size_bytes"))
        return ModelInfo(model_id, name, description, model_type, method, created, last_modified, last_access,
                         source_train, configuration, size_bytes)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"id": self.model_id, "name": self.name, "description": self.description,
                "type": self.model_type.name, "method": self.method.name, "created": self.created.isoformat(),
                "last_modified": self.last_modified.isoformat(), "last_access": self.last_access.isoformat(),
                "source_train": self.source_train, "configuration": self.configuration,
                "size_bytes": self.size_bytes}


class ModelPredictions:
    """Operates over the prediction options of a concrete model.

    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.model.Model`
    
    Attributes:
        model: the model with which to operate with its predictions
    """

    def __init__(self, model: 'Model'):
        self.model = model

    def evaluation(self) -> Dict[str, Any]:
        """Retrieves a model's evaluation.

        Returns:
            a dictionary contianing the model's evaluation
        """

        # request
        path = f'/api/v1/workspace/{self.model.workspace_id}/models/{self.model.info.model_id}/evaluation'
        headers = {'x-deepint-organization': self.model.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.model.credentials)

        return response

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """Uses a model to predict a single input.
        
        Note: The maximum number of instances to evaluate at once is one. For the evaluation of more instances, 
            check the :obj:`deepint.core.model.ModelPredictions.predict_batch`

        Args:
            data: data to be used as prediction inputs. The column names must correspond to the model's input feature names.

        Returns:
            a copy of the given input data with a new column with the prediction (output features) performed
        """

        # check
        if not isinstance(data, pd.DataFrame):
            raise DeepintBaseError(code='TYPE_MISMATCH', message='The provided input is not a DataFrame.')
        elif data.empty or data is None:
            raise DeepintBaseError(code='EMPTY_DATA', message='The provided DataFrame is empty.')
        elif len(data) > 1:
            raise DeepintBaseError(code='LARGE_DATA', message='The provided DataFrame must have a lenght of 1')
        elif len(data.columns) != len(self.model.input_features):
            raise DeepintBaseError(code='INPUTS_MISMATCH',
                                   message='The provided DataFrame must have same number of columns as current model\'s features.')
        else:
            for c in data.columns:
                if c not in [f.name for f in self.model.input_features]:
                    raise DeepintBaseError(code='INPUTS_MISMATCH',
                                           message='The provided DataFrame columns must have same names as the model\'s features.')

                    # prepare inputs
        try:
            data = data.where(pd.notnull(data), None)
            instance = data.to_dict(orient='records')[0]
            inputs = json.dumps([instance[f.name] for f in self.model.input_features])
        except:
            raise DeepintBaseError(code='CONVERSION_ERROR',
                                   message='Unable to convert DataFrame to inputs array. Please, check the index, columns and the capability of serialization for the DataFrame fields.')

        # request
        path = f'/api/v1/workspace/{self.model.workspace_id}/models/{self.model.info.model_id}/predict'
        parameters = {'inputs': inputs}
        headers = {'x-deepint-organization': self.model.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, parameters=parameters, credentials=self.model.credentials)

        # map response
        try:
            data_copy = data.copy()
            data_copy[self.model.output_features.name] = response['output']
        except:
            raise DeepintBaseError(code='CONVERSION_ERROR',
                                   message='Unable to convert the response to DataFrame. Please, check the model\'s features.')

        return data_copy

    def predict_batch(self, data: pd.DataFrame) -> pd.DataFrame:
        """Uses a model to predict multiple inputs.
        
        The maximum number of instances to evaluate at once is 25. 

        Args:
            data: data to be used as prediction inputs. The column names must correspond to the model's input feature names.

        Returns:
            a copy of the given input data with a new column with the predictions (output features) performed
        """

        # check
        if not isinstance(data, pd.DataFrame):
            raise DeepintBaseError(code='TYPE_MISMATCH', message='The provided input is not a DataFrame.')
        elif data.empty or data is None:
            raise DeepintBaseError(code='EMPTY_DATA', message='The provided DataFrame is empty.')
        elif len(data) > 25:
            raise DeepintBaseError(code='LARGE_DATA', message='The provided DataFrame must have a maximum lenght of 25')
        elif len(data.columns) != len(self.model.input_features):
            raise DeepintBaseError(code='INPUTS_MISMATCH',
                                   message='The provided DataFrame must have same number of columns as current model\'s features.')
        else:
            for c in data.columns:
                if c not in [f.name for f in self.model.input_features]:
                    raise DeepintBaseError(code='INPUTS_MISMATCH',
                                           message='The provided DataFrame columns must have same names as the model\'s features.')

                    # prepare inputs
        try:
            data = data.where(pd.notnull(data), None)
            instances = data.to_dict(orient='records')
            inputs = [{'inputs': [instance[f.name] for f in self.model.input_features]} for instance in instances]
        except:
            raise DeepintBaseError(code='CONVERSION_ERROR',
                                   message='Unable to convert DataFrame to inputs array. Please, check the index, columns and the capability of serialization for the DataFrame fields.')

        # request
        path = f'/api/v1/workspace/{self.model.workspace_id}/models/{self.model.info.model_id}/batch-predict'
        parameters = {'data': inputs}
        headers = {'x-deepint-organization': self.model.organization_id}
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.model.credentials)

        # map response
        try:
            data_copy = data.copy()
            data_copy[self.model.output_features.name] = response['outputs']
        except:
            raise DeepintBaseError(code='CONVERSION_ERROR',
                                   message='Unable to convert the response to DataFrame. Please, check the model\'s features.')

        return data_copy

    def predict_unidimensional(self, data: pd.DataFrame, variations: List[Any],
                               variations_feature_name: str) -> pd.DataFrame:
        """Uses a model to perform an unidimensional predict. Keeping all the input variables with the same value and vary one of them.
        
        Note: The maximum number of instances to evaluate at once is one (with a maximuym of 255 variations).

        Note: All values must be providen in the data, including the variated feature (although the last one is not going to be used).

        Args:
            data: data to be used as prediction inputs. The column names must correspond to the model's input feature names.
            variations: list of variations to perform over a single feature.
            variations_feature_name: name of the feature on which the variations are to be carried out

        Returns:
            a copy of the given input data replacing the variated feature with the list of variations, and a new column 
            with the predictions (output features) performed
        """


        # check
        if not isinstance(data, pd.DataFrame):
            raise DeepintBaseError(code='TYPE_MISMATCH', message='The provided input is not a DataFrame.')
        elif data.empty or data is None:
            raise DeepintBaseError(code='EMPTY_DATA', message='The provided DataFrame is empty.')
        elif len(data) > 255:
            raise DeepintBaseError(code='LARGE_DATA',
                                   message='The provided DataFrame must have a maximum lenght of 255')
        elif len(data.columns) != len(self.model.input_features):
            raise DeepintBaseError(code='INPUTS_MISMATCH',
                                   message='The provided DataFrame must have same number of columns as current model\'s features.')
        elif variations_feature_name not in data.columns:
            raise DeepintBaseError(code='INPUTS_MISMATCH',
                                   message='The provided variations column must match with input data\'s columns.')
        else:
            for c in data.columns:
                if c not in [f.name for f in self.model.input_features]:
                    raise DeepintBaseError(code='INPUTS_MISMATCH',
                                           message='The provided DataFrame columns must have same names as the model\'s features.')

        try:
            # prepare inputs
            data = data.where(pd.notnull(data), None)
            instance = data.to_dict(orient='records')[0]
            inputs = [instance[f.name] for f in self.model.input_features]
            # variable to vary index
            variations_feature_index = \
                [f.index for f in self.model.input_features if f.name == variations_feature_name][0]
        except:
            raise DeepintBaseError(code='CONVERSION_ERROR',
                                   message='Unable to convert DataFrame to inputs array. Please, check the index, columns and the capability of serialization for the DataFrame fields.')

        # request
        path = f'/api/v1/workspace/{self.model.workspace_id}/models/{self.model.info.model_id}/predict-1d'
        headers = {'x-deepint-organization': self.model.organization_id}
        parameters = {'inputs': inputs, 'vary': variations_feature_index, 'values': variations}
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.model.credentials)

        # map response
        try:
            data_copy = data.copy()
            data_copy = data_copy.loc[data_copy.index.repeat(len(variations))].reset_index(drop=True)
            data_copy[variations_feature_name] = variations
            data_copy[self.model.output_features.name] = response['outputs']
        except:
            raise DeepintBaseError(code='CONVERSION_ERROR',
                                   message='Unable to convert the response to DataFrame. Please, check the model\'s features.')

        return data_copy


class Model:
    """A Deep Intelligence model.
    
    Note: This class should not be instanced directly, and it's recommended to use the :obj:`deepint.core.model.Model.build`
    or :obj:`deepint.core.model.Model.from_url` methods. 
    
    Attributes:
        organization_id: organization where model is located.
        workspace_id: workspace where model is located.
        info: :obj:`deepint.core.model.ModelInfo` to operate with model's information.
        input_features: :obj:`list` of :obj:`deepint.core.model.ModelFeature` to operate with model's input features.
        output_features: :obj:`list` of :obj:`deepint.core.model.ModelFeature` to operate with model's output features.
        predictions: :obj:`deepint.core.model.ModelPredictions` to operate with model's predictions.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the model. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    def __init__(self, organization_id: str, workspace_id: str, credentials: Credentials, info: ModelInfo, 
                 input_features: List[ModelFeature], output_features: ModelFeature) -> None:
        self.organization_id = organization_id
        self.info = info
        self.credentials = credentials
        self.workspace_id = workspace_id
        self.input_features = input_features
        self.output_features = output_features
        if self.input_features is not None:
            self.input_features.sort(key=lambda x: x.index)
        self.predictions = ModelPredictions(self)

    def __str__(self):
        return f'<Model organization_id={self.organization_id} workspace={self.workspace_id} {self.info}>'

    def __eq__(self, other):
        if not isinstance(other, Model):
            return False
        else:
            return self.info == other.info

    @classmethod
    def build(cls,organization_id: str, workspace_id: str, model_id: str, credentials: Credentials = None) -> 'Model':
        """Builds a model.
        
        Note: when model is created, the model's information and features are retrieved from API.

        Args:
            organization_id: organization where model is located.
            workspace_id: workspace where model is located.
            model_id: model's id.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the model. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the model build with the given parameters and credentials.
        """

        credentials = credentials if credentials is not None else Credentials.build()
        info = ModelInfo(model_id=model_id, name=None, description=None, model_type=None, method=None, created=None,
                         last_modified=None,
                         last_access=None, source_train=None, configuration=None, size_bytes=None)
        model = cls(organization_id=organization_id, workspace_id=workspace_id, credentials=credentials, info=info, 
                      input_features=None, output_features=None)
        model.load()
        return model

    @classmethod
    def from_url(cls, url: str, organization_id: str = None, credentials: Credentials = None) -> 'Model':
        """Builds a model from it's API or web associated URL.

        The url must contain the workspace's id and the model's id as in the following examples:

        Example:
            - https://app.deepint.net/o/3a874c05-26d1-4b8c-894d-caf90e40078b/workspace?ws=f0e2095f-fe2b-479e-be4b-bbc77207f42d&s=model&i=db98f976-f4bb-43d5-830e-bc18a3a89641
            - https://app.deepint.net/api/v1/workspace/f0e2095f-fe2b-479e-be4b-bbc77207f42/models/db98f976-f4bb-43d5-830e-bc18a3a89641
        
        Note: when model is created, the model's information and features are retrieved from API.
            Also it is remmarkable that if the API URL is providen, the organization_id must be provided in the optional parameter, otherwise
            this ID won't be found on the URL and the Organization will not be created, raising a value error.

        Args:
            url: the model's API or web associated URL.
            organization_id: the id of the organziation. Must be providen if the API URL is used.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the model. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the model build with the URL and credentials.
        """

        url_info, hostname = parse_url(url)

        if 'organization_id' not in url_info and organization_id is None:
            raise ValueError('Fields organization_id must be in url to build the object. Or providen as optional parameter.')

        if 'workspace_id' not in url_info or 'model_id' not in url_info:
            raise ValueError('Fields workspace_id and model_id must be in url to build the object.')

        organization_id = url_info['organization_id'] if 'organization_id' in url_info else organization_id

        # create new credentials
        new_credentials = Credentials(token=credentials.token, instance=hostname)
        
        return cls.build(organization_id=organization_id, workspace_id=url_info['workspace_id'], model_id=url_info['model_id'], 
                credentials=new_credentials)

    def load(self):
        """Loads the model's information.

        If the model's information is already loaded, is replace by the new one after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/models/{self.info.model_id}'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.credentials)

        # map results
        self.info = ModelInfo.from_dict(response)
        self.input_features = [ModelFeature.from_dict(f, index=i) for i, f in enumerate(response['inputs'])]
        self.output_features = ModelFeature.from_dict(response['output'])

    def update(self, name: str=None, description: str=None):
        """Updates a model's name and description.

        Args:
            name: model's name. If not provided the model's name stored in the :obj:`deepint.core.model.Model.model_info` attribute is taken.
            descrpition: model's description. If not provided the model's description stored in the :obj:`deepint.core.model.Model.model_info` attribute is taken.
        """

        # check parameters
        name = name if name is not None else self.info.name
        description = description if description is not None else self.info.description

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/models/{self.info.model_id}'
        headers = {'x-deepint-organization': self.organization_id}
        parameters = {'name': name, 'description': description}
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.credentials)

        # update local state
        self.info.name = name
        self.info.description = description

    def delete(self):
        """Deletes a model.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/models/{self.info.model_id}'
        headers = {'x-deepint-organization': self.organization_id}
        handle_request(method='DELETE', path=path, headers=headers, credentials=self.credentials)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary contining the information stored in the current object.
        """

        return {"info": self.info, "input_features": [x.to_dict() for x in self.input_features],
                "output_features": self.output_features.to_dict()}
