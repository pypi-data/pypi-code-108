from abc import ABC, abstractmethod
from typing import List, Union, Optional
from datalogue.models.datastore import (
    Datastore,
    DatastoreDef,
    _datastore_def_from_payload,
    CredentialType,
)
from datalogue.models.transformations import (
    Transformation,
    _transformation_from_payload,
)
from datalogue.models.transformations.commons import DataType
from datalogue.models.transformations.structure import Structure, PathNodeDescription
from datalogue.models.pipeline_behavior import (
    PipelineBehavior,
    Write,
    _pipeline_behavior_from_payload,
)
from datalogue.dtl_utils import _parse_list, _parse_uuid, map_option
from datalogue.errors import DtlError, _property_not_found
from uuid import UUID


class Definition:
    """
    A Pipeline is a series of transformations that will output its results to a target
    and can contain Child(ren ?) Pipelines. cf diagram below.

        Parent Pipelines -> Transformations -+-> Target
                                             |
                                             +-> Children Pipelines
    """

    def __init__(
        self,
        transformations: List[Transformation],
        forks: List["Definition"],
        target: Union[Datastore, DatastoreDef],
        pipeline_behavior: PipelineBehavior = Write(),
    ):
        if isinstance(target, Datastore):
            target = target.definition

        self.transformations = transformations
        self.forks = forks
        self.target = target
        self.pipeline_behavior = pipeline_behavior

    def __repr__(self):
        return (
            f"Definition(transformations= {self.transformations!r}, forks= {self.forks!r}, target= {self.target!r}"
            f", pipeline_behavior= {self.pipeline_behavior})"
        )

    def __eq__(self, other: "Definition"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def _as_payload(self) -> Union[DtlError, dict]:
        if self.target.datastore_id is None:
            return DtlError("Cannot serialize a pipeline with a target that was not saved to the database (id missing)")

        if self.target.type != CredentialType.JDBC and not isinstance(self.pipeline_behavior, Write):
            return DtlError("Only JDBC targets can have pipeline behavior other than 'Write'")

        target_payload = self.target._as_payload()
        target_payload["pipelineBehavior"] = self.pipeline_behavior._as_payload()
        return {
            "transformations": list(map(lambda s: s._as_payload(), self.transformations)),
            "pipelines": list(map(lambda s: s._as_payload(), self.forks)),
            "target": target_payload,
        }

    @staticmethod
    def _from_payload(payload: dict) -> Union[DtlError, "Definition"]:
        """
        Builds a pipeline object from a dictionary,

        :param payload: dictionary parsed from json
        :return:
        """

        transformations = payload.get("transformations")
        if transformations is not None:
            transformations = _parse_list(_transformation_from_payload)(transformations)
            if isinstance(transformations, DtlError):
                return transformations
        else:
            transformations = list()

        forks = payload.get("pipelines")
        if forks is not None:
            forks = _parse_list(Definition._from_payload)(forks)
            if isinstance(forks, DtlError):
                return forks
        else:
            forks = list()

        target = payload.get("target")
        if target is None:
            return DtlError("Cannot have a pipeline without a 'target' property")
        else:
            target = _datastore_def_from_payload(target)
            if isinstance(target, DtlError):
                return target

        pipeline_behavior = payload.get("target").get("pipelineBehavior")
        if pipeline_behavior is not None:
            pipeline_behavior = _pipeline_behavior_from_payload(pipeline_behavior)
            if isinstance(pipeline_behavior, DtlError):
                return pipeline_behavior
        else:
            pipeline_behavior = Write()

        return Definition(transformations, forks, target, pipeline_behavior)


class EnvVariable:
    """
    Object that represents an environment variable.

    An environment variable can be either a literal or an expression that returns a value.

    Right now you can input as a value:
        - a string: "a"
        - an int: 3
        - a float: 4.3
        - a boolean: false
        - a script to index a source of data: `Source(<source_json_object>).index(n => n.label == "some_label")`. This
           will cache the data into a `Map` with the key being the value of the label you specified and value being
           the whole adg.

    The environment variables are injected as arguments into the lambda functions defined inside transformations.

        EX: MapFunction transformation

    ALPHA FEATURE
    """

    def __init__(self, data_type: DataType, value: str, key: str):
        """
        Builds an environment variable to be evaluated before execution of a stream

        :param data_type: type of the variable
        :param value: string to be evaluated
        :param key: key to be used to retrieve the value inside a lambda function
        """
        self.type = data_type
        self.value = value
        self.key = key

    def __eq__(self, other: "EnvVariable"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"EnvVariable(type= {self.type.value}, value= {self.value!r}, key= {self.key!r})"

    def _as_payload(self):
        return {"type": self.type.value, "value": self.value, "key": self.key}

    @staticmethod
    def _from_payload(payload: dict) -> Union["EnvVariable", DtlError]:

        data_type = payload.get("type")
        if data_type is None:
            return _property_not_found("type", payload)

        data_type = DataType.from_str(data_type)
        if isinstance(data_type, DtlError):
            return data_type

        value = payload.get("value")
        if value is None:
            return _property_not_found("value", payload)

        key = payload.get("key")
        if key is None:
            return _property_not_found("key", payload)

        return EnvVariable(data_type, value, key)


class PipelineDef:
    """
    Describes a stream of data flowing from a source to one or several destinations with transformations

        Source -+-> Pipeline 0
                |
                +-> Pipeline 1

               ...
    """

    def __init__(
        self,
        source: Union[DatastoreDef, Datastore],
        definitions: List[Definition],
        env: Optional[List[EnvVariable]] = None,
    ):
        """
        Creates a forks from a source flowing into different definitions

        :param source: source of the streaming data
        :param definitions: pipelines containing the transformations and targets for the data
        :param env: list of environment variables to be evaluated before beginning streaming the data
        """
        if isinstance(source, Datastore):
            source = source.definition

        self.source = source
        self.definitions = definitions
        self.env = env

    def __repr__(self):
        return f"PipelineDef(source= {self.source!r}, definitions= {self.definitions!r}, env= {self.env!r})"

    def __eq__(self, other: "PipelineDef"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def _as_payload(self):
        base = {
            "source": self.source._as_payload(),
            "pipelines": list(map(lambda s: s._as_payload(), self.definitions)),
        }
        if self.env is not None:
            base["env"] = list(map(lambda s: s._as_payload(), self.env))

        return base

    @staticmethod
    def _from_payload(payload: dict) -> Union[DtlError, "PipelineDef"]:
        """
        Builds a PipelineDef instance from a payload object

        :param payload:
        :return: if fails returns a string with the error message
        """
        source = payload.get("source")
        if source is None:
            return DtlError("stream needs a source of data")
        else:
            source = _datastore_def_from_payload(source)
            if isinstance(source, DtlError):
                return source

        pipelines = payload.get("pipelines")
        if pipelines is None:
            return DtlError("streams needs a 'pipelines' property")
        else:
            pipelines = _parse_list(Definition._from_payload)(pipelines)
            if isinstance(pipelines, DtlError):
                return pipelines

        env = payload.get("env")
        if env is not None:
            env = _parse_list(EnvVariable._from_payload)(env)
            if isinstance(env, DtlError):
                return env

        return PipelineDef(source, pipelines, env)

    @staticmethod
    def simple_builder(
        source_datastore: Datastore,
        transformation_list: List[Transformation],
        destination_datastore: Datastore,
        prepend_structure: bool = False,
    ) -> Union["PipelineDef", DtlError]:
        """
        Helper to create a simple PipelineDef from one source to one destination, optionally with 
        transformations
        :param source_datastore: the existing datastore to be used as pipeline source
        :param transformation_list: a list of transformations 
        :param destination_datastore: the existing datastore to be used as pipeline destination
        :param prepend_structure: constructs a leading Structure transformation based on source 
        fields
        """
        if prepend_structure == True:
            field_list = []
            if source_datastore.schema_paths:
                for path in source_datastore.schema_paths:
                    field_list.append(PathNodeDescription([path[-1]], [path[-1]]))
                transformations = [Structure(field_list)] + transformation_list
            else:
                return DtlError(
                    "Could not find fields within source "
                    + source_datastore.name
                    + " to build the leading Structure transformation"
                )
        else:
            transformations = transformation_list
        return PipelineDef(
            source=source_datastore,
            definitions=[Definition(transformations=transformations, forks=[], target=destination_datastore)],
        )


class Pipeline:
    def __init__(
        self, id: UUID, name: str, pipeline_def: PipelineDef, warnings: List[str] = [], is_resilient: bool = False,
    ):
        self.id = id
        self.name = name
        self.pipeline_def = pipeline_def
        self.warnings = warnings
        self.is_resilient = is_resilient

    def __eq__(self, other: "Pipeline"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Pipeline(id= {self.id}, name= {self.name!r}, pipeline_def= {self.pipeline_def!r}, warnings= {self.warnings!r}, is_resilient= {self.is_resilient})"

    def _as_payload(self):
        base = dict()
        base["id"] = str(self.id)
        base["name"] = self.name
        base["definition"] = self.pipeline_def._as_payload()
        base["warnings"] = self.warnings
        return base

    @staticmethod
    def _from_payload(payload: dict) -> Union[DtlError, "Pipeline"]:
        pipeline_id = map_option(payload.get("id"), _parse_uuid)
        if isinstance(pipeline_id, DtlError):
            return pipeline_id

        name = payload.get("name")
        if name is None:
            return DtlError("Missing parameter for Pipeline: 'name'")

        definition = payload.get("definition")
        if definition is None:
            return DtlError("Missing parameter for Pipeline: 'definition'")
        else:
            definition = PipelineDef._from_payload(definition)
            if isinstance(definition, DtlError):
                return definition

        resilient = payload.get("resilient")
        if name is None:
            resilient = False

        warnings = payload.get("warnings")
        return Pipeline(pipeline_id, name, definition, warnings, resilient)
