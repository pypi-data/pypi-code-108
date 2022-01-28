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
    LoggerOptions as _LoggerOptions_eb0f6309,
    Project as _Project_57d89203,
    ProjectType as _ProjectType_fd80c725,
    ProjenrcOptions as _ProjenrcOptions_164bd039,
    SampleReadmeProps as _SampleReadmeProps_3518b03b,
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


class JavaProject(
    _GitHubProject_c48bc7ea,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.java.JavaProject",
):
    '''(experimental) Java project.

    :stability: experimental
    :pjid: java
    '''

    def __init__(
        self,
        *,
        sample: typing.Optional[builtins.bool] = None,
        sample_java_package: typing.Optional[builtins.str] = None,
        compile_options: typing.Optional["MavenCompileOptions"] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        distdir: typing.Optional[builtins.str] = None,
        junit: typing.Optional[builtins.bool] = None,
        junit_options: typing.Optional["JunitOptions"] = None,
        packaging_options: typing.Optional["MavenPackagingOptions"] = None,
        projenrc_java: typing.Optional[builtins.bool] = None,
        projenrc_java_options: typing.Optional["ProjenrcOptions"] = None,
        test_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
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
        artifact_id: builtins.str,
        group_id: builtins.str,
        version: builtins.str,
        description: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        name: builtins.str,
        logging: typing.Optional[_LoggerOptions_eb0f6309] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_Project_57d89203] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[_ProjenrcOptions_164bd039] = None,
    ) -> None:
        '''
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist. Default: true
        :param sample_java_package: (experimental) The java package to use for the code sample. Default: "org.acme"
        :param compile_options: (experimental) Compile options. Default: - defaults
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<groupId>/<artifactId>@<semver>`` Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param distdir: (experimental) Final artifact output directory. Default: "dist/java"
        :param junit: (experimental) Include junit tests. Default: true
        :param junit_options: (experimental) junit options. Default: - defaults
        :param packaging_options: (experimental) Packaging options. Default: - defaults
        :param projenrc_java: (experimental) Use projenrc in java. This will install ``projen`` as a java dependency and will add a ``synth`` task which will compile & execute ``main()`` from ``src/main/java/projenrc.java``. Default: true
        :param projenrc_java_options: (experimental) Options related to projenrc in java. Default: - default options
        :param test_deps: (experimental) List of test dependencies for this project. Dependencies use the format: ``<groupId>/<artifactId>@<semver>`` Additional dependencies can be added via ``project.addTestDependency()``. Default: []
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
        :param artifact_id: (experimental) The artifactId is generally the name that the project is known by. Although the groupId is important, people within the group will rarely mention the groupId in discussion (they are often all be the same ID, such as the MojoHaus project groupId: org.codehaus.mojo). It, along with the groupId, creates a key that separates this project from every other project in the world (at least, it should :) ). Along with the groupId, the artifactId fully defines the artifact's living quarters within the repository. In the case of the above project, my-project lives in $M2_REPO/org/codehaus/mojo/my-project. Default: "my-app"
        :param group_id: (experimental) This is generally unique amongst an organization or a project. For example, all core Maven artifacts do (well, should) live under the groupId org.apache.maven. Group ID's do not necessarily use the dot notation, for example, the junit project. Note that the dot-notated groupId does not have to correspond to the package structure that the project contains. It is, however, a good practice to follow. When stored within a repository, the group acts much like the Java packaging structure does in an operating system. The dots are replaced by OS specific directory separators (such as '/' in Unix) which becomes a relative directory structure from the base repository. In the example given, the org.codehaus.mojo group lives within the directory $M2_REPO/org/codehaus/mojo. Default: "org.acme"
        :param version: (experimental) This is the last piece of the naming puzzle. groupId:artifactId denotes a single project but they cannot delineate which incarnation of that project we are talking about. Do we want the junit:junit of 2018 (version 4.12), or of 2007 (version 3.8.2)? In short: code changes, those changes should be versioned, and this element keeps those versions in line. It is also used within an artifact's repository to separate versions from each other. my-project version 1.0 files live in the directory structure $M2_REPO/org/codehaus/mojo/my-project/1.0. Default: "0.1.0"
        :param description: (experimental) Description of a project is always good. Although this should not replace formal documentation, a quick comment to any readers of the POM is always helpful. Default: undefined
        :param packaging: (experimental) Project packaging format. Default: "jar"
        :param url: (experimental) The URL, like the name, is not required. This is a nice gesture for projects users, however, so that they know where the project lives. Default: undefined
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options

        :stability: experimental
        '''
        options = JavaProjectOptions(
            sample=sample,
            sample_java_package=sample_java_package,
            compile_options=compile_options,
            deps=deps,
            distdir=distdir,
            junit=junit,
            junit_options=junit_options,
            packaging_options=packaging_options,
            projenrc_java=projenrc_java,
            projenrc_java_options=projenrc_java_options,
            test_deps=test_deps,
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
            artifact_id=artifact_id,
            group_id=group_id,
            version=version,
            description=description,
            packaging=packaging,
            url=url,
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

        :param spec: Format ``<groupId>/<artifactId>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDependency", [spec]))

    @jsii.member(jsii_name="addPlugin")
    def add_plugin(
        self,
        spec: builtins.str,
        *,
        configuration: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        executions: typing.Optional[typing.Sequence["PluginExecution"]] = None,
    ) -> _Dependency_f510e013:
        '''(experimental) Adds a build plugin to the pom.

        The plug in is also added as a BUILD dep to the project.

        :param spec: dependency spec (``group/artifact@version``).
        :param configuration: (experimental) Plugin key/value configuration. Default: {}
        :param dependencies: (experimental) You could configure the dependencies for the plugin. Dependencies are in ``<groupId>/<artifactId>@<semver>`` format. Default: []
        :param executions: (experimental) Plugin executions. Default: []

        :stability: experimental
        '''
        options = PluginOptions(
            configuration=configuration,
            dependencies=dependencies,
            executions=executions,
        )

        return typing.cast(_Dependency_f510e013, jsii.invoke(self, "addPlugin", [spec, options]))

    @jsii.member(jsii_name="addTestDependency")
    def add_test_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a test dependency.

        :param spec: Format ``<groupId>/<artifactId>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addTestDependency", [spec]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compile")
    def compile(self) -> "MavenCompile":
        '''(experimental) Compile component.

        :stability: experimental
        '''
        return typing.cast("MavenCompile", jsii.get(self, "compile"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distdir")
    def distdir(self) -> builtins.str:
        '''(experimental) Maven artifact output directory.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "distdir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="packaging")
    def packaging(self) -> "MavenPackaging":
        '''(experimental) Packaging component.

        :stability: experimental
        '''
        return typing.cast("MavenPackaging", jsii.get(self, "packaging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pom")
    def pom(self) -> "Pom":
        '''(experimental) API for managing ``pom.xml``.

        :stability: experimental
        '''
        return typing.cast("Pom", jsii.get(self, "pom"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="junit")
    def junit(self) -> typing.Optional["Junit"]:
        '''(experimental) JUnit component.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["Junit"], jsii.get(self, "junit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="projenrc")
    def projenrc(self) -> typing.Optional["Projenrc"]:
        '''(experimental) Projenrc component.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["Projenrc"], jsii.get(self, "projenrc"))


class Junit(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.java.Junit",
):
    '''(experimental) Implements JUnit-based testing.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        pom: "Pom",
        sample_java_package: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param pom: (experimental) Java pom.
        :param sample_java_package: (experimental) Java package for test sample. Default: "org.acme"
        :param version: (experimental) Junit version. Default: "5.7.0"

        :stability: experimental
        '''
        options = JunitOptions(
            pom=pom, sample_java_package=sample_java_package, version=version
        )

        jsii.create(self.__class__, self, [project, options])


@jsii.data_type(
    jsii_type="projen.java.JunitOptions",
    jsii_struct_bases=[],
    name_mapping={
        "pom": "pom",
        "sample_java_package": "sampleJavaPackage",
        "version": "version",
    },
)
class JunitOptions:
    def __init__(
        self,
        *,
        pom: "Pom",
        sample_java_package: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``Junit``.

        :param pom: (experimental) Java pom.
        :param sample_java_package: (experimental) Java package for test sample. Default: "org.acme"
        :param version: (experimental) Junit version. Default: "5.7.0"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "pom": pom,
        }
        if sample_java_package is not None:
            self._values["sample_java_package"] = sample_java_package
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def pom(self) -> "Pom":
        '''(experimental) Java pom.

        :stability: experimental
        '''
        result = self._values.get("pom")
        assert result is not None, "Required property 'pom' is missing"
        return typing.cast("Pom", result)

    @builtins.property
    def sample_java_package(self) -> typing.Optional[builtins.str]:
        '''(experimental) Java package for test sample.

        :default: "org.acme"

        :stability: experimental
        '''
        result = self._values.get("sample_java_package")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Junit version.

        :default: "5.7.0"

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JunitOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MavenCompile(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.java.MavenCompile",
):
    '''(experimental) Adds the maven-compiler plugin to a POM file and the ``compile`` task.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        pom: "Pom",
        *,
        source: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param pom: -
        :param source: (experimental) Source language version. Default: "1.8"
        :param target: (experimental) Target JVM version. Default: "1.8"

        :stability: experimental
        '''
        options = MavenCompileOptions(source=source, target=target)

        jsii.create(self.__class__, self, [project, pom, options])


@jsii.data_type(
    jsii_type="projen.java.MavenCompileOptions",
    jsii_struct_bases=[],
    name_mapping={"source": "source", "target": "target"},
)
class MavenCompileOptions:
    def __init__(
        self,
        *,
        source: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``MavenCompile``.

        :param source: (experimental) Source language version. Default: "1.8"
        :param target: (experimental) Target JVM version. Default: "1.8"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if source is not None:
            self._values["source"] = source
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''(experimental) Source language version.

        :default: "1.8"

        :stability: experimental
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''(experimental) Target JVM version.

        :default: "1.8"

        :stability: experimental
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MavenCompileOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MavenPackaging(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.java.MavenPackaging",
):
    '''(experimental) Configures a maven project to produce a .jar archive with sources and javadocs.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        pom: "Pom",
        *,
        distdir: typing.Optional[builtins.str] = None,
        javadocs: typing.Optional[builtins.bool] = None,
        javadocs_exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        sources: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param pom: -
        :param distdir: (experimental) Where to place the package output? Default: "dist/java"
        :param javadocs: (experimental) Include javadocs jar in package. Default: true
        :param javadocs_exclude: (experimental) Exclude source files from docs. Default: []
        :param sources: (experimental) Include sources jar in package. Default: true

        :stability: experimental
        '''
        options = MavenPackagingOptions(
            distdir=distdir,
            javadocs=javadocs,
            javadocs_exclude=javadocs_exclude,
            sources=sources,
        )

        jsii.create(self.__class__, self, [project, pom, options])


@jsii.data_type(
    jsii_type="projen.java.MavenPackagingOptions",
    jsii_struct_bases=[],
    name_mapping={
        "distdir": "distdir",
        "javadocs": "javadocs",
        "javadocs_exclude": "javadocsExclude",
        "sources": "sources",
    },
)
class MavenPackagingOptions:
    def __init__(
        self,
        *,
        distdir: typing.Optional[builtins.str] = None,
        javadocs: typing.Optional[builtins.bool] = None,
        javadocs_exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        sources: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for ``MavenPackage``.

        :param distdir: (experimental) Where to place the package output? Default: "dist/java"
        :param javadocs: (experimental) Include javadocs jar in package. Default: true
        :param javadocs_exclude: (experimental) Exclude source files from docs. Default: []
        :param sources: (experimental) Include sources jar in package. Default: true

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if distdir is not None:
            self._values["distdir"] = distdir
        if javadocs is not None:
            self._values["javadocs"] = javadocs
        if javadocs_exclude is not None:
            self._values["javadocs_exclude"] = javadocs_exclude
        if sources is not None:
            self._values["sources"] = sources

    @builtins.property
    def distdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Where to place the package output?

        :default: "dist/java"

        :stability: experimental
        '''
        result = self._values.get("distdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def javadocs(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include javadocs jar in package.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("javadocs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def javadocs_exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Exclude source files from docs.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("javadocs_exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sources(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include sources jar in package.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sources")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MavenPackagingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MavenSample(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.java.MavenSample",
):
    '''(experimental) Java code sample.

    :stability: experimental
    '''

    def __init__(self, project: _Project_57d89203, *, package: builtins.str) -> None:
        '''
        :param project: -
        :param package: (experimental) Project root java package.

        :stability: experimental
        '''
        options = MavenSampleOptions(package=package)

        jsii.create(self.__class__, self, [project, options])


@jsii.data_type(
    jsii_type="projen.java.MavenSampleOptions",
    jsii_struct_bases=[],
    name_mapping={"package": "package"},
)
class MavenSampleOptions:
    def __init__(self, *, package: builtins.str) -> None:
        '''
        :param package: (experimental) Project root java package.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "package": package,
        }

    @builtins.property
    def package(self) -> builtins.str:
        '''(experimental) Project root java package.

        :stability: experimental
        '''
        result = self._values.get("package")
        assert result is not None, "Required property 'package' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MavenSampleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.java.PluginExecution",
    jsii_struct_bases=[],
    name_mapping={"goals": "goals", "id": "id"},
)
class PluginExecution:
    def __init__(
        self,
        *,
        goals: typing.Sequence[builtins.str],
        id: builtins.str,
    ) -> None:
        '''(experimental) Plugin execution definition.

        :param goals: (experimental) Which Maven goals this plugin should be associated with.
        :param id: (experimental) The ID.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "goals": goals,
            "id": id,
        }

    @builtins.property
    def goals(self) -> typing.List[builtins.str]:
        '''(experimental) Which Maven goals this plugin should be associated with.

        :stability: experimental
        '''
        result = self._values.get("goals")
        assert result is not None, "Required property 'goals' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def id(self) -> builtins.str:
        '''(experimental) The ID.

        :stability: experimental
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PluginExecution(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.java.PluginOptions",
    jsii_struct_bases=[],
    name_mapping={
        "configuration": "configuration",
        "dependencies": "dependencies",
        "executions": "executions",
    },
)
class PluginOptions:
    def __init__(
        self,
        *,
        configuration: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        executions: typing.Optional[typing.Sequence[PluginExecution]] = None,
    ) -> None:
        '''(experimental) Options for Maven plugins.

        :param configuration: (experimental) Plugin key/value configuration. Default: {}
        :param dependencies: (experimental) You could configure the dependencies for the plugin. Dependencies are in ``<groupId>/<artifactId>@<semver>`` format. Default: []
        :param executions: (experimental) Plugin executions. Default: []

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if configuration is not None:
            self._values["configuration"] = configuration
        if dependencies is not None:
            self._values["dependencies"] = dependencies
        if executions is not None:
            self._values["executions"] = executions

    @builtins.property
    def configuration(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Plugin key/value configuration.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("configuration")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) You could configure the dependencies for the plugin.

        Dependencies are in ``<groupId>/<artifactId>@<semver>`` format.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def executions(self) -> typing.Optional[typing.List[PluginExecution]]:
        '''(experimental) Plugin executions.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("executions")
        return typing.cast(typing.Optional[typing.List[PluginExecution]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PluginOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Pom(_Component_2b0ad27f, metaclass=jsii.JSIIMeta, jsii_type="projen.java.Pom"):
    '''(experimental) A Project Object Model or POM is the fundamental unit of work in Maven.

    It is
    an XML file that contains information about the project and configuration
    details used by Maven to build the project.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        artifact_id: builtins.str,
        group_id: builtins.str,
        version: builtins.str,
        description: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param artifact_id: (experimental) The artifactId is generally the name that the project is known by. Although the groupId is important, people within the group will rarely mention the groupId in discussion (they are often all be the same ID, such as the MojoHaus project groupId: org.codehaus.mojo). It, along with the groupId, creates a key that separates this project from every other project in the world (at least, it should :) ). Along with the groupId, the artifactId fully defines the artifact's living quarters within the repository. In the case of the above project, my-project lives in $M2_REPO/org/codehaus/mojo/my-project. Default: "my-app"
        :param group_id: (experimental) This is generally unique amongst an organization or a project. For example, all core Maven artifacts do (well, should) live under the groupId org.apache.maven. Group ID's do not necessarily use the dot notation, for example, the junit project. Note that the dot-notated groupId does not have to correspond to the package structure that the project contains. It is, however, a good practice to follow. When stored within a repository, the group acts much like the Java packaging structure does in an operating system. The dots are replaced by OS specific directory separators (such as '/' in Unix) which becomes a relative directory structure from the base repository. In the example given, the org.codehaus.mojo group lives within the directory $M2_REPO/org/codehaus/mojo. Default: "org.acme"
        :param version: (experimental) This is the last piece of the naming puzzle. groupId:artifactId denotes a single project but they cannot delineate which incarnation of that project we are talking about. Do we want the junit:junit of 2018 (version 4.12), or of 2007 (version 3.8.2)? In short: code changes, those changes should be versioned, and this element keeps those versions in line. It is also used within an artifact's repository to separate versions from each other. my-project version 1.0 files live in the directory structure $M2_REPO/org/codehaus/mojo/my-project/1.0. Default: "0.1.0"
        :param description: (experimental) Description of a project is always good. Although this should not replace formal documentation, a quick comment to any readers of the POM is always helpful. Default: undefined
        :param packaging: (experimental) Project packaging format. Default: "jar"
        :param url: (experimental) The URL, like the name, is not required. This is a nice gesture for projects users, however, so that they know where the project lives. Default: undefined

        :stability: experimental
        '''
        options = PomOptions(
            artifact_id=artifact_id,
            group_id=group_id,
            version=version,
            description=description,
            packaging=packaging,
            url=url,
        )

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="addDependency")
    def add_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a runtime dependency.

        :param spec: Format ``<groupId>/<artifactId>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDependency", [spec]))

    @jsii.member(jsii_name="addPlugin")
    def add_plugin(
        self,
        spec: builtins.str,
        *,
        configuration: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        executions: typing.Optional[typing.Sequence[PluginExecution]] = None,
    ) -> _Dependency_f510e013:
        '''(experimental) Adds a build plugin to the pom.

        The plug in is also added as a BUILD dep to the project.

        :param spec: dependency spec (``group/artifact@version``).
        :param configuration: (experimental) Plugin key/value configuration. Default: {}
        :param dependencies: (experimental) You could configure the dependencies for the plugin. Dependencies are in ``<groupId>/<artifactId>@<semver>`` format. Default: []
        :param executions: (experimental) Plugin executions. Default: []

        :stability: experimental
        '''
        options = PluginOptions(
            configuration=configuration,
            dependencies=dependencies,
            executions=executions,
        )

        return typing.cast(_Dependency_f510e013, jsii.invoke(self, "addPlugin", [spec, options]))

    @jsii.member(jsii_name="addProperty")
    def add_property(self, key: builtins.str, value: builtins.str) -> None:
        '''(experimental) Adds a key/value property to the pom.

        :param key: the key.
        :param value: the value.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addProperty", [key, value]))

    @jsii.member(jsii_name="addTestDependency")
    def add_test_dependency(self, spec: builtins.str) -> None:
        '''(experimental) Adds a test dependency.

        :param spec: Format ``<groupId>/<artifactId>@<semver>``.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addTestDependency", [spec]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactId")
    def artifact_id(self) -> builtins.str:
        '''(experimental) Maven artifact ID.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "artifactId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> builtins.str:
        '''(experimental) The name of the pom file.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "fileName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> builtins.str:
        '''(experimental) Maven group ID.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "groupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="packaging")
    def packaging(self) -> builtins.str:
        '''(experimental) Maven packaging format.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "packaging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''(experimental) Project version.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Project description.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Project display name.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Project URL.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))


@jsii.data_type(
    jsii_type="projen.java.PomOptions",
    jsii_struct_bases=[],
    name_mapping={
        "artifact_id": "artifactId",
        "group_id": "groupId",
        "version": "version",
        "description": "description",
        "packaging": "packaging",
        "url": "url",
    },
)
class PomOptions:
    def __init__(
        self,
        *,
        artifact_id: builtins.str,
        group_id: builtins.str,
        version: builtins.str,
        description: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``Pom``.

        :param artifact_id: (experimental) The artifactId is generally the name that the project is known by. Although the groupId is important, people within the group will rarely mention the groupId in discussion (they are often all be the same ID, such as the MojoHaus project groupId: org.codehaus.mojo). It, along with the groupId, creates a key that separates this project from every other project in the world (at least, it should :) ). Along with the groupId, the artifactId fully defines the artifact's living quarters within the repository. In the case of the above project, my-project lives in $M2_REPO/org/codehaus/mojo/my-project. Default: "my-app"
        :param group_id: (experimental) This is generally unique amongst an organization or a project. For example, all core Maven artifacts do (well, should) live under the groupId org.apache.maven. Group ID's do not necessarily use the dot notation, for example, the junit project. Note that the dot-notated groupId does not have to correspond to the package structure that the project contains. It is, however, a good practice to follow. When stored within a repository, the group acts much like the Java packaging structure does in an operating system. The dots are replaced by OS specific directory separators (such as '/' in Unix) which becomes a relative directory structure from the base repository. In the example given, the org.codehaus.mojo group lives within the directory $M2_REPO/org/codehaus/mojo. Default: "org.acme"
        :param version: (experimental) This is the last piece of the naming puzzle. groupId:artifactId denotes a single project but they cannot delineate which incarnation of that project we are talking about. Do we want the junit:junit of 2018 (version 4.12), or of 2007 (version 3.8.2)? In short: code changes, those changes should be versioned, and this element keeps those versions in line. It is also used within an artifact's repository to separate versions from each other. my-project version 1.0 files live in the directory structure $M2_REPO/org/codehaus/mojo/my-project/1.0. Default: "0.1.0"
        :param description: (experimental) Description of a project is always good. Although this should not replace formal documentation, a quick comment to any readers of the POM is always helpful. Default: undefined
        :param packaging: (experimental) Project packaging format. Default: "jar"
        :param url: (experimental) The URL, like the name, is not required. This is a nice gesture for projects users, however, so that they know where the project lives. Default: undefined

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "artifact_id": artifact_id,
            "group_id": group_id,
            "version": version,
        }
        if description is not None:
            self._values["description"] = description
        if packaging is not None:
            self._values["packaging"] = packaging
        if url is not None:
            self._values["url"] = url

    @builtins.property
    def artifact_id(self) -> builtins.str:
        '''(experimental) The artifactId is generally the name that the project is known by.

        Although
        the groupId is important, people within the group will rarely mention the
        groupId in discussion (they are often all be the same ID, such as the
        MojoHaus project groupId: org.codehaus.mojo). It, along with the groupId,
        creates a key that separates this project from every other project in the
        world (at least, it should :) ). Along with the groupId, the artifactId
        fully defines the artifact's living quarters within the repository. In the
        case of the above project, my-project lives in
        $M2_REPO/org/codehaus/mojo/my-project.

        :default: "my-app"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("artifact_id")
        assert result is not None, "Required property 'artifact_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_id(self) -> builtins.str:
        '''(experimental) This is generally unique amongst an organization or a project.

        For example,
        all core Maven artifacts do (well, should) live under the groupId
        org.apache.maven. Group ID's do not necessarily use the dot notation, for
        example, the junit project. Note that the dot-notated groupId does not have
        to correspond to the package structure that the project contains. It is,
        however, a good practice to follow. When stored within a repository, the
        group acts much like the Java packaging structure does in an operating
        system. The dots are replaced by OS specific directory separators (such as
        '/' in Unix) which becomes a relative directory structure from the base
        repository. In the example given, the org.codehaus.mojo group lives within
        the directory $M2_REPO/org/codehaus/mojo.

        :default: "org.acme"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("group_id")
        assert result is not None, "Required property 'group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) This is the last piece of the naming puzzle.

        groupId:artifactId denotes a
        single project but they cannot delineate which incarnation of that project
        we are talking about. Do we want the junit:junit of 2018 (version 4.12), or
        of 2007 (version 3.8.2)? In short: code changes, those changes should be
        versioned, and this element keeps those versions in line. It is also used
        within an artifact's repository to separate versions from each other.
        my-project version 1.0 files live in the directory structure
        $M2_REPO/org/codehaus/mojo/my-project/1.0.

        :default: "0.1.0"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description of a project is always good.

        Although this should not replace
        formal documentation, a quick comment to any readers of the POM is always
        helpful.

        :default: undefined

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def packaging(self) -> typing.Optional[builtins.str]:
        '''(experimental) Project packaging format.

        :default: "jar"

        :stability: experimental
        '''
        result = self._values.get("packaging")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The URL, like the name, is not required.

        This is a nice gesture for
        projects users, however, so that they know where the project lives.

        :default: undefined

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PomOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Projenrc(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.java.Projenrc",
):
    '''(experimental) Allows writing projenrc files in java.

    This will install ``org.projen/projen`` as a Maven dependency and will add a
    ``synth`` task which will compile & execute ``main()`` from
    ``src/main/java/projenrc.java``.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        pom: Pom,
        *,
        class_name: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        test_scope: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param pom: -
        :param class_name: (experimental) The name of the Java class which contains the ``main()`` method for projen. Default: "projenrc"
        :param projen_version: (experimental) The projen version to use. Default: - current version
        :param test_scope: (experimental) Defines projenrc under the test scope instead of the main scope, which is reserved to the app. This means that projenrc will be under ``src/test/java/projenrc.java`` and projen will be defined as a test dependency. This enforces that application code does not take a dependency on projen code. If this is disabled, projenrc should be under ``src/main/java/projenrc.java``. Default: true

        :stability: experimental
        '''
        options = ProjenrcOptions(
            class_name=class_name, projen_version=projen_version, test_scope=test_scope
        )

        jsii.create(self.__class__, self, [project, pom, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="className")
    def class_name(self) -> builtins.str:
        '''(experimental) The name of the java class that includes the projen entrypoint.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "className"))


