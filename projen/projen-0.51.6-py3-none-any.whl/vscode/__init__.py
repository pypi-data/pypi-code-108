import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import (
    Component as _Component_2b0ad27f,
    DevEnvironmentDockerImage as _DevEnvironmentDockerImage_4a8d8ffd,
    DevEnvironmentOptions as _DevEnvironmentOptions_b10d89d1,
    IDevEnvironment as _IDevEnvironment_9a084622,
    Project as _Project_57d89203,
    Task as _Task_9fa875b6,
)


@jsii.implements(_IDevEnvironment_9a084622)
class DevContainer(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.vscode.DevContainer",
):
    '''(experimental) A development environment running VSCode in a container;

    used by GitHub
    codespaces.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        docker_image: typing.Optional[_DevEnvironmentDockerImage_4a8d8ffd] = None,
        ports: typing.Optional[typing.Sequence[builtins.str]] = None,
        tasks: typing.Optional[typing.Sequence[_Task_9fa875b6]] = None,
        vscode_extensions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param project: -
        :param docker_image: (experimental) A Docker image or Dockerfile for the container.
        :param ports: (experimental) An array of ports that should be exposed from the container.
        :param tasks: (experimental) An array of tasks that should be run when the container starts.
        :param vscode_extensions: (experimental) An array of extension IDs that specify the extensions that should be installed inside the container when it is created.

        :stability: experimental
        '''
        options = DevContainerOptions(
            docker_image=docker_image,
            ports=ports,
            tasks=tasks,
            vscode_extensions=vscode_extensions,
        )

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="addDockerImage")
    def add_docker_image(self, image: _DevEnvironmentDockerImage_4a8d8ffd) -> None:
        '''(experimental) Add a custom Docker image or Dockerfile for the container.

        :param image: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDockerImage", [image]))

    @jsii.member(jsii_name="addPorts")
    def add_ports(self, *ports: builtins.str) -> None:
        '''(experimental) Adds ports that should be exposed (forwarded) from the container.

        :param ports: The new ports.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addPorts", [*ports]))

    @jsii.member(jsii_name="addTasks")
    def add_tasks(self, *tasks: _Task_9fa875b6) -> None:
        '''(experimental) Adds tasks to run when the container starts.

        Tasks will be run in sequence.

        :param tasks: The new tasks.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addTasks", [*tasks]))

    @jsii.member(jsii_name="addVscodeExtensions")
    def add_vscode_extensions(self, *extensions: builtins.str) -> None:
        '''(experimental) Adds a list of VSCode extensions that should be automatically installed in the container.

        :param extensions: The extension IDs.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addVscodeExtensions", [*extensions]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="config")
    def config(self) -> typing.Any:
        '''(experimental) Direct access to the devcontainer configuration (escape hatch).

        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.get(self, "config"))


@jsii.data_type(
    jsii_type="projen.vscode.DevContainerOptions",
    jsii_struct_bases=[_DevEnvironmentOptions_b10d89d1],
    name_mapping={
        "docker_image": "dockerImage",
        "ports": "ports",
        "tasks": "tasks",
        "vscode_extensions": "vscodeExtensions",
    },
)
class DevContainerOptions(_DevEnvironmentOptions_b10d89d1):
    def __init__(
        self,
        *,
        docker_image: typing.Optional[_DevEnvironmentDockerImage_4a8d8ffd] = None,
        ports: typing.Optional[typing.Sequence[builtins.str]] = None,
        tasks: typing.Optional[typing.Sequence[_Task_9fa875b6]] = None,
        vscode_extensions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Constructor options for the DevContainer component.

        The default docker image used for GitHub Codespaces is defined here:

        :param docker_image: (experimental) A Docker image or Dockerfile for the container.
        :param ports: (experimental) An array of ports that should be exposed from the container.
        :param tasks: (experimental) An array of tasks that should be run when the container starts.
        :param vscode_extensions: (experimental) An array of extension IDs that specify the extensions that should be installed inside the container when it is created.

        :see: https://github.com/microsoft/vscode-dev-containers/tree/master/containers/codespaces-linux
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if docker_image is not None:
            self._values["docker_image"] = docker_image
        if ports is not None:
            self._values["ports"] = ports
        if tasks is not None:
            self._values["tasks"] = tasks
        if vscode_extensions is not None:
            self._values["vscode_extensions"] = vscode_extensions

    @builtins.property
    def docker_image(self) -> typing.Optional[_DevEnvironmentDockerImage_4a8d8ffd]:
        '''(experimental) A Docker image or Dockerfile for the container.

        :stability: experimental
        '''
        result = self._values.get("docker_image")
        return typing.cast(typing.Optional[_DevEnvironmentDockerImage_4a8d8ffd], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) An array of ports that should be exposed from the container.

        :stability: experimental
        '''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tasks(self) -> typing.Optional[typing.List[_Task_9fa875b6]]:
        '''(experimental) An array of tasks that should be run when the container starts.

        :stability: experimental
        '''
        result = self._values.get("tasks")
        return typing.cast(typing.Optional[typing.List[_Task_9fa875b6]], result)

    @builtins.property
    def vscode_extensions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) An array of extension IDs that specify the extensions that should be installed inside the container when it is created.

        :stability: experimental
        '''
        result = self._values.get("vscode_extensions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DevContainerOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.vscode.InternalConsoleOptions")
class InternalConsoleOptions(enum.Enum):
    '''(experimental) Controls the visibility of the VSCode Debug Console panel during a debugging session Source: https://code.visualstudio.com/docs/editor/debugging#_launchjson-attributes.

    :stability: experimental
    '''

    NEVER_OPEN = "NEVER_OPEN"
    '''
    :stability: experimental
    '''
    OPEN_ON_FIRST_SESSION_START = "OPEN_ON_FIRST_SESSION_START"
    '''
    :stability: experimental
    '''
    OPEN_ON_SESSION_START = "OPEN_ON_SESSION_START"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="projen.vscode.Presentation",
    jsii_struct_bases=[],
    name_mapping={"group": "group", "hidden": "hidden", "order": "order"},
)
class Presentation:
    def __init__(
        self,
        *,
        group: builtins.str,
        hidden: builtins.bool,
        order: jsii.Number,
    ) -> None:
        '''(experimental) VSCode launch configuration Presentation interface "using the order, group, and hidden attributes in the presentation object you can sort, group, and hide configurations and compounds in the Debug configuration dropdown and in the Debug quick pick." Source: https://code.visualstudio.com/docs/editor/debugging#_launchjson-attributes.

        :param group: 
        :param hidden: 
        :param order: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "group": group,
            "hidden": hidden,
            "order": order,
        }

    @builtins.property
    def group(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("group")
        assert result is not None, "Required property 'group' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hidden(self) -> builtins.bool:
        '''
        :stability: experimental
        '''
        result = self._values.get("hidden")
        assert result is not None, "Required property 'hidden' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def order(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("order")
        assert result is not None, "Required property 'order' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Presentation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.vscode.ServerReadyAction",
    jsii_struct_bases=[],
    name_mapping={"action": "action", "pattern": "pattern", "uri_format": "uriFormat"},
)
class ServerReadyAction:
    def __init__(
        self,
        *,
        action: builtins.str,
        pattern: typing.Optional[builtins.str] = None,
        uri_format: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) VSCode launch configuration ServerReadyAction interface "if you want to open a URL in a web browser whenever the program under debugging outputs a specific message to the debug console or integrated terminal." Source: https://code.visualstudio.com/docs/editor/debugging#_launchjson-attributes.

        :param action: 
        :param pattern: 
        :param uri_format: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
        }
        if pattern is not None:
            self._values["pattern"] = pattern
        if uri_format is not None:
            self._values["uri_format"] = uri_format

    @builtins.property
    def action(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pattern(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("pattern")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uri_format(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("uri_format")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerReadyAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VsCode(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.vscode.VsCode",
):
    '''
    :stability: experimental
    '''

    def __init__(self, project: _Project_57d89203) -> None:
        '''
        :param project: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [project])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchConfiguration")
    def launch_configuration(self) -> "VsCodeLaunchConfig":
        '''
        :stability: experimental
        '''
        return typing.cast("VsCodeLaunchConfig", jsii.get(self, "launchConfiguration"))


class VsCodeLaunchConfig(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.vscode.VsCodeLaunchConfig",
):
    '''(experimental) VSCode launch configuration file (launch.json), useful for enabling in-editor debugger.

    :stability: experimental
    '''

    def __init__(self, vscode: VsCode) -> None:
        '''
        :param vscode: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [vscode])

    @jsii.member(jsii_name="addConfiguration")
    def add_configuration(
        self,
        *,
        name: builtins.str,
        request: builtins.str,
        type: builtins.str,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
        debug_server: typing.Optional[jsii.Number] = None,
        internal_console_options: typing.Optional[InternalConsoleOptions] = None,
        out_files: typing.Optional[typing.Sequence[builtins.str]] = None,
        post_debug_task: typing.Optional[builtins.str] = None,
        pre_launch_task: typing.Optional[builtins.str] = None,
        presentation: typing.Optional[Presentation] = None,
        program: typing.Optional[builtins.str] = None,
        runtime_args: typing.Optional[typing.Sequence[builtins.str]] = None,
        server_ready_action: typing.Optional[ServerReadyAction] = None,
        skip_files: typing.Optional[typing.Sequence[builtins.str]] = None,
        url: typing.Optional[builtins.str] = None,
        web_root: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Adds a VsCodeLaunchConfigurationEntry (e.g. a node.js debugger) to `.vscode/launch.json. Each configuration entry has following mandatory fields: type, request and name. See https://code.visualstudio.com/docs/editor/debugging#_launchjson-attributes for details.

        :param name: 
        :param request: 
        :param type: 
        :param args: 
        :param debug_server: 
        :param internal_console_options: 
        :param out_files: 
        :param post_debug_task: 
        :param pre_launch_task: 
        :param presentation: 
        :param program: 
        :param runtime_args: 
        :param server_ready_action: 
        :param skip_files: 
        :param url: 
        :param web_root: 

        :stability: experimental
        '''
        cfg = VsCodeLaunchConfigurationEntry(
            name=name,
            request=request,
            type=type,
            args=args,
            debug_server=debug_server,
            internal_console_options=internal_console_options,
            out_files=out_files,
            post_debug_task=post_debug_task,
            pre_launch_task=pre_launch_task,
            presentation=presentation,
            program=program,
            runtime_args=runtime_args,
            server_ready_action=server_ready_action,
            skip_files=skip_files,
            url=url,
            web_root=web_root,
        )

        return typing.cast(None, jsii.invoke(self, "addConfiguration", [cfg]))


@jsii.data_type(
    jsii_type="projen.vscode.VsCodeLaunchConfigurationEntry",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "request": "request",
        "type": "type",
        "args": "args",
        "debug_server": "debugServer",
        "internal_console_options": "internalConsoleOptions",
        "out_files": "outFiles",
        "post_debug_task": "postDebugTask",
        "pre_launch_task": "preLaunchTask",
        "presentation": "presentation",
        "program": "program",
        "runtime_args": "runtimeArgs",
        "server_ready_action": "serverReadyAction",
        "skip_files": "skipFiles",
        "url": "url",
        "web_root": "webRoot",
    },
)
class VsCodeLaunchConfigurationEntry:
    def __init__(
        self,
        *,
        name: builtins.str,
        request: builtins.str,
        type: builtins.str,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
        debug_server: typing.Optional[jsii.Number] = None,
        internal_console_options: typing.Optional[InternalConsoleOptions] = None,
        out_files: typing.Optional[typing.Sequence[builtins.str]] = None,
        post_debug_task: typing.Optional[builtins.str] = None,
        pre_launch_task: typing.Optional[builtins.str] = None,
        presentation: typing.Optional[Presentation] = None,
        program: typing.Optional[builtins.str] = None,
        runtime_args: typing.Optional[typing.Sequence[builtins.str]] = None,
        server_ready_action: typing.Optional[ServerReadyAction] = None,
        skip_files: typing.Optional[typing.Sequence[builtins.str]] = None,
        url: typing.Optional[builtins.str] = None,
        web_root: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for a 'VsCodeLaunchConfigurationEntry' Source: https://code.visualstudio.com/docs/editor/debugging#_launchjson-attributes.

        :param name: 
        :param request: 
        :param type: 
        :param args: 
        :param debug_server: 
        :param internal_console_options: 
        :param out_files: 
        :param post_debug_task: 
        :param pre_launch_task: 
        :param presentation: 
        :param program: 
        :param runtime_args: 
        :param server_ready_action: 
        :param skip_files: 
        :param url: 
        :param web_root: 

        :stability: experimental
        '''
        if isinstance(presentation, dict):
            presentation = Presentation(**presentation)
        if isinstance(server_ready_action, dict):
            server_ready_action = ServerReadyAction(**server_ready_action)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "request": request,
            "type": type,
        }
        if args is not None:
            self._values["args"] = args
        if debug_server is not None:
            self._values["debug_server"] = debug_server
        if internal_console_options is not None:
            self._values["internal_console_options"] = internal_console_options
        if out_files is not None:
            self._values["out_files"] = out_files
        if post_debug_task is not None:
            self._values["post_debug_task"] = post_debug_task
        if pre_launch_task is not None:
            self._values["pre_launch_task"] = pre_launch_task
        if presentation is not None:
            self._values["presentation"] = presentation
        if program is not None:
            self._values["program"] = program
        if runtime_args is not None:
            self._values["runtime_args"] = runtime_args
        if server_ready_action is not None:
            self._values["server_ready_action"] = server_ready_action
        if skip_files is not None:
            self._values["skip_files"] = skip_files
        if url is not None:
            self._values["url"] = url
        if web_root is not None:
            self._values["web_root"] = web_root

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def request(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("request")
        assert result is not None, "Required property 'request' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def debug_server(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("debug_server")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def internal_console_options(self) -> typing.Optional[InternalConsoleOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("internal_console_options")
        return typing.cast(typing.Optional[InternalConsoleOptions], result)

    @builtins.property
    def out_files(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("out_files")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def post_debug_task(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("post_debug_task")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_launch_task(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("pre_launch_task")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def presentation(self) -> typing.Optional[Presentation]:
        '''
        :stability: experimental
        '''
        result = self._values.get("presentation")
        return typing.cast(typing.Optional[Presentation], result)

    @builtins.property
    def program(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("program")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runtime_args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("runtime_args")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def server_ready_action(self) -> typing.Optional[ServerReadyAction]:
        '''
        :stability: experimental
        '''
        result = self._values.get("server_ready_action")
        return typing.cast(typing.Optional[ServerReadyAction], result)

    @builtins.property
    def skip_files(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("skip_files")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def web_root(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("web_root")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VsCodeLaunchConfigurationEntry(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DevContainer",
    "DevContainerOptions",
    "InternalConsoleOptions",
    "Presentation",
    "ServerReadyAction",
    "VsCode",
    "VsCodeLaunchConfig",
    "VsCodeLaunchConfigurationEntry",
]

publication.publish()
