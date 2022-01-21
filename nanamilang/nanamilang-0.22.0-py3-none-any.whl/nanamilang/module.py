"""NanamiLang Module Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import time
from typing import List, Dict

from nanamilang.ast import AST
from nanamilang.token import Token
from nanamilang.datatypes import Base
from nanamilang.tokenizer import Tokenizer
from nanamilang.formatter import Formatter
from nanamilang.shortcuts import ASSERT_IS_INSTANCE_OF
from nanamilang.shortcuts import ASSERT_COLLECTION_IS_NOT_EMPTY


class Module:
    """
    NanamiLang Module

    from nanamilang import bdb
    from nanamilang import module
    from nanamilang import builtin

    # These steps are required to make builtins work

    bdb.BuiltinMacrosDB.initialize(builtin.BuiltinMacros)
    bdb.BuiltinFunctionsDB.initialize(builtin.BuiltinFunctions)

    source = str('(+ 2 2 (* 2 2))')
    m = module.Module(source=source)

    # or you can create empty module, then prepare a source code

    m: module.Module = module.Module()
    m.prepare(source)

    m.format() # => '(+ 2 2 (* 2 2))'
    m.ast() # => will return an encapsulated AST instance
    m.tokenized() # => will return a collection of a Token instances
    <..you can also lookup for other getters using a dir() function...>

    results = m.evaluate().results() # will return an (<IntegerNumber>: 8)
    """

    class EnvironStorage:
        """NanamiLang Module Environ"""

        _storage: dict
        _m_ref: 'Module'
        _m_mapping: dict

        def __init__(self,
                     m_ref: 'Module') -> None:
            """Initialize a new Environ instance"""

            self._storage = {}
            self._m_ref = m_ref
            self._m_mapping = {m_ref.name(): m_ref}

            # Initialize with empty storage && module mapping

        def storage(self) -> dict:
            """Module::Environ self._storage getter"""

            return self._storage

        def _from_qualified_name(self,
                                 g_name: str) -> tuple:
            """Module::Environ from qualified global' name"""

            m_name, g_name = g_name.split('/') \
                if '/' in g_name and not g_name.startswith('/') \
                else (self._m_ref.name(), g_name)

            return g_name,  self._m_mapping.get(m_name)  # <- name and module ref

        def get(self, g_name: str, default: Base = None) -> Base:
            """Module::Environ get global by its name and module"""

            unq_g_name, m_ref = self._from_qualified_name(g_name)
            if not m_ref:
                m_ref = self._m_ref
            if m_ref is not self._m_ref:
                return m_ref.environ().get(unq_g_name, default=default)
            retval = self._storage.get(unq_g_name, default)  # <- actually do get
            m_ref.event('environment::get')([unq_g_name])  # <- trigger get event
            return retval  # <- actually return a getting operation result to top

        def set(self, g_name: str, dtype: Base) -> None:
            """Module::Environ set global by its name and module"""

            unq_g_name, m_ref = self._from_qualified_name(g_name)
            if not m_ref:
                m_ref = self._m_ref
            if m_ref is not self._m_ref:
                return m_ref.environ().set(unq_g_name, dtype=dtype)
            retval = self._storage.update({unq_g_name: dtype})  # <- actually set
            m_ref.event('environment::set')([unq_g_name])  # <- trigger set event
            return retval  # <- actually return a setting operation result to top

        def grab(self, m_ref: 'Module') -> None:
            """Module::Environ take another module and grab environ from there"""

            self._m_mapping.update({m_ref.name(): m_ref})
            for g_name, dtype in m_ref.environ().storage().items():
                self.set(f'{m_ref.name()}/{g_name}', dtype)  # <- update globals!

    _on: dict
    _ast: AST
    _name: str
    _source: str
    _formatter = Formatter
    _tokenized: List[Token]
    _environ: EnvironStorage
    _evaluation_results = tuple
    _measurements: Dict[str, float] = None

    def __init__(self,
                 name: str = None,
                 source: str = None) -> None:
        """
        Initialize a new NanamiLang Module instance

        :param source: your NanamiLang module source code
        """

        self._measurements = {}
        self._name = name or '__main__'
        self._environ = self.EnvironStorage(self)
        self._on = {'environment::set': lambda args: None,
                    'environment::get': lambda args: None}

        # Module name is optional value, but if present - set to it

        if source:
            self.prepare(source)

        # Source code is optional value, but if present - call prepare

    def name(self):
        """NanamiLang Module, self._name getter"""

        return self._name

    def environ(self) -> EnvironStorage:
        """NanamiLang Module, self._environ getter"""

        return self._environ  # <- to get/set global

    def prepare(self, source: str):
        """NanamiLang Module, prepare a source code"""

        ASSERT_IS_INSTANCE_OF(source, str)
        ASSERT_COLLECTION_IS_NOT_EMPTY(source)

        self._source = source
        __tokenize_start__ = time.perf_counter()
        self._tokenized = Tokenizer(source=self._source,
                                    name=self._name).tokenize()
        __tokenize_delta__ = time.perf_counter() - __tokenize_start__
        __make_wood_start__ = time.perf_counter()
        self._ast = AST(self._tokenized, self.name())
        __make_wood_delta__ = time.perf_counter() - __make_wood_start__
        self._formatter = Formatter(self._tokenized)
        self._measurements = {
            '[Tree]': __make_wood_delta__, '[Parse]': __tokenize_delta__,
        }

    def ast(self) -> AST:
        """NanamiLang Module, self._ast getter"""

        return self._ast

    def event(self, event: str) -> callable:
        """NanamiLang Module, a self._on getter"""

        return self._on.get(event, lambda _: None)

    def on(self, event: str, cb) -> None:
        """Allows set a certain module event handler"""

        self._on[event] = cb  # <- store event callback

    def tokenized(self) -> List[Token]:
        """NanamiLang Module, self._tokenized getter"""

        return self._tokenized

    def measurements(self) -> Dict[str, float]:
        """NanamiLang Module, self._measurements getter"""

        return self._measurements

    def results(self) -> tuple:
        """NanamiLang Module, self.__evaluation_results getter"""

        return self._evaluation_results

    def format(self) -> str:
        """NanamiLang Module, call self._formatter.format() to format source"""

        return self._formatter.format()

    def evaluate(self) -> 'Module':
        """NanamiLang Module, call self._ast.evaluate() to evaluate your module"""

        __evaluate_start__ = time.perf_counter()
        self._evaluation_results = self._ast.evaluate(self._environ)
        __evaluate_delta__ = time.perf_counter() - __evaluate_start__
        self._measurements.update({'[Evaluation]': __evaluate_delta__})
        return self

        # Measure [Evaluation] time and store measurement in self._measurements dictionary
        # Store all evaluated trees of the self.ast().wood() and return self to the caller
