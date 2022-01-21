"""NanamiLang BDB CLasses"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


class BuiltinFunctionsDB:
    """BuiltinFunctionsDB: __should__ be initialized to work"""

    cached = {}
    source_cls: callable = None

    @classmethod
    def initialize(cls, source_cls):
        """Initialize BuiltinFunctionsDB"""

        cls.source_cls = source_cls  # <- should be BuiltinFunctions

    @classmethod
    def initialized(cls) -> bool:
        """Whether source is None or not"""

        return cls.source_cls is not None  # <- but it can be whatever user want

    @classmethod
    def resolve(cls, fn_name: str) -> dict:
        """Resolve builtin func by its name"""

        if not cls.initialized():
            return {}  # <- return {} if there is no source class to consume from

        if fun := cls.cached.get(fn_name, {}):
            return fun
        for macro in cls.functions():
            if macro.meta.get('name') == fn_name:
                resolved: dict = {'function_name': fn_name,
                                  'function_reference': macro}
                cls.cached.update({fn_name: resolved})
                return resolved
        return {}

    @classmethod
    def names(cls) -> list:
        """Return LISP names"""

        return [_.meta.get('name') for _ in cls.functions()]

    @classmethod
    def functions(cls) -> list:
        """Return all builtin function handles"""

        if not cls.initialized():
            return []  # <- return {} if there is no source class to consume from

        attrib_names = filter(lambda _: '_func' in _, cls.source_cls().__dir__())

        return list(map(lambda n: getattr(cls.source_cls, n, None), attrib_names))


class BuiltinMacrosDB:
    """BuiltinMacrosDB: __should__ be initialized to work"""

    cached = {}
    source_cls: callable = None

    @classmethod
    def initialize(cls, source_cls):
        """Initialize BuiltinMacroDB"""

        cls.source_cls = source_cls  # <- should be BuiltinMacro

    @classmethod
    def initialized(cls) -> bool:
        """Whether source is None or not"""

        return cls.source_cls is not None  # <- but it can be whatever user want

    @classmethod
    def resolve(cls, mc_name: str) -> dict:
        """Resolve builtin macro by its name"""

        if not cls.initialized():
            return {}  # <- return {} if there is no source class to consume from

        if fun := cls.cached.get(mc_name, {}):
            return fun
        for macro in cls.functions():
            if macro.meta.get('name') == mc_name:
                resolved: dict = {'macro_name': mc_name,
                                  'macro_reference': macro}
                cls.cached.update({mc_name: resolved})
                return resolved
        return {}

    @classmethod
    def names(cls) -> list:
        """Return LISP names"""

        return [_.meta.get('name') for _ in cls.functions()]

    @classmethod
    def functions(cls) -> list:
        """Return all builtin macro handles"""

        if not cls.initialized():
            return []  # <- return {} if there is no source class to consume from

        attrib_names = filter(lambda _: '_macro' in _, cls.source_cls().__dir__())

        return list(map(lambda n: getattr(cls.source_cls, n, None), attrib_names))
