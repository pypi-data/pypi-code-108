"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Dict, List, Optional, Union

import networkx as nx
from datarobot import Project
from .datarobot_client import (
    UserBlueprint,
    UserBlueprintTask,
    UserBlueprintHexColumnNameLookupEntry,
)
from .datarobot_client import UserBlueprintTaskDefinition as TaskDefinition
from .datarobot_client import VertexContextItem
from networkx import DiGraph

from .exceptions import (
    UnsavedBlueprintException,
    CycleException,
    NoProjectSpecifiedException,
)
from .friendly_repr import FriendlyRepr
from .task import Task, hex_or_identity
from .utils import (
    Colors,
    TaskInput,
    TaskOutputMethod,
    colorize,
    refresh_cached,
    represents_input_data,
    Roles,
    PrettyString,
)
from .visualize import Visualize, DisplayGraphviz
from .workshop_interface import WorkshopInterface


class BlueprintGraph(FriendlyRepr):
    """
    Provides a mechanism to declare a set of tasks in the form of a directed acyclic graph.

    Should not be used directly. Use `Workshop.Blueprint` instead.

    Parameters
    ----------
    workshop: WorkshopInterface
        Reference to the workshop
    final_task_or_tasks: Task or list(task)
        Either:
            - the task to use as the final task in a blueprint, which will be inspected
              to find all inputs.
            - the list of tasks to be used in the BlueprintGraph

    name: str or None
        The name to give the Blueprint Graph, which will be used to label the UserBlueprint
        if saved to DataRobot.
    """

    def __init__(
        self,
        workshop: WorkshopInterface,
        final_task_or_tasks: Union[Task, List[Task]],
        name: Optional[str] = None,
    ):
        self._workshop = workshop
        self._frozen: bool = False
        self._cached_graph: Optional[DiGraph] = None
        self._task_definitions: Dict[
            str, TaskDefinition
        ] = workshop._task_definitions_by_task_code
        self._custom_task_definitions: Dict[
            str, TaskDefinition
        ] = workshop._custom_tasks_by_id
        self._custom_task_version_definitions: Dict[
            str, TaskDefinition
        ] = workshop._custom_tasks_by_version_id
        self._input_name_lookup: Dict[str, str] = workshop._input_name_lookup
        self.user_blueprint_id: Optional[str] = None
        if isinstance(final_task_or_tasks, Task):
            self.tasks = list(set(self._tasks_from_task(final_task_or_tasks).values()))
        else:
            self.tasks = final_task_or_tasks

        if any([not isinstance(v, Task) for v in self.tasks]):
            raise TypeError("`tasks` must be a list of Task objects")

        self.name = name
        self.vertex_context: List[VertexContextItem] = []
        self._user_blueprint: Optional[UserBlueprint] = None
        self.project_id = None

        # Extra information that may be available
        self.creator: Optional[str] = None
        self.last_modifier_name: Optional[str] = None

    def __call__(self, final_task: Task, name=None):
        """ Assign a new final task for an existing BlueprintGraph. """
        self.tasks = list(set(self._tasks_from_task(final_task).values()))
        if name is not None:
            self.name = name

    def save(
        self,
        name=None,
        user_blueprint_id=None,
        save_as_new=False,
        validate_parameters=True,
        color=True,
    ) -> BlueprintGraph:
        """
        Save a BlueprintGraph as a User Blueprint in DataRobot.

        Returns
        -------
        BlueprintGraph
        """
        errors = []
        if validate_parameters:
            for task in self._traverse_dag():
                errors += task.validate_task_parameters(only_output_errors=True)

        if errors:
            failure = "Failed to save: parameter validation failed."
            if color:
                failure = colorize(failure, Colors.RED)
            print(failure)
            return self

        name = name or self.name
        user_blueprint_id = user_blueprint_id or self.user_blueprint_id
        # Update
        with self._workshop.auto_rate_limiter:
            if not save_as_new and user_blueprint_id is not None:
                user_blueprint = UserBlueprint.update(
                    self.serialize(),
                    user_blueprint_id=user_blueprint_id,
                    model_type=name,
                )
            else:
                # Insert
                user_blueprint = UserBlueprint.create(
                    self.serialize(),
                    model_type=name,
                    project_id=self._workshop.project_id,
                )

        return self._update_with_user_blueprint(
            user_blueprint, overwrite_blueprint_data=False
        )

    def delete(self, quiet=False):
        """
        Delete the blueprint from DataRobot

        Parameters
        ----------
        quiet: bool, Default=False
            If True, will not print a success message upon successful deletion.

        Raises
        ------
        ValueError
        """
        if not self.user_blueprint_id:
            raise ValueError(
                "Missing `user_blueprint_id`, has this BlueprintGraph been saved?"
            )
        with self._workshop.auto_rate_limiter:
            UserBlueprint.delete(user_blueprint_id=self.user_blueprint_id)
            if not quiet:
                print(colorize("Blueprint deleted.", Colors.SUCCESS))

    def link_to_project(
        self, project_id: Optional[str], user_blueprint_id: Optional[str] = None
    ):
        """
        Allows linking or unlinking of a user blueprint from a project.

        When a user blueprint is linked to a project, it will be able to validate and otherwise use
        project specific tasks, such as feature selection.

        If a user blueprint is linked to a project, it is expected that it will only be used with
        that project, or clones of that project.

        If a user blueprint is not linked to a project, it is expected that it should be able to be
        project-agnostic, that is, used with any project which shares the same target type as the
        user blueprint.

        Parameters
        ----------
        project_id: str or None
            If None is passed, unlink the user blueprint from the project
        user_blueprint_id: str or None
            If None is passed, fallback to `self.user_blueprint`, if also None, raise ValueError

        Raises
        ------
        ValueError

        """
        user_blueprint_id = user_blueprint_id or self.user_blueprint_id
        if not user_blueprint_id:
            raise ValueError(
                "Missing `user_blueprint_id`, has this BlueprintGraph been saved? "
                "If not, `user_blueprint_id` must be passed."
            )
        user_blueprint = UserBlueprint.update(
            None,
            user_blueprint_id=user_blueprint_id,
            project_id=project_id,
            include_project_id_if_none=True,
        )
        return self._update_with_user_blueprint(
            user_blueprint, overwrite_blueprint_data=False
        )

    def show(self, vertical=False, as_image=True) -> Optional[DisplayGraphviz]:
        """
        IPython specific drawing functionality.

        Wraps `as_image`.

        Parameters
        ----------
        vertical: bool (Default=False)
            Whether to display the graph top to bottom, rather than left to right
        as_image: bool (Default=True)
            If enabled, will render as a PNG, otherwise will rely on IPython to display
            the `Source` directly. Rendering as a PNG is preferred as it will auto-resize
            to the size of the rendering space provided, while `Source` will overflow.
        """
        return Visualize.show(
            self.as_graphviz_string(vertical=vertical), as_image=as_image
        )

    def as_graphviz_string(self, graph_name=None, vertical=False) -> str:
        """
        Used to render the graphviz form of the blueprint.

        Parameters
        ----------
        graph_name: string
            Name to display in the graph
        vertical: bool
            Whether to display the graph top to bottom, rather than left to right
        """
        if graph_name is None and self.name is not None:
            graph_name = self.name

        if self.creator is not None:
            graph_name += " \n(Created By: {})".format(self.creator)

        g = self._as_graph().copy()

        edges = []
        with self._frozen_tasks() as tasks:
            hash_mapping = {task.__hash__(): task.original_or_task_id for task in tasks}
            labels = {task.__hash__(): task.label for task in tasks}

        task_lookup = self._get_task_lookup()
        for task_id in g.nodes():
            if not isinstance(task_lookup.get(task_id), Task):
                _id = str(task_id)
                if represents_input_data(_id):
                    edges += [(Visualize.DATA_NODE, _id)]
                    labels[_id] = TaskInput.get_long_name(_id)
                else:
                    labels[_id] = _id

        labels[Visualize.DATA_NODE] = Visualize.DATA_NODE
        labels[Visualize.PREDICT_NODE] = Visualize.PREDICT_NODE
        for node in self._get_sink_task_ids(graph=g):
            g.add_edge(node, Visualize.PREDICT_NODE)

        g.add_node(Visualize.DATA_NODE)
        g.add_node(Visualize.PREDICT_NODE)

        for vw in g.edges():
            edge = []
            for e in vw:
                if isinstance(task_lookup.get(e), Task):
                    edge += [task_lookup.get(e).__hash__()]
                else:
                    edge += [e]
            edges += [edge]

        vertex_context_lookup = {
            item.task_id: item.messages for item in self.vertex_context
        }

        nodes_to_draw = [
            {"label": "{}".format(label), "id": node} for node, label in labels.items()
        ]

        return Visualize.to_graphviz_string(
            nodes_to_draw,
            edges,
            graph_name=graph_name,
            node_to_task_lookup=hash_mapping,
            vertex_context_lookup=vertex_context_lookup,
            vertical=vertical,
        )

    def to_source_code(
        self,
        to_stdout: bool = False,
        blueprint_ref: str = None,
        workshop_ref: str = None,
        pretty_repr: bool = True,
    ) -> str:
        """
        Convenience method for developers to help understand how to use the API.

        Construct the Blueprint using `deserialize`, and output the source code
        which can be used to create it using this new functional method.

        Parameters
        ----------
        to_stdout: bool (Default=False)
            Whether the source code of the blueprint should be printed to stdout.
        blueprint_ref: str (Default=None)
            A variable to store the new `BlueprintGraph` instead of generating one
        workshop_ref: str (Default=None)
            A variable to use to refer to an existing instance of `Workshop` instead
            of creating a new one.
        pretty_repr: bool (Default=True)
            Whether to pretty-print the result of execution. Useful for easy copy-paste
            in a notebook environment. Note: Does not change the content / actual value
            of what is returned, just how it is displayed (i.e. `repr` method).

        Returns
        -------
        str
            Executable source code to construct itself, in a functional manner.
            Useful as a tutorial, or large refactors.
        """
        variable_counter = {}
        variable_lookup = {}
        source_code_lines = []

        if self._user_blueprint:
            self._workshop.ensure_definitions_for_user_blueprint(self._user_blueprint)

        if workshop_ref is None:
            user_bp_project_id = (
                self._user_blueprint.project_id
                if self._user_blueprint is not None
                else None
            )
            project_id = user_bp_project_id or self._workshop.project_id
            workshop_args = dict()
            if self._user_blueprint:
                workshop_args[
                    "user_blueprint_id"
                ] = self._user_blueprint.user_blueprint_id

            if project_id is not None:
                workshop_args["project_id"] = project_id

            workshop_args_string = ", ".join(
                "{}={}".format(k, v.__repr__()) for k, v in workshop_args.items()
            )
            workshop_line = "w = Workshop({workshop_args_string})".format(
                workshop_args_string=workshop_args_string
            )
            source_code_lines += [workshop_line, ""]
            workshop_ref = "w"

        def build_variable(_task):
            """ Build an appropriate variable name based on the task. """
            # Task code by default
            variable_name = _task.task_code.lower()

            # If we're selecting features, get the name if just one, otherwise
            # refer to it as 'selected_features'
            if len(_task.selected_features) > 0:
                variable_name = (
                    _task.selected_features[0].colname.lower()
                    if len(_task.selected_features) == 1
                    else "feature_selection"
                )

            # Retrieve count
            counter = variable_counter.get(variable_name, 0)

            # We added a variable, so increment the counter for next time
            variable_counter[variable_name] = counter + 1

            # If we've already got a variable of this name, add '_<count>' (starting at '_1')
            if counter > 0:
                variable_name += "_{}".format(counter)

            # Save it in our lookup table
            variable_lookup[_task.task_id] = variable_name

            return variable_name

        task = None
        variable_task_pairs = [
            (variable_lookup.get(task.task_id, build_variable(task)), task)
            for task in self._traverse_dag()
        ]

        # Make the proper functional calls for each task
        for variable, task in variable_task_pairs:
            # Construct the inputs for each functional call
            input_variables = ", ".join(
                [
                    self._built_input_ref(workshop_ref, variable_lookup, name)
                    for name in task.input_names
                ]
            )
            # Write the actual functional task call
            if task.selected_features:
                source_code_lines.extend(self._handle_feature_selection(task, variable))
            else:
                template = "{variable} = w.{select_task}({method_args})"
                method_args = "{inputs}".format(inputs=input_variables)
                if not task.using_default_output_method:
                    method_args += ", output_method={output_method}".format(
                        output_method="{w}.{o}".format(
                            w=workshop_ref,
                            o=TaskOutputMethod.get_variable_name(task.output_method),
                        )
                    )

                select_task = "Tasks.{task_code}".format(task_code=task.task_code)

                # Handle custom tasks
                if task.custom_task_id and task.version:
                    select_task = "CustomTasks.{task_code}_{task_id}".format(
                        task_code=task.task_code, task_id=task.custom_task_id
                    )
                    method_args += ", version={version}".format(
                        version=task.version.__repr__()
                    )

                source_code_lines.append(
                    template.format(
                        select_task=select_task,
                        variable=variable,
                        method_args=method_args,
                    )
                )

                parameter_assignments = ", ".join(
                    [
                        "{}={}".format(k, "'{}'".format(v) if isinstance(v, str) else v)
                        for k, v in task._minified_task_parameters.items()
                        if not (task.custom_task_id and k == "version_id")
                    ]
                )
                if parameter_assignments:
                    source_code_lines.append(
                        "{variable}.set_task_parameters({parameters})".format(
                            variable=variable, parameters=parameter_assignments
                        )
                    )

            # New line for readability
            source_code_lines.append("")

        if task is None:
            raise ValueError("Blueprint empty. Nothing to do.")

        # Save as the provided reference, if one was provided
        blueprint_name = (
            blueprint_ref
            if blueprint_ref
            else "{variable}_blueprint".format(variable=variable_lookup[task.task_id])
        )
        # Declare the final blueprint
        source_code_lines.append(
            "{blueprint_name} = {w}.BlueprintGraph({variable}, name={name})".format(
                w=workshop_ref,
                blueprint_name=blueprint_name,
                variable=variable_lookup[task.task_id],
                name=self.name if self.name is None else self.name.__repr__(),
            )
        )

        result = "\n".join(source_code_lines)
        if to_stdout:
            print(result)

        return PrettyString(result) if pretty_repr else result

    def _built_input_ref(self, workshop_ref, variable_lookup, name):
        return (
            "{w}.TaskInputs.{i}".format(w=workshop_ref, i=name)
            if represents_input_data(name)
            else variable_lookup[name]
        )

    def _handle_feature_selection(self, task, variable):
        source_code_lines = []
        if len(task.selected_features) == 1:
            template = "{variable} = w.Features.{feature_name}"
            source_code_lines.append(
                template.format(
                    variable=variable, feature_name=task.selected_features[0].colname,
                )
            )
        else:
            by_type = {}
            for feature in task.selected_features:
                if feature.type in task.input_names:
                    by_type.setdefault(feature.type, []).append(feature.colname)

            for data_type, features in sorted(by_type.items(), key=lambda x: x[0]):
                template = (
                    "{variable} = w.FeatureSelection({features}, exclude={exclude})"
                )
                source_code_lines.append(
                    template.format(
                        variable=variable,
                        features=", ".join(["'{}'".format(f) for f in features]),
                        exclude=task.task_parameters.method == "exclude",
                    )
                )
        return source_code_lines

    def add_to_repository(
        self, project_id: Optional[str] = None, validate_parameters: bool = True,
    ) -> Optional[str]:
        """Add a user blueprint to a project's repository

        Parameters
        ----------
        project_id: str or None - required if Workshop not set to project
            the id of the project

        Returns
        -------
        str or None
            blueprint_id if the user blueprint was successfully
            added to the repository. None otherwise.
        validate_parameters: bool
            Ensure all parameters are valid (recommended)

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        project_id = project_id or self._workshop._project_id
        if project_id is None:
            raise NoProjectSpecifiedException(
                "The project id must be set in the Workshop or directly provided."
            )

        # If always save before adding to menu.
        self.save(validate_parameters=validate_parameters)

        with self._workshop.auto_rate_limiter:
            response = UserBlueprint.add_to_project(
                project_id=project_id, user_blueprint_ids=[self.user_blueprint_id]
            )
        added = response.added_to_menu
        if not added:
            if not self._user_blueprint or not self._user_blueprint.blueprint_id:
                print("Failure: Nothing was added to the project.")
                return None
            blueprint_id = self._user_blueprint.blueprint_id
        else:
            blueprint_id = added[0].blueprint_id
        return blueprint_id

    def train(
        self,
        project_id: Optional[str] = None,
        validate_parameters: bool = True,
        *args,
        **kwargs
    ) -> BlueprintGraph:
        """
        Train it.

        See datarobot.Project.train or datarobot.Project.train_datetime
        for parameters.

        Parameters
        ----------
        project_id: str or None - required if Workshop not set to project
            the id of the project to train the blueprint on
        validate_parameters: bool
            Ensure all parameters are valid (recommended)

        Returns
        -------
        BlueprintGraph
            Returns self
        """
        project_id = project_id or self._workshop._project_id
        if project_id is None:
            raise NoProjectSpecifiedException(
                "The project id must be set in the Workshop or directly provided."
            )

        project = Project(project_id)
        bp = self.add_to_repository(project_id, validate_parameters=validate_parameters)
        if project.is_datetime_partitioned:
            project.train_datetime(bp, *args, **kwargs)
        else:
            project._train(bp, *args, **kwargs)
        print("Training requested! Blueprint Id: {}".format(bp))
        return self

    @classmethod
    def from_user_blueprint_tasks(
        cls,
        workshop: WorkshopInterface,
        user_blueprint_tasks: List[UserBlueprintTask],
        hex_column_name_lookup: Optional[
            List[UserBlueprintHexColumnNameLookupEntry]
        ] = None,
    ) -> BlueprintGraph:
        """ Generate a BlueprintGraph from a list of UserBlueprintTask """
        task_mapping = {
            user_blueprint_task.task_id: Task.from_user_blueprint_task(
                workshop=workshop,
                task_data=user_blueprint_task.task_data,
                original_id=user_blueprint_task.task_id,
                hex_column_name_lookup=hex_column_name_lookup,
            )
            for user_blueprint_task in user_blueprint_tasks
        }
        # Convert all inputs referencing ids into true references
        for task in task_mapping.values():
            task._map_inputs(task_mapping)

        return BlueprintGraph(
            workshop=workshop, final_task_or_tasks=list(task_mapping.values()),
        )

    @classmethod
    def from_user_blueprint(
        cls,
        workshop: WorkshopInterface,
        user_blueprint: UserBlueprint,
        creator: Optional[str] = None,
        last_modifier_name: Optional[str] = None,
    ) -> BlueprintGraph:
        """ Create a BlueprintGraph from a UserBlueprint instance."""

        workshop.ensure_definitions_for_user_blueprint(user_blueprint)

        bp = cls.from_user_blueprint_tasks(
            workshop=workshop,
            user_blueprint_tasks=user_blueprint.blueprint,
            hex_column_name_lookup=user_blueprint.hex_column_name_lookup,
        )
        bp.name = user_blueprint.model_type
        bp.user_blueprint_id = user_blueprint.user_blueprint_id
        bp.project_id = user_blueprint.project_id
        bp.vertex_context = user_blueprint.vertex_context or []
        bp._user_blueprint = user_blueprint
        bp.creator = creator
        bp.last_modifier_name = last_modifier_name
        return bp

    @classmethod
    def deserialize(
        cls, workshop: WorkshopInterface, bp_json: List[Dict]
    ) -> BlueprintGraph:
        """ Generate a BlueprintGraph from the JSON representation. """
        return BlueprintGraph.from_user_blueprint_tasks(
            workshop=workshop,
            user_blueprint_tasks=[
                UserBlueprintTask(**task_id_data_pair) for task_id_data_pair in bp_json
            ],
        )

    def serialize(self, minify=True) -> List[Dict]:
        """"
        Used to view Blueprint in the familiar blueprint dictionary format.

        Returns
        -------
        list(dict)
            A list of dictionaries representing the tasks in the blueprint.
        """
        try:
            graph = self._as_graph(only_include_tasks=True)
            final_task: Task = self._get_task_lookup()[self._sorted_task_ids(graph)[-1]]
            self.tasks = list(set(self._tasks_from_task(final_task).values()))
            graph = self._as_graph(only_include_tasks=True)

            return [
                {
                    "task_id": self._get_task_lookup()[task_id].original_or_task_id,
                    "task_data": self._get_task_lookup()[task_id].serialize(
                        minify=minify
                    ),
                }
                for task_id in self._sorted_task_ids(graph)
                if task_id in self._get_task_lookup()
            ]
        except CycleException:
            raise ValueError("Blueprint is not a directed acyclic graph.")

    def share(self, usernames: Union[str, List[str]], role: str = Roles.CONSUMER):
        """ Share a User Blueprint with a user or list of other users by username. """
        if self.user_blueprint_id is None:
            raise UnsavedBlueprintException(
                "Ensure the blueprint has been saved before sharing."
            )
        return self._workshop.share(
            self.user_blueprint_id, usernames=usernames, role=role
        )

    def share_with_group(
        self, group_ids: Union[str, List[str]], role: str = Roles.CONSUMER
    ):
        """ Share a User Blueprint with a group or list of groups by id. """
        return self._workshop.share_with_group(
            user_blueprint_id=self.user_blueprint_id, group_ids=group_ids, role=role,
        )

    def share_with_org(
        self, org_ids: Union[str, List[str]], role: str = Roles.CONSUMER
    ):
        """ Share a User Blueprint with a group or list of organizations by id. """
        return self._workshop.share_with_org(
            user_blueprint_id=self.user_blueprint_id, org_ids=org_ids, role=role,
        )

    # Methods below this point are not meant to be called directly by users.

    def __friendly_repr__(self) -> str:
        lookup = self._get_task_lookup()
        unique_task_names = set([])
        inputs = []
        task_names = []

        for task in self._traverse_dag():
            if task.label not in unique_task_names:
                task_names += [task.label]
            unique_task_names.add(task.label)
            for input_name in task.input_names:
                if input_name not in lookup:
                    input_label = self._input_name_lookup[input_name]
                    if input_label not in inputs:
                        inputs += [input_label]

        lines = [
            "Name: {}".format(
                "(Untitled)" if self.name is None else self.name.__repr__()
            ),
            "",
            "Input Data: " + " | ".join(inputs),
            "Tasks: " + " | ".join(task_names),
        ]

        if self.creator is not None:
            lines += ["Created By: {}".format(self.creator)]

        if self.last_modifier_name is not None:
            lines += ["Last Modified By: {}".format(self.last_modifier_name)]

        if self.project_id is not None:
            lines += ["Linked Project Id: {}".format(self.project_id)]

        return "\n".join(lines)

    def __eq__(self, other):
        if not isinstance(other, BlueprintGraph):
            return False
        return self.serialize() == other.serialize()

    @classmethod
    def _tasks_from_task(
        cls, task: Task, lookup: Optional[Dict[str, Task]] = None, freeze: bool = False
    ) -> Dict[str, Task]:
        """
        Build a list of tasks by finding and recursively
        finding all inputs to tasks.
        """
        lookup = lookup or {}

        task._freeze()

        lookup.update({task.task_id: task})
        inputs = [i for i in task.inputs if isinstance(i, Task)]
        for task in inputs:
            task._freeze()
            if isinstance(task, Task):
                lookup[task.task_id] = task
                # Is there an input not already stored in lookup?
                if any(
                    [
                        v.task_id not in lookup
                        for v in task.inputs
                        if isinstance(v, Task)
                    ]
                ):
                    # If so, make sure we pass the current lookup, and descend into
                    # the inputs which have not already been added.
                    # This can always be frozen as we will unfreeze at the outer-most call
                    lookup.update(cls._tasks_from_task(task, lookup, freeze=True))

        if not freeze:
            # Unfreeze all tasks to allow for modification
            for task in lookup.values():
                task._unfreeze()

        return lookup

    def _freeze(self):
        """
        Some fields such as the deterministic id of tasks and deterministic topological ordering
        require computation to find. If we can guarantee the tasks will not change, we can save
        significant computation, by using cached fields instead of recalculating them.
        """
        if self._frozen:
            return
        for task in self.tasks:
            if isinstance(task, Task):
                task._freeze()
        self._refresh_cached()
        self._frozen = True

    def _unfreeze(self):
        """
        Ready blueprint to be modified again.
        """
        for task in self.tasks:
            if isinstance(task, Task):
                task._unfreeze()
        self._frozen = False

    def _refresh_cached(self, attr_to_exclude=None):
        """Refresh cached attributes (set to None) of BlueprintGraph.

        Parameters
        ----------
        attr_to_exclude:
            A list of attributes which are not to be refreshed.
        """

        attr_to_refresh = ["_cached_graph"]
        refresh_cached(self, attr_to_refresh, attr_to_exclude)

    @contextmanager
    def _frozen_tasks(self, dag_order=False):
        """
        Freeze blueprint and iterate through the tasks.

        Parameters
        ----------
        dag_order: boolean
            Whether the tasks should be yielded in topologically sorted order.

        Yields
        ------
        list(Task)
        """
        frozen_before = self._frozen
        self._freeze()
        if dag_order:
            yield self._traverse_dag()
        else:
            yield self.tasks
        if not frozen_before:
            self._unfreeze()

    def _get_task_lookup(self) -> Dict[str, Task]:
        """
        Retrieve a lookup from hex representation to Task objects,
        or input data keys (e.g. 'NUM') to their identity.
        """
        with self._frozen_tasks() as tasks:
            return {hex_or_identity(v): v for v in tasks}

    def _is_dag(self, graph=None):
        """
        Determine whether the Blueprint is a DAG.

        Returns
        -------
        boolean
        """
        try:
            if graph is None:
                graph = self._as_graph(only_include_tasks=True)
            return nx.is_directed_acyclic_graph(graph)
        except CycleException:
            return False

    def _traverse_dag(self):
        """
        Simple, convenient, way to iterate through DAG in a topologically sorted manner.

        Note: Don't use this if modifying tasks as their hash will change during iteration
        and lookups will fail.

        Yields
        ------
        Task
        """
        not_dag = "Blueprint is not a directed acyclic graph, and cannot be reliably iterated."
        try:
            graph = self._as_graph(only_include_tasks=True)
            if not self._is_dag(graph):
                raise ValueError(not_dag)
            for task_id in self._sorted_task_ids(graph):
                yield self._get_task_lookup()[task_id]
        except CycleException:
            raise ValueError(not_dag)

    def _sorted_task_ids(self, graph=None):
        """
        Retrieve task ids in topologically sorted order.

        Estimators are preferred to be as late as possible, and if there are multiple possible
        topological sorts, this prioritizes sorts with estimators / models as late as possible.

        This is due to an expectation in DataRobot that models should follow tasks.

        Parameters
        ----------
        graph: DiGraph or None
            A graph to use instead of building it from scratch.

        Returns
        -------
        list(str)
        """
        # Ensure topological sort is deterministic.
        # If there is a tie, prefer estimators / models as late as possible,
        # otherwise sort lexicographically, and pick the first (arbitrary but deterministic)

        def get_sorting_name(task_hex):
            """
            0 comes before 1, so if it is an estimator, it will be chosen last to break a tie
            """
            is_estimator = self._get_task_lookup()[task_hex].is_estimator
            return "{}-{}".format(str(int(is_estimator)), task_hex)

        if graph is None:
            graph = self._as_graph(only_include_tasks=True)
        return list(nx.lexicographical_topological_sort(graph, key=get_sorting_name))

    def _as_graph(self, only_include_tasks=False):
        """
        Used to interpret the blueprint in the form of network

        Parameters
        ----------
        only_include_tasks: boolean. (Default=False)
            If false, will also add input data nodes, though they are not necessary for topological
            sorting (as they are always degree 0), and hurts performance.

        Returns
        -------
        DiGraph
            The Blueprint stored as a Directed Graph.
        """
        if self._frozen and self._cached_graph:
            return self._cached_graph

        g = nx.DiGraph()
        node_set = set()
        edge_set = set()

        def get_inputs(task):
            if only_include_tasks:
                return [
                    name for name in task.input_names if name in self._get_task_lookup()
                ]
            return task.input_names

        with self._frozen_tasks() as tasks:
            for task in tasks:
                inputs = get_inputs(task)
                task_hex = task.task_id
                node_set.add(task_hex)
                node_set |= {j for j in inputs}
                edge_set |= {(j, task_hex) for j in inputs}

        g.add_nodes_from(node_set)
        g.add_edges_from(edge_set)

        self._cached_graph = g
        return g

    def _update_with_user_blueprint(
        self, user_blueprint: UserBlueprint, overwrite_blueprint_data: bool = True
    ):
        """
        Parameters
        ----------
        user_blueprint: UserBlueprint

        overwrite_blueprint_data: bool

        Returns
        -------
        BlueprintGraph
            Returns self
        """
        self.name = user_blueprint.model_type
        self.project_id = user_blueprint.project_id
        self.user_blueprint_id = user_blueprint.user_blueprint_id
        self.vertex_context = user_blueprint.vertex_context or []
        self._user_blueprint = user_blueprint
        if overwrite_blueprint_data:
            temp_bp = self.from_user_blueprint_tasks(
                workshop=self._workshop,
                user_blueprint_tasks=user_blueprint.blueprint,
                hex_column_name_lookup=user_blueprint.hex_column_name_lookup,
            )
            self.tasks = temp_bp.tasks
        return self

    def _get_sink_task_ids(self, graph=None):
        """
        Retrieve all Sink task ids (no output edges).

        This can be useful for a number of applications including pruning, and
        finding the "predict" node.

        Parameters
        ----------
        graph: DiGraph (Default=None), if none provided, will create one.

        Returns
        -------
        list(str)
            A list of the nodes with no outgoing edges.
        """
        if graph is None:
            graph = self._as_graph().copy()
        return [node for node in graph.nodes() if len(graph.out_edges(node)) == 0]
