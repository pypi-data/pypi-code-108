from __future__ import annotations

import pathlib
import shutil
from configparser import ConfigParser
from itertools import chain
from pathlib import Path
from shlex import quote
from typing import Any, Dict, Iterator, List, Optional, Union

from stdlib_list import stdlib_list
from tomlkit import dumps, parse

from .console import console, style_str
from .datatypes import Dependency, Pyproject, RepoConfig
from .errors import DirectoryNotFoundError, PackageNotFoundError, PyprojectNotFoundError
from .utils import current_directory, run


class Project:
    """An object representation of a python project managed using Poetry."""

    def __init__(self, root: Union[Path, str]) -> None:
        """Create a new instance of Project from given root directory.

        Arguments:
            * root: The root path of the project. Can be a string or a `pathlib.Path` object.

        Raises:
            * DirectoryNotFoundError: When project directory does not exist.
            * PyprojectNotFoundError: When a pyproject.toml cannot be found in project root directory.
            * ValidationError: When a pyproject.toml is not valid.
        """
        # Store the canonical path ('.' and '..' are resolved and variables are expanded)
        self.root = Path(root).resolve(True)
        # Ensure path exists
        if not self.root.exists():
            raise DirectoryNotFoundError(f"Directory {self.root} does not exist")
        self.pyproject_file = self.root / "pyproject.toml"
        # Ensure pyproject.toml (we don't use try/catch to avoid long traceback)
        if not self.pyproject_file.exists():
            raise PyprojectNotFoundError(f"File {self.pyproject_file} does not exist")
        # We can now read without try/catch
        self.pyproject_content = self.pyproject_file.read_text()
        # If file content is not valid, a ValidationError is
        self._pyproject = parse(self.pyproject_content)
        self.pyproject = Pyproject(**self._pyproject["tool"]["poetry"])  # type: ignore

    def __repr__(self) -> str:
        return f"Project(name={self.pyproject.name}, root={self.root})"

    # def glob(self, expr: str, ignore: Sequence[Union[str, Path]]):
    #     generator = self.root.glob(expr)
    #     for path in generator:
    #         if path

    @property
    def tests_found(self) -> bool:
        """Indicate whether a test directory as been found"""
        return (self.root / "tests").exists()

    @property
    def src(self) -> List[str]:
        sources = []
        if not self.pyproject.packages:
            default = self.root / self.pyproject.name.replace("-", "_")
            if default.exists():
                return [str(default.resolve())]
            else:
                return []
        for pkg in self.pyproject.packages:
            if isinstance(pkg, str):
                default = Path(self.root / pkg).resolve(True)
                if default.exists():
                    sources.append(default)
                else:
                    default = Path(self.root / "src" / pkg).resolve(True)
                    if default.exists():
                        sources.append(default)
                continue
            if pkg.from_:
                root = self.root / pkg.from_
            else:
                root = self.root
            default = root / pkg.include
            if default.exists():
                sources.append(default)
        return [str(source.resolve()) for source in sources]

    @property
    def private_dependencies(self) -> List[Project]:
        """Private dependencies are dependencies that cannot be fetched from external repositories.

        Nested private dependencies are not handled.
        """
        dependencies = []
        # Path are resolved when creating a Project instance
        # In order to successfully resolve path of private dependencies
        # we must be located in the root directory of the project.
        with current_directory(self.root):
            # Private dependencies are dependencies
            for dependency in self.pyproject.dependencies:
                # That are also declared as development dependencies
                if dependency in self.pyproject.dev_dependencies:
                    # We can safely ignore type because if .path attribute does not exist we catch the AttributeError.
                    dep: Dependency = self.pyproject.dev_dependencies[dependency]
                    # And that have a "path" attribute
                    try:
                        path = dep.path
                    except AttributeError:
                        continue
                    # If the path attribute does exist, then this is a private dependency
                    if path:
                        dependencies.append(Project((self.root / path).resolve(True)))
        return dependencies

    @property
    def wheels(self) -> Iterator[Path]:
        return self.root.glob("dist/*.whl")

    @property
    def sdists(self) -> Iterator[Path]:
        return self.root.glob("dist/*.tar.gz")

    @property
    def dist_files(self) -> Iterator[Path]:
        return chain(self.wheels, self.sdists)

    @classmethod
    def from_pyproject(cls, pyproject: Union[Path, str]) -> Project:
        """Create a new instance of Project from `pyproject.toml` location.

        Arguments:
            * pyproject: The path to `pyproject.toml` file. Can be a string or a `pathlib.Path` object.

        Raises:
            * PyprojectNotFoundError: When a pyproject.toml cannot be found in project root directory.
            * ValidationError: When a pyproject.toml is not valid.
        """
        return cls(Path(pyproject).parent.resolve(True))

    def install(self, extras: List[str] = [], skip: List[str] = []) -> None:
        """Install package using `poetry install`."""
        if self.pyproject.name in skip:
            return
        with current_directory(self.root):
            console.print(
                f"Installing project {style_str(self.pyproject.name, 'bold blue')}"
            )
            extras_opts = " ".join(["-E " + quote(extra) for extra in extras])
            try:
                run(f"poetry install {extras_opts}")
            except Exception:
                console.print(
                    f"Failed to install {self.pyproject.name} from {style_str(self.root, 'red')}",
                    style="red",
                )
            console.print(
                f"Successfully installed {self.pyproject.name} from {style_str(self.root, 'green')}",
                style="green",
            )

    def build(self, format: Optional[str] = None) -> None:
        """Build package using `poetry build`."""
        with current_directory(self.root):
            format_opt = f"--format {quote(format)}" if format else ""
            console.print(f"Building package {style_str(self.pyproject.name, 'blue')}")
            run(f"poetry build {format_opt}")

    def test(
        self, markers: List[str] = [], exprs: List[str] = [], add_src: List[str] = []
    ) -> None:
        """Run tests using `pytest`."""
        marker_opts = " ".join((f"-m {quote(marker)}" for marker in markers))
        expr_opts = " ".join((f"-m {quote(expr)}" for expr in exprs))
        cov_opts = " ".join((f"--cov {quote(src)}" for src in set(self.src + add_src)))
        with current_directory(self.root):
            cmd = f"pytest {cov_opts} {expr_opts} {marker_opts}"
            console.print(
                f"[bold blue]Testing[/bold blue] package {style_str(self.pyproject.name, 'blue')} with command: {style_str(cmd, 'blue')}"
            )
            run(cmd)

    def lint(self) -> None:
        """Lint package and tests using `flake8`."""
        cmd = f"flake8 {' '.join([quote(src) for src in self.src])}" + (
            " tests/" if self.tests_found else ""
        )
        with current_directory(self.root):
            console.print(
                f"[bold blue]Linting[/bold blue] package {style_str(self.pyproject.name, 'blue')} with command: {style_str(cmd, 'blue')}"
            )
            run(cmd)

    def format(self) -> None:
        """Format package and tests using `isort` and `black`."""
        src_dirs = " ".join([quote(src) for src in self.src])
        test_dirs = " tests/" if self.tests_found else ""
        black_cmd = f"black {src_dirs}" + test_dirs
        isort_cmd = f"isort {src_dirs}" + test_dirs
        with current_directory(self.root):
            console.print(
                f"[bold blue]Formatting[/bold blue] package {style_str(self.pyproject.name, 'blue')} with command: {style_str(black_cmd, 'blue')}"
            )
            run(black_cmd)
            console.print(
                f"[bold blue]Sorting[/bold blue] imports for package {style_str(self.pyproject.name, 'blue')} with command: {style_str(isort_cmd, 'blue')}"
            )
            run(isort_cmd)

    def typecheck(self) -> None:
        """Run `mypy` against package source."""
        sources = " ".join([quote(src) for src in self.src])
        cmd = f"mypy {sources}"
        console.print(
            f"[bold blue]Typechecking[/bold blue] package {style_str(self.pyproject.name, 'blue')} with command: {style_str(cmd, 'blue')}"
        )
        run(cmd)

    def bump(self, version: str) -> None:
        """Bump package version using `poetry version`."""
        console.print(
            f"[bold blue]Bumping[/bold blue] package {style_str(self.pyproject.name, 'blue')} from version {style_str(self.pyproject.version, 'bold blue')} to {style_str(version, 'bold blue')}"
        )
        with current_directory(self.root):
            deps_to_bump = {
                dep.pyproject.name: f"^{version}" for dep in self.private_dependencies
            }
            if deps_to_bump:
                console.print(
                    f"[blue]Bumping relative dependencies[/blue]: {list(deps_to_bump)}"
                )
                self.update_dependencies(deps_to_bump)
            self.set_version(version)
            run("poetry lock --no-update")
            console.print(
                f"Successfully bumped package {self.pyproject.name}",
                style="green",
            )

    def clean(self, no_dist: bool = False) -> None:
        """Clean a package dist directory."""
        for _file in self.root.glob("**/requirements.txt"):
            _file.unlink()
        for _file in self.root.glob("**/*.pyc"):
            _file.unlink()
        for _file in self.root.glob("**/junit.xml"):
            _file.unlink()
        for _file in self.root.glob("**/cov.xml"):
            _file.unlink()
        for _dir in self.root.glob("**/__pycache__"):
            shutil.rmtree(_dir)
        if not no_dist:
            shutil.rmtree(self.root / "dist", ignore_errors=True)
            shutil.rmtree(self.root / "coverage-report", ignore_errors=True)

    def update(self) -> None:
        """Update package dependencies using `poetry udpate`."""
        with current_directory(self.root):
            console.print(f"Updating package {self.pyproject.name}")
            run("poetry update")

    def export_requirements(
        self, requirements: Union[str, Path] = "requirements.txt", mode: str = ">"
    ) -> None:
        """Export dependencies into a requirements file."""
        # Just to be sure...
        if mode not in (">>", ">"):
            mode = ">"
        with current_directory(self.root):
            run(f"poetry export --without-hashes {mode} {requirements}")

    def export(self, clean: bool = True) -> None:
        """Export packages and its dependencies to directory."""
        console.print(f"Exporting package {self.pyproject.name} and its dependencies")
        if clean:
            self.clean()
        export = self.root / "export"
        requirements = export / "requirements.txt"
        shutil.rmtree(export, ignore_errors=True)
        export.mkdir(parents=True, exist_ok=True)
        self.build()
        for wheel in self.wheels:
            shutil.move(str(wheel), export / wheel.name)
        shutil.rmtree(self.root / "dist")
        self.export_requirements(requirements)
        for dependency in self.private_dependencies:
            dependency.build()
            for wheel in dependency.wheels:
                shutil.move(str(wheel), export / wheel.name)
            dependency.export_requirements(requirements, mode=">>")
        _requirements = requirements.read_text()
        requirements.write_text(
            "\n".join(
                [
                    requirement
                    for requirement in _requirements.split("\n")
                    if "@" not in requirement
                ]
            )
        )
        with current_directory(export):
            run(f"pip download -r {requirements}")
            requirements.unlink()
        dist = Path("dist").resolve(True)
        dist.mkdir(exist_ok=True, parents=True)
        out = dist / f"{self.pyproject.name}-{self.pyproject.version}"
        shutil.make_archive(
            str(out),
            format="zip",
            root_dir=export,
        )
        shutil.rmtree(export)

    def add_dep(self, name: str, *, dev: bool = False) -> None:
        with current_directory(self.root):
            dev_opt = "--dev" if dev else ""
            cmd = f"poetry add {name} {dev_opt}".strip()
            console.print(
                f"[blue]Installing[/blue] dependency [bold blue]{name}[/bold blue] for project [bold blue]{self.pyproject.name}[/bold blue] with command [blue]{quote(cmd)}[/blue]"
            )
            run(cmd)

    def set_version(self, value: str) -> None:
        self._pyproject["tool"]["poetry"]["version"] = value  # type: ignore
        self.pyproject = Pyproject.construct(**self._pyproject["tool"]["poetry"])  # type: ignore
        self.pyproject_content = dumps(self._pyproject)
        self.pyproject_file.write_text(self.pyproject_content)

    def set_authors(self, values: List[str]) -> None:
        self._pyproject["tool"]["poetry"]["authors"] = [  # type: ignore
            value.lower() for value in values
        ]
        self.pyproject = Pyproject.construct(**self._pyproject["tool"]["poetry"])  # type: ignore
        self.pyproject_content = dumps(self._pyproject)
        self.pyproject_file.write_text(self.pyproject_content)

    def set_include_packages(self, values: List[str]) -> None:
        self._pyproject["tool"]["poetry"]["packages"] = [  # type: ignore
            {"include": value} for value in values
        ]
        self.pyproject = Pyproject.construct(**self._pyproject["tool"]["poetry"])  # type: ignore
        self.pyproject_content = dumps(self._pyproject)
        self.pyproject_file.write_text(self.pyproject_content)

    def update_dependencies(self, values: Dict[str, Any]) -> None:
        new_deps: Dict[str, Any] = {
            **self.pyproject.dependencies,
            **values,
        }
        for key, value in new_deps.items():
            if isinstance(value, Dependency):
                new_deps[key] = value.dict(exclude_unset=True)
        self._pyproject["tool"]["poetry"]["dependencies"] = new_deps  # type: ignore
        self.pyproject_content = dumps(self._pyproject)
        self.pyproject_file.write_text(self.pyproject_content)


