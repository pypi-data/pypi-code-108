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
    Dependency as _Dependency_f510e013,
    FileBase as _FileBase_aff596dc,
    IResolver as _IResolver_0b7d1958,
    LoggerOptions as _LoggerOptions_eb0f6309,
    Project as _Project_57d89203,
    ProjectType as _ProjectType_fd80c725,
    ProjenrcOptions as _ProjenrcOptions_164bd039,
    SampleReadmeProps as _SampleReadmeProps_3518b03b,
    Task as _Task_9fa875b6,
    TomlFile as _TomlFile_dab3b22f,
)
from ..github import (
    AutoApproveOptions as _AutoApproveOptions_dac86cbe,
    AutoMergeOptions as _AutoMergeOptions_d112cd3c,
    GitHubOptions as _GitHubOptions_21553699,
    GitHubProject as _GitHubProject_c48bc7ea,
    GitHubProjectOptions as _GitHubProjectOptions_547f2d08,
    MergifyOptions as _MergifyOptions_a6faaab3,
    StaleOptions as _StaleOptions_929db764,
)


@jsii.interface(jsii_type="projen.python.IPackageProvider")
class IPackageProvider(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="packages")
    def packages(self) -> typing.List[_Dependency_f510e013]:
        '''(experimental) An array of packages (may be dynamically generated).

        :stability: experimental
        '''
        ...


