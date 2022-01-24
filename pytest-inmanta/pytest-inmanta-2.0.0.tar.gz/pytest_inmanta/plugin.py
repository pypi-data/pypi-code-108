"""
    Copyright 2021 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""
import importlib
import inspect
import json
import logging
import math
import os
import re
import shutil
import sys
import tempfile
import typing
import warnings
from collections import defaultdict
from distutils import dir_util
from itertools import chain
from pathlib import Path
from textwrap import dedent
from types import FunctionType, ModuleType

import pydantic
import pytest
import yaml
from pytest import CaptureFixture
from tornado import ioloop

import inmanta.ast
from inmanta import compiler, config, const, module, plugins, protocol
from inmanta.agent import cache, handler
from inmanta.agent import io as agent_io
from inmanta.agent.handler import HandlerContext, ResourceHandler
from inmanta.data import LogLine
from inmanta.data.model import AttributeStateChange, ResourceIdStr
from inmanta.execute.proxy import DynamicProxy
from inmanta.export import Exporter, ResourceDict, cfg_env
from inmanta.protocol import json_encode
from inmanta.resources import Resource

if typing.TYPE_CHECKING:
    from inmanta.agent.io.local import IOBase

from .handler import DATA

CURDIR = os.getcwd()
LOGGER = logging.getLogger()


option_to_env = {
    "inm_venv": "INMANTA_TEST_ENV",
    "inm_module_repo": "INMANTA_MODULE_REPO",
    "inm_install_mode": "INMANTA_INSTALL_MODE",
    "inm_no_load_plugins": "INMANTA_TEST_NO_LOAD_PLUGINS",
}


def pytest_addoption(parser) -> None:
    group = parser.getgroup("inmanta", "inmanta module testing plugin")
    group.addoption(
        "--venv",
        dest="inm_venv",
        help="folder in which to place the virtual env for tests (will be shared by all tests), overrides INMANTA_TEST_ENV. "
        "This options depends on symlink support. This does not work on all windows versions. "
        "On windows 10 you need to run pytest in an admin shell. "
        "Using a fixed virtual environment can speed up running the tests.",
    )
    group.addoption(
        "--use-module-in-place",
        action="store_true",
        help="tell pytest-inmanta to run with the module in place, useful for debugging. "
        "Makes inmanta add the parent directory of your module directory to it's directory path, instead of copying your "
        "module to a temporary libs directory. "
        "It allows testing the current module against specific versions of dependent modules. "
        "Using this option can speed up the tests, because the module dependencies are not downloaded multiple times.",
    )
    group.addoption(
        "--module_repo",
        dest="inm_module_repo",
        action="append",
        help="location to download modules from, overrides INMANTA_MODULE_REPO."
        "Can be specified multiple times to add multiple locations",
    )
    group.addoption(
        "--install_mode",
        dest="inm_install_mode",
        help="Install mode for modules downloaded during this test, overrides INMANTA_INSTALL_MODE.",
        choices=module.INSTALL_OPTS,
    )
    group.addoption(
        "--no_load_plugins",
        action="store_true",
        dest="inm_no_load_plugins",
        help="Don't load plugins in the Project class. Overrides INMANTA_TEST_NO_LOAD_PLUGINS."
        "The value of INMANTA_TEST_NO_LOAD_PLUGINS environment variable has to be a non-empty string to not load plugins."
        "When not using this option during the testing of plugins with the `project.get_plugin_function` method, "
        "it's possible that the module's `plugin/__init__.py` is loaded multiple times, "
        "which can cause issues when it has side effects, as they are executed multiple times as well.",
    )


def get_opt_or_env_or(config, key: str, default: str) -> str:
    if config.getoption(key):
        return config.getoption(key)
    if option_to_env[key] in os.environ:
        return os.environ[option_to_env[key]]
    return default


def get_module() -> typing.Tuple[module.Module, str]:
    """
    Returns the module instance for the module being tested, as well as the path to its root.
    For v2 modules, the returned path is the same as the module's path attribute.
    """

    def find_module(path: str) -> typing.Optional[typing.Tuple[module.Module, str]]:
        mod: typing.Optional[module.Module]
        if hasattr(module.Module, "from_path"):
            mod = module.Module.from_path(path)
        else:
            # older versions of inmanta-core
            try:
                mod = module.Module(project=None, path=path)
            except module.InvalidModuleException:
                mod = None
        if mod is not None:
            return mod, path
        parent: str = os.path.dirname(path)
        return find_module(parent) if parent != path else None

    mod_info: typing.Optional[typing.Tuple[module.Module, str]] = find_module(CURDIR)
    if mod_info is None:
        raise Exception(
            "Module test case have to be saved in the module they are intended for. "
            "%s not part of module path" % CURDIR
        )
    return mod_info


@pytest.fixture()
def inmanta_plugins(
    project: "Project",
) -> typing.Iterator["InmantaPluginsImportLoader"]:
    importer: InmantaPluginsImporter = InmantaPluginsImporter(project)
    yield importer.loader


@pytest.fixture()
def project(
    project_shared: "Project", capsys: CaptureFixture
) -> typing.Iterator["Project"]:
    DATA.clear()
    project_shared.clean()
    project_shared.init(capsys)
    yield project_shared
    project_shared.clean()


@pytest.fixture()
def project_no_plugins(
    project_shared_no_plugins, capsys: CaptureFixture
) -> typing.Iterator["Project"]:
    warnings.warn(
        DeprecationWarning(
            "The project_no_plugins fixture is deprecated in favor of the %s environment variable."
            % option_to_env["inm_no_load_plugins"]
        )
    )
    DATA.clear()
    project_shared_no_plugins.clean()
    project_shared_no_plugins.init(capsys)
    yield project_shared_no_plugins
    project_shared_no_plugins.clean()


def get_module_data(filename: str) -> str:
    """
    Get the given filename from the module directory in the source tree
    """
    current_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_path, "module", filename), "r") as fd:
        return fd.read()


@pytest.fixture(scope="session")
def project_shared(
    project_factory: typing.Callable[[typing.Dict[str, typing.Any]], "Project"]
) -> "Project":
    """
    A test fixture that creates a new inmanta project with the current module in. The returned object can be used
    to add files to the unittest module, compile a model and access the results, stdout and stderr.
    """
    yield project_factory()


# Temporary workaround for plugins loading multiple times (inmanta/pytest-inmanta#49)
@pytest.fixture(scope="session")
def project_shared_no_plugins(
    project_factory: typing.Callable[[typing.Dict[str, typing.Any]], "Project"]
) -> "Project":
    """
    A test fixture that creates a new inmanta project with the current module in. The returned object can be used
    to add files to the unittest module, compile a model and access the results, stdout and stderr.
    This project is initialized with load_plugins == False.
    """
    yield project_factory(load_plugins=False)


def get_project_repos(repo_options: typing.Sequence[str]) -> typing.Sequence[object]:
    """
    Returns the list of repos for the project as a serializable object. For recent versions of core, includes repo types.

    :param repo_options: The desired repos as plain strings in the form "[<type>:]<url>". If type is omitted, defaults to git
        for backwards compatibility. Explicitly passing type is only supported for inmanta versions that accept type in the
        project metadata.
    """

    def parse_repo(repo_str: str) -> object:
        parts: typing.Sequence[str] = repo_str.split(":", maxsplit=1)
        if not hasattr(module, "ModuleRepoType"):
            # compatibility mode
            return repo_str
        else:
            repo_info: module.ModuleRepoInfo
            try:
                repo_info = module.ModuleRepoInfo(url=parts[1], type=parts[0])
            # there might be only one part or part might be just "https"
            except (IndexError, pydantic.ValidationError):
                repo_info = module.ModuleRepoInfo(url=repo_str)
            return json.loads(repo_info.json())

    return [parse_repo(repo) for repo in repo_options]


@pytest.fixture(scope="session")
def project_factory(request: pytest.FixtureRequest) -> typing.Callable[[], "Project"]:
    """
    A factory that constructs a single Project.
    """
    _sys_path = sys.path
    test_project_dir = tempfile.mkdtemp()
    os.mkdir(os.path.join(test_project_dir, "libs"))

    repo_options = get_opt_or_env_or(
        request.config, "inm_module_repo", "https://github.com/inmanta/"
    )
    repos: typing.Sequence[object] = get_project_repos(
        chain.from_iterable(
            repo.split(" ")
            for repo in (
                repo_options if isinstance(repo_options, list) else [repo_options]
            )
        )
    )

    install_mode = get_opt_or_env_or(request.config, "inm_install_mode", "release")

    modulepath = ["libs"]
    in_place = request.config.getoption("--use-module-in-place")
    if in_place:
        modulepath.append(str(Path(CURDIR).parent))

    env_override = get_opt_or_env_or(request.config, "inm_venv", None)
    env_dir = os.path.join(test_project_dir, ".env")
    if env_override and not os.path.isdir(env_override):
        raise Exception(f"Specified venv {env_override} does not exist")
    if env_override is not None:
        try:
            os.symlink(os.path.abspath(env_override), env_dir)
        except OSError:
            LOGGER.exception(
                "Unable to use shared env (symlink creation from %s to %s failed).",
                env_override,
                os.path.join(test_project_dir, ".env"),
            )
            raise

    with open(os.path.join(test_project_dir, "project.yml"), "w+") as fd:
        metadata: typing.Mapping[str, object] = {
            "name": "testcase",
            "description": "Project for testcase",
            "repo": repos,
            "modulepath": modulepath,
            "downloadpath": "libs",
            "install_mode": install_mode,
        }
        yaml.dump(metadata, fd)

    ensure_current_module_install(os.path.join(test_project_dir, "libs"), in_place)

    def create_project(**kwargs: object):
        extended_kwargs: typing.Dict[str, object] = {
            "load_plugins": not get_opt_or_env_or(
                request.config, "inm_no_load_plugins", False
            ),
            "env_path": env_dir,
            **kwargs,
        }
        test_project = Project(test_project_dir, **extended_kwargs)

        # create the unittest module
        test_project.create_module(
            "unittest",
            initcf=get_module_data("init.cf"),
            initpy=get_module_data("init.py"),
        )

        return test_project

    yield create_project

    try:
        shutil.rmtree(test_project_dir)
    except PermissionError:
        LOGGER.warning(
            "Cannot cleanup test project %s. This can be caused because we try to remove a virtual environment, "
            "loaded by this python process. Try to use a shared environment with --venv",
            test_project_dir,
        )

    sys.path = _sys_path


def ensure_current_module_install(v1_modules_dir: str, in_place: bool = False) -> None:
    """
    Ensures that the current module is installed: if it is a v1 module, adds it to the modules path, otherwise verifies that it
    has been installed.
    """
    # copy the current module in
    mod: module.Module
    path: str
    mod, path = get_module()
    if not hasattr(module, "ModuleV2") or isinstance(mod, module.ModuleV1):
        if not in_place:
            dir_util.copy_tree(path, os.path.join(v1_modules_dir, mod.name))
    else:
        installed: typing.Optional[module.ModuleV2] = module.ModuleV2Source(
            urls=[]
        ).get_installed_module(None, mod.name)
        if installed is None:
            raise Exception(
                "The module being tested is not installed in the current Python environment. Please install it with"
                " `inmanta module install -e .` before running the tests."
            )
        if not installed.is_editable():
            LOGGER.warning(
                "The module being tested is not installed in editable mode. As a result the tests will not pick up any changes"
                " to the local source files. To install it in editable mode, run `inmanta module install -e .`."
            )


class MockProcess(object):
    """
    A mock agentprocess
    """

    def __init__(self):
        self._io_loop = ioloop.IOLoop.current()


class MockAgent(object):
    """
    A mock agent for unit testing
    """

    def __init__(self, uri):
        self.uri = uri
        self.process = MockProcess()
        self._env_id = cfg_env.get()


class InmantaPluginsImportLoader:
    """
    Makes inmanta_plugins packages (Python source for inmanta modules) available dynamically so that tests can use them
    safely without having to refresh imports when the compiler is reset.
    """

    def __init__(self, importer: "InmantaPluginsImporter") -> None:
        self._importer: InmantaPluginsImporter = importer

    def __getattr__(self, name: str):
        submodules: typing.Optional[
            typing.Dict[str, ModuleType]
        ] = self._importer.get_submodules(name)
        fq_mod_name: str = f"inmanta_plugins.{name}"
        if submodules is None or fq_mod_name not in submodules:
            raise AttributeError("No inmanta module named %s" % name)
        return submodules[fq_mod_name]


class InmantaPluginsImporter:
    def __init__(self, project: "Project") -> None:
        self.project: Project = project
        self.loader: InmantaPluginsImportLoader = InmantaPluginsImportLoader(self)

    def get_submodules(
        self, module_name: str
    ) -> typing.Optional[typing.Dict[str, ModuleType]]:
        inmanta_project: module.Project = module.Project.get()
        if not inmanta_project.loaded:
            raise Exception(
                "Dynamically importing from inmanta_plugins requires a loaded inmanta.module.Project. Make sure to use the"
                " project fixture."
            )
        modules: typing.Dict[str, module.Module] = inmanta_project.get_modules()
        if module_name not in modules:
            return None
        result = {}
        importlib.invalidate_caches()
        for _, fq_submod_name in modules[module_name].get_plugin_files():
            result[str(fq_submod_name)] = importlib.import_module(str(fq_submod_name))
        return result


class ProjectLoader:
    """
    Singleton providing methods for managing project loading and associated side effects. Since these operations have global
    side effects, managing them calls for a centralized manager rather than managing them on the Project instance level.

    This class manages the setting and loading of a project, as well as the following side effects:
        - Python modules: under normal operation, an inmanta module's Python modules are loaded when the project is loaded.
            However, to support top-level Python imports in test cases, pytest-inmanta instructs the project to not clean
            up loaded Python modules when setting a new project as this would force a reload, changing object identities.
            One exception is when working with dynamic modules whose content might change between project loads (for example
            the unittest module and any module created with Project.create_module). Therefore any dynamic modules are always
            forcefully cleaned up, forcing a reload when next imported.
        - Python module state: since Python module objects are kept alive (see above), any state kept on those objects is
            carried over accross compiles. To start each compile from a fresh state, any stateful modules must define one or
            more cleanup functions. This class is responsible for calling these functions when appropriate.
        - plugins: under normal operation, loading a project registers all modules' plugins as a side effect of loading each
            module's Python modules. However, pytest-inmanta does not reload said Python modules (see above). To make sure only
            loaded modules' plugins are registered (and thus accessible from the model), each loaded project starts with a clean
            (empty) set of registered plugins. Loading the project registers any plugins for newly loaded modules while this
            class is responsible for completing the set with appropriate previously registered plugins.
    """

    _registered_plugins: typing.Dict[str, typing.Type[plugins.Plugin]] = {}
    _dynamic_modules: typing.Set[str] = set()

    @classmethod
    def load(cls, project: module.Project) -> None:
        """
        Sets and loads the given project.
        """
        # unload dynamic modules before fetching currently registered plugins: they should not be included
        cls._unload_dynamic_modules()
        # add currently registered plugins to tracked plugins before loading the project
        cls._refresh_registered_plugins()
        # reset modules' state
        cls._reset_module_state()

        # For supported versions of core, don't clean up loaded modules between invocations to keep top-level imports valid
        signature_set: inspect.Signature = inspect.Signature.from_callable(
            module.Project.set
        )
        extra_kwargs_set = (
            {"clean": False} if "clean" in signature_set.parameters.keys() else {}
        )
        module.Project.set(project, **extra_kwargs_set)

        # deregister plugins
        plugins.PluginMeta.clear()

        # load the project
        if hasattr(project, "install_modules"):
            # more recent versions of core require explicit modules installation (ISO5+)
            project.install_modules()
        project.load()

        # complete the set of registered plugins from the previously registered ones
        cls._register_plugins(project)

    @classmethod
    def _refresh_registered_plugins(cls) -> None:
        """
        Refresh the tracked registered plugins. Should be called at least once between project loads.
        """
        cls._registered_plugins.update(plugins.PluginMeta.get_functions())

    @classmethod
    def _register_plugins(cls, project: module.Project) -> None:
        """
        Registers all plugin functions for a given project. For each of the project's loaded modules, reregisters any plugins
        that are not currently registered from the set of tracked plugins.
        """
        currently_registered_plugins: typing.Mapping[
            str, typing.Type[plugins.Plugin]
        ] = plugins.PluginMeta.get_functions()
        loaded_mod_ns_pattern: typing.Pattern[str] = re.compile(
            "(" + "|".join(re.escape(mod) for mod in project.modules.keys()) + ")::"
        )
        for fq_plugin_name, plugin in cls._registered_plugins.items():
            if (
                fq_plugin_name not in currently_registered_plugins
                and loaded_mod_ns_pattern.match(fq_plugin_name)
            ):
                plugins.PluginMeta.add_function(plugin)

    @classmethod
    def register_dynamic_module(cls, module_name: str) -> None:
        """
        Register a module as dynamic by name. Dynamic modules are forcefully reloaded on each project load.
        """
        cls._dynamic_modules.add(module_name)

    @classmethod
    def _unload_dynamic_modules(cls) -> None:
        """
        Unload all registered dynamic modules to force a reload on the next compile. Should be called at least once between
        project loads because it assumes that either a dynamic module is loaded by the currently active project or it was
        not loaded at all.
        """
        if not hasattr(module.Module, "unload"):
            # older versions of core (<6) don't support (and don't require) explicit module unloading
            return
        project: module.Project
        try:
            project = module.Project.get()
        except module.ProjectNotFoundException:
            # no project has been loaded yet, no need to unload any modules
            return
        for mod in cls._dynamic_modules:
            if mod in project.modules:
                project.modules[mod].unload()

    @classmethod
    def clear_dynamic_modules(cls) -> None:
        """
        Clear the set of registered dynamic modules, unloading them first.
        """
        cls._unload_dynamic_modules()
        cls._dynamic_modules = set()

    @classmethod
    def _reset_module_state(cls) -> None:
        """
        Resets any state kept on Python module objects associated with Inmanta modules by calling predefined cleanup functions.
        """
        for mod_name, mod in sys.modules.items():
            if mod_name.startswith("inmanta_plugins."):
                for func_name, func in mod.__dict__.items():
                    if func_name.startswith("inmanta_reset_state") and callable(func):
                        func()


class Project:
    """
    This class provides a TestCase class for creating module unit tests. It uses the current module and loads required
    modules from the provided repositories. Additional repositories can be provided by setting the INMANTA_MODULE_REPO
    environment variable. Repositories are separated with spaces.
    """

    def __init__(
        self,
        project_dir: str,
        env_path: str,
        load_plugins: typing.Optional[bool] = True,
    ) -> None:
        """
        :param project_dir: Directory containing the Inmanta project.
        :param env_path: The path to the venv to be used by the compiler.
        :param load_plugins: Load plugins iff this value is not None.
        """
        self._test_project_dir = project_dir
        self._env_path = env_path
        self._stdout: typing.Optional[str] = None
        self._stderr: typing.Optional[str] = None
        self.types: typing.Optional[typing.Dict[str, inmanta.ast.Type]] = None
        self.version: typing.Optional[int] = None
        self.resources: ResourceDict = {}
        self._root_scope: typing.Optional[inmanta.ast.Namespace] = None
        self._exporter: typing.Optional[Exporter] = None
        self._blobs: typing.Dict[str, bytes] = {}
        self._facts: typing.Dict[
            ResourceIdStr, typing.Dict[str, typing.Any]
        ] = defaultdict(dict)
        self._should_load_plugins: typing.Optional[bool] = load_plugins
        self._plugins: typing.Optional[typing.Dict[str, FunctionType]] = None
        self._load()
        self._capsys: typing.Optional[CaptureFixture] = None
        self.ctx: typing.Optional[HandlerContext] = None
        self._handlers: typing.Set[ResourceHandler] = set()
        config.Config.load_config()

    def init(self, capsys: CaptureFixture) -> None:
        self._stdout = None
        self._stderr = None
        self._capsys = capsys
        self.types = None
        self.version = None
        self.resources = {}
        self._root_scope = None
        self._exporter = None
        self._blobs = {}
        self._facts = defaultdict(dict)
        self.ctx = None
        self._handlers = set()
        self._load()
        config.Config.load_config()

    def _create_project_and_load(self, model: str) -> module.Project:
        """
        This method doesn the following:
        * Add the given model file to the Inmanta project
        * Install the module dependencies
        * Load the project

        :param init: True iff the project should start from a clean slate. Ignored for older (<6) versions of core.
        :return: The newly created module.Project instance.
        """
        with open(os.path.join(self._test_project_dir, "main.cf"), "w+") as fd:
            fd.write(model)

        signature_init: inspect.Signature = inspect.Signature.from_callable(
            module.Project.__init__
        )
        # The venv_path parameter only exists on ISO5+
        extra_kwargs_init = (
            {"venv_path": self._env_path}
            if "venv_path" in signature_init.parameters.keys()
            else {}
        )
        test_project = module.Project(self._test_project_dir, **extra_kwargs_init)

        ProjectLoader.load(test_project)

        # refresh plugins
        if self._should_load_plugins is not None:
            self._plugins = self._load_plugins()
        return test_project

    def add_blob(self, key: str, content: bytes, allow_overwrite: bool = True) -> None:
        """
        Add a blob identified with the hash of the content as key
        """
        if isinstance(content, str):
            warnings.warn("received a string, but expect bytes", DeprecationWarning)
            content = content.encode("utf-8")
        if key in self._blobs and not allow_overwrite:
            raise Exception("Key %s already stored in blobs" % key)
        self._blobs[key] = content

    def stat_blob(self, key: str) -> bool:
        return key in self._blobs

    def get_blob(self, key: str) -> bytes:
        return self._blobs[key]

    def add_fact(self, resource_id: ResourceIdStr, name: str, value: object) -> None:
        self._facts[resource_id][name] = value

    def get_handler(self, resource: Resource, run_as_root: bool) -> ResourceHandler:
        # TODO: if user is root, do not use remoting
        c = cache.AgentCache()
        if run_as_root:
            agent = MockAgent("ssh://root@localhost")
        else:
            agent = MockAgent("local:")

        c.open_version(resource.id.version)
        try:
            p = handler.Commander.get_provider(c, agent, resource)  # type: ignore
            p.set_cache(c)
            p.get_file = lambda x: self.get_blob(x)  # type: ignore
            p.stat_file = lambda x: self.stat_blob(x)  # type: ignore
            p.upload_file = lambda x, y: self.add_blob(x, y)  # type: ignore
            p.run_sync = ioloop.IOLoop.current().run_sync  # type: ignore
            self._handlers.add(p)
            return p
        except Exception as e:
            raise e

    def finalize_context(self, ctx: handler.HandlerContext) -> None:
        # ensure logs can be serialized
        json_encode({"message": ctx.logs})

    def get_resource(
        self, resource_type: str, **filter_args: object
    ) -> typing.Optional[Resource]:
        """
        Get a resource of the given type and given filter on the resource attributes. If multiple resource match, the
        first one is returned. If none match, None is returned.

        :param resource_type: The exact type used in the model (no super types)
        """

        def apply_filter(resource: Resource) -> bool:
            for arg, value in filter_args.items():
                if not hasattr(resource, arg):
                    return False

                if getattr(resource, arg) != value:
                    return False

            return True

        for resource in self.resources.values():
            if not resource.is_type(resource_type):
                continue

            if not apply_filter(resource):
                continue

            resource = self.check_serialization(resource)
            return resource

        return None

    def deploy(
        self, resource: Resource, dry_run: bool = False, run_as_root: bool = False
    ) -> HandlerContext:
        """
        Deploy the given resource with a handler
        """
        assert resource is not None

        h = self.get_handler(resource, run_as_root)

        assert h is not None

        ctx = handler.HandlerContext(resource)
        h.execute(ctx, resource, dry_run)
        self.finalize_context(ctx)
        self.ctx = ctx
        self.finalize_handler(h)
        return ctx

    def dryrun(self, resource: Resource, run_as_root: bool = False) -> HandlerContext:
        return self.deploy(resource, True, run_as_root)

    def deploy_resource(
        self,
        resource_type: str,
        status: const.ResourceState = const.ResourceState.deployed,
        run_as_root: bool = False,
        change: const.Change = None,
        **filter_args: object,
    ) -> Resource:
        """
        Deploy a resource of the given type, that matches the filter and assert the outcome

        :param resource_type: the type of resource to deploy
        :param filter_args: a set of kwargs, the resource must have all matching attributes set to the given values
        :param run_as_root: run the handler as root or not
        :param status: the expected status of the deployment
        :param change: the expected change performed by the handler

        :return: the resource
        """
        res = self.get_resource(resource_type, **filter_args)
        assert res is not None, "No resource found of given type and filter args"

        ctx = self.deploy(res, run_as_root)
        if ctx.status != status:
            print("Deploy did not result in correct status")
            print("Requested changes: ", ctx._changes)
            for log in ctx.logs:
                print("Log: ", log._data["msg"])
                print(
                    "Kwargs: ",
                    [
                        "%s: %s" % (k, v)
                        for k, v in log._data["kwargs"].items()
                        if k != "traceback"
                    ],
                )
                if "traceback" in log._data["kwargs"]:
                    print("Traceback:\n", log._data["kwargs"]["traceback"])

        assert ctx.status == status
        if change is not None:
            assert ctx._change == change
        self.finalize_context(ctx)
        return res

    def dryrun_resource(
        self,
        resource_type: str,
        status: const.ResourceState = const.ResourceState.dry,
        run_as_root: bool = False,
        **filter_args: object,
    ) -> typing.Dict[str, AttributeStateChange]:
        """
        Run a dryrun for a specific resource.

        :param resource_type: the type of resource to run, as a fully qualified inmanta type (e.g. `unittest::Resource`),
            see :py:meth:`get_resource`
        :param status: the expected result status
            (for dryrun the success status is :py:attr:`inmanta.const.ResourceState.dry`)
        :param run_as_root: run the mock agent as root
        :param filter_args: filters for selecting the resource, see :py:meth:`get_resource`
        """
        res = self.get_resource(resource_type, **filter_args)
        assert res is not None, "No resource found of given type and filter args"

        ctx = self.dryrun(res, run_as_root)
        assert ctx.status == status
        return ctx.changes

    def io(self, run_as_root: bool = False) -> "IOBase":
        version = 1
        if run_as_root:
            ret = agent_io.get_io(None, "ssh://root@localhost", version)
        else:
            ret = agent_io.get_io(None, "local:", version)
        return ret

    def create_module(self, name: str, initcf: str = "", initpy: str = "") -> None:
        module_dir = os.path.join(self._test_project_dir, "libs", name)
        os.mkdir(module_dir)
        os.mkdir(os.path.join(module_dir, "model"))
        os.mkdir(os.path.join(module_dir, "files"))
        os.mkdir(os.path.join(module_dir, "templates"))
        os.mkdir(os.path.join(module_dir, "plugins"))

        with open(os.path.join(module_dir, "model", "_init.cf"), "w+") as fd:
            fd.write(initcf)

        with open(os.path.join(module_dir, "plugins", "__init__.py"), "w+") as fd:
            fd.write(initpy)

        with open(os.path.join(module_dir, "module.yml"), "w+") as fd:
            fd.write(
                f"""name: {name}
