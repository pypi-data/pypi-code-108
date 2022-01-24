#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import trafaret as t

from datarobot._compat import String
from datarobot.models.api_object import APIObject

from ..utils import deprecation_warning, encode_utf8_if_py2


class BlueprintTaskDocument(APIObject):
    """ Document describing a task from a blueprint.

    Attributes
    ----------
    title : str
        Title of document.
    task : str
        Name of the task described in document.
    description : str
        Task description.
    parameters : list of dict(name, type, description)
        Parameters that task can receive in human-readable format.
    links : list of dict(name, url)
        External links used in document
    references : list of dict(name, url)
        References used in document. When no link available url equals None.
    """

    _converter = t.Dict(
        {
            t.Key("title"): String,
            t.Key("task"): String(allow_blank=True),
            t.Key("description"): String(allow_blank=True),
            t.Key("parameters"): t.List(
                t.Dict(
                    {t.Key("name"): String, t.Key("type"): String, t.Key("description"): String}
                ).ignore_extra("*")
            ),
            t.Key("links"): t.List(
                t.Dict({t.Key("name"): String, t.Key("url"): String}).ignore_extra("*")
            ),
            t.Key("references"): t.List(
                t.Dict(
                    {
                        t.Key("name"): String,
                        # from_api method drops None, so we need this when there is no url
                        t.Key("url", optional=True, default=None): String | t.Null,
                    }
                ).ignore_extra("*")
            ),
        }
    ).ignore_extra("*")

    def __init__(
        self, title=None, task=None, description=None, parameters=None, links=None, references=None
    ):
        self.title = title
        self.task = task
        self.description = description
        self.parameters = parameters
        self.links = links
        self.references = references

    def __repr__(self):
        return encode_utf8_if_py2(u"BlueprintTaskDocument({})".format(self.title))


class BlueprintChart(APIObject):
    """ A Blueprint chart that can be used to understand data flow in blueprint.

    Attributes
    ----------
    nodes : list of dict (id, label)
        Chart nodes, id unique in chart.
    edges : list of tuple (id1, id2)
        Directions of data flow between blueprint chart nodes.
    """

    _converter = t.Dict(
        {
            t.Key("nodes", optional=True): t.List(
                t.Dict({t.Key("id"): String, t.Key("label"): String})
            ),
            t.Key("edges", optional=True): t.List(t.Tuple(String, String)),
        }
    )

    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

    def __repr__(self):
        return encode_utf8_if_py2(
            u"BlueprintChart({} nodes, {} edges)".format(len(self.nodes), len(self.edges))
        )

    @classmethod
    def get(cls, project_id, blueprint_id):
        """ Retrieve a blueprint chart.

        Parameters
        ----------
        project_id : str
            The project's id.
        blueprint_id : str
            Id of blueprint to retrieve chart.

        Returns
        -------
        BlueprintChart
            The queried blueprint chart.
        """
        url = "projects/{}/blueprints/{}/blueprintChart/".format(project_id, blueprint_id)
        return cls.from_location(url)

    def to_graphviz(self):
        """ Get blueprint chart in graphviz DOT format.

        Returns
        -------
        unicode
            String representation of chart in graphviz DOT language.
        """
        digraph = u'digraph "Blueprint Chart" {'
        digraph += u"\ngraph [rankdir=LR]"
        for node in self.nodes:
            digraph += u'\n{id} [label="{label}"]'.format(id=node["id"], label=node["label"])
        for edge in self.edges:
            digraph += u"\n{id0} -> {id1}".format(id0=edge[0], id1=edge[1])
        digraph += u"\n}"
        return digraph


class ModelBlueprintChart(BlueprintChart):
    """ A Blueprint chart that can be used to understand data flow in model.
    Model blueprint chart represents reduced repository blueprint chart with
    only elements that used to build this particular model.

    Attributes
    ----------
    nodes : list of dict (id, label)
        Chart nodes, id unique in chart.
    edges : list of tuple (id1, id2)
        Directions of data flow between blueprint chart nodes.
    """

    def __repr__(self):
        return encode_utf8_if_py2(
            u"ModelBlueprintChart({} nodes, {} edges)".format(len(self.nodes), len(self.edges))
        )

    @classmethod
    def get(cls, project_id, model_id):
        """ Retrieve a model blueprint chart.

        Parameters
        ----------
        project_id : str
            The project's id.
        model_id : str
            Id of model to retrieve model blueprint chart.

        Returns
        -------
        ModelBlueprintChart
            The queried model blueprint chart.
        """
        url = "projects/{}/models/{}/blueprintChart/".format(project_id, model_id)
        return cls.from_location(url)


