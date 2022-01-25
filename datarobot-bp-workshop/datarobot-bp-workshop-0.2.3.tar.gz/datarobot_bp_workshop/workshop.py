"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""
import re
import sys
from typing import Dict, List, Optional, Union

from datarobot import Project, CustomModelVersion
from datarobot.errors import ClientError

from datarobot_bp_workshop.exceptions import CannotInitializeWorkshopException
from .blueprint_graph import BlueprintGraph
from .datarobot_client import (
    UserBlueprint,
    CustomTask,
    UserBlueprintAvailableInput,
    UserBlueprintsInputType,
    UserBlueprintTaskDefinition,
    UserBlueprintTaskLookupEntry,
    ColnameAndType,
    ParamValuePair,
    UserBlueprintCatalogSearch,
)
from .factories import SimpleFactory, TaskFactory
from .settings import Settings
from .task import Task, TaskDict, Feature, FeatureSelection
from .utils import (
    Colors,
    PrettyList,
    TaskOutputMethod,
    colorize,
    HiddenList,
    override_user_agent,
)
from .workshop_interface import WorkshopInterface


class Workshop(WorkshopInterface):
    """The Workshop for building and modifying blueprints."""

    def __init__(
        self,
        auto_initialize=True,
        project_id=None,
        enforce_rate_limit=True,
        user_blueprint_id=None,
    ):
        Settings().check_if_should_upgrade()
        super(Workshop, self).__init__(
            project_id=project_id, enforce_rate_limit=enforce_rate_limit
        )
        self.project = None

        self._task_definitions_by_task_code: Dict[str, UserBlueprintTaskDefinition] = {}
        self._custom_tasks_by_id: Dict[str, UserBlueprintTaskDefinition] = {}
        self._custom_tasks_by_version_id: Dict[str, UserBlueprintTaskDefinition] = {}
        self._custom_task_definitions_by_task_code: Dict[
            str, List[UserBlueprintTaskDefinition]
        ] = {}

        if auto_initialize:
            self.initialize(user_blueprint_id=user_blueprint_id)

    def set_project(self, project_id: Optional[str] = None) -> WorkshopInterface:
        """
        Set the current context of the Workshop to be within a specific project.

        This will provide the ability to select specific columns from a project.
        """
        self._project_id = project_id
        self.initialize()
        return self

    def initialize(
        self, user_blueprint_id: Optional[str] = None, clean: bool = False
    ) -> WorkshopInterface:
        """
        Initialize the tasks in the Workshop. Useful when creating custom tasks mid-session
        or turning on new feature flags.

        Note: Creating a new, or replacing the current, instance of `Workshop`
        will achieve the same.
        """
        override_user_agent(UserBlueprint)

        try:

            if self._project_id:
                self.project = Project(id=self._project_id)

            if self._associated_user_blueprint_id:
                user_blueprint_id = self._associated_user_blueprint_id

            with self.auto_rate_limiter:
                self._available_tasks = UserBlueprint.get_available_tasks(
                    project_id=self._project_id, user_blueprint_id=user_blueprint_id
                )
            self._construct_task_lookups(clean=clean)
            self._task_factory = TaskFactory(self)

            self._dynamic_initialization()
        except Exception:
            error_msg = (
                "Failed to initialize: is the environment properly configured? "
                "See: https://blueprint-workshop.datarobot.com/configuration.html for more info."
            )
            print(error_msg, file=sys.stderr)
            raise CannotInitializeWorkshopException(error_msg)

        return self

    def refresh(self) -> WorkshopInterface:
        """
        Refresh the tasks in the Workshop. Useful when creating custom tasks mid-session
        or turning on new feature flags.

        Note: this is functionally identical to `initialize`.
        """
        return self.initialize()

    def get(
        self,
        user_blueprint_id: str,
        creator: Optional[str] = None,
        last_modifier_name: Optional[str] = None,
    ) -> BlueprintGraph:
        """
        Retrieve a user blueprint using an id.

        Parameters
        ----------
        user_blueprint_id: str
            The id of the User Blueprint
        creator: str, Optional
            The full name of the creator of the user blueprint, if available.
        last_modifier_name: str, Optional
            The full name of the last modifier of the user blueprint, if available.
        """
        with self.auto_rate_limiter:
            return self.blueprint_from_user_blueprint(
                UserBlueprint.get(user_blueprint_id=user_blueprint_id),
                creator=creator,
                last_modifier_name=last_modifier_name,
            )

    def search_blueprints(
        self,
        search: str = None,
        tag: Union[str, List[str]] = None,
        offset: int = 0,
        limit: int = 100,
        show: bool = False,
        as_list: bool = False,
    ) -> List[BlueprintGraph]:
        """ Search for blueprints by keyword """
        if isinstance(tag, list):
            tag = ",".join(tag)

        try:
            search_results = UserBlueprint.search_catalog(
                search=search,
                tag=tag,
                limit=limit,
                offset=offset,
                owner_user_id=None,
                owner_username=None,
                order_by="-created",
            )
            result = self._blueprints_from_search(search_results)

        except ClientError as e:
            if e.status_code != 403:
                raise e
            print(
                "Search is not yet released, falling back to list with client-side search."
            )
            result = self.list(offset=offset, limit=limit, search=search)

        # If the user requests to show the results as a list or visualized...
        consumed = []
        if show or as_list:
            # If we want to show, we need to collect the results too
            for bp in result:
                if show:
                    bp.show()
                consumed.append(bp)

            # Now we can pretty print it
            return PrettyList(consumed)

        return result

    def list(
        self, offset: int = 0, limit: int = 10, search: str = None
    ) -> List[BlueprintGraph]:
        """ Retrieve a list of your personal user blueprints. """
        with self.auto_rate_limiter:
            return self._blueprints_from_search(
                UserBlueprint.list(offset=offset, limit=limit), local_search=search
            )

    def _blueprints_from_search(
        self,
        results: List[Union[UserBlueprint, UserBlueprintCatalogSearch]],
        local_search: str = None,
    ) -> List[BlueprintGraph]:
        """ Retrieve each User Blueprint object and provide a generator for them. """
        for b in results:
            if not local_search or re.match(local_search, b.model_type):
                yield self.get(
                    b.user_blueprint_id,
                    creator=getattr(b, "creator", None),
                    last_modifier_name=getattr(b, "last_modifier_name", None),
                )

    def clone(
        self,
        blueprint_id: str,
        project_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> BlueprintGraph:
        """ Clone a blueprint from a project and save it as a user blueprint. """
        if project_id is None:
            project_id = self._project_id

        if project_id is None:
            raise ValueError(
                "Project Id must be provided if not set for the `Workshop`."
            )

        with self.auto_rate_limiter:
            return self.blueprint_from_user_blueprint(
                UserBlueprint.clone_project_blueprint(
                    blueprint_id=blueprint_id, project_id=project_id, model_type=name
                )
            )

    def delete(self, *user_blueprint_ids: str):
        """ Delete user blueprints using ids. """
        for user_blueprint_id in user_blueprint_ids:
            with self.auto_rate_limiter:
                UserBlueprint.delete(user_blueprint_id=user_blueprint_id)
        print(colorize("Blueprints deleted.", Colors.SUCCESS))

    def list_categories(
        self,
        categories: List[str] = None,
        show_tasks: bool = False,
        color: bool = True,
        margin: str = "",
    ) -> HiddenList:
        """ List the categories of tasks, and optionally the tasks themselves. """
        categories = (
            self._available_tasks.categories if categories is None else categories
        )
        seen_custom_task_id = set()
        for category in categories:

            name = category.name
            if color:
                name = colorize(name, Colors.BLUE)
            print("{}{}\n".format(margin, name))
            # This is a tree structure: show any subcategories first
            self.list_categories(
                color=color,
                margin="{}  ".format(margin),
                categories=category.subcategories or [],
                show_tasks=show_tasks,
            )

            if show_tasks:
                items = []
                for task_code in category.task_codes:
                    task = self._get_task(task_code, fallback_to_none=True)
                    # For example, a custom task...
                    if task is not None:
                        items += ["  - {} ({})".format(task.label, task_code)]
                    elif task_code in self._custom_task_definitions_by_task_code:
                        for definition in self._custom_task_definitions_by_task_code[
                            task_code
                        ]:
                            if definition.custom_task_id in seen_custom_task_id:
                                continue
                            seen_custom_task_id.add(definition.custom_task_id)
                            task = self._get_custom_task(
                                definition.custom_task_id, fallback_to_none=True
                            )
                            item = "  - {} ({})".format(
                                task.label,
                                "{}_{}".format(task_code, definition.custom_task_id),
                            )
                            items += [item]

                print("{}".format(margin) + "\n{}".format(margin).join(items))

        return HiddenList(categories)

    def search_tasks(
        self, term: str, ignore_case: bool = True, fuzzy: bool = True
    ) -> PrettyList:
        """
        Search for tasks which match a given term, optionally
        ignoring case (default) or performing a fuzzy search (default).
        """
        flags = 0
        if ignore_case:
            flags = re.IGNORECASE

        def match(task):
            code = (
                task.task_code
                if hasattr(task, "custom_task_id")
                else task.custom_task_id
            )
            return re.match(
                ".*".join([""] + term.split(" ") + [""] if fuzzy else term.split(" ")),
                " ".join(
                    [task.label, task.description, code, " ".join(task.categories)]
                ),
                flags,
            )

        built_in_tasks = [
            self._get_task(task.task_code, fallback_to_none=True)
            for task in self._task_definitions_by_task_code.values()
            if match(task)
        ]

        custom_tasks = [
            self._get_custom_task(task.custom_task_id)
            for task in self._custom_tasks_by_id.values()
            if match(task)
        ]

        tasks = sorted(built_in_tasks + custom_tasks, key=lambda t: str(t))
        return PrettyList([t for t in tasks if t is not None])

    def BlueprintGraph(
        self, final_task: Task, name: Optional[str] = None
    ) -> BlueprintGraph:
        """
        Provides a mechanism to declare a set of tasks in the form of a directed acyclic graph.

        Parameters
        ----------
        final_task: Task
            The task to use as the final task in a blueprint, which will be inspected
            to find all inputs.
        name: str
            Specify a name to use for the blueprint
        """
        return BlueprintGraph(workshop=self, final_task_or_tasks=final_task, name=name)

    def Task(
        self,
        task_code: str,
        output_method: Optional[str] = None,
        task_parameters: Union[List[ParamValuePair], dict] = None,
        output_method_parameters: Union[List[ParamValuePair], dict] = None,
        x_transformations: Union[List[ParamValuePair], dict] = None,
        y_transformations: Union[List[ParamValuePair], dict] = None,
        freeze: bool = False,
    ) -> Task:
        """
        Provides a mechanism to specify how to transform or provide predictions for input
        data.
        """
        task = Task(
            workshop=self,
            task_code=task_code,
            output_method=output_method,
            task_parameters=task_parameters,
            output_method_parameters=output_method_parameters,
            x_transformations=x_transformations,
            y_transformations=y_transformations,
            freeze=freeze,
        )
        return task

    def CustomTask(
        self,
        custom_task_id: str,
        output_method=None,
        task_parameters: List[ParamValuePair] = None,
        output_method_parameters: List[ParamValuePair] = None,
        x_transformations: List[ParamValuePair] = None,
        y_transformations: List[ParamValuePair] = None,
        freeze: bool = False,
        version: Optional[str] = None,
    ) -> Task:
        """ Create a custom task, using a `custom_task_id`, and optionally a version. """
        # Let the user pass CUSTOMR_<id> or <id>
        custom_task_id = self._parse_custom_id(custom_task_id)
        version = self._parse_custom_id(version)

        task = Task(
            workshop=self,
            task_code=self._custom_tasks_by_id[custom_task_id].task_code,
            output_method=output_method,
            task_parameters=task_parameters,
            output_method_parameters=output_method_parameters,
            x_transformations=x_transformations,
            y_transformations=y_transformations,
            freeze=freeze,
            custom_task_id=custom_task_id,
            version=version,
        )
        return task

    def Feature(self, feature_name: str) -> Feature:
        """
        Selects a feature from the project data.

        Ensure to call `set_project` or reinitialize the `Workshop` with a `project_id`,
        before attempting to select a feature.

        Parameters
        ----------
        feature_name: str
            The feature to select from the project data.
        """
        return Feature(self, feature_name)

    def FeatureSelection(
        self, *feature_names: Union[str, ColnameAndType], exclude=False
    ) -> FeatureSelection:
        """
        Selects a number of features from the project data of a specific data type.

        Ensure to call `set_project` or reinitialize the `Workshop` with a `project_id`,
        before attempting to select a feature.

        Parameters
        ----------
        feature_names: *Union[str, ColnameAndType]
            Include features which match the list provided.
        exclude: bool
            Whether to exclude the list of provided features, instead of include.
        """
        return FeatureSelection(self, feature_names, exclude=exclude)

    def deserialize_blueprint(self, bp_json: List[Dict]) -> BlueprintGraph:
        """ Create a BlueprintGraph from a list of dictionaries representing a BlueprintGraph. """
        return BlueprintGraph.deserialize(workshop=self, bp_json=bp_json)

    def deserialize_task(
        self, task_json: TaskDict, original_id: Optional[str] = None
    ) -> Task:
        """ Create a Task from a dictionary representing Task. """
        return Task.deserialize(
            workshop=self, task_dict=task_json, original_id=original_id,
        )

    def blueprint_from_user_blueprint(
        self,
        user_blueprint: UserBlueprint,
        creator: Optional[str] = None,
        last_modifier_name: Optional[str] = None,
    ) -> BlueprintGraph:
        """
        Create a BlueprintGraph from a UserBlueprint object

        Parameters
        ----------
        user_blueprint: UserBlueprint
        creator: str, Optional
            The full name of the creator of the user blueprint, if available.
        last_modifier_name: str, Optional
            The full name of the last modifier of the user blueprint, if available.

        Returns
        -------
        BlueprintGraph
        """
        return BlueprintGraph.from_user_blueprint(
            self, user_blueprint, creator=creator, last_modifier_name=last_modifier_name
        )

    def add_to_repository(
        self, project_id: str, user_blueprint_id: str
    ) -> Optional[str]:
        """Add a user blueprint to a project's repository

        Parameters
        ----------
        project_id: str
            the id of the project
        user_blueprint_id: str
            the id of the user blueprint

        Returns
        -------
        str or None
            blueprint_id if the user blueprint was successfully
            added to the repository. None otherwise.
        """
        with self.auto_rate_limiter:
            response = UserBlueprint.add_to_project(
                project_id=project_id, user_blueprint_ids=[user_blueprint_id]
            )
        added = response.added_to_menu
        if not added:
            return UserBlueprint.get(user_blueprint_id).blueprint_id
        return added[0].blueprint_id

    def link_to_project(self, user_blueprint_id: str, project_id: Optional[str]):
        """
        Allows linking or unlinking of a user blueprint from a project.
        Especially useful for unlinking a blueprint from a project you no longer have access to.

        When a user blueprint is linked to a project, it will be able to validate and otherwise use
        project specific tasks, such as feature selection.

        If a user blueprint is linked to a project, it is expected that it will only be used with
        that project, or clones of that project.

        If a user blueprint is not linked to a project, it is expected that it should be able to be
        project-agnostic, that is, used with any project which shares the same target type as the
        user blueprint.

        Parameters
        ----------
        user_blueprint_id: str
            Id of the User Blueprint
        project_id: str or None
            Id of the project to link to (or None).
            If None is passed, unlink the user blueprint from the project
        """
        user_blueprint = UserBlueprint.update(
            None,
            user_blueprint_id=user_blueprint_id,
            project_id=project_id,
            include_project_id_if_none=True,
        )
        return BlueprintGraph.from_user_blueprint(self, user_blueprint)

    def create_custom_task(
        self, environment_id: str, name: str, target_type: str, description: str = None
    ):
        """
        Create a custom task, which can then be updated using code via %%update_custom
        or via the DataRobot API.

        Parameters
        ----------
        environment_id: str
            ID of the environment to use to create the model
        name: str
            The name of the custom task
        target_type: str
            One of: ("Anomaly", "Binary", "Multiclass", "Regression", "Transform")
        description: Optional[str]
            An optional description of the model

        Returns
        -------
        CustomTask
        """
        custom_task = CustomTask.create(
            name=name, target_type=target_type, description=description
        )
        _ = CustomModelVersion.create_from_previous(
            custom_task.id, environment_id, is_major_update=False
        )
        self.initialize()
        return custom_task

    def get_custom_task(self, custom_task_id: str):
        """ Retrieve a custom task. """
        return CustomTask.get(custom_task_id)

    def _dynamic_initialization(self):
        """ Perform dynamic initialization of objects, classes, and methods. """
        stock_tasks: List[UserBlueprintTaskLookupEntry] = []
        custom_tasks: List[UserBlueprintTaskLookupEntry] = []
        columns_and_types: List[ColnameAndType] = []

        for task in self._available_tasks.tasks:
            task_definition: UserBlueprintTaskDefinition = task.task_definition
            if task_definition.custom_task_id is None:
                stock_tasks += [task]
            else:
                custom_tasks += [task]

            if not columns_and_types and task_definition.colnames_and_types:
                columns_and_types = task_definition.colnames_and_types

        self._colname_and_type_colname_lookup = {
            t.colname: t for t in columns_and_types
        }
        self._colname_and_type_hex_lookup = {t.hex: t for t in columns_and_types}

        # Tasks
        self.Tasks = self._build_tasks(stock_tasks)
        self.TaskCodes = self._build_tasks_codes(stock_tasks)

        # Custom Tasks
        self.CustomTasks = self._build_custom_tasks(custom_tasks)

        # Inputs
        with self.auto_rate_limiter:
            input_types: UserBlueprintAvailableInput = UserBlueprint.get_input_types()
        self._input_name_lookup = {i.type: i.name for i in input_types.input_types}
        self.TaskInputs = self._build_input_types(input_types.input_types)
        self.TaskOutputMethod = TaskOutputMethod

        # Feature Lookup
        self.Features = self._build_feature_data(columns_and_types)
        self.feature_lookup = {item.colname: item.hex for item in columns_and_types}

    def _parse_custom_id(self, custom_id: Optional[str]):
        if not custom_id or not isinstance(custom_id, str):
            return custom_id

        if "_" in custom_id:
            for possible in custom_id.split("_"):
                if possible in self._custom_tasks_by_id:
                    custom_id = possible
        return custom_id

    def _construct_task_lookups(self, clean=False):
        if clean:
            self._task_definitions_by_task_code = {}
            self._custom_tasks_by_id = {}
            self._custom_tasks_by_version_id = {}
            self._custom_task_definitions_by_task_code = {}

        for task in self._available_tasks.tasks:
            self._task_argument_lookup[task.task_code] = {
                a.key: a.argument for a in task.task_definition.arguments
            }
            custom_task_id = task.task_definition.custom_task_id
            if custom_task_id:
                self._custom_task_definitions_by_task_code.setdefault(
                    task.task_code, []
                ).append(task.task_definition)
                self._custom_tasks_by_id[custom_task_id] = task.task_definition
                for version in task.task_definition.custom_task_versions:
                    self._custom_tasks_by_version_id[version.id] = task.task_definition
            else:
                self._task_definitions_by_task_code[
                    task.task_code
                ] = task.task_definition
        return self._available_tasks

    def _get_task(self, task_code: str, fallback_to_none: bool = False) -> Task:
        if fallback_to_none and not hasattr(self.Tasks, task_code):
            return None
        return getattr(self.Tasks, task_code)

    def _get_custom_task_key(self, task: UserBlueprintTaskLookupEntry) -> str:
        return self._custom_task_key_string(task.task_definition.custom_task_id)

    def _get_custom_task(
        self, custom_task_id: str, fallback_to_none: bool = False
    ) -> Task:
        custom_task_string = self._custom_task_key_string(custom_task_id)
        if fallback_to_none and not hasattr(self.CustomTasks, custom_task_string):
            return None
        return getattr(self.CustomTasks, custom_task_string)

    def _build_tasks_codes(self, tasks: List[UserBlueprintTaskLookupEntry]):
        return SimpleFactory(tasks)(
            get_key=lambda i: i.task_code,
            get_value=lambda i: i.task_code,
            get_type=lambda i: "string",
            get_description=lambda i: i.task_definition.description,
            title="Unique Codes of the Available Tasks in the Workshop",
            class_name="TaskCodes",
        )

    def _build_tasks(self, tasks: List[UserBlueprintTaskLookupEntry]):
        return SimpleFactory(tasks)(
            get_key=lambda i: i.task_code,
            get_value=lambda i: self._task_factory(i.task_definition),
            get_type=lambda i: "Callable -> Task",
            get_description=lambda i: i.task_definition.description,
            title="Available Tasks in the Workshop",
            class_name="Tasks",
        )

    def _build_custom_tasks(self, tasks: List[UserBlueprintTaskLookupEntry]):
        return SimpleFactory(tasks)(
            get_key=self._get_custom_task_key,
            get_value=lambda i: self._task_factory(i.task_definition),
            get_type=lambda i: "Callable -> Task",
            get_description=lambda i: i.task_definition.description,
            title="Available Custom Tasks in the Workshop",
            class_name="CustomTasks",
        )

    def _build_input_types(self, input_types: List[UserBlueprintsInputType]):
        return SimpleFactory(input_types)(
            get_key=lambda i: i.type,
            get_value=lambda i: i.type,
            get_type=lambda i: "string",
            get_description=lambda i: i.name,
            title="Available Input Types in the Workshop",
            class_name="TaskInputs",
        )

    def _build_feature_data(self, columns_and_types: List[ColnameAndType]):
        return SimpleFactory(columns_and_types)(
            get_key=lambda i: i.colname,
            get_value=lambda i: self.Feature(i.colname),
            get_type=lambda i: "Feature",
            get_description=lambda i: "{} input data from the feature: '{}'".format(
                self._input_name_lookup[i.type], i.colname
            ),
            title="Specific Features Available in the Associated Project",
            class_name="Features",
        )
