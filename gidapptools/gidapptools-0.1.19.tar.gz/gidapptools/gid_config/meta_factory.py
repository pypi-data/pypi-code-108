"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import json
from typing import TYPE_CHECKING, Any, Union, Literal, Callable, Optional
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import attr

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.utility.helper import make_pretty, merge_content_to_json_file
from gidapptools.gid_config.interface import GidIniConfig
from gidapptools.abstract_classes.abstract_meta_factory import AbstractMetaItem, AbstractMetaFactory

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.meta_data.config_kwargs import ConfigKwargs

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

CONFIG_SPEC_PAIRS_TYPE = dict[
    str, dict[
        Union[Literal["config_file"], Literal["spec_file"]], Path
    ]
]


@attr.s(auto_attribs=True, auto_detect=True, kw_only=True)
class MetaConfig(AbstractMetaItem):
    config_paths: list[Path] = attr.ib()
    spec_paths: list[Path] = attr.ib()
    config_name_suffix: str = attr.ib(default='_config', converter=lambda x: x.casefold())
    spec_name_suffix: str = attr.ib(default="_configspec", converter=lambda x: x.casefold())
    config_class: type = attr.ib(default=GidIniConfig)
    file_changed_parameter: str = attr.ib(default='size')
    instances: dict[tuple[Path, Path], config_class] = {}

    @property
    def config_spec_pairs(self) -> CONFIG_SPEC_PAIRS_TYPE:
        pairs = {}
        configs = {item.stem.casefold().removesuffix(self.config_name_suffix): item for item in self.config_paths}
        specs = {item.stem.casefold().removesuffix(self.spec_name_suffix): item for item in self.spec_paths}
        for name, path in configs.items():
            pairs[name] = {"config_file": path, "spec_file": specs.get(name, None)}

        return pairs

    def get_config(self, name: str) -> Optional[GidIniConfig]:
        config_spec_pair = self.config_spec_pairs[name.casefold()]
        if (config_spec_pair.get("config_file"), config_spec_pair.get("spec_file")) not in self.instances:
            config = self.config_class(**config_spec_pair, file_changed_parameter=self.file_changed_parameter)
            config.reload()
            self.instances[(config_spec_pair.get("config_file"), config_spec_pair.get("spec_file"))] = config

        return self.instances[(config_spec_pair.get("config_file"), config_spec_pair.get("spec_file"))]

    def to_storager(self, storager: Callable = None) -> None:
        if storager is None:
            return
        storager(self)

    def clean_up(self, **kwargs) -> None:
        pass

    def as_dict(self, pretty: bool = False) -> dict[str, Any]:

        if pretty is True:
            return make_pretty(self)
        return attr.asdict(self)


class MetaConfigFactory(AbstractMetaFactory):
    product_class = MetaConfig
    default_configuration = {}

    def __init__(self, config_kwargs: "ConfigKwargs") -> None:
        super().__init__(config_kwargs=config_kwargs)
        self.config_dir: Path = config_kwargs.get("config_dir")
        self.spec_dir: Path = config_kwargs.get("config_spec_dir")
        self.config_paths: list[Path] = []
        self.spec_paths: list[Path] = []

    def _dev_init(self) -> None:
        self.config_dir: Path = self.config_kwargs.get("code_base_dir").joinpath("dev_temp", "config")
        self.spec_dir: Path = self.config_kwargs.get("code_base_dir").joinpath("dev_temp", "config", "spec")

    def _create_spec_file(self, name: str, content: Union[str, dict]) -> Path:
        self.spec_dir.mkdir(exist_ok=True, parents=True)
        full_path = self.spec_dir.joinpath(name).with_suffix('.json')
        if not isinstance(content, str):
            content = json.dumps(content, default=str, sort_keys=False, indent=4)

        full_path.write_text(content, encoding='utf-8', errors='ignore')

        return full_path

    def _create_config_file(self, name: str, content: str) -> Path:
        self.config_dir.mkdir(exist_ok=True, parents=True)
        full_path = self.config_dir.joinpath(name).with_suffix('.ini')
        if full_path.exists() is False:
            full_path.write_text(content, encoding='utf-8', errors='ignore')
        return full_path

    def create_files(self, file_to_create: Union[Path, tuple[str, Union[str, dict]]], typus) -> Path:
        if isinstance(file_to_create, Path):
            file_to_create = (file_to_create.name, file_to_create.read_text(encoding='utf-8', errors='ignore'))
        func = self._create_config_file if typus == "config" else self._create_spec_file
        return func(*file_to_create)

    def setup(self) -> None:
        if self.config_kwargs.get('is_dev', False) is True:
            self._dev_init()

        for config_to_create in self.config_kwargs.get("configs_to_create", []):
            self.config_paths.append(self.create_files(config_to_create, "config"))
        for spec_to_create in self.config_kwargs.get("spec_to_create", []):
            self.spec_paths.append(self.create_files(spec_to_create, "spec"))

    def _build(self) -> AbstractMetaItem:
        if self.is_setup is False:
            self.setup()
        kwargs = self.config_kwargs.get_kwargs_for(self.product_class, defaults={"config_paths": self.config_paths, "spec_paths": self.spec_paths})
        return self.product_class(**kwargs)

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