@jsii.data_type(
    jsii_type="projen.java.ProjenrcOptions",
    jsii_struct_bases=[],
    name_mapping={
        "class_name": "className",
        "projen_version": "projenVersion",
        "test_scope": "testScope",
    },
)
class ProjenrcOptions:
    def __init__(
        self,
        *,
        class_name: typing.Optional[builtins.str] = None,
        projen_version: typing.Optional[builtins.str] = None,
        test_scope: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for ``Projenrc``.

        :param class_name: (experimental) The name of the Java class which contains the ``main()`` method for projen. Default: "projenrc"
        :param projen_version: (experimental) The projen version to use. Default: - current version
        :param test_scope: (experimental) Defines projenrc under the test scope instead of the main scope, which is reserved to the app. This means that projenrc will be under ``src/test/java/projenrc.java`` and projen will be defined as a test dependency. This enforces that application code does not take a dependency on projen code. If this is disabled, projenrc should be under ``src/main/java/projenrc.java``. Default: true

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if class_name is not None:
            self._values["class_name"] = class_name
        if projen_version is not None:
            self._values["projen_version"] = projen_version
        if test_scope is not None:
            self._values["test_scope"] = test_scope

    @builtins.property
    def class_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the Java class which contains the ``main()`` method for projen.

        :default: "projenrc"

        :stability: experimental
        '''
        result = self._values.get("class_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The projen version to use.

        :default: - current version

        :stability: experimental
        '''
        result = self._values.get("projen_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def test_scope(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines projenrc under the test scope instead of the main scope, which is reserved to the app.

        This means that projenrc will be under
        ``src/test/java/projenrc.java`` and projen will be defined as a test
        dependency. This enforces that application code does not take a dependency
        on projen code.

        If this is disabled, projenrc should be under
        ``src/main/java/projenrc.java``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("test_scope")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjenrcOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.java.JavaProjectCommonOptions",
    jsii_struct_bases=[_GitHubProjectOptions_547f2d08, PomOptions],
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
        "artifact_id": "artifactId",
        "group_id": "groupId",
        "version": "version",
        "description": "description",
        "packaging": "packaging",
        "url": "url",
        "compile_options": "compileOptions",
        "deps": "deps",
        "distdir": "distdir",
        "junit": "junit",
        "junit_options": "junitOptions",
        "packaging_options": "packagingOptions",
        "projenrc_java": "projenrcJava",
        "projenrc_java_options": "projenrcJavaOptions",
        "test_deps": "testDeps",
    },
)
class JavaProjectCommonOptions(_GitHubProjectOptions_547f2d08, PomOptions):
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
        artifact_id: builtins.str,
        group_id: builtins.str,
        version: builtins.str,
        description: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        compile_options: typing.Optional[MavenCompileOptions] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        distdir: typing.Optional[builtins.str] = None,
        junit: typing.Optional[builtins.bool] = None,
        junit_options: typing.Optional[JunitOptions] = None,
        packaging_options: typing.Optional[MavenPackagingOptions] = None,
        projenrc_java: typing.Optional[builtins.bool] = None,
        projenrc_java_options: typing.Optional[ProjenrcOptions] = None,
        test_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Options for ``JavaProject``.

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
        :param artifact_id: (experimental) The artifactId is generally the name that the project is known by. Although the groupId is important, people within the group will rarely mention the groupId in discussion (they are often all be the same ID, such as the MojoHaus project groupId: org.codehaus.mojo). It, along with the groupId, creates a key that separates this project from every other project in the world (at least, it should :) ). Along with the groupId, the artifactId fully defines the artifact's living quarters within the repository. In the case of the above project, my-project lives in $M2_REPO/org/codehaus/mojo/my-project. Default: "my-app"
        :param group_id: (experimental) This is generally unique amongst an organization or a project. For example, all core Maven artifacts do (well, should) live under the groupId org.apache.maven. Group ID's do not necessarily use the dot notation, for example, the junit project. Note that the dot-notated groupId does not have to correspond to the package structure that the project contains. It is, however, a good practice to follow. When stored within a repository, the group acts much like the Java packaging structure does in an operating system. The dots are replaced by OS specific directory separators (such as '/' in Unix) which becomes a relative directory structure from the base repository. In the example given, the org.codehaus.mojo group lives within the directory $M2_REPO/org/codehaus/mojo. Default: "org.acme"
        :param version: (experimental) This is the last piece of the naming puzzle. groupId:artifactId denotes a single project but they cannot delineate which incarnation of that project we are talking about. Do we want the junit:junit of 2018 (version 4.12), or of 2007 (version 3.8.2)? In short: code changes, those changes should be versioned, and this element keeps those versions in line. It is also used within an artifact's repository to separate versions from each other. my-project version 1.0 files live in the directory structure $M2_REPO/org/codehaus/mojo/my-project/1.0. Default: "0.1.0"
        :param description: (experimental) Description of a project is always good. Although this should not replace formal documentation, a quick comment to any readers of the POM is always helpful. Default: undefined
        :param packaging: (experimental) Project packaging format. Default: "jar"
        :param url: (experimental) The URL, like the name, is not required. This is a nice gesture for projects users, however, so that they know where the project lives. Default: undefined
        :param compile_options: (experimental) Compile options. Default: - defaults
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<groupId>/<artifactId>@<semver>`` Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param distdir: (experimental) Final artifact output directory. Default: "dist/java"
        :param junit: (experimental) Include junit tests. Default: true
        :param junit_options: (experimental) junit options. Default: - defaults
        :param packaging_options: (experimental) Packaging options. Default: - defaults
        :param projenrc_java: (experimental) Use projenrc in java. This will install ``projen`` as a java dependency and will add a ``synth`` task which will compile & execute ``main()`` from ``src/main/java/projenrc.java``. Default: true
        :param projenrc_java_options: (experimental) Options related to projenrc in java. Default: - default options
        :param test_deps: (experimental) List of test dependencies for this project. Dependencies use the format: ``<groupId>/<artifactId>@<semver>`` Additional dependencies can be added via ``project.addTestDependency()``. Default: []

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
        if isinstance(compile_options, dict):
            compile_options = MavenCompileOptions(**compile_options)
        if isinstance(junit_options, dict):
            junit_options = JunitOptions(**junit_options)
        if isinstance(packaging_options, dict):
            packaging_options = MavenPackagingOptions(**packaging_options)
        if isinstance(projenrc_java_options, dict):
            projenrc_java_options = ProjenrcOptions(**projenrc_java_options)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "artifact_id": artifact_id,
            "group_id": group_id,
            "version": version,
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
        if description is not None:
            self._values["description"] = description
        if packaging is not None:
            self._values["packaging"] = packaging
        if url is not None:
            self._values["url"] = url
        if compile_options is not None:
            self._values["compile_options"] = compile_options
        if deps is not None:
            self._values["deps"] = deps
        if distdir is not None:
            self._values["distdir"] = distdir
        if junit is not None:
            self._values["junit"] = junit
        if junit_options is not None:
            self._values["junit_options"] = junit_options
        if packaging_options is not None:
            self._values["packaging_options"] = packaging_options
        if projenrc_java is not None:
            self._values["projenrc_java"] = projenrc_java
        if projenrc_java_options is not None:
            self._values["projenrc_java_options"] = projenrc_java_options
        if test_deps is not None:
            self._values["test_deps"] = test_deps

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
    def artifact_id(self) -> builtins.str:
        '''(experimental) The artifactId is generally the name that the project is known by.

        Although
        the groupId is important, people within the group will rarely mention the
        groupId in discussion (they are often all be the same ID, such as the
        MojoHaus project groupId: org.codehaus.mojo). It, along with the groupId,
        creates a key that separates this project from every other project in the
        world (at least, it should :) ). Along with the groupId, the artifactId
        fully defines the artifact's living quarters within the repository. In the
        case of the above project, my-project lives in
        $M2_REPO/org/codehaus/mojo/my-project.

        :default: "my-app"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("artifact_id")
        assert result is not None, "Required property 'artifact_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_id(self) -> builtins.str:
        '''(experimental) This is generally unique amongst an organization or a project.

        For example,
        all core Maven artifacts do (well, should) live under the groupId
        org.apache.maven. Group ID's do not necessarily use the dot notation, for
        example, the junit project. Note that the dot-notated groupId does not have
        to correspond to the package structure that the project contains. It is,
        however, a good practice to follow. When stored within a repository, the
        group acts much like the Java packaging structure does in an operating
        system. The dots are replaced by OS specific directory separators (such as
        '/' in Unix) which becomes a relative directory structure from the base
        repository. In the example given, the org.codehaus.mojo group lives within
        the directory $M2_REPO/org/codehaus/mojo.

        :default: "org.acme"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("group_id")
        assert result is not None, "Required property 'group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) This is the last piece of the naming puzzle.

        groupId:artifactId denotes a
        single project but they cannot delineate which incarnation of that project
        we are talking about. Do we want the junit:junit of 2018 (version 4.12), or
        of 2007 (version 3.8.2)? In short: code changes, those changes should be
        versioned, and this element keeps those versions in line. It is also used
        within an artifact's repository to separate versions from each other.
        my-project version 1.0 files live in the directory structure
        $M2_REPO/org/codehaus/mojo/my-project/1.0.

        :default: "0.1.0"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description of a project is always good.

        Although this should not replace
        formal documentation, a quick comment to any readers of the POM is always
        helpful.

        :default: undefined

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def packaging(self) -> typing.Optional[builtins.str]:
        '''(experimental) Project packaging format.

        :default: "jar"

        :stability: experimental
        '''
        result = self._values.get("packaging")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The URL, like the name, is not required.

        This is a nice gesture for
        projects users, however, so that they know where the project lives.

        :default: undefined

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compile_options(self) -> typing.Optional[MavenCompileOptions]:
        '''(experimental) Compile options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("compile_options")
        return typing.cast(typing.Optional[MavenCompileOptions], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of runtime dependencies for this project.

        Dependencies use the format: ``<groupId>/<artifactId>@<semver>``

        Additional dependencies can be added via ``project.addDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def distdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Final artifact output directory.

        :default: "dist/java"

        :stability: experimental
        '''
        result = self._values.get("distdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def junit(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include junit tests.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("junit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def junit_options(self) -> typing.Optional[JunitOptions]:
        '''(experimental) junit options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("junit_options")
        return typing.cast(typing.Optional[JunitOptions], result)

    @builtins.property
    def packaging_options(self) -> typing.Optional[MavenPackagingOptions]:
        '''(experimental) Packaging options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("packaging_options")
        return typing.cast(typing.Optional[MavenPackagingOptions], result)

    @builtins.property
    def projenrc_java(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use projenrc in java.

        This will install ``projen`` as a java dependency and will add a ``synth`` task which
        will compile & execute ``main()`` from ``src/main/java/projenrc.java``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projenrc_java")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_java_options(self) -> typing.Optional[ProjenrcOptions]:
        '''(experimental) Options related to projenrc in java.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_java_options")
        return typing.cast(typing.Optional[ProjenrcOptions], result)

    @builtins.property
    def test_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of test dependencies for this project.

        Dependencies use the format: ``<groupId>/<artifactId>@<semver>``

        Additional dependencies can be added via ``project.addTestDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("test_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JavaProjectCommonOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.java.JavaProjectOptions",
    jsii_struct_bases=[JavaProjectCommonOptions],
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
        "artifact_id": "artifactId",
        "group_id": "groupId",
        "version": "version",
        "description": "description",
        "packaging": "packaging",
        "url": "url",
        "compile_options": "compileOptions",
        "deps": "deps",
        "distdir": "distdir",
        "junit": "junit",
        "junit_options": "junitOptions",
        "packaging_options": "packagingOptions",
        "projenrc_java": "projenrcJava",
        "projenrc_java_options": "projenrcJavaOptions",
        "test_deps": "testDeps",
        "sample": "sample",
        "sample_java_package": "sampleJavaPackage",
    },
)
class JavaProjectOptions(JavaProjectCommonOptions):
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
        artifact_id: builtins.str,
        group_id: builtins.str,
        version: builtins.str,
        description: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        compile_options: typing.Optional[MavenCompileOptions] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        distdir: typing.Optional[builtins.str] = None,
        junit: typing.Optional[builtins.bool] = None,
        junit_options: typing.Optional[JunitOptions] = None,
        packaging_options: typing.Optional[MavenPackagingOptions] = None,
        projenrc_java: typing.Optional[builtins.bool] = None,
        projenrc_java_options: typing.Optional[ProjenrcOptions] = None,
        test_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        sample: typing.Optional[builtins.bool] = None,
        sample_java_package: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``JavaProject``.

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
        :param artifact_id: (experimental) The artifactId is generally the name that the project is known by. Although the groupId is important, people within the group will rarely mention the groupId in discussion (they are often all be the same ID, such as the MojoHaus project groupId: org.codehaus.mojo). It, along with the groupId, creates a key that separates this project from every other project in the world (at least, it should :) ). Along with the groupId, the artifactId fully defines the artifact's living quarters within the repository. In the case of the above project, my-project lives in $M2_REPO/org/codehaus/mojo/my-project. Default: "my-app"
        :param group_id: (experimental) This is generally unique amongst an organization or a project. For example, all core Maven artifacts do (well, should) live under the groupId org.apache.maven. Group ID's do not necessarily use the dot notation, for example, the junit project. Note that the dot-notated groupId does not have to correspond to the package structure that the project contains. It is, however, a good practice to follow. When stored within a repository, the group acts much like the Java packaging structure does in an operating system. The dots are replaced by OS specific directory separators (such as '/' in Unix) which becomes a relative directory structure from the base repository. In the example given, the org.codehaus.mojo group lives within the directory $M2_REPO/org/codehaus/mojo. Default: "org.acme"
        :param version: (experimental) This is the last piece of the naming puzzle. groupId:artifactId denotes a single project but they cannot delineate which incarnation of that project we are talking about. Do we want the junit:junit of 2018 (version 4.12), or of 2007 (version 3.8.2)? In short: code changes, those changes should be versioned, and this element keeps those versions in line. It is also used within an artifact's repository to separate versions from each other. my-project version 1.0 files live in the directory structure $M2_REPO/org/codehaus/mojo/my-project/1.0. Default: "0.1.0"
        :param description: (experimental) Description of a project is always good. Although this should not replace formal documentation, a quick comment to any readers of the POM is always helpful. Default: undefined
        :param packaging: (experimental) Project packaging format. Default: "jar"
        :param url: (experimental) The URL, like the name, is not required. This is a nice gesture for projects users, however, so that they know where the project lives. Default: undefined
        :param compile_options: (experimental) Compile options. Default: - defaults
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<groupId>/<artifactId>@<semver>`` Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param distdir: (experimental) Final artifact output directory. Default: "dist/java"
        :param junit: (experimental) Include junit tests. Default: true
        :param junit_options: (experimental) junit options. Default: - defaults
        :param packaging_options: (experimental) Packaging options. Default: - defaults
        :param projenrc_java: (experimental) Use projenrc in java. This will install ``projen`` as a java dependency and will add a ``synth`` task which will compile & execute ``main()`` from ``src/main/java/projenrc.java``. Default: true
        :param projenrc_java_options: (experimental) Options related to projenrc in java. Default: - default options
        :param test_deps: (experimental) List of test dependencies for this project. Dependencies use the format: ``<groupId>/<artifactId>@<semver>`` Additional dependencies can be added via ``project.addTestDependency()``. Default: []
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist. Default: true
        :param sample_java_package: (experimental) The java package to use for the code sample. Default: "org.acme"

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
        if isinstance(compile_options, dict):
            compile_options = MavenCompileOptions(**compile_options)
        if isinstance(junit_options, dict):
            junit_options = JunitOptions(**junit_options)
        if isinstance(packaging_options, dict):
            packaging_options = MavenPackagingOptions(**packaging_options)
        if isinstance(projenrc_java_options, dict):
            projenrc_java_options = ProjenrcOptions(**projenrc_java_options)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "artifact_id": artifact_id,
            "group_id": group_id,
            "version": version,
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
        if description is not None:
            self._values["description"] = description
        if packaging is not None:
            self._values["packaging"] = packaging
        if url is not None:
            self._values["url"] = url
        if compile_options is not None:
            self._values["compile_options"] = compile_options
        if deps is not None:
            self._values["deps"] = deps
        if distdir is not None:
            self._values["distdir"] = distdir
        if junit is not None:
            self._values["junit"] = junit
        if junit_options is not None:
            self._values["junit_options"] = junit_options
        if packaging_options is not None:
            self._values["packaging_options"] = packaging_options
        if projenrc_java is not None:
            self._values["projenrc_java"] = projenrc_java
        if projenrc_java_options is not None:
            self._values["projenrc_java_options"] = projenrc_java_options
        if test_deps is not None:
            self._values["test_deps"] = test_deps
        if sample is not None:
            self._values["sample"] = sample
        if sample_java_package is not None:
            self._values["sample_java_package"] = sample_java_package

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
    def artifact_id(self) -> builtins.str:
        '''(experimental) The artifactId is generally the name that the project is known by.

        Although
        the groupId is important, people within the group will rarely mention the
        groupId in discussion (they are often all be the same ID, such as the
        MojoHaus project groupId: org.codehaus.mojo). It, along with the groupId,
        creates a key that separates this project from every other project in the
        world (at least, it should :) ). Along with the groupId, the artifactId
        fully defines the artifact's living quarters within the repository. In the
        case of the above project, my-project lives in
        $M2_REPO/org/codehaus/mojo/my-project.

        :default: "my-app"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("artifact_id")
        assert result is not None, "Required property 'artifact_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_id(self) -> builtins.str:
        '''(experimental) This is generally unique amongst an organization or a project.

        For example,
        all core Maven artifacts do (well, should) live under the groupId
        org.apache.maven. Group ID's do not necessarily use the dot notation, for
        example, the junit project. Note that the dot-notated groupId does not have
        to correspond to the package structure that the project contains. It is,
        however, a good practice to follow. When stored within a repository, the
        group acts much like the Java packaging structure does in an operating
        system. The dots are replaced by OS specific directory separators (such as
        '/' in Unix) which becomes a relative directory structure from the base
        repository. In the example given, the org.codehaus.mojo group lives within
        the directory $M2_REPO/org/codehaus/mojo.

        :default: "org.acme"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("group_id")
        assert result is not None, "Required property 'group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) This is the last piece of the naming puzzle.

        groupId:artifactId denotes a
        single project but they cannot delineate which incarnation of that project
        we are talking about. Do we want the junit:junit of 2018 (version 4.12), or
        of 2007 (version 3.8.2)? In short: code changes, those changes should be
        versioned, and this element keeps those versions in line. It is also used
        within an artifact's repository to separate versions from each other.
        my-project version 1.0 files live in the directory structure
        $M2_REPO/org/codehaus/mojo/my-project/1.0.

        :default: "0.1.0"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description of a project is always good.

        Although this should not replace
        formal documentation, a quick comment to any readers of the POM is always
        helpful.

        :default: undefined

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def packaging(self) -> typing.Optional[builtins.str]:
        '''(experimental) Project packaging format.

        :default: "jar"

        :stability: experimental
        '''
        result = self._values.get("packaging")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The URL, like the name, is not required.

        This is a nice gesture for
        projects users, however, so that they know where the project lives.

        :default: undefined

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compile_options(self) -> typing.Optional[MavenCompileOptions]:
        '''(experimental) Compile options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("compile_options")
        return typing.cast(typing.Optional[MavenCompileOptions], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of runtime dependencies for this project.

        Dependencies use the format: ``<groupId>/<artifactId>@<semver>``

        Additional dependencies can be added via ``project.addDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def distdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Final artifact output directory.

        :default: "dist/java"

        :stability: experimental
        '''
        result = self._values.get("distdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def junit(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include junit tests.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("junit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def junit_options(self) -> typing.Optional[JunitOptions]:
        '''(experimental) junit options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("junit_options")
        return typing.cast(typing.Optional[JunitOptions], result)

    @builtins.property
    def packaging_options(self) -> typing.Optional[MavenPackagingOptions]:
        '''(experimental) Packaging options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("packaging_options")
        return typing.cast(typing.Optional[MavenPackagingOptions], result)

    @builtins.property
    def projenrc_java(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use projenrc in java.

        This will install ``projen`` as a java dependency and will add a ``synth`` task which
        will compile & execute ``main()`` from ``src/main/java/projenrc.java``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projenrc_java")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_java_options(self) -> typing.Optional[ProjenrcOptions]:
        '''(experimental) Options related to projenrc in java.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_java_options")
        return typing.cast(typing.Optional[ProjenrcOptions], result)

    @builtins.property
    def test_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of test dependencies for this project.

        Dependencies use the format: ``<groupId>/<artifactId>@<semver>``

        Additional dependencies can be added via ``project.addTestDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("test_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sample(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include sample code and test if the relevant directories don't exist.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sample_java_package(self) -> typing.Optional[builtins.str]:
        '''(experimental) The java package to use for the code sample.

        :default: "org.acme"

        :stability: experimental
        '''
        result = self._values.get("sample_java_package")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JavaProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "JavaProject",
    "JavaProjectCommonOptions",
    "JavaProjectOptions",
    "Junit",
    "JunitOptions",
    "MavenCompile",
    "MavenCompileOptions",
    "MavenPackaging",
    "MavenPackagingOptions",
    "MavenSample",
    "MavenSampleOptions",
    "PluginExecution",
    "PluginOptions",
    "Pom",
    "PomOptions",
    "Projenrc",
    "ProjenrcOptions",
]

publication.publish()
