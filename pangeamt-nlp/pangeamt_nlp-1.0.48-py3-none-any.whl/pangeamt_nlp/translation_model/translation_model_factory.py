import pkgutil
import inspect
import os
import importlib
from pangeamt_nlp.translation_model.translation_model_base import (
    TranslationModelBase,
)


class TranslationModelFactory:
    NAME = "NAME"
    INITIALIZED = False
    TRANSLATION_MODELS = {}

    @staticmethod
    def _init() -> None:
        if not TranslationModelFactory.INITIALIZED:
            package_dir = os.path.dirname(__file__)
            for _, mod, is_package in pkgutil.walk_packages(
                [package_dir], "pangeamt_nlp.translation_model."
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
                    if (
                        issubclass(cls, TranslationModelBase)
                        and cls != TranslationModelBase
                    ):
                        # Get the "name" of the tokenizer
                        if not hasattr(cls, TranslationModelFactory.NAME):
                            raise ValueError(
                                f"Trainer `{cls}` has not attribute {TranslationModelFactory.NAME}."
                            )
                        name = getattr(cls, TranslationModelFactory.NAME)

                        # Avoid duplicate
                        if name in TranslationModelFactory.TRANSLATION_MODELS:
                            raise ValueError(
                                f"Trainer `{cls}` {TranslationModelFactory.NAME} attribute already exists"
                            )
                        TranslationModelFactory.TRANSLATION_MODELS[name] = cls
        TranslationModelFactory.INITIALIZED = True

    @staticmethod
    def new(translation_model_name, *args, **kwargs):
        if not TranslationModelFactory.INITIALIZED:
            TranslationModelFactory._init()

        if (
            translation_model_name
            not in TranslationModelFactory.TRANSLATION_MODELS
        ):
            raise ValueError(
                f"Translation model `{translation_model}` not found."
            )
        cls = TranslationModelFactory.TRANSLATION_MODELS[
            translation_model_name
        ]

        obj = cls(*args, **kwargs)
        return obj

    @staticmethod
    def get_class(translation_model_name: str):
        if not TranslationModelFactory.INITIALIZED:
            TranslationModelFactory._init()

        if (
            translation_model_name
            not in TranslationModelFactory.TRANSLATION_MODELS
        ):
            raise ValueError(
                f"Translation model `{translation_model}` not found."
            )
        cls = TranslationModelFactory.TRANSLATION_MODELS[
            translation_model_name
        ]
        return cls

    @staticmethod
    def get_available():
        if not TranslationModelFactory.INITIALIZED:
            TranslationModelFactory._init()
        return TranslationModelFactory.TRANSLATION_MODELS