class Monorepo(Project):
    def __init__(self, root: Union[Path, str]) -> None:
        super().__init__(root)
        self.config = self.parse_config_from_setupcfg(self.root / "setup.cfg")
        self._projects = list(self._find_projects())

    def _find_projects(self) -> Iterator[Project]:
        yield Project(self.root)
        for pyproject_file in self.root.glob(self.config.glob):
            if ".venv" in str(pyproject_file.resolve(True)):
                continue
            yield Project.from_pyproject(pyproject_file)

    @staticmethod
    def parse_config_from_setupcfg(path: pathlib.Path) -> RepoConfig:
        if path.exists():
            setupcfg_parser = ConfigParser()
            setupcfg_parser.read_string(path.read_text())
            setupcfg_config = {
                s: dict(setupcfg_parser.items(s)) for s in setupcfg_parser.sections()
            }
            if setupcfg_config.get("tool:repo"):
                _dict = setupcfg_config["tool:repo"]
                if not _dict.get("prefix"):
                    _dict.pop("prefix", None)
                return RepoConfig(**_dict)
        return RepoConfig()

    @property
    def project_names(self) -> List[str]:
        return [project.pyproject.name for project in self._projects]

    @property
    def projects(self) -> Dict[str, Project]:
        return {project.pyproject.name: project for project in self._projects}

    def get_packages(self, packages: Optional[List[str]] = None) -> List[Project]:
        """Get a subset of packages from name."""
        if not packages:
            return self._projects
        if not isinstance(packages, list):
            packages = list(packages)
        unknown = [name for name in packages if name not in self.project_names]
        if len(unknown) > 1:
            raise PackageNotFoundError(f"Cannot find packages: {', '.join(unknown)}")
        elif unknown:
            raise PackageNotFoundError(f"Cannot find package {unknown[0]}")
        return [self.projects[package] for package in packages]

    def install_packages(
        self,
        packages: Optional[List[str]] = None,
        extras: Optional[List[str]] = None,
        skip: Optional[List[str]] = None,
    ) -> None:
        if packages is None:
            packages = []
        packages = list(packages)
        if extras is None:
            extras = []
        extras = list(extras)
        if skip is None:
            skip = []
        skip = list(skip)
        projects = self.get_packages(packages)
        for project in projects:
            for dep in project.private_dependencies:
                if dep not in skip:
                    self.install_packages([dep.pyproject.name], [], skip)
                    skip.append(dep.pyproject.name)
                    skip.extend(
                        [
                            nested_dep.pyproject.name
                            for nested_dep in dep.private_dependencies
                        ]
                    )
            if project not in skip:
                project.install(extras=extras, skip=skip)
                skip.append(project.pyproject.name)

    def build_packages(
        self, packages: List[str] = [], format: Optional[str] = None
    ) -> None:
        projects = self.get_packages(packages)
        out = self.root / "dist"
        out.mkdir(exist_ok=True)
        for project in projects:
            if project.pyproject.packages == []:
                continue
            project.build(format=format)
            for _file in project.dist_files:
                shutil.move(str(_file), out / _file.name)
            shutil.rmtree(project.root / "dist")

    def clean_packages(self, packages: List[str] = [], no_dist: bool = False) -> None:
        for project in self.get_packages(packages):
            project.clean(no_dist=no_dist)

    def test_packages(
        self, packages: List[str] = [], markers: List[str] = [], exprs: List[str] = []
    ) -> None:
        if not packages:
            all_sources = []
            for package in self.get_packages():
                all_sources += package.src
            self.test(markers, exprs, add_src=[str(source) for source in all_sources])
            return
        else:
            for project in self.get_packages(packages):
                project.test(markers=markers, exprs=exprs)

    def bump_packages(
        self, version: str, packages: List[str] = [], skip: List[str] = []
    ) -> None:
        for project in self.get_packages(packages):
            for dep in project.private_dependencies:
                if dep in skip:
                    continue
                self.bump_packages(version, [dep.pyproject.name], skip=skip)
                skip.append(dep.pyproject.name)
            if project.pyproject.name not in skip:
                project.bump(version)

    def lint_packages(self, packages: List[str] = []) -> None:
        for project in self.get_packages(packages):
            if project.pyproject.packages == []:
                continue
            project.lint()

    def typecheck_packages(self, packages: List[str] = []) -> None:
        for project in self.get_packages(packages):
            if project.pyproject.packages == []:
                continue
            project.typecheck()

    def format_packages(self, packages: List[str] = []) -> None:
        for project in self.get_packages(packages):
            if project.pyproject.packages == []:
                continue
            project.format()

    def update_packages(self, packages: Optional[List[str]] = None) -> None:
        packages = packages or []
        for project in self.get_packages(packages):
            project.update()

    def add_dependency(
        self, name: str, packages: List[str] = [], dev: bool = False
    ) -> None:
        for package in self.get_packages(packages):
            package.add_dep(name, dev=dev)

    def new_library(self, name: str) -> None:
        self._new_project(name, "libraries")

    def new_plugin(self, name: str) -> None:
        self._new_project(name, "plugins")

    def new_app(self, name: str) -> None:
        self._new_project(name, "applications", sources_parent="apps")

    def _new_project(
        self, name: str, folder: str, sources_parent: Optional[str] = None
    ) -> None:
        # Declare variable type
        to_include: Optional[str]
        # Create project directory. Dash character is allowed in project directory name
        project_root = self.root / folder / name
        project_root.mkdir(parents=True, exist_ok=True)
        # Convert dash to underscores for python package names
        package_name = name.replace("-", "_")
        # Relevant only when using a prefix in project configuration
        if self.config.prefix:
            sources_root = project_root / self.config.prefix.replace("-", "_")
            to_include = self.config.prefix.replace("-", "_")
            if package_name.startswith(self.config.prefix + "_"):
                package_name = package_name[len(self.config.prefix) + 1 :]
        else:
            to_include = None
        if sources_parent:
            sources_dir = sources_root / sources_parent / package_name
        else:
            sources_dir = sources_root / package_name
        # Bootstrap source directory
        sources_dir.mkdir(parents=True, exist_ok=False)
        init_file = sources_dir / "__init__.py"
        init_file.touch()
        # Bootstrap test directory
        project_tests = project_root / "tests"
        project_tests.mkdir(exist_ok=False, parents=False)
        conftest = project_tests / "conftest.py"
        conftest.touch()
        # Create pyproject.toml
        with current_directory(project_root):
            run(f"poetry init -n --name {name}")
        # Bootstrap source directory
        if package_name in stdlib_list():
            console.print(
                f"Warning: Generated module with name {package_name}. "
                f"The {package_name} module already exists in the standard library. "
                "You're gonna have a bad time.",
                style="yellow",
            )
        # Create project instance
        project = Project(project_root)
        # Update project version
        project.set_version(self.pyproject.version)
        # Update project authors
        project.set_authors(self.pyproject.authors)
        # Update project packages
        if to_include:
            project.set_include_packages([to_include])

    def export_packages(self) -> None:
        """Export packages using poetry and pip for offline usage."""
        export_directory = self.root / "dist"
        download_directory = export_directory / "_downloads"
        requirements = download_directory / "export.requirements"
        shutil.rmtree(export_directory, ignore_errors=True)
        download_directory.mkdir(parents=True, exist_ok=True)
        requirements.touch()
        for package in self.get_packages():
            with current_directory(package.root):
                if package.pyproject.packages != []:
                    package.build()
                run(f"poetry export >> {requirements}")
                _requirements = requirements.read_text()
                requirements.write_text(
                    "\n".join(
                        [
                            requirement
                            for requirement in _requirements.split("\n")
                            if "@" not in requirement
                        ]
                    )
                )
                wheels = package.root.glob("dist/*.whl")
                for wheel in wheels:
                    shutil.move(str(wheel), download_directory / wheel.name)
                if package.root == self.root:
                    continue
                shutil.rmtree(package.root / "dist")

        with current_directory(download_directory):
            run(f"pip download -r {requirements}")
        out_name = self.pyproject.name + "-" + self.pyproject.version
        shutil.make_archive(out_name, format="zip", root_dir=download_directory)
        out_file = self.root / "dist" / (out_name + ".zip")
        shutil.move(out_name + ".zip", str(out_file))
        shutil.rmtree(download_directory)