class _IPackageProviderProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "projen.python.IPackageProvider"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="packages")
    def packages(self) -> typing.List[_Dependency_f510e013]:
        '''(experimental) An array of packages (may be dynamically generated).

        :stability: experimental
        '''
        return typing.cast(typing.List[_Dependency_f510e013], jsii.get(self, "packages"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPackageProvider).__jsii_proxy_class__ = lambda : _IPackageProviderProxy


@jsii.interface(jsii_type="projen.python.IPythonDeps")
class IPythonDeps(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installTask")
    def install_task(self) -> _Task_9fa875b6:
        '''(experimental) A task that installs and updates dependencies.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addDependency")
    def add_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a runtime dependency.

        :param spec: Format ``<module>@<semver>``.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addDevDependency")
    def add_dev_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a dev dependency.

        :param spec: Format ``<module>@<semver>``.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="installDependencies")
    def install_dependencies(self) -> None:
        '''(experimental) Installs dependencies (called during post-synthesis).

        :stability: experimental
        '''
        ...


class _IPythonDepsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "projen.python.IPythonDeps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installTask")
    def install_task(self) -> _Task_9fa875b6:
        '''(experimental) A task that installs and updates dependencies.

        :stability: experimental
        '''
        return typing.cast(_Task_9fa875b6, jsii.get(self, "installTask"))

    @jsii.member(jsii_name="addDependency")
    def add_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a runtime dependency.

        :param spec: Format ``<module>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDependency", [spec]))

    @jsii.member(jsii_name="addDevDependency")
    def add_dev_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a dev dependency.

        :param spec: Format ``<module>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDevDependency", [spec]))

    @jsii.member(jsii_name="installDependencies")
    def install_dependencies(self) -> None:
        '''(experimental) Installs dependencies (called during post-synthesis).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "installDependencies", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPythonDeps).__jsii_proxy_class__ = lambda : _IPythonDepsProxy


@jsii.interface(jsii_type="projen.python.IPythonEnv")
class IPythonEnv(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @jsii.member(jsii_name="setupEnvironment")
    def setup_environment(self) -> None:
        '''(experimental) Initializes the virtual environment if it doesn't exist (called during post-synthesis).

        :stability: experimental
        '''
        ...


class _IPythonEnvProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "projen.python.IPythonEnv"

    @jsii.member(jsii_name="setupEnvironment")
    def setup_environment(self) -> None:
        '''(experimental) Initializes the virtual environment if it doesn't exist (called during post-synthesis).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "setupEnvironment", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPythonEnv).__jsii_proxy_class__ = lambda : _IPythonEnvProxy


@jsii.interface(jsii_type="projen.python.IPythonPackaging")
class IPythonPackaging(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishTask")
    def publish_task(self) -> _Task_9fa875b6:
        '''(experimental) A task that uploads the package to a package repository.

        :stability: experimental
        '''
        ...


class _IPythonPackagingProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "projen.python.IPythonPackaging"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishTask")
    def publish_task(self) -> _Task_9fa875b6:
        '''(experimental) A task that uploads the package to a package repository.

        :stability: experimental
        '''
        return typing.cast(_Task_9fa875b6, jsii.get(self, "publishTask"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPythonPackaging).__jsii_proxy_class__ = lambda : _IPythonPackagingProxy


@jsii.implements(IPythonDeps)
class Pip(_Component_2b0ad27f, metaclass=jsii.JSIIMeta, jsii_type="projen.python.Pip"):
    '''(experimental) Manages dependencies using a requirements.txt file and the pip CLI tool.

    :stability: experimental
    '''

    def __init__(self, project: "PythonProject") -> None:
        '''
        :param project: -

        :stability: experimental
        '''
        _options = PipOptions()

        jsii.create(self.__class__, self, [project, _options])

    @jsii.member(jsii_name="addDependency")
    def add_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a runtime dependency.

        :param spec: Format ``<module>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDependency", [spec]))

    @jsii.member(jsii_name="addDevDependency")
    def add_dev_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a dev dependency.

        :param spec: Format ``<module>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDevDependency", [spec]))

    @jsii.member(jsii_name="installDependencies")
    def install_dependencies(self) -> None:
        '''(experimental) Installs dependencies (called during post-synthesis).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "installDependencies", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installTask")
    def install_task(self) -> _Task_9fa875b6:
        '''(experimental) A task that installs and updates dependencies.

        :stability: experimental
        '''
        return typing.cast(_Task_9fa875b6, jsii.get(self, "installTask"))


@jsii.data_type(
    jsii_type="projen.python.PipOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class PipOptions:
    def __init__(self) -> None:
        '''(experimental) Options for pip.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPythonDeps, IPythonEnv, IPythonPackaging)
class Poetry(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.python.Poetry",
):
    '''(experimental) Manage project dependencies, virtual environments, and packaging through the poetry CLI tool.

    :stability: experimental
    '''

    def __init__(
        self,
        project: "PythonProject",
        *,
        author_email: builtins.str,
        author_name: builtins.str,
        version: builtins.str,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        poetry_options: typing.Optional["PoetryPyprojectOptionsWithoutDeps"] = None,
        setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param project: -
        :param author_email: (experimental) Author's e-mail. Default: $GIT_USER_EMAIL
        :param author_name: (experimental) Author's name. Default: $GIT_USER_NAME
        :param version: (experimental) Version of the package. Default: "0.1.0"
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package.
        :param homepage: (experimental) A URL to the website of the project.
        :param license: (experimental) License of this package as an SPDX identifier.
        :param poetry_options: (experimental) Additional options to set for poetry if using poetry.
        :param setup_config: (experimental) Additional fields to pass in the setup() function if using setuptools.

        :stability: experimental
        '''
        options = PythonPackagingOptions(
            author_email=author_email,
            author_name=author_name,
            version=version,
            classifiers=classifiers,
            description=description,
            homepage=homepage,
            license=license,
            poetry_options=poetry_options,
            setup_config=setup_config,
        )

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="addDependency")
    def add_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a runtime dependency.

        :param spec: Format ``<module>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDependency", [spec]))

    @jsii.member(jsii_name="addDevDependency")
    def add_dev_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a dev dependency.

        :param spec: Format ``<module>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDevDependency", [spec]))

    @jsii.member(jsii_name="installDependencies")
    def install_dependencies(self) -> None:
        '''(experimental) Installs dependencies (called during post-synthesis).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "installDependencies", []))

    @jsii.member(jsii_name="setupEnvironment")
    def setup_environment(self) -> None:
        '''(experimental) Initializes the virtual environment if it doesn't exist (called during post-synthesis).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "setupEnvironment", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installTask")
    def install_task(self) -> _Task_9fa875b6:
        '''(experimental) A task that installs and updates dependencies.

        :stability: experimental
        '''
        return typing.cast(_Task_9fa875b6, jsii.get(self, "installTask"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishTask")
    def publish_task(self) -> _Task_9fa875b6:
        '''(experimental) A task that uploads the package to a package repository.

        :stability: experimental
        '''
        return typing.cast(_Task_9fa875b6, jsii.get(self, "publishTask"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishTestTask")
    def publish_test_task(self) -> _Task_9fa875b6:
        '''(experimental) A task that uploads the package to the Test PyPI repository.

        :stability: experimental
        '''
        return typing.cast(_Task_9fa875b6, jsii.get(self, "publishTestTask"))


class PoetryPyproject(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.python.PoetryPyproject",
):
    '''(experimental) Represents configuration of a pyproject.toml file for a Poetry project.

    :see: https://python-poetry.org/docs/pyproject/
    :stability: experimental
    '''

    def __init__(
        self,
        project: "PythonProject",
        *,
        dependencies: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dev_dependencies: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        authors: typing.Optional[typing.Sequence[builtins.str]] = None,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        documentation: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        extras: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        homepage: typing.Optional[builtins.str] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        maintainers: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        packages: typing.Optional[typing.Sequence[typing.Any]] = None,
        plugins: typing.Any = None,
        readme: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        source: typing.Optional[typing.Sequence[typing.Any]] = None,
        urls: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param dependencies: (experimental) A list of dependencies for the project. The python version for which your package is compatible is also required.
        :param dev_dependencies: (experimental) A list of development dependencies for the project.
        :param authors: (experimental) The authors of the package. Must be in the form "name "
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package (required).
        :param documentation: (experimental) A URL to the documentation of the project.
        :param exclude: (experimental) A list of patterns that will be excluded in the final package. If a VCS is being used for a package, the exclude field will be seeded with the VCS’ ignore settings (.gitignore for git for example).
        :param extras: (experimental) Package extras.
        :param homepage: (experimental) A URL to the website of the project.
        :param include: (experimental) A list of patterns that will be included in the final package.
        :param keywords: (experimental) A list of keywords (max: 5) that the package is related to.
        :param license: (experimental) License of this package as an SPDX identifier. If the project is proprietary and does not use a specific license, you can set this value as "Proprietary".
        :param maintainers: (experimental) the maintainers of the package. Must be in the form "name "
        :param name: (experimental) Name of the package (required).
        :param packages: (experimental) A list of packages and modules to include in the final distribution.
        :param plugins: (experimental) Plugins. Must be specified as a table.
        :param readme: (experimental) The name of the readme file of the package.
        :param repository: (experimental) A URL to the repository of the project.
        :param scripts: (experimental) The scripts or executables that will be installed when installing the package.
        :param source: (experimental) Source registries from which packages are retrieved.
        :param urls: (experimental) Project custom URLs, in addition to homepage, repository and documentation. E.g. "Bug Tracker"
        :param version: (experimental) Version of the package (required).

        :stability: experimental
        '''
        options = PoetryPyprojectOptions(
            dependencies=dependencies,
            dev_dependencies=dev_dependencies,
            authors=authors,
            classifiers=classifiers,
            description=description,
            documentation=documentation,
            exclude=exclude,
            extras=extras,
            homepage=homepage,
            include=include,
            keywords=keywords,
            license=license,
            maintainers=maintainers,
            name=name,
            packages=packages,
            plugins=plugins,
            readme=readme,
            repository=repository,
            scripts=scripts,
            source=source,
            urls=urls,
            version=version,
        )

        jsii.create(self.__class__, self, [project, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="file")
    def file(self) -> _TomlFile_dab3b22f:
        '''
        :stability: experimental
        '''
        return typing.cast(_TomlFile_dab3b22f, jsii.get(self, "file"))


@jsii.data_type(
    jsii_type="projen.python.PoetryPyprojectOptionsWithoutDeps",
    jsii_struct_bases=[],
    name_mapping={
        "authors": "authors",
        "classifiers": "classifiers",
        "description": "description",
        "documentation": "documentation",
        "exclude": "exclude",
        "extras": "extras",
        "homepage": "homepage",
        "include": "include",
        "keywords": "keywords",
        "license": "license",
        "maintainers": "maintainers",
        "name": "name",
        "packages": "packages",
        "plugins": "plugins",
        "readme": "readme",
        "repository": "repository",
        "scripts": "scripts",
        "source": "source",
        "urls": "urls",
        "version": "version",
    },
)
class PoetryPyprojectOptionsWithoutDeps:
    def __init__(
        self,
        *,
        authors: typing.Optional[typing.Sequence[builtins.str]] = None,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        documentation: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        extras: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        homepage: typing.Optional[builtins.str] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        maintainers: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        packages: typing.Optional[typing.Sequence[typing.Any]] = None,
        plugins: typing.Any = None,
        readme: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        source: typing.Optional[typing.Sequence[typing.Any]] = None,
        urls: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Poetry-specific options.

        :param authors: (experimental) The authors of the package. Must be in the form "name "
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package (required).
        :param documentation: (experimental) A URL to the documentation of the project.
        :param exclude: (experimental) A list of patterns that will be excluded in the final package. If a VCS is being used for a package, the exclude field will be seeded with the VCS’ ignore settings (.gitignore for git for example).
        :param extras: (experimental) Package extras.
        :param homepage: (experimental) A URL to the website of the project.
        :param include: (experimental) A list of patterns that will be included in the final package.
        :param keywords: (experimental) A list of keywords (max: 5) that the package is related to.
        :param license: (experimental) License of this package as an SPDX identifier. If the project is proprietary and does not use a specific license, you can set this value as "Proprietary".
        :param maintainers: (experimental) the maintainers of the package. Must be in the form "name "
        :param name: (experimental) Name of the package (required).
        :param packages: (experimental) A list of packages and modules to include in the final distribution.
        :param plugins: (experimental) Plugins. Must be specified as a table.
        :param readme: (experimental) The name of the readme file of the package.
        :param repository: (experimental) A URL to the repository of the project.
        :param scripts: (experimental) The scripts or executables that will be installed when installing the package.
        :param source: (experimental) Source registries from which packages are retrieved.
        :param urls: (experimental) Project custom URLs, in addition to homepage, repository and documentation. E.g. "Bug Tracker"
        :param version: (experimental) Version of the package (required).

        :see: https://python-poetry.org/docs/pyproject/
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if authors is not None:
            self._values["authors"] = authors
        if classifiers is not None:
            self._values["classifiers"] = classifiers
        if description is not None:
            self._values["description"] = description
        if documentation is not None:
            self._values["documentation"] = documentation
        if exclude is not None:
            self._values["exclude"] = exclude
        if extras is not None:
            self._values["extras"] = extras
        if homepage is not None:
            self._values["homepage"] = homepage
        if include is not None:
            self._values["include"] = include
        if keywords is not None:
            self._values["keywords"] = keywords
        if license is not None:
            self._values["license"] = license
        if maintainers is not None:
            self._values["maintainers"] = maintainers
        if name is not None:
            self._values["name"] = name
        if packages is not None:
            self._values["packages"] = packages
        if plugins is not None:
            self._values["plugins"] = plugins
        if readme is not None:
            self._values["readme"] = readme
        if repository is not None:
            self._values["repository"] = repository
        if scripts is not None:
            self._values["scripts"] = scripts
        if source is not None:
            self._values["source"] = source
        if urls is not None:
            self._values["urls"] = urls
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def authors(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The authors of the package.

        Must be in the form "name "

        :stability: experimental
        '''
        result = self._values.get("authors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of PyPI trove classifiers that describe the project.

        :see: https://pypi.org/classifiers/
        :stability: experimental
        '''
        result = self._values.get("classifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A short description of the package (required).

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def documentation(self) -> typing.Optional[builtins.str]:
        '''(experimental) A URL to the documentation of the project.

        :stability: experimental
        '''
        result = self._values.get("documentation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of patterns that will be excluded in the final package.

        If a VCS is being used for a package, the exclude field will be seeded with
        the VCS’ ignore settings (.gitignore for git for example).

        :stability: experimental
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def extras(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        '''(experimental) Package extras.

        :stability: experimental
        '''
        result = self._values.get("extras")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) A URL to the website of the project.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of patterns that will be included in the final package.

        :stability: experimental
        '''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of keywords (max: 5) that the package is related to.

        :stability: experimental
        '''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License of this package as an SPDX identifier.

        If the project is proprietary and does not use a specific license, you
        can set this value as "Proprietary".

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintainers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) the maintainers of the package.

        Must be in the form "name "

        :stability: experimental
        '''
        result = self._values.get("maintainers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the package (required).

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def packages(self) -> typing.Optional[typing.List[typing.Any]]:
        '''(experimental) A list of packages and modules to include in the final distribution.

        :stability: experimental
        '''
        result = self._values.get("packages")
        return typing.cast(typing.Optional[typing.List[typing.Any]], result)

    @builtins.property
    def plugins(self) -> typing.Any:
        '''(experimental) Plugins.

        Must be specified as a table.

        :see: https://toml.io/en/v1.0.0#table
        :stability: experimental
        '''
        result = self._values.get("plugins")
        return typing.cast(typing.Any, result)

    @builtins.property
    def readme(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the readme file of the package.

        :stability: experimental
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) A URL to the repository of the project.

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scripts(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) The scripts or executables that will be installed when installing the package.

        :stability: experimental
        '''
        result = self._values.get("scripts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def source(self) -> typing.Optional[typing.List[typing.Any]]:
        '''(experimental) Source registries from which packages are retrieved.

        :stability: experimental
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[typing.List[typing.Any]], result)

    @builtins.property
    def urls(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Project custom URLs, in addition to homepage, repository and documentation.

        E.g. "Bug Tracker"

        :stability: experimental
        '''
        result = self._values.get("urls")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of the package (required).

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PoetryPyprojectOptionsWithoutDeps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Projenrc(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.python.Projenrc",
):
    '''(experimental) Allows writing projenrc files in python.

    This will install ``projen`` as a Python dependency and will add a
    ``synth`` task which will run ``.projenrc.py``.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        filename: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param filename: (experimental) The name of the projenrc file. Default: ".projenrc.py"
        :param projen_version: (experimental) The projen version to use. Default: - current version

        :stability: experimental
        '''
        options = ProjenrcOptions(filename=filename, projen_version=projen_version)

        jsii.create(self.__class__, self, [project, options])


@jsii.data_type(
    jsii_type="projen.python.ProjenrcOptions",
    jsii_struct_bases=[],
    name_mapping={"filename": "filename", "projen_version": "projenVersion"},
)
class ProjenrcOptions:
    def __init__(
        self,
        *,
        filename: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``Projenrc``.

        :param filename: (experimental) The name of the projenrc file. Default: ".projenrc.py"
        :param projen_version: (experimental) The projen version to use. Default: - current version

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if filename is not None:
            self._values["filename"] = filename
        if projen_version is not None:
            self._values["projen_version"] = projen_version

    @builtins.property
    def filename(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the projenrc file.

        :default: ".projenrc.py"

        :stability: experimental
        '''
        result = self._values.get("filename")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The projen version to use.

        :default: - current version

        :stability: experimental
        '''
        result = self._values.get("projen_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjenrcOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Pytest(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.python.Pytest",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        project: "PythonProject",
        *,
        max_failures: typing.Optional[jsii.Number] = None,
        testdir: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param max_failures: (experimental) Stop the testing process after the first N failures.
        :param testdir: (experimental) Directory with tests. Default: 'tests'
        :param version: (experimental) Pytest version. Default: "6.2.1"

        :stability: experimental
        '''
        options = PytestOptions(
            max_failures=max_failures, testdir=testdir, version=version
        )

        jsii.create(self.__class__, self, [project, options])


@jsii.data_type(
    jsii_type="projen.python.PytestOptions",
    jsii_struct_bases=[],
    name_mapping={
        "max_failures": "maxFailures",
        "testdir": "testdir",
        "version": "version",
    },
)
class PytestOptions:
    def __init__(
        self,
        *,
        max_failures: typing.Optional[jsii.Number] = None,
        testdir: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param max_failures: (experimental) Stop the testing process after the first N failures.
        :param testdir: (experimental) Directory with tests. Default: 'tests'
        :param version: (experimental) Pytest version. Default: "6.2.1"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if max_failures is not None:
            self._values["max_failures"] = max_failures
        if testdir is not None:
            self._values["testdir"] = testdir
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def max_failures(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Stop the testing process after the first N failures.

        :stability: experimental
        '''
        result = self._values.get("max_failures")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def testdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Directory with tests.

        :default: 'tests'

        :stability: experimental
        '''
        result = self._values.get("testdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Pytest version.

        :default: "6.2.1"

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PytestOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.python.PythonPackagingOptions",
    jsii_struct_bases=[],
    name_mapping={
        "author_email": "authorEmail",
        "author_name": "authorName",
        "version": "version",
        "classifiers": "classifiers",
        "description": "description",
        "homepage": "homepage",
        "license": "license",
        "poetry_options": "poetryOptions",
        "setup_config": "setupConfig",
    },
)
class PythonPackagingOptions:
    def __init__(
        self,
        *,
        author_email: builtins.str,
        author_name: builtins.str,
        version: builtins.str,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        poetry_options: typing.Optional[PoetryPyprojectOptionsWithoutDeps] = None,
        setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param author_email: (experimental) Author's e-mail. Default: $GIT_USER_EMAIL
        :param author_name: (experimental) Author's name. Default: $GIT_USER_NAME
        :param version: (experimental) Version of the package. Default: "0.1.0"
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package.
        :param homepage: (experimental) A URL to the website of the project.
        :param license: (experimental) License of this package as an SPDX identifier.
        :param poetry_options: (experimental) Additional options to set for poetry if using poetry.
        :param setup_config: (experimental) Additional fields to pass in the setup() function if using setuptools.

        :stability: experimental
        '''
        if isinstance(poetry_options, dict):
            poetry_options = PoetryPyprojectOptionsWithoutDeps(**poetry_options)
        self._values: typing.Dict[str, typing.Any] = {
            "author_email": author_email,
            "author_name": author_name,
            "version": version,
        }
        if classifiers is not None:
            self._values["classifiers"] = classifiers
        if description is not None:
            self._values["description"] = description
        if homepage is not None:
            self._values["homepage"] = homepage
        if license is not None:
            self._values["license"] = license
        if poetry_options is not None:
            self._values["poetry_options"] = poetry_options
        if setup_config is not None:
            self._values["setup_config"] = setup_config

    @builtins.property
    def author_email(self) -> builtins.str:
        '''(experimental) Author's e-mail.

        :default: $GIT_USER_EMAIL

        :stability: experimental
        '''
        result = self._values.get("author_email")
        assert result is not None, "Required property 'author_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def author_name(self) -> builtins.str:
        '''(experimental) Author's name.

        :default: $GIT_USER_NAME

        :stability: experimental
        '''
        result = self._values.get("author_name")
        assert result is not None, "Required property 'author_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) Version of the package.

        :default: "0.1.0"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of PyPI trove classifiers that describe the project.

        :see: https://pypi.org/classifiers/
        :stability: experimental
        '''
        result = self._values.get("classifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A short description of the package.

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) A URL to the website of the project.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License of this package as an SPDX identifier.

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def poetry_options(self) -> typing.Optional[PoetryPyprojectOptionsWithoutDeps]:
        '''(experimental) Additional options to set for poetry if using poetry.

        :stability: experimental
        '''
        result = self._values.get("poetry_options")
        return typing.cast(typing.Optional[PoetryPyprojectOptionsWithoutDeps], result)

    @builtins.property
    def setup_config(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional fields to pass in the setup() function if using setuptools.

        :stability: experimental
        '''
        result = self._values.get("setup_config")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PythonPackagingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PythonProject(
    _GitHubProject_c48bc7ea,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.python.PythonProject",
):
    '''(experimental) Python project.

    :stability: experimental
    :pjid: python
    '''

    def __init__(
        self,
        *,
        module_name: builtins.str,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pip: typing.Optional[builtins.bool] = None,
        poetry: typing.Optional[builtins.bool] = None,
        projenrc_python: typing.Optional[builtins.bool] = None,
        projenrc_python_options: typing.Optional[ProjenrcOptions] = None,
        pytest: typing.Optional[builtins.bool] = None,
        pytest_options: typing.Optional[PytestOptions] = None,
        sample: typing.Optional[builtins.bool] = None,
        setuptools: typing.Optional[builtins.bool] = None,
        venv: typing.Optional[builtins.bool] = None,
        venv_options: typing.Optional["VenvOptions"] = None,
        auto_approve_options: typing.Optional[_AutoApproveOptions_dac86cbe] = None,
        auto_merge_options: typing.Optional[_AutoMergeOptions_d112cd3c] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[_GitHubOptions_21553699] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[_MergifyOptions_a6faaab3] = None,
        project_type: typing.Optional[_ProjectType_fd80c725] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[_SampleReadmeProps_3518b03b] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[_StaleOptions_929db764] = None,
        vscode: typing.Optional[builtins.bool] = None,
        author_email: builtins.str,
        author_name: builtins.str,
        version: builtins.str,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        poetry_options: typing.Optional[PoetryPyprojectOptionsWithoutDeps] = None,
        setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        name: builtins.str,
        logging: typing.Optional[_LoggerOptions_eb0f6309] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_Project_57d89203] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[_ProjenrcOptions_164bd039] = None,
    ) -> None:
        '''
        :param module_name: (experimental) Name of the python package as used in imports and filenames. Must only consist of alphanumeric characters and underscores. Default: $PYTHON_MODULE_NAME
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param dev_deps: (experimental) List of dev dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDevDependency()``. Default: []
        :param pip: (experimental) Use pip with a requirements.txt file to track project dependencies. Default: true
        :param poetry: (experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing. Default: false
        :param projenrc_python: (experimental) Use projenrc in python. This will install ``projen`` as a python dependency and will add a ``synth`` task which will run ``.projenrc.py``. Default: true
        :param projenrc_python_options: (experimental) Options related to projenrc in python. Default: - default options
        :param pytest: (experimental) Include pytest tests. Default: true
        :param pytest_options: (experimental) pytest options. Default: - defaults
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist. Default: true
        :param setuptools: (experimental) Use setuptools with a setup.py script for packaging and publishing. Default: - true if the project type is library
        :param venv: (experimental) Use venv to manage a virtual environment for installing dependencies inside. Default: true
        :param venv_options: (experimental) Venv options. Default: - defaults
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param author_email: (experimental) Author's e-mail. Default: $GIT_USER_EMAIL
        :param author_name: (experimental) Author's name. Default: $GIT_USER_NAME
        :param version: (experimental) Version of the package. Default: "0.1.0"
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package.
        :param homepage: (experimental) A URL to the website of the project.
        :param license: (experimental) License of this package as an SPDX identifier.
        :param poetry_options: (experimental) Additional options to set for poetry if using poetry.
        :param setup_config: (experimental) Additional fields to pass in the setup() function if using setuptools.
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options

        :stability: experimental
        '''
        options = PythonProjectOptions(
            module_name=module_name,
            deps=deps,
            dev_deps=dev_deps,
            pip=pip,
            poetry=poetry,
            projenrc_python=projenrc_python,
            projenrc_python_options=projenrc_python_options,
            pytest=pytest,
            pytest_options=pytest_options,
            sample=sample,
            setuptools=setuptools,
            venv=venv,
            venv_options=venv_options,
            auto_approve_options=auto_approve_options,
            auto_merge_options=auto_merge_options,
            clobber=clobber,
            dev_container=dev_container,
            github=github,
            github_options=github_options,
            gitpod=gitpod,
            mergify=mergify,
            mergify_options=mergify_options,
            project_type=project_type,
            projen_token_secret=projen_token_secret,
            readme=readme,
            stale=stale,
            stale_options=stale_options,
            vscode=vscode,
            author_email=author_email,
            author_name=author_name,
            version=version,
            classifiers=classifiers,
            description=description,
            homepage=homepage,
            license=license,
            poetry_options=poetry_options,
            setup_config=setup_config,
            name=name,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="addDependency")
    def add_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a runtime dependency.

        :param spec: Format ``<module>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDependency", [spec]))

    @jsii.member(jsii_name="addDevDependency")
    def add_dev_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a dev dependency.

        :param spec: Format ``<module>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDevDependency", [spec]))

    @jsii.member(jsii_name="postSynthesize")
    def post_synthesize(self) -> None:
        '''(experimental) Called after all components are synthesized.

        Order is *not* guaranteed.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "postSynthesize", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="depsManager")
    def deps_manager(self) -> IPythonDeps:
        '''(experimental) API for managing dependencies.

        :stability: experimental
        '''
        return typing.cast(IPythonDeps, jsii.get(self, "depsManager"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="envManager")
    def env_manager(self) -> IPythonEnv:
        '''(experimental) API for mangaging the Python runtime environment.

        :stability: experimental
        '''
        return typing.cast(IPythonEnv, jsii.get(self, "envManager"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="moduleName")
    def module_name(self) -> builtins.str:
        '''(experimental) Python module name (the project name, with any hyphens or periods replaced with underscores).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "moduleName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''(experimental) Version of the package for distribution (should follow semver).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="packagingManager")
    def packaging_manager(self) -> typing.Optional[IPythonPackaging]:
        '''(experimental) API for managing packaging the project as a library.

        Only applies when the ``projectType`` is LIB.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IPythonPackaging], jsii.get(self, "packagingManager"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pytest")
    def pytest(self) -> typing.Optional[Pytest]:
        '''(experimental) Pytest component.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[Pytest], jsii.get(self, "pytest"))


@jsii.data_type(
    jsii_type="projen.python.PythonProjectOptions",
    jsii_struct_bases=[_GitHubProjectOptions_547f2d08, PythonPackagingOptions],
    name_mapping={
        "name": "name",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "auto_approve_options": "autoApproveOptions",
        "auto_merge_options": "autoMergeOptions",
        "clobber": "clobber",
        "dev_container": "devContainer",
        "github": "github",
        "github_options": "githubOptions",
        "gitpod": "gitpod",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "project_type": "projectType",
        "projen_token_secret": "projenTokenSecret",
        "readme": "readme",
        "stale": "stale",
        "stale_options": "staleOptions",
        "vscode": "vscode",
        "author_email": "authorEmail",
        "author_name": "authorName",
        "version": "version",
        "classifiers": "classifiers",
        "description": "description",
        "homepage": "homepage",
        "license": "license",
        "poetry_options": "poetryOptions",
        "setup_config": "setupConfig",
        "module_name": "moduleName",
        "deps": "deps",
        "dev_deps": "devDeps",
        "pip": "pip",
        "poetry": "poetry",
        "projenrc_python": "projenrcPython",
        "projenrc_python_options": "projenrcPythonOptions",
        "pytest": "pytest",
        "pytest_options": "pytestOptions",
        "sample": "sample",
        "setuptools": "setuptools",
        "venv": "venv",
        "venv_options": "venvOptions",
    },
)
class PythonProjectOptions(_GitHubProjectOptions_547f2d08, PythonPackagingOptions):
    def __init__(
        self,
        *,
        name: builtins.str,
        logging: typing.Optional[_LoggerOptions_eb0f6309] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_Project_57d89203] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[_ProjenrcOptions_164bd039] = None,
        auto_approve_options: typing.Optional[_AutoApproveOptions_dac86cbe] = None,
        auto_merge_options: typing.Optional[_AutoMergeOptions_d112cd3c] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[_GitHubOptions_21553699] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[_MergifyOptions_a6faaab3] = None,
        project_type: typing.Optional[_ProjectType_fd80c725] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[_SampleReadmeProps_3518b03b] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[_StaleOptions_929db764] = None,
        vscode: typing.Optional[builtins.bool] = None,
        author_email: builtins.str,
        author_name: builtins.str,
        version: builtins.str,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        poetry_options: typing.Optional[PoetryPyprojectOptionsWithoutDeps] = None,
        setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        module_name: builtins.str,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pip: typing.Optional[builtins.bool] = None,
        poetry: typing.Optional[builtins.bool] = None,
        projenrc_python: typing.Optional[builtins.bool] = None,
        projenrc_python_options: typing.Optional[ProjenrcOptions] = None,
        pytest: typing.Optional[builtins.bool] = None,
        pytest_options: typing.Optional[PytestOptions] = None,
        sample: typing.Optional[builtins.bool] = None,
        setuptools: typing.Optional[builtins.bool] = None,
        venv: typing.Optional[builtins.bool] = None,
        venv_options: typing.Optional["VenvOptions"] = None,
    ) -> None:
        '''(experimental) Options for ``PythonProject``.

        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param author_email: (experimental) Author's e-mail. Default: $GIT_USER_EMAIL
        :param author_name: (experimental) Author's name. Default: $GIT_USER_NAME
        :param version: (experimental) Version of the package. Default: "0.1.0"
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package.
        :param homepage: (experimental) A URL to the website of the project.
        :param license: (experimental) License of this package as an SPDX identifier.
        :param poetry_options: (experimental) Additional options to set for poetry if using poetry.
        :param setup_config: (experimental) Additional fields to pass in the setup() function if using setuptools.
        :param module_name: (experimental) Name of the python package as used in imports and filenames. Must only consist of alphanumeric characters and underscores. Default: $PYTHON_MODULE_NAME
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param dev_deps: (experimental) List of dev dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDevDependency()``. Default: []
        :param pip: (experimental) Use pip with a requirements.txt file to track project dependencies. Default: true
        :param poetry: (experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing. Default: false
        :param projenrc_python: (experimental) Use projenrc in python. This will install ``projen`` as a python dependency and will add a ``synth`` task which will run ``.projenrc.py``. Default: true
        :param projenrc_python_options: (experimental) Options related to projenrc in python. Default: - default options
        :param pytest: (experimental) Include pytest tests. Default: true
        :param pytest_options: (experimental) pytest options. Default: - defaults
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist. Default: true
        :param setuptools: (experimental) Use setuptools with a setup.py script for packaging and publishing. Default: - true if the project type is library
        :param venv: (experimental) Use venv to manage a virtual environment for installing dependencies inside. Default: true
        :param venv_options: (experimental) Venv options. Default: - defaults

        :stability: experimental
        '''
        if isinstance(logging, dict):
            logging = _LoggerOptions_eb0f6309(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = _ProjenrcOptions_164bd039(**projenrc_json_options)
        if isinstance(auto_approve_options, dict):
            auto_approve_options = _AutoApproveOptions_dac86cbe(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = _AutoMergeOptions_d112cd3c(**auto_merge_options)
        if isinstance(github_options, dict):
            github_options = _GitHubOptions_21553699(**github_options)
        if isinstance(mergify_options, dict):
            mergify_options = _MergifyOptions_a6faaab3(**mergify_options)
        if isinstance(readme, dict):
            readme = _SampleReadmeProps_3518b03b(**readme)
        if isinstance(stale_options, dict):
            stale_options = _StaleOptions_929db764(**stale_options)
        if isinstance(poetry_options, dict):
            poetry_options = PoetryPyprojectOptionsWithoutDeps(**poetry_options)
        if isinstance(projenrc_python_options, dict):
            projenrc_python_options = ProjenrcOptions(**projenrc_python_options)
        if isinstance(pytest_options, dict):
            pytest_options = PytestOptions(**pytest_options)
        if isinstance(venv_options, dict):
            venv_options = VenvOptions(**venv_options)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "author_email": author_email,
            "author_name": author_name,
            "version": version,
            "module_name": module_name,
        }
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if clobber is not None:
            self._values["clobber"] = clobber
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if readme is not None:
            self._values["readme"] = readme
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if vscode is not None:
            self._values["vscode"] = vscode
        if classifiers is not None:
            self._values["classifiers"] = classifiers
        if description is not None:
            self._values["description"] = description
        if homepage is not None:
            self._values["homepage"] = homepage
        if license is not None:
            self._values["license"] = license
        if poetry_options is not None:
            self._values["poetry_options"] = poetry_options
        if setup_config is not None:
            self._values["setup_config"] = setup_config
        if deps is not None:
            self._values["deps"] = deps
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if pip is not None:
            self._values["pip"] = pip
        if poetry is not None:
            self._values["poetry"] = poetry
        if projenrc_python is not None:
            self._values["projenrc_python"] = projenrc_python
        if projenrc_python_options is not None:
            self._values["projenrc_python_options"] = projenrc_python_options
        if pytest is not None:
            self._values["pytest"] = pytest
        if pytest_options is not None:
            self._values["pytest_options"] = pytest_options
        if sample is not None:
            self._values["sample"] = sample
        if setuptools is not None:
            self._values["setuptools"] = setuptools
        if venv is not None:
            self._values["venv"] = venv
        if venv_options is not None:
            self._values["venv_options"] = venv_options

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logging(self) -> typing.Optional[_LoggerOptions_eb0f6309]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_LoggerOptions_eb0f6309], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[_Project_57d89203]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[_Project_57d89203], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(self) -> typing.Optional[_ProjenrcOptions_164bd039]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[_ProjenrcOptions_164bd039], result)

    @builtins.property
    def auto_approve_options(self) -> typing.Optional[_AutoApproveOptions_dac86cbe]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[_AutoApproveOptions_dac86cbe], result)

    @builtins.property
    def auto_merge_options(self) -> typing.Optional[_AutoMergeOptions_d112cd3c]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[_AutoMergeOptions_d112cd3c], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[_GitHubOptions_21553699]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[_GitHubOptions_21553699], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(self) -> typing.Optional[_MergifyOptions_a6faaab3]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[_MergifyOptions_a6faaab3], result)

    @builtins.property
    def project_type(self) -> typing.Optional[_ProjectType_fd80c725]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[_ProjectType_fd80c725], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme(self) -> typing.Optional[_SampleReadmeProps_3518b03b]:
        '''(experimental) The README setup.

        :default: - { filename: 'README.md', contents: '# replace this' }

        :stability: experimental

        Example::

            "{ filename: 'readme.md', contents: '# title' }"
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[_SampleReadmeProps_3518b03b], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[_StaleOptions_929db764]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[_StaleOptions_929db764], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_email(self) -> builtins.str:
        '''(experimental) Author's e-mail.

        :default: $GIT_USER_EMAIL

        :stability: experimental
        '''
        result = self._values.get("author_email")
        assert result is not None, "Required property 'author_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def author_name(self) -> builtins.str:
        '''(experimental) Author's name.

        :default: $GIT_USER_NAME

        :stability: experimental
        '''
        result = self._values.get("author_name")
        assert result is not None, "Required property 'author_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) Version of the package.

        :default: "0.1.0"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of PyPI trove classifiers that describe the project.

        :see: https://pypi.org/classifiers/
        :stability: experimental
        '''
        result = self._values.get("classifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A short description of the package.

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) A URL to the website of the project.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License of this package as an SPDX identifier.

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def poetry_options(self) -> typing.Optional[PoetryPyprojectOptionsWithoutDeps]:
        '''(experimental) Additional options to set for poetry if using poetry.

        :stability: experimental
        '''
        result = self._values.get("poetry_options")
        return typing.cast(typing.Optional[PoetryPyprojectOptionsWithoutDeps], result)

    @builtins.property
    def setup_config(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional fields to pass in the setup() function if using setuptools.

        :stability: experimental
        '''
        result = self._values.get("setup_config")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def module_name(self) -> builtins.str:
        '''(experimental) Name of the python package as used in imports and filenames.

        Must only consist of alphanumeric characters and underscores.

        :default: $PYTHON_MODULE_NAME

        :stability: experimental
        '''
        result = self._values.get("module_name")
        assert result is not None, "Required property 'module_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of runtime dependencies for this project.

        Dependencies use the format: ``<module>@<semver>``

        Additional dependencies can be added via ``project.addDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dev dependencies for this project.

        Dependencies use the format: ``<module>@<semver>``

        Additional dependencies can be added via ``project.addDevDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pip(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use pip with a requirements.txt file to track project dependencies.

        :default: true

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("pip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def poetry(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing.

        :default: false

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("poetry")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_python(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use projenrc in python.

        This will install ``projen`` as a python dependency and will add a ``synth``
        task which will run ``.projenrc.py``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projenrc_python")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_python_options(self) -> typing.Optional[ProjenrcOptions]:
        '''(experimental) Options related to projenrc in python.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_python_options")
        return typing.cast(typing.Optional[ProjenrcOptions], result)

    @builtins.property
    def pytest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include pytest tests.

        :default: true

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("pytest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pytest_options(self) -> typing.Optional[PytestOptions]:
        '''(experimental) pytest options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("pytest_options")
        return typing.cast(typing.Optional[PytestOptions], result)

    @builtins.property
    def sample(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include sample code and test if the relevant directories don't exist.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def setuptools(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use setuptools with a setup.py script for packaging and publishing.

        :default: - true if the project type is library

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("setuptools")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def venv(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use venv to manage a virtual environment for installing dependencies inside.

        :default: true

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("venv")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def venv_options(self) -> typing.Optional["VenvOptions"]:
        '''(experimental) Venv options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("venv_options")
        return typing.cast(typing.Optional["VenvOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PythonProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PythonSample(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.python.PythonSample",
):
    '''(experimental) Python code sample.

    :stability: experimental
    '''

    def __init__(self, project: PythonProject) -> None:
        '''
        :param project: -

        :stability: experimental
        '''
        _options = PythonSampleOptions()

        jsii.create(self.__class__, self, [project, _options])


@jsii.data_type(
    jsii_type="projen.python.PythonSampleOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class PythonSampleOptions:
    def __init__(self) -> None:
        '''(experimental) Options for python sample code.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PythonSampleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RequirementsFile(
    _FileBase_aff596dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.python.RequirementsFile",
):
    '''(experimental) Specifies a list of packages to be installed using pip.

    :see: https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format
    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        file_path: builtins.str,
        *,
        package_provider: typing.Optional[IPackageProvider] = None,
    ) -> None:
        '''
        :param project: -
        :param file_path: -
        :param package_provider: (experimental) Provide a list of packages that can be dynamically updated.

        :stability: experimental
        '''
        options = RequirementsFileOptions(package_provider=package_provider)

        jsii.create(self.__class__, self, [project, file_path, options])

    @jsii.member(jsii_name="addPackages")
    def add_packages(self, *packages: builtins.str) -> None:
        '''(experimental) Adds the specified packages provided in semver format.

        Comment lines (start with ``#``) are ignored.

        :param packages: Package version in format ``<module>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addPackages", [*packages]))

    @jsii.member(jsii_name="synthesizeContent")
    def _synthesize_content(
        self,
        resolver: _IResolver_0b7d1958,
    ) -> typing.Optional[builtins.str]:
        '''(experimental) Implemented by derived classes and returns the contents of the file to emit.

        :param resolver: -

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "synthesizeContent", [resolver]))


@jsii.data_type(
    jsii_type="projen.python.RequirementsFileOptions",
    jsii_struct_bases=[],
    name_mapping={"package_provider": "packageProvider"},
)
class RequirementsFileOptions:
    def __init__(
        self,
        *,
        package_provider: typing.Optional[IPackageProvider] = None,
    ) -> None:
        '''
        :param package_provider: (experimental) Provide a list of packages that can be dynamically updated.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if package_provider is not None:
            self._values["package_provider"] = package_provider

    @builtins.property
    def package_provider(self) -> typing.Optional[IPackageProvider]:
        '''(experimental) Provide a list of packages that can be dynamically updated.

        :stability: experimental
        '''
        result = self._values.get("package_provider")
        return typing.cast(typing.Optional[IPackageProvider], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RequirementsFileOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SetupPy(
    _FileBase_aff596dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.python.SetupPy",
):
    '''(experimental) Python packaging script where package metadata can be placed.

    :stability: experimental
    '''

    def __init__(
        self,
        project: PythonProject,
        *,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short project description.
        :param homepage: (experimental) Package's Homepage / Website.
        :param license: (experimental) The project license.
        :param name: (experimental) Name of the package.
        :param packages: (experimental) List of submodules to be packaged.
        :param version: (experimental) Manually specify package version.

        :stability: experimental
        '''
        options = SetupPyOptions(
            author_email=author_email,
            author_name=author_name,
            classifiers=classifiers,
            description=description,
            homepage=homepage,
            license=license,
            name=name,
            packages=packages,
            version=version,
        )

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="synthesizeContent")
    def _synthesize_content(
        self,
        resolver: _IResolver_0b7d1958,
    ) -> typing.Optional[builtins.str]:
        '''(experimental) Implemented by derived classes and returns the contents of the file to emit.

        :param resolver: -

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "synthesizeContent", [resolver]))


@jsii.data_type(
    jsii_type="projen.python.SetupPyOptions",
    jsii_struct_bases=[],
    name_mapping={
        "author_email": "authorEmail",
        "author_name": "authorName",
        "classifiers": "classifiers",
        "description": "description",
        "homepage": "homepage",
        "license": "license",
        "name": "name",
        "packages": "packages",
        "version": "version",
    },
)
class SetupPyOptions:
    def __init__(
        self,
        *,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Fields to pass in the setup() function of setup.py.

        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short project description.
        :param homepage: (experimental) Package's Homepage / Website.
        :param license: (experimental) The project license.
        :param name: (experimental) Name of the package.
        :param packages: (experimental) List of submodules to be packaged.
        :param version: (experimental) Manually specify package version.

        :see: https://docs.python.org/3/distutils/setupscript.html
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if author_email is not None:
            self._values["author_email"] = author_email
        if author_name is not None:
            self._values["author_name"] = author_name
        if classifiers is not None:
            self._values["classifiers"] = classifiers
        if description is not None:
            self._values["description"] = description
        if homepage is not None:
            self._values["homepage"] = homepage
        if license is not None:
            self._values["license"] = license
        if name is not None:
            self._values["name"] = name
        if packages is not None:
            self._values["packages"] = packages
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def author_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's e-mail.

        :stability: experimental
        '''
        result = self._values.get("author_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's name.

        :stability: experimental
        '''
        result = self._values.get("author_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of PyPI trove classifiers that describe the project.

        :see: https://pypi.org/classifiers/
        :stability: experimental
        '''
        result = self._values.get("classifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A short project description.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Homepage / Website.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) The project license.

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the package.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of submodules to be packaged.

        :stability: experimental
        '''
        result = self._values.get("packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Manually specify package version.

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SetupPyOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPythonPackaging)
class Setuptools(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.python.Setuptools",
):
    '''(experimental) Manages packaging through setuptools with a setup.py script.

    :stability: experimental
    '''

    def __init__(
        self,
        project: PythonProject,
        *,
        author_email: builtins.str,
        author_name: builtins.str,
        version: builtins.str,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        poetry_options: typing.Optional[PoetryPyprojectOptionsWithoutDeps] = None,
        setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param project: -
        :param author_email: (experimental) Author's e-mail. Default: $GIT_USER_EMAIL
        :param author_name: (experimental) Author's name. Default: $GIT_USER_NAME
        :param version: (experimental) Version of the package. Default: "0.1.0"
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package.
        :param homepage: (experimental) A URL to the website of the project.
        :param license: (experimental) License of this package as an SPDX identifier.
        :param poetry_options: (experimental) Additional options to set for poetry if using poetry.
        :param setup_config: (experimental) Additional fields to pass in the setup() function if using setuptools.

        :stability: experimental
        '''
        options = PythonPackagingOptions(
            author_email=author_email,
            author_name=author_name,
            version=version,
            classifiers=classifiers,
            description=description,
            homepage=homepage,
            license=license,
            poetry_options=poetry_options,
            setup_config=setup_config,
        )

        jsii.create(self.__class__, self, [project, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishTask")
    def publish_task(self) -> _Task_9fa875b6:
        '''(experimental) A task that uploads the package to a package repository.

        :stability: experimental
        '''
        return typing.cast(_Task_9fa875b6, jsii.get(self, "publishTask"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishTestTask")
    def publish_test_task(self) -> _Task_9fa875b6:
        '''(experimental) A task that uploads the package to the Test PyPI repository.

        :stability: experimental
        '''
        return typing.cast(_Task_9fa875b6, jsii.get(self, "publishTestTask"))


@jsii.implements(IPythonEnv)
class Venv(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.python.Venv",
):
    '''(experimental) Manages a virtual environment through the Python venv module.

    :stability: experimental
    '''

    def __init__(
        self,
        project: PythonProject,
        *,
        envdir: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param envdir: (experimental) Name of directory to store the environment in. Default: ".env"

        :stability: experimental
        '''
        options = VenvOptions(envdir=envdir)

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="setupEnvironment")
    def setup_environment(self) -> None:
        '''(experimental) Initializes the virtual environment if it doesn't exist (called during post-synthesis).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "setupEnvironment", []))


@jsii.data_type(
    jsii_type="projen.python.VenvOptions",
    jsii_struct_bases=[],
    name_mapping={"envdir": "envdir"},
)
class VenvOptions:
    def __init__(self, *, envdir: typing.Optional[builtins.str] = None) -> None:
        '''(experimental) Options for venv.

        :param envdir: (experimental) Name of directory to store the environment in. Default: ".env"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if envdir is not None:
            self._values["envdir"] = envdir

    @builtins.property
    def envdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of directory to store the environment in.

        :default: ".env"

        :stability: experimental
        '''
        result = self._values.get("envdir")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VenvOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.python.PoetryPyprojectOptions",
    jsii_struct_bases=[PoetryPyprojectOptionsWithoutDeps],
    name_mapping={
        "authors": "authors",
        "classifiers": "classifiers",
        "description": "description",
        "documentation": "documentation",
        "exclude": "exclude",
        "extras": "extras",
        "homepage": "homepage",
        "include": "include",
        "keywords": "keywords",
        "license": "license",
        "maintainers": "maintainers",
        "name": "name",
        "packages": "packages",
        "plugins": "plugins",
        "readme": "readme",
        "repository": "repository",
        "scripts": "scripts",
        "source": "source",
        "urls": "urls",
        "version": "version",
        "dependencies": "dependencies",
        "dev_dependencies": "devDependencies",
    },
)
class PoetryPyprojectOptions(PoetryPyprojectOptionsWithoutDeps):
    def __init__(
        self,
        *,
        authors: typing.Optional[typing.Sequence[builtins.str]] = None,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        documentation: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        extras: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        homepage: typing.Optional[builtins.str] = None,
        include: typing.Optional[typing.Sequence[builtins.str]] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        maintainers: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        packages: typing.Optional[typing.Sequence[typing.Any]] = None,
        plugins: typing.Any = None,
        readme: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        source: typing.Optional[typing.Sequence[typing.Any]] = None,
        urls: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
        dependencies: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dev_dependencies: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''(experimental) Poetry-specific options.

        :param authors: (experimental) The authors of the package. Must be in the form "name "
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package (required).
        :param documentation: (experimental) A URL to the documentation of the project.
        :param exclude: (experimental) A list of patterns that will be excluded in the final package. If a VCS is being used for a package, the exclude field will be seeded with the VCS’ ignore settings (.gitignore for git for example).
        :param extras: (experimental) Package extras.
        :param homepage: (experimental) A URL to the website of the project.
        :param include: (experimental) A list of patterns that will be included in the final package.
        :param keywords: (experimental) A list of keywords (max: 5) that the package is related to.
        :param license: (experimental) License of this package as an SPDX identifier. If the project is proprietary and does not use a specific license, you can set this value as "Proprietary".
        :param maintainers: (experimental) the maintainers of the package. Must be in the form "name "
        :param name: (experimental) Name of the package (required).
        :param packages: (experimental) A list of packages and modules to include in the final distribution.
        :param plugins: (experimental) Plugins. Must be specified as a table.
        :param readme: (experimental) The name of the readme file of the package.
        :param repository: (experimental) A URL to the repository of the project.
        :param scripts: (experimental) The scripts or executables that will be installed when installing the package.
        :param source: (experimental) Source registries from which packages are retrieved.
        :param urls: (experimental) Project custom URLs, in addition to homepage, repository and documentation. E.g. "Bug Tracker"
        :param version: (experimental) Version of the package (required).
        :param dependencies: (experimental) A list of dependencies for the project. The python version for which your package is compatible is also required.
        :param dev_dependencies: (experimental) A list of development dependencies for the project.

        :see: https://python-poetry.org/docs/pyproject/
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if authors is not None:
            self._values["authors"] = authors
        if classifiers is not None:
            self._values["classifiers"] = classifiers
        if description is not None:
            self._values["description"] = description
        if documentation is not None:
            self._values["documentation"] = documentation
        if exclude is not None:
            self._values["exclude"] = exclude
        if extras is not None:
            self._values["extras"] = extras
        if homepage is not None:
            self._values["homepage"] = homepage
        if include is not None:
            self._values["include"] = include
        if keywords is not None:
            self._values["keywords"] = keywords
        if license is not None:
            self._values["license"] = license
        if maintainers is not None:
            self._values["maintainers"] = maintainers
        if name is not None:
            self._values["name"] = name
        if packages is not None:
            self._values["packages"] = packages
        if plugins is not None:
            self._values["plugins"] = plugins
        if readme is not None:
            self._values["readme"] = readme
        if repository is not None:
            self._values["repository"] = repository
        if scripts is not None:
            self._values["scripts"] = scripts
        if source is not None:
            self._values["source"] = source
        if urls is not None:
            self._values["urls"] = urls
        if version is not None:
            self._values["version"] = version
        if dependencies is not None:
            self._values["dependencies"] = dependencies
        if dev_dependencies is not None:
            self._values["dev_dependencies"] = dev_dependencies

    @builtins.property
    def authors(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The authors of the package.

        Must be in the form "name "

        :stability: experimental
        '''
        result = self._values.get("authors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of PyPI trove classifiers that describe the project.

        :see: https://pypi.org/classifiers/
        :stability: experimental
        '''
        result = self._values.get("classifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A short description of the package (required).

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def documentation(self) -> typing.Optional[builtins.str]:
        '''(experimental) A URL to the documentation of the project.

        :stability: experimental
        '''
        result = self._values.get("documentation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of patterns that will be excluded in the final package.

        If a VCS is being used for a package, the exclude field will be seeded with
        the VCS’ ignore settings (.gitignore for git for example).

        :stability: experimental
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def extras(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        '''(experimental) Package extras.

        :stability: experimental
        '''
        result = self._values.get("extras")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) A URL to the website of the project.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of patterns that will be included in the final package.

        :stability: experimental
        '''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of keywords (max: 5) that the package is related to.

        :stability: experimental
        '''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License of this package as an SPDX identifier.

        If the project is proprietary and does not use a specific license, you
        can set this value as "Proprietary".

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintainers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) the maintainers of the package.

        Must be in the form "name "

        :stability: experimental
        '''
        result = self._values.get("maintainers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the package (required).

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def packages(self) -> typing.Optional[typing.List[typing.Any]]:
        '''(experimental) A list of packages and modules to include in the final distribution.

        :stability: experimental
        '''
        result = self._values.get("packages")
        return typing.cast(typing.Optional[typing.List[typing.Any]], result)

    @builtins.property
    def plugins(self) -> typing.Any:
        '''(experimental) Plugins.

        Must be specified as a table.

        :see: https://toml.io/en/v1.0.0#table
        :stability: experimental
        '''
        result = self._values.get("plugins")
        return typing.cast(typing.Any, result)

    @builtins.property
    def readme(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the readme file of the package.

        :stability: experimental
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) A URL to the repository of the project.

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scripts(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) The scripts or executables that will be installed when installing the package.

        :stability: experimental
        '''
        result = self._values.get("scripts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def source(self) -> typing.Optional[typing.List[typing.Any]]:
        '''(experimental) Source registries from which packages are retrieved.

        :stability: experimental
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[typing.List[typing.Any]], result)

    @builtins.property
    def urls(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Project custom URLs, in addition to homepage, repository and documentation.

        E.g. "Bug Tracker"

        :stability: experimental
        '''
        result = self._values.get("urls")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of the package (required).

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependencies(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) A list of dependencies for the project.

        The python version for which your package is compatible is also required.

        :stability: experimental

        Example::

            { requests: "^2.13.0" }
        '''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def dev_dependencies(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) A list of development dependencies for the project.

        :stability: experimental

        Example::

            { requests: "^2.13.0" }
        '''
        result = self._values.get("dev_dependencies")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PoetryPyprojectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IPackageProvider",
    "IPythonDeps",
    "IPythonEnv",
    "IPythonPackaging",
    "Pip",
    "PipOptions",
    "Poetry",
    "PoetryPyproject",
    "PoetryPyprojectOptions",
    "PoetryPyprojectOptionsWithoutDeps",
    "Projenrc",
    "ProjenrcOptions",
    "Pytest",
    "PytestOptions",
    "PythonPackagingOptions",
    "PythonProject",
    "PythonProjectOptions",
    "PythonSample",
    "PythonSampleOptions",
    "RequirementsFile",
    "RequirementsFileOptions",
    "SetupPy",
    "SetupPyOptions",
    "Setuptools",
    "Venv",
    "VenvOptions",
]

publication.publish()
