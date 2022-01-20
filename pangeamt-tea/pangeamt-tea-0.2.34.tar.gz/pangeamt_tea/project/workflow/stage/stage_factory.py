import pkgutil
import inspect
import os
import importlib
from pangeamt_tea.project.workflow.stage.base_stage import BaseStage


class StageFactory:
    NAME = "NAME"
    INITIALIZED = False
    STAGES = {}

    @staticmethod
    def _init() -> None:
        if not StageFactory.INITIALIZED:
            package_dir = os.path.dirname(__file__)
            for _, mod, is_package in pkgutil.walk_packages(
                [package_dir], "pangeamt_tea.project.workflow.stage."
            ):
                # Import module
                mods = mod.split(".")
                module = mods[-1]
                package = ".".join(mods[0:-1])
                imported_module = importlib.import_module(
                    "." + module, package=package
                )

                # List all class in the imported module
                for _, cls in inspect.getmembers(
                    imported_module, inspect.isclass
                ):
                    if issubclass(cls, BaseStage) and cls != BaseStage:
                        # Get the "name" of the tokenizer
                        if not hasattr(cls, StageFactory.NAME):
                            raise ValueError(f"{cls} has no NAME attribute.")
                        name = getattr(cls, StageFactory.NAME)

                        # Avoid duplicate
                        if name in StageFactory.STAGES:
                            raise ValueError(
                                f"Stage name: {name} already exists."
                            )
                        StageFactory.STAGES[name] = cls
        StageFactory.INITIALIZED = True

    @staticmethod
    def new(stage_name, *args, **kwargs):
        if not StageFactory.INITIALIZED:
            StageFactory._init()

        if stage_name not in StageFactory.STAGES:
            raise ValueError(f"Stage `{stage_name}` not found.")
        cls = StageFactory.STAGES[stage_name]

        obj = cls(*args, **kwargs)
        return obj

    @staticmethod
    def get_available():
        if not StageFactory.INITIALIZED:
            StageFactory._init()
        return StageFactory.STAGES
