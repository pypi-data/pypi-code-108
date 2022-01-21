'''dummy_base_class_importer.py

Custom importer that imports classes with dummy base classes
that get properly resolved later.

Example:
    To defer the registering of a base class on import,

        >>> with DummyBaseClassImport():
        >>>     from x import y

'''

import importlib.util
import sys
import os
import re
import warnings
from collections import OrderedDict

from mastapy._internal import base
from mastapy._internal.custom_warnings import MastapyImportWarning
from mastapy._internal.mastapy_import_exception import MastapyImportException


class _DummyBaseClassImporter:

    _debug = False
    _score = 0
    _depth = 0
    _class_re = re.compile(
        r'class ([A-Z][A-Za-z0-9]*)'
        r'(\((((_[0-9]+\.)?[A-Z][A-Za-z0-9\[\'\]]*(, )?)*)\))?')

    _generic_re = re.compile(r'Generic\[([A-z0-9_ ,]+)\]')
    _generic_bases = (
        base.GenericBase,
        base.GenericBase2,
        base.GenericBase3,
        base.GenericBase4,
        base.GenericBase5,
        base.GenericBase6,
        base.GenericBase7)

    class_map = dict()
    id_to_full_path = dict()

    @classmethod
    def _remove_brackets(cls, name):
        name = name.strip()
        try:
            num_index = name.rindex('[')
            return name[:num_index]
        except ValueError:
            return name

    @classmethod
    def _replace_with_generic_base(cls, bases):
        if not bases:
            return base.Base

        found_generic = cls._generic_re.search(bases)

        if found_generic:
            num_bases = len(found_generic.group(1).split(','))
            return cls._generic_bases[num_bases - 1]

        return base.Base

    @classmethod
    def _get_class_name_and_dummy_class(cls, source):
        found_class = cls._class_re.search(source)

        if found_class:
            class_name = found_class.group(1)
            bases = found_class.group(3)
            dummy_class = cls._replace_with_generic_base(bases)

            bases_it = map(
                cls._remove_brackets, bases.split(',')) if bases else None
            return class_name, dummy_class, bases_it

    @classmethod
    def _get_last_item_in_path(cls, module_name):
        num_index = module_name.rindex('.')
        return module_name[num_index + 1:]

    @classmethod
    def _safe_insert(cls):
        if cls not in sys.meta_path:
            sys.meta_path.insert(0, cls)

    @classmethod
    def _safe_remove(cls):
        if cls in sys.meta_path:
            sys.meta_path.remove(cls)

    @classmethod
    def _get_line_no(cls):
        x = sys.exc_info()[-1]
        while x.tb_next:
            x = x.tb_next
        return x.tb_lineno

    @classmethod
    def _load_module_with_dummy_class(cls, package, module_name):
        cls._safe_remove()

        try:
            spec = importlib.util.find_spec(module_name, package)

            if spec:
                cls._score = cls._score + 1

                if cls._debug:
                    print(' >>> Finding spec ({}): {}'.format(
                        cls._score, module_name))

                source_path = package + module_name if package else module_name
                source = spec.loader.get_source(source_path)
                class_data = cls._get_class_name_and_dummy_class(source)

                if not class_data:
                    return

                class_name, dummy_class, base_classes = class_data

                module = importlib.util.module_from_spec(spec)
                module.__dict__[class_name] = dummy_class
                sys.modules[module_name] = module
                code_obj = compile(source, module.__spec__.origin, 'exec')

                class_map_number = cls._get_last_item_in_path(module_name)
                cls.class_map[class_map_number] = (
                    class_name,
                    ([tuple(x.split('.')) for x in base_classes]
                        if base_classes else []))
                cls.id_to_full_path[class_map_number] = module_name

                cls._safe_insert()
                try:
                    exec(code_obj, module.__dict__)
                except Exception as e:
                    if cls._debug:
                        line_no = cls._get_line_no()
                        print((
                            'An exception occurred while interpreting {} '
                            'on line {}: {}').format(module_name, line_no, e))
                    raise
            else:
                raise ImportError(
                    'Failed to load module {}.'.format(module_name))
        finally:
            cls._safe_insert()

        return spec

    @classmethod
    def find_spec(cls, name, path, target=None):
        '''Finds the module spec'''

        try:
            end = os.sep + 'mastapy'
            my_dir = __file__[:__file__.rindex(end) + len(end)]
            if (name and path and path[0].startswith(my_dir) and
                    ('_internal.implicit' in path[0]
                        or '_internal' not in path[0])):
                return cls._load_module_with_dummy_class(None, name)
        except Exception as e:
            raise MastapyImportException(str(e))

    @classmethod
    def start_deferring_base_classes(cls, debug):
        ''' Flags the start of the deferring operations.

        Args:
            debug (bool): Print debug information or not
        '''

        cls._debug = debug
        cls._depth += 1
        return cls._depth == 1

    @classmethod
    def resolve_base_classes(cls):
        ''' Flags the end of the deferring operations.'''

        cls._depth -= 1
        return cls._depth == 0


class _DummyBaseClassImport:

    _num_re = re.compile(r'_[0-9]+$')

    def __init__(self, recursion_limit=2500, debug=False):
        self._debug = debug
        self._recursion_limit = recursion_limit
        self._old_recursion_limit = sys.getrecursionlimit()

    def __enter__(self):
        if self._debug:
            print('---------------Entered ({})---------------'.format(
                _DummyBaseClassImporter._depth))
        if _DummyBaseClassImporter.start_deferring_base_classes(self._debug):
            sys.setrecursionlimit(self._recursion_limit)
            sys.meta_path.insert(0, _DummyBaseClassImporter)

    def _resolve_imports(self, id_to_path_map):
        for module_id, (class_name, base_class_data) in \
                _DummyBaseClassImporter.class_map.items():
            module_name = id_to_path_map[module_id]
            module = sys.modules[module_name]

            base_classes = tuple([getattr(
                sys.modules[id_to_path_map[base_data[0]]], base_data[1])
                for base_data in base_class_data if len(base_data) > 1])

            base_classes_length = len(base_classes)
            if base_classes_length > 0:
                class_ = getattr(module, class_name)
                old_bases = class_.__bases__
                merged_bases = base_classes + old_bases[base_classes_length:]
                class_.__bases__ = (
                    tuple(OrderedDict.fromkeys(merged_bases).keys())
                    if len(old_bases) > base_classes_length else
                    tuple(base_classes))

    def __exit__(self, type_, value, traceback):
        if _DummyBaseClassImporter.resolve_base_classes():

            sys.meta_path.pop(0)
            sys.setrecursionlimit(self._old_recursion_limit)

            try:
                self._resolve_imports(_DummyBaseClassImporter.id_to_full_path)
            except (KeyError, TypeError, AttributeError):
                warnings.warn((
                    'Failed to import mastapy correctly. Please read the '
                    'following exception (The last line of the exception '
                    'will be the error!)\n'), MastapyImportWarning)

        if self._debug:
            print('---------------Exited  ({})---------------'.format(
                _DummyBaseClassImporter._depth))