version: 0.1
license: Test License
            """
            )

        ProjectLoader.register_dynamic_module(name)

    def _load(self) -> None:
        """
        Load the current module and compile an otherwise empty project
        """
        mod: module.Module
        mod, _ = get_module()
        self._create_project_and_load(model=f"import {mod.name}")

    def compile(self, main: str, export: bool = False, no_dedent: bool = True) -> None:
        """
        Compile the configuration model in main. This method will load all required modules.

        :param main: The model to compile
        :param export: Whether the model should be exported after the compile
        :param no_dedent: Don't remove additional indentation in the model
        """
        # logging model with line numbers
        def enumerate_model(model: str):
            lines = model.split("\n")
            leading_zeros = math.floor(math.log(len(lines), 10)) + 1
            line_numbers_model = "\n".join(
                [
                    f"{str(number).zfill(leading_zeros)}    {line}"
                    for number, line in enumerate(lines, start=1)
                ]
            )
            return line_numbers_model

        # Dedent the input format
        model = dedent(main.strip("\n")) if not no_dedent else main
        LOGGER.debug(f"Compiling model:\n{enumerate_model(model)}")
        self._create_project_and_load(model)

        # flush io capture buffer
        self._capsys.readouterr()

        (types, scopes) = compiler.do_compile(refs={"facts": self._facts})

        exporter = Exporter()

        version, resources = exporter.run(types, scopes, no_commit=not export)

        for key, blob in exporter._file_store.items():
            self.add_blob(key, blob)

        self._root_scope = scopes
        self.version = version
        self.resources = resources
        self.types = types
        self._exporter = exporter

        captured = self._capsys.readouterr()

        self._stdout = captured.out
        self._stderr = captured.err

    def deploy_latest_version(self, full_deploy: bool = False) -> None:
        """Release and push the latest version to the server (uses the current configuration, either with a fixture or
        set by the test.
        """
        if self.version is None:
            raise Exception("Run project.compile first")
        conn = protocol.SyncClient("compiler")
        LOGGER.info("Triggering deploy for version %d" % self.version)
        tid = cfg_env.get()
        agent_trigger_method = const.AgentTriggerMethod.get_agent_trigger_method(
            full_deploy
        )
        conn.release_version(tid, self.version, True, agent_trigger_method)

    def get_last_context(self) -> typing.Optional[HandlerContext]:
        return self.ctx

    def get_last_logs(self) -> typing.Optional[typing.List[LogLine]]:
        if self.ctx:
            return self.ctx.logs
        return None

    def get_stdout(self) -> typing.Optional[str]:
        return self._stdout

    def get_stderr(self) -> typing.Optional[str]:
        return self._stderr

    def get_root_scope(self) -> typing.Optional[inmanta.ast.Namespace]:
        return self._root_scope

    def add_mock_file(self, subdir: str, name: str, content: str) -> None:
        """
        This method can be used to register mock templates or files in the virtual "unittest" module.
        """
        dir_name = os.path.join(self._test_project_dir, "libs", "unittest", subdir)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        with open(os.path.join(dir_name, name), "w+") as fd:
            fd.write(content)

        ProjectLoader.register_dynamic_module("unittest")

    def _load_plugins(self) -> typing.Dict[str, FunctionType]:
        mod: module.Module
        mod, _ = get_module()
        submodules: typing.Optional[
            typing.Dict[str, ModuleType]
        ] = InmantaPluginsImporter(self).get_submodules(mod.name)
        return (
            {}
            if submodules is None
            else {
                k: v
                for submod in submodules.values()
                for k, v in submod.__dict__.items()
                if isinstance(v, FunctionType)
            }
        )

    def get_plugin_function(self, function_name: str) -> FunctionType:
        if self._plugins is None:
            raise Exception(
                "Plugins not loaded, perhaps you should use the `project` fixture or"
                " initialize the Project with load_plugins == True"
            )
        if function_name not in self._plugins:
            raise Exception(f"Plugin function with name {function_name} not found")
        return self._plugins[function_name]

    def get_plugins(self) -> typing.Dict[str, FunctionType]:
        if self._plugins is None:
            raise Exception(
                "Plugins not loaded, perhaps you should use the `project` fixture or"
                " initialize the Project with load_plugins == True"
            )
        return dict(self._plugins)

    def get_instances(self, fortype: str = "std::Entity") -> typing.List[DynamicProxy]:
        if self.types is None:
            raise Exception("No compile has been done")
        if fortype not in self.types:
            raise Exception(f"No entities of type {fortype} found in the model")

        # extract all objects of a specific type from the compiler
        allof = self.types[fortype].get_all_instances()
        # wrap in DynamicProxy to hide internal compiler structure
        # and get inmanta objects as if they were python objects
        return [DynamicProxy.return_value(port) for port in allof]

    def unittest_resource_exists(self, name: str) -> bool:
        """
        Check if a unittest resource with name exists or not
        """
        return name in DATA

    def unittest_resource_get(
        self, name: str
    ) -> typing.Dict[str, typing.Union[str, bool, float, int]]:
        """
        Get the state of the unittest resource
        """
        return DATA[name]

    def unittest_resource_set(
        self, name: str, **kwargs: typing.Union[str, bool, float, int]
    ) -> None:
        """
        Change a value of the unittest resource
        """
        DATA[name].update(kwargs)

    def check_serialization(self, resource: Resource) -> Resource:
        """ Check if the resource is serializable """
        serialized = json.loads(json_encode(resource.serialize()))
        return Resource.deserialize(serialized)

    def clean(self) -> None:
        shutil.rmtree(os.path.join(self._test_project_dir, "libs", "unittest"))
        self.finalize_all_handlers()
        self.create_module(
            "unittest",
            initcf=get_module_data("init.cf"),
            initpy=get_module_data("init.py"),
        )
        ProjectLoader.clear_dynamic_modules()

    def finalize_handler(self, handler: ResourceHandler) -> None:
        handler.cache.close()

    def finalize_all_handlers(self) -> None:
        for handler_instance in self._handlers:
            self.finalize_handler(handler_instance)
