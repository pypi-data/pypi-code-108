from collections import defaultdict
from logging import getLogger
from pathlib import Path, PurePosixPath
from typing import (
    Any,
    DefaultDict,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

from attr import Attribute, Factory, attrib, attrs
from pydantic import BaseModel, ValidationError
from yaml import safe_load as safe_load

from deckz.exceptions import DeckzException
from deckz.paths import Paths

_logger = getLogger(__name__)


@attrs(auto_attribs=True)
class Title:
    title: str
    level: int


class DirSectionConfig(BaseModel):
    default_titles: Optional[Dict[str, str]]
    flavors: Dict[str, List[Union[str, Dict[str, Optional[str]]]]]
    title: str

    @classmethod
    def from_yaml_file(cls, path: Path) -> "DirSectionConfig":
        try:
            return cls.parse_obj(safe_load(path.read_text(encoding="utf8")))
        except (IOError, ValidationError) as e:
            raise DeckzException(f"Could not load {path} section config") from e


Content = str
ContentOrTitle = Union[Content, Title]


@attrs(auto_attribs=True)
class Part:
    title: Optional[str]
    sections: List[ContentOrTitle] = Factory(list)


@attrs(auto_attribs=True)
class Dependencies:
    used: Set[Path] = Factory(set)
    missing: Set[str] = Factory(set)
    unused: Set[Path] = Factory(set)

    def update(self, other: "Dependencies") -> None:
        self.used |= other.used
        self.missing |= other.missing
        self.unused |= other.unused - self.used
        self.unused -= other.used

    @staticmethod
    def merge(*dependencies_list: "Dependencies") -> "Dependencies":
        dependencies = Dependencies()
        for ds in dependencies_list:
            dependencies.used |= ds.used
            dependencies.missing |= ds.missing
            dependencies.unused |= ds.unused - dependencies.used
            dependencies.unused -= ds.used
        return dependencies

    @staticmethod
    def merge_dicts(
        *dependencies_dicts: Dict[str, "Dependencies"]
    ) -> Dict[str, "Dependencies"]:
        keys = set.union(*(set(d) for d in dependencies_dicts))
        merged_dict = {}
        for key in keys:
            merged_dict[key] = Dependencies.merge(
                *(d[key] for d in dependencies_dicts if key in d)
            )
        return merged_dict


@attrs(auto_attribs=True)
class Target:
    name: str
    dependencies: Dependencies
    parts: List[Part]
    section_dependencies: DefaultDict[str, Dependencies]
    section_flavors: DefaultDict[str, Set[str]]

    @classmethod
    def from_targets(cls, targets: Iterable["Target"], name: str) -> "Target":
        dependencies = Dependencies.merge(*(t.dependencies for t in targets))
        parts = [p for t in targets for p in t.parts]
        section_dependencies: DefaultDict[str, Dependencies] = defaultdict(Dependencies)
        for t in targets:
            for k, v in t.section_dependencies.items():
                section_dependencies[k].update(v)
        section_flavors = defaultdict(set)
        for target in targets:
            for key, value in target.section_flavors.items():
                section_flavors[key].update(value)
        return Target(name, dependencies, parts, section_dependencies, section_flavors)


@attrs(auto_attribs=True)
class TargetBuilder:
    _data: Dict[str, Any]
    _paths: Paths

    def build(self) -> Target:
        all_dependencies = Dependencies()
        all_dependencies.unused.update(self._paths.local_latex_dir.glob("**/*.tex"))
        all_items = []
        section_dependencies: DefaultDict[str, Dependencies] = defaultdict(Dependencies)
        section_flavors = defaultdict(set)
        for section_config in self._data["sections"]:
            if not isinstance(section_config, dict):
                section_config = dict(path=section_config)
            section_path = section_config["path"]
            section_flavors[section_path].add(section_config.get("flavor"))
            result = self._parse_section_dir(
                section_path, section_config, 0, section_flavors, section_dependencies
            )
            if result is None:
                result = self._parse_section_file(section_path, section_config, 0)
            if result is not None:
                items, dependencies = result
                all_items.extend(items)
            else:
                dependencies = Dependencies()
                dependencies.missing.add(section_path)
            all_dependencies.update(dependencies)
            section_dependencies[section_path].update(dependencies)
        return Target(
            name=self._data["name"],
            dependencies=all_dependencies,
            parts=[Part(title=self._data["title"], sections=all_items)],
            section_dependencies=section_dependencies,
            section_flavors=section_flavors,
        )

    def _parse_section_dir(
        self,
        section_path_str: str,
        custom_config: Dict[str, Any],
        title_level: int,
        section_flavors: DefaultDict[str, Set[str]],
        section_dependencies: DefaultDict[str, Dependencies],
    ) -> Optional[Tuple[List[ContentOrTitle], Dependencies]]:
        section_path = Path(section_path_str)
        local_section_dir = self._paths.local_latex_dir / section_path
        local_section_config_path = (local_section_dir / section_path).with_suffix(
            ".yml"
        )
        shared_section_dir = self._paths.shared_latex_dir / section_path
        shared_section_config_path = (
            shared_section_dir / section_path.parts[-1]
        ).with_suffix(".yml")
        dependencies = Dependencies()
        if local_section_config_path.exists():
            section_config_path = local_section_config_path
        elif shared_section_config_path.exists():
            section_config_path = shared_section_config_path
        else:
            return None
        section_config = DirSectionConfig.from_yaml_file(section_config_path)
        title = (
            custom_config["title"] if "title" in custom_config else section_config.title
        )
        if "flavor" not in custom_config:
            raise DeckzException(
                f"Incorrect targets {self._paths.targets}. "
                f"Mandatory flavor not specified in {section_path} configuration."
            )
        flavor_name = custom_config["flavor"]
        if flavor_name not in section_config.flavors:
            flavors_string = ", ".join("'%s'" % f for f in section_config.flavors)
            raise DeckzException(
                f"Incorrect targets {self._paths.targets}. "
                f"'{flavor_name}' not amongst available flavors: {flavors_string} "
                f"of {section_config_path}."
            )

        flavor = section_config.flavors[flavor_name]
        items: List[ContentOrTitle] = [Title(title=title, level=title_level)]
        for item in flavor:
            self._process_item(
                item=item,
                items=items,
                dependencies=dependencies,
                default_titles=section_config.default_titles,
                section_config=custom_config,
                local_section_dir=local_section_dir,
                shared_section_dir=shared_section_dir,
                section_path_str=section_path_str,
                title_level=title_level + 1,
                section_flavors=section_flavors,
                section_dependencies=section_dependencies,
            )
        return items, dependencies

    def _process_item(
        self,
        item: Union[str, Dict[str, Optional[str]]],
        items: List[ContentOrTitle],
        dependencies: Dependencies,
        default_titles: Optional[Dict[str, str]],
        section_config: Dict[str, Any],
        local_section_dir: Path,
        shared_section_dir: Path,
        section_path_str: str,
        title_level: int,
        section_flavors: DefaultDict[str, Set[str]],
        section_dependencies: DefaultDict[str, Dependencies],
    ) -> None:
        if isinstance(item, str):
            filename = item
            if default_titles is not None:
                title = default_titles.get(filename)
            else:
                title = None
        else:
            filename, title = next(iter(item.items()))
        if "excludes" in section_config and filename in section_config["excludes"]:
            return
        if filename.startswith("/"):
            local_path = (self._paths.local_latex_dir / filename[1:]).with_suffix(
                ".tex"
            )
            shared_path = (self._paths.shared_latex_dir / filename[1:]).with_suffix(
                ".tex"
            )
        elif filename.startswith("$"):
            assert title is not None
            self._process_nested_section(
                section_path_str=section_path_str,
                nested_section_path_str=filename,
                flavor=title,
                title_level=title_level,
                section_flavors=section_flavors,
                section_dependencies=section_dependencies,
                items=items,
                dependencies=dependencies,
            )
            return
        else:
            local_path = (local_section_dir / filename).with_suffix(".tex")
            shared_path = (shared_section_dir / filename).with_suffix(".tex")
        if title is not None:
            items.append(Title(title=title, level=title_level))
        local_relative_path = local_path.relative_to(self._paths.current_dir)
        shared_relative_path = shared_path.relative_to(self._paths.shared_dir)
        if local_path.exists():
            items.append(str(PurePosixPath(local_relative_path.with_suffix(""))))
            dependencies.used.add(local_path.resolve())
        elif shared_path.exists():
            items.append(str(PurePosixPath(shared_relative_path.with_suffix(""))))
            dependencies.used.add(shared_path.resolve())
        else:
            dependencies.missing.add(filename)

    def _process_nested_section(
        self,
        section_path_str: str,
        nested_section_path_str: str,
        flavor: str,
        title_level: int,
        section_flavors: DefaultDict[str, Set[str]],
        section_dependencies: DefaultDict[str, Dependencies],
        items: List[ContentOrTitle],
        dependencies: Dependencies,
    ) -> None:
        if nested_section_path_str.startswith("$/"):
            nested_section_path = nested_section_path_str[2:]
        else:
            nested_section_path = f"{section_path_str}/{nested_section_path_str[1:]}"
        parsed_nested_dir = self._parse_section_dir(
            nested_section_path,
            dict(flavor=flavor),
            title_level,
            section_flavors,
            section_dependencies,
        )
        assert parsed_nested_dir is not None
        nested_items, nested_dependencies = parsed_nested_dir
        section_flavors[nested_section_path].add(flavor)
        section_dependencies[nested_section_path].update(nested_dependencies)
        items.extend(nested_items)
        dependencies.update(nested_dependencies)

    def _parse_section_file(
        self, section_path: str, config: Dict[str, Any], title_level: int
    ) -> Optional[Tuple[List[ContentOrTitle], Dependencies]]:
        local_section_file = (self._paths.local_latex_dir / section_path).with_suffix(
            ".tex"
        )
        shared_section_file = (self._paths.shared_latex_dir / section_path).with_suffix(
            ".tex"
        )
        if local_section_file.exists():
            section_file = local_section_file
            relative_path = section_file.relative_to(self._paths.current_dir)
        elif shared_section_file.exists():
            section_file = shared_section_file
            relative_path = section_file.relative_to(self._paths.shared_dir)
        else:
            return None
        config_file = section_file.with_suffix(".yml")
        items: List[ContentOrTitle] = []
        if "title" in config:
            title = config["title"]
        elif config_file.exists():
            title = safe_load(config_file.read_text(encoding="utf8"))["title"]
        else:
            title = None
        if title is not None:
            items.append(Title(title=title, level=title_level))
        items.append(str(PurePosixPath(relative_path)))
        dependencies = Dependencies()
        dependencies.used.add(section_file.resolve())
        return items, dependencies


@attrs(auto_attribs=True)
class Targets(Iterable[Target]):
    _targets: List[Target] = attrib()
    _paths: Paths

    @classmethod
    def from_file(
        cls, paths: Paths, whitelist: Optional[List[str]] = None
    ) -> "Targets":
        if not paths.targets.exists():
            raise DeckzException(f"Could not find {paths.targets}.")
        content = safe_load(paths.targets.read_text(encoding="utf8"))
        return cls.from_data(data=content, paths=paths, whitelist=whitelist)

    @classmethod
    def from_data(
        cls,
        data: List[Dict[str, Any]],
        paths: Paths,
        whitelist: Optional[List[str]] = None,
    ) -> "Targets":
        for target_data in data:
            if target_data["name"] == "all":
                raise DeckzException(
                    f"Incorrect targets {paths.targets}: "
                    '"all" is a reserved target name.'
                )
        targets = [TargetBuilder(data=target, paths=paths).build() for target in data]
        if whitelist is not None:
            cls._filter_targets(targets, frozenset(whitelist), paths)
        return Targets(targets, paths)

    @_targets.validator
    def _check_targets(self, attribute: Attribute, value: List[Target]) -> None:
        missing_dependencies = {
            target.name: target.dependencies.missing
            for target in value
            if target.dependencies.missing
        }
        if missing_dependencies:
            raise DeckzException(
                f"Incorrect targets {self._paths.targets}. "
                "Could not find the following dependencies:\n%s"
                % "\n".join(
                    "  - %s:\n%s" % (k, "\n".join(f"    - {p}" for p in v))
                    for k, v in missing_dependencies.items()
                ),
            )

    @staticmethod
    def _filter_targets(
        targets: Iterable[Target], whiteset: FrozenSet[str], paths: Paths
    ) -> List[Target]:
        unmatched = whiteset - frozenset(target.name for target in targets)
        if unmatched:
            raise DeckzException(
                f"Incorrect targets {paths.targets}. "
                "Could not find the following targets:\n%s"
                % "\n".join("  - %s" % name for name in unmatched)
            )
        return [target for target in targets if target.name in whiteset]

    def __iter__(self) -> Iterator[Target]:
        return iter(self._targets)

    def __len__(self) -> int:
        return len(self._targets)