class Blueprint(APIObject):
    """ A Blueprint which can be used to fit models

    Attributes
    ----------
    id : str
        the id of the blueprint
    processes : list of str
        the processes used by the blueprint
    model_type : str
        the model produced by the blueprint
    project_id : str
        the project the blueprint belongs to
    blueprint_category : str
        (New in version v2.6) Describes the category of the blueprint and the kind of model it
        produces.
    recommended_featurelist_id: str or null
        (New in v2.18) The ID of the feature list recommended for this blueprint.
        If this field is not present, then there is no recommended feature list.
    supports_composable_ml : bool or None
        (New in version v2.26)
        whether this blueprint is supported in the Composable ML.
    """

    _converter = t.Dict(
        {
            t.Key("id", optional=True): String(),
            t.Key("processes", optional=True): t.List(String()),
            t.Key("model_type", optional=True): String(),
            t.Key("project_id", optional=True): String(),
            t.Key("blueprint_category", optional=True): String(),
            t.Key("monotonic_increasing_featurelist_id", optional=True): String(),
            t.Key("monotonic_decreasing_featurelist_id", optional=True): String(),
            t.Key("supports_monotonic_constraints", optional=True): t.Bool(),
            t.Key("recommended_featurelist_id", optional=True): String(),
            t.Key("supports_composable_ml", optional=True): t.Bool(),
        }
    ).allow_extra("*")

    def __init__(
        self,
        id=None,
        processes=None,
        model_type=None,
        project_id=None,
        blueprint_category=None,
        monotonic_increasing_featurelist_id=None,
        monotonic_decreasing_featurelist_id=None,
        supports_monotonic_constraints=None,
        recommended_featurelist_id=None,
        supports_composable_ml=None,
    ):
        if isinstance(id, dict):
            deprecation_warning(
                "Blueprint instantiation from a dict",
                deprecated_since_version="v2.3",
                will_remove_version="v3.0",
                message="Use Blueprint.from_data instead",
            )
            self.__init__(**id)
        else:
            self.id = id
            self.processes = processes
            self.model_type = model_type
            self.project_id = project_id
            self.blueprint_category = blueprint_category
            self.monotonic_increasing_featurelist_id = monotonic_increasing_featurelist_id
            self.monotonic_decreasing_featurelist_id = monotonic_decreasing_featurelist_id
            self.supports_monotonic_constraints = supports_monotonic_constraints
            self.recommended_featurelist_id = recommended_featurelist_id
            self.supports_composable_ml = supports_composable_ml

    def __repr__(self):
        return encode_utf8_if_py2(u"Blueprint({})".format(self.model_type))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    @classmethod
    def get(cls, project_id, blueprint_id):
        """ Retrieve a blueprint.

        Parameters
        ----------
        project_id : str
            The project's id.
        blueprint_id : str
            Id of blueprint to retrieve.

        Returns
        -------
        blueprint : Blueprint
            The queried blueprint.
        """
        url = "projects/{}/blueprints/{}/".format(project_id, blueprint_id)
        return cls.from_location(url)

    def get_chart(self):
        """ Retrieve a chart.

        Returns
        -------
        BlueprintChart
            The current blueprint chart.
        """
        return BlueprintChart.get(self.project_id, self.id)

    def get_documents(self):
        """ Get documentation for tasks used in the blueprint.

        Returns
        -------
        list of BlueprintTaskDocument
            All documents available for blueprint.
        """
        url = "projects/{}/blueprints/{}/blueprintDocs/".format(self.project_id, self.id)
        return [BlueprintTaskDocument.from_server_data(data) for data in self._server_data(url)]
