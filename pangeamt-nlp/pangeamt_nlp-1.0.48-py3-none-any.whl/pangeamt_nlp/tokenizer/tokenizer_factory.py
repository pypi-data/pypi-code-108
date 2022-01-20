import pkgutil
import inspect
import os
import importlib
from pangeamt_nlp.tokenizer.tokenizer_base import TokenizerBase


class TokenizerFactory:
    NAME = "NAME"
    LANGS = "LANGS"
    INITIALIZED = False
    TOKENIZERS = {}

    @staticmethod
    def _init() -> None:
        if not TokenizerFactory.INITIALIZED:
            package_dir = os.path.dirname(__file__)
            for _, mod, is_package in pkgutil.walk_packages(
                [package_dir], "pangeamt_nlp.tokenizer."
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
                    if issubclass(cls, TokenizerBase) and cls != TokenizerBase:
                        # Get the "name" of the tokenizer
                        if not hasattr(cls, TokenizerFactory.NAME):
                            raise ValueError(
                                f"Tokenizer `{cls}` has not attribute {TokenizerFactory.NAME}."
                            )
                        name = getattr(cls, TokenizerFactory.NAME)

                        # Check that the tokenizer has a LANGS attributes
                        if not hasattr(cls, TokenizerFactory.LANGS):
                            raise ValueError(
                                f"Tokenizer `{cls}` has not attribute {TokenizerFactory.LANGS}."
                            )

                        # Avoid duplicate
                        if name in TokenizerFactory.TOKENIZERS:
                            raise ValueError(
                                f"Tokenizer `{cls}` {TokenizerFactory.NAME} attribute already exists"
                            )
                        TokenizerFactory.TOKENIZERS[name] = cls
        TokenizerFactory.INITIALIZED = True

    @staticmethod
    def new(lang, tokenizer_name, *argv, **kwargs):
        if not TokenizerFactory.INITIALIZED:
            TokenizerFactory._init()

        if tokenizer_name not in TokenizerFactory.TOKENIZERS:
            raise ValueError(f"Tokenizer `{tokenizer_name}` not found.")
        cls = TokenizerFactory.TOKENIZERS[tokenizer_name]

        # if lang not in getattr(cls, TokenizerFactory.LANGS):
        #    raise ValueError(f'Tokenizer `{tokenizer_name}` isn\'t valid for language `{lang}`')

        obj = cls(lang, *argv, **kwargs)
        return obj

    def get_available(self):
        return self.TOKENIZERS
