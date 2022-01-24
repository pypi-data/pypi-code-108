#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from .console import AdvancedConsole
import logging
from . import config
from . import tools as Tools
import importlib
from cleep.common import CATEGORIES
import re
import inspect
import glob
import copy
import json
import time

class Check():
    """
    Handle module check:
        - check backend: variables, function
        - check frontend: config, desc.json, modImgSrc directive
        - run pylint on backend
    """

    PYLINTRC = """[MASTER]
extension-pkg-whitelist=
ignore=git
ignore-patterns=
jobs=1
load-plugins=
persistent=yes
suggestion-mode=yes
unsafe-load-any-extension=no

[MESSAGES CONTROL]
confidence=
disable=print-statement,
        parameter-unpacking,
        unpacking-in-except,
        old-raise-syntax,
        backtick,
        long-suffix,
        old-ne-operator,
        old-octal-literal,
        import-star-module-level,
        non-ascii-bytes-literal,
        invalid-unicode-literal,
        raw-checker-failed,
        bad-inline-option,
        locally-disabled,
        locally-enabled,
        file-ignored,
        suppressed-message,
        useless-suppression,
        deprecated-pragma,
        apply-builtin,
        basestring-builtin,
        buffer-builtin,
        cmp-builtin,
        coerce-builtin,
        execfile-builtin,
        file-builtin,
        long-builtin,
        raw_input-builtin,
        reduce-builtin,
        standarderror-builtin,
        unicode-builtin,
        xrange-builtin,
        coerce-method,
        delslice-method,
        getslice-method,
        setslice-method,
        no-absolute-import,
        old-division,
        dict-iter-method,
        dict-view-method,
        next-method-called,
        metaclass-assignment,
        indexing-exception,
        raising-string,
        reload-builtin,
        oct-method,
        hex-method,
        nonzero-method,
        cmp-method,
        input-builtin,
        round-builtin,
        intern-builtin,
        unichr-builtin,
        map-builtin-not-iterating,
        zip-builtin-not-iterating,
        range-builtin-not-iterating,
        filter-builtin-not-iterating,
        using-cmp-argument,
        eq-without-hash,
        div-method,
        idiv-method,
        rdiv-method,
        exception-message-attribute,
        invalid-str-codec,
        sys-max-int,
        # bad-python3-import,
        # deprecated-string-function,
        deprecated-str-translate-call,
        # deprecated-itertools-function,
        # deprecated-types-field,
        next-method-defined,
        # dict-items-not-iterating,
        # dict-keys-not-iterating,
        # dict-values-not-iterating,
        # deprecated-operator-function,
        # deprecated-urllib-function,
        xreadlines-attribute,
        # deprecated-sys-function,
        exception-escape,
        comprehension-escape,
        too-few-public-methods,
        too-many-instance-attributes,
        trailing-newlines,
        len-as-condition,
        logging-not-lazy,
        broad-except,
        missing-module-docstring,
        relative-beyond-top-level, # to remove when pylint bug resolved
enable=c-extension-no-member

[REPORTS]
evaluation=10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)
output-format=text
reports=no
score=yes

[REFACTORING]
max-nested-blocks=5
never-returning-functions=optparse.Values,sys.exit

[TYPECHECK]
contextmanager-decorators=contextlib.contextmanager
# zmq.{LINGER,REQ,ROUTER,NOBLOCK} are dynamically generated and so pylint
# doesn't see them, causing false positives.
generated-members=PAIR,RCVHWM,SNDHWM,SNDTIMEO,RCVTIMEO,netifaces.*
ignore-mixin-members=yes
ignore-on-opaque-inference=yes
ignored-classes=optparse.Values,thread._local,_thread._local
ignored-modules=
missing-member-hint=yes
missing-member-hint-distance=1
missing-member-max-choices=1

[VARIABLES]
additional-builtins=
allow-global-unused-variables=yes
callbacks=cb_,
          _cb
dummy-variables-rgx=_+$|(_[a-zA-Z0-9_]*[a-zA-Z0-9]+?$)|dummy|^ignored_|^unused_
ignored-argument-names=_.*|^ignored_|^unused_
init-import=no
redefining-builtins-modules=six.moves,past.builtins,future.builtins,io,builtins

[SPELLING]
max-spelling-suggestions=4
spelling-dict=
spelling-ignore-words=
spelling-private-dict-file=
spelling-store-unknown-words=no

[FORMAT]
expected-line-ending-format=
ignore-long-lines=^\s*(# )?<?https?://\S+>?$
indent-after-paren=4
indent-string='    '
max-line-length=130
max-module-lines=1000
no-space-check=trailing-comma,
               dict-separator
single-line-class-stmt=no
single-line-if-stmt=no

[BASIC]
argument-naming-style=snake_case
attr-naming-style=snake_case
bad-names=foo,
          bar,
          baz,
          toto,
          tutu,
          tata
class-attribute-naming-style=any
class-naming-style=PascalCase
const-naming-style=UPPER_CASE
docstring-min-length=-1
function-naming-style=snake_case
good-names=i,
           j,
           k,
           ex,
           Run,
           to,
           _
include-naming-hint=no
inlinevar-naming-style=any
method-naming-style=snake_case
module-naming-style=snake_case
name-group=
no-docstring-rgx=^_
property-classes=abc.abstractproperty
variable-naming-style=snake_case

[MISCELLANEOUS]
notes=FIXME,
      XXX,
      TODO

[SIMILARITIES]
ignore-comments=yes
ignore-docstrings=yes
ignore-imports=no
min-similarity-lines=4

[LOGGING]
logging-modules=logging

[IMPORTS]
allow-wildcard-with-all=no
analyse-fallback-blocks=no
deprecated-modules=regsub,
                   TERMIOS,
                   Bastion,
                   rexec
ext-import-graph=
import-graph=
int-import-graph=
known-standard-library=
known-third-party=enchant

[DESIGN]
max-args=5
max-attributes=7
max-bool-expr=5
max-branches=12
max-locals=15
max-parents=7
max-public-methods=20
max-returns=6
max-statements=50
min-public-methods=2

[CLASSES]
defining-attr-methods=__init__,
                      __new__,
                      setUp
exclude-protected=_asdict,
                  _fields,
                  _replace,
                  _source,
                  _make
valid-classmethod-first-arg=cls
valid-metaclass-classmethod-first-arg=mcs

[EXCEPTIONS]
overgeneral-exceptions=Exception

    """

    VERSION_UNRELEASED = 'UNRELEASED'

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def check_backend(self, module_name, module_author=None):
        """
        Check backend

        Args:
            module_name (string): module name to check
            module_author (string): if specified check if author is corresponding

        Returns:
            dict: backend informations::

            {
                errors (list): list of errors
                warnings (list): list of warnings
                metadata (dict): module metadata
                files (dict): collection of files::
                    {
                        module (dict): main module informations
                        events (list): events informations
                        formatters (list): formatters informations
                        drivers (list): drivers informations
                        misc (list): others files informations
                    }
            }

        """
        if not os.path.exists(os.path.join(config.MODULES_DST, module_name)):
            raise Exception('Module "%s" does not exist' % module_name)

        # get module instance
        try:
            module_ = importlib.import_module(u'cleep.modules.%s' % (module_name))
            app_filename = getattr(module_, 'APP_FILENAME', module_name)
            del module_
            module_ = importlib.import_module('cleep.modules.%s.%s' % (module_name, app_filename))
            class_name = next((item for item in dir(module_) if item.lower() == app_filename.lower()), None)
            class_ = getattr(module_, class_name or '', None)
        except Exception as e:
            self.logger.exception('Unable to load application "%s". Please check your code' % module_name)
            raise Exception('Unable to load application "%s". Please check your code' % module_name) from e
        if not class_:
            raise Exception('Main class was not found for app "%s". Application class must have the same name than app name' % module_name)

        # build metadata and list of files
        metadata = self.__build_metadata(class_, module_author)
        files = self.__build_files_list(class_)

        return {
            'errors': metadata['errors'] + files['errors'],
            'warnings': metadata['warnings'] + files['warnings'],
            'metadata': metadata['metadata'],
            'files': {
                'module': files['module'],
                'events': files['events'],
                'drivers': files['drivers'],
                'formatters': files['formatters'],
                'misc': files['misc'],
            }
        }
        
    def __build_files_list(self, class_):
        """
        Build module list of files

        Args:
            class_ (Class): loaded module class

        Returns:
            dict: list of modules files::

            {
                errors (list): list of errors
                warnings (list): list of warnings
                module (dict): file infos for main module
                events (list): list of events infos
                formatters (list): list or formatters infos
                drivers (list): list of drivers infos
                misc (list): list of miscellaneous files
            }
                
        """
        errors = []
        warnings = []

        # get all application files
        all_files = self.__get_backend_files(class_)
        self.logger.debug('All files: %s' % all_files)

        # analyse files
        events = self.__get_files_for_kind(all_files['files'], {'endswith': 'event', 'class': 'Event'})
        errors += events['errors']
        warnings += events['warnings']
        drivers = self.__get_files_for_kind(all_files['files'], {'endswith': 'driver', 'class': 'Driver'})
        errors += drivers['errors']
        warnings += drivers['warnings']
        formatters = self.__get_files_for_kind(all_files['files'], {'endswith': 'formatter', 'class': 'ProfileFormatter'})
        errors += formatters['errors']
        warnings += formatters['warnings']

        # fill misc files
        found_files = ([e['fullpath'] for e in events['files']] + 
                       [f['fullpath'] for f in formatters['files']] +
                       [d['fullpath'] for d in drivers['files']])
        self.logger.debug('Found files: %s' % found_files)
        misc = [f for f in all_files['files'] if f['fullpath'] not in found_files]
        misc += all_files['initpy']
        self.logger.debug('Misc: %s' % misc)

        # check __init__.py
        initpy_fullpaths = [a_file['fullpath'] for a_file in all_files['initpy']]
        if not self.__has_init_py(initpy_fullpaths, all_files['folders']):
            errors.append('Some __init__.py files are missing in root folder or sub folders')

        return {
            'errors': errors,
            'warnings': warnings,
            'module': all_files['module'],
            'misc': sorted(misc, key=lambda k: k['fullpath']),
            'events': sorted(events['files'], key=lambda k: k['fullpath']),
            'formatters': sorted(formatters['files'], key=lambda k: k['fullpath']),
            'drivers': sorted(drivers['files'], key=lambda k: k['fullpath']),
        }

    def __has_init_py(self, initpy, folders):
        """
        Check if __init__.py files exists in all folders

        Args:
            initpy (list): list of existing __init__.py fullpaths
            folders (list): list of application folders

        Returns:
            bool: True if all __init__.py exists
        """
        return all([os.path.join(folder, '__init__.py') in initpy for folder in folders])

    def __get_files_for_kind(self, all_files, kind):
        """
        Return files infos according to specified type

        Args:
            all_files (list): list of files in module folder
            kind (dict): kind of files to search for::
            
                {
                    class (string): must be Event|ProfileFormatter|Driver
                    endswith (string): event|formatter|driver
                }

        Returns:
            list: list of files of requested kind
        """
        out = {
            'errors': [],
            'warnings': [],
            'files': []
        }

        for a_file in all_files:
            # drop useless files
            if not a_file['filename'].lower().endswith(kind['endswith'] + '.py'):
                continue

            # load file
            try:
                mod_name = a_file['filename'].replace('.py', '')
                parts = Tools.full_split_path(a_file['fullpath'])
                mod_ = importlib.import_module('cleep.modules.%s.%s' % (parts[-2], mod_name))
            except Exception as e:
                self.logger.exception('Error loading file "%s"' % a_file['fullpath'])
                out['errors'].append('Error loading file "%s". Please check file [%s]' % (
                    a_file['fullpath'], str(e)
                ))
                continue

            # check class name
            class_name = next((item for item in dir(mod_) if item.lower() == mod_name.lower()), None)
            if not class_name:
                out['errors'].append('Error loading file "%s": class name should have the same name than filename' % a_file['fullpath'])
                continue
            class_ = getattr(mod_, class_name)

            # check base class
            if not any([True for c in inspect.getmro(class_) if c.__name__ == kind['class']]):
                out['errors'].append('Error loading file "%s": class "%s" should inherit from "%s" due to its name. Please fix it' % (
                    a_file['fullpath'],
                    class_name,
                    kind['class'],
                ))
                continue

            out['files'].append({
                'fullpath': a_file['fullpath'],
                'filename': a_file['filename'],
                'path': a_file['path'],
                'classname': class_name,
            })

        return out

    def __get_backend_files(self, class_):
        """
        Get list of backend files

        Args:
            class_ (Class): loadde module class

        Returns:
            list: list of found files::

            {
                initpy (list): list of __init__.py fullpaths
                module (dict): main module infos::
                    {
                        fullpath (string): fullpath
                        filename (string): filename
                        path (string): path within module
                    },
                files (dict): other files infos::
                    [
                        {
                            fullpath (string): fullpath
                            filename (string): filename
                            path (string): path within module
                        },
                        ...
                    ],
                folders (list): list of module subfolders
            }

        """
        class_path = inspect.getfile(class_).replace('.pyc', '.py')
        module_path = class_path.rsplit('/',1)[0]

        fullpaths = glob.glob(module_path + '/**/*', recursive=True)
        out = {
            'module': {},
            'files': [],
            'initpy': [],
            'folders': [],
        }
        for fullpath in fullpaths:
            # drop useless files
            fileext = os.path.splitext(fullpath)[1]
            if '__pycache__' in fullpath:
                continue
            if any([True for f in ['.pylintrc', ] if fullpath.find(f) >= 0]):
                continue
            if fileext != '.py':
                continue

            if fullpath.endswith('__init__.py'):
                # handle __init__.py file
                out['initpy'].append({
                    'fullpath': fullpath,
                    'filename': os.path.split(fullpath)[1],
                    'path': fullpath.split('modules/')[1],
                })
            elif fullpath == class_path:
                # handle main module
                out['module'] = {
                    'fullpath': fullpath,
                    'filename': os.path.split(fullpath)[1],
                    'path': fullpath.split('modules/')[1],
                }
            else:
                # handle other file
                out['files'].append({
                    'fullpath': fullpath,
                    'filename': os.path.split(fullpath)[1],
                    'path': fullpath.split('modules/')[1],
                })

            # add scanned folders
            folder = os.path.dirname(fullpath)
            if folder not in out['folders']:
                out['folders'].append(folder)

        return out

    def __build_metadata(self, class_, module_author=None):
        """
        Build module metadata from module constants

        Args:
            class_ (Class): loaded module class
            module_author (string): module author to check

        Returns:
            dict: metadata::

            {
                metadata (dict): list of module properties
                errors (list): list of errors
                warnings (list): list of warnings
            }

        """
        check = self.__check_backend_constants(class_, module_author)

        return {
            'metadata': {
                'author': getattr(class_, 'MODULE_AUTHOR', None),
                'description': getattr(class_, 'MODULE_DESCRIPTION', None),
                'longdescription': getattr(class_, 'MODULE_LONGDESCRIPTION', None),
                'category': getattr(class_, 'MODULE_CATEGORY', None),
                'deps': getattr(class_, 'MODULE_DEPS', []),
                'version': getattr(class_, 'MODULE_VERSION', None),
                'tags': getattr(class_, 'MODULE_TAGS', []),
                'country': getattr(class_, 'MODULE_COUNTRY', None),
                'urls': {
                    'info': getattr(class_, 'MODULE_URLINFO', None),
                    'help': getattr(class_, 'MODULE_URLHELP', None),
                    'site': getattr(class_, 'MODULE_URLSITE', None),
                    'bugs': getattr(class_, 'MODULE_URLBUGS', None),
                },
                'price': getattr(class_, 'MODULE_PRICE', None),
                'label': getattr(class_, 'MODULE_LABEL', class_.__name__),
            },
            'errors': check['errors'],
            'warnings': check['warnings'],
        }

    def __check_constant(self, constant):
        """
        Check specified constant

        Args:
            parameters (list): list of parameters to check::

                {
                    name (string): parameter name
                    type (type): parameter primitive type (str, bool...)
                    none (bool): True if parameter can be None
                    empty (bool): True if string value can be empty
                    value (any): parameter value
                    validator (function): validator function. Take value in parameter and must return bool
                    message (string): custom message to return instead of generic error
                },
                ...

        Returns:
            string: message in case of error or warning, None if nothing to report

        """
        # check None
        if ('none' not in constant or ('none' in constant and not constant['none'])) and constant['value'] is None:
            return 'Constant "%s" is missing' % constant['name']

        # check value
        if constant['value'] is None:
            # nothing else to check, constant value is allowed as None above
            return None

        # check type
        if not isinstance(constant['value'], constant['type']):
            return 'Constant "%s" has wrong type ("%s" instead of "%s")' % (
                constant['name'],
                type(constant['value']).__name__,
                constant['type'].__name__,
            )

        # use validator if provided
        if 'validator' in constant and not constant['validator'](constant['value']):
            return constant['message'] if 'message' in constant else 'Constant "%s" is invalid (specified="%s")' % (
                constant['name'],
                constant['value'],
            )

        # check empty
        if (('empty' not in constant or ('empty' in constant and not constant['empty'])) and
                getattr(constant['value'], '__len__', None) and
                len(constant['value']) == 0):
            return constant['message'] if 'message' in constant else 'Constant "%s" is empty (specified="%s")' % (
                constant['name'],
                constant['value'],
            )

        return None

    def __check_backend_constants(self, class_, module_author=None):
        """
        Check module constants

        Args:
            class_ (Class): loaded module class
            module_author (string): module author to check

        Returns:
            dict: errors and warnings::

            {
                errors (list): list of errors
                warnings (list): list of warnings
            }

        """
        out = {
            'errors': [],
            'warnings': [],
        }

        # MODULE_AUTHOR
        author = getattr(class_, 'MODULE_AUTHOR', None)
        msg = self.__check_constant({'name': 'MODULE_AUTHOR', 'type': str, 'value': author})
        if msg:
            out['errors'].append(msg)
        if module_author and author and module_author.lower() != author.lower():
            out['errors'].append('Application author must be the same than repository: %s != %s' % (author, module_author))

        # MODULE_DESCRIPTION
        msg = self.__check_constant({'name': 'MODULE_DESCRIPTION', 'type': str, 'value': getattr(class_, 'MODULE_DESCRIPTION', None)})
        if msg:
            out['errors'].append(msg)

        # MODULE_LONGDESCRIPTION
        msg = self.__check_constant({'name': 'MODULE_LONGDESCRIPTION', 'type': str, 'value': getattr(class_, 'MODULE_LONGDESCRIPTION', None)})
        if msg:
            out['errors'].append(msg)

        # MODULE_CATEGORY
        msg = self.__check_constant({
            'name': 'MODULE_CATEGORY',
            'type': str,
            'value': getattr(class_, 'MODULE_CATEGORY', None),
            'validator': lambda val: val in CATEGORIES.ALL,
            'message': 'MODULE_CATEGORY must be filled with existing categories. See cleep.common.CATEGORIES'
        })
        if msg:
            out['errors'].append(msg)

        # MODULE_DEPS
        msg = self.__check_constant({'name': 'MODULE_DEPS', 'type': list, 'value': getattr(class_, 'MODULE_DEPS', None), 'empty': True})
        if msg:
            out['errors'].append(msg)

        # MODULE_VERSION
        msg = self.__check_constant({
            'name': 'MODULE_VERSION',
            'type': str,
            'value': getattr(class_, 'MODULE_VERSION', None),
            'validator': lambda val: re.compile(r'\d+\.\d+\.\d+').match(val),
            'message': 'MODULE_VERSION must follow semver rules https://semver.org/',
        })
        if msg:
            out['errors'].append(msg)

        # MODULE_TAGS
        msg = self.__check_constant({'name': 'MODULE_TAGS', 'type': list, 'value': getattr(class_, 'MODULE_TAGS', None)})
        if msg:
            out['warnings'].append(msg)

        # MODULE_URLINFO
        msg = self.__check_constant({'name': 'MODULE_URLINFO', 'type': str, 'value': getattr(class_, 'MODULE_URLINFO', None)})
        if msg:
            out['warnings'].append(msg)

        # MODULE_URLHELP
        msg = self.__check_constant({'name': 'MODULE_URLHELP', 'type': str, 'value': getattr(class_, 'MODULE_URLHELP', None)})
        if msg:
            out['warnings'].append(msg)

        # MODULE_URLSITE
        msg = self.__check_constant({'name': 'MODULE_URLSITE', 'type': str, 'value': getattr(class_, 'MODULE_URLSITE', None)})
        if msg:
            out['warnings'].append(msg)

        # MODULE_URLBUGS
        msg = self.__check_constant({'name': 'MODULE_URLBUGS', 'type': str, 'value': getattr(class_, 'MODULE_URLBUGS', None)})
        if msg:
            out['warnings'].append(msg)

        # MODULE_COUNTRY
        msg = self.__check_constant({
            'name': 'MODULE_URLCOUNTRY',
            'type': str,
            'value': getattr(class_, 'MODULE_COUNTRY', None),
            'none': True,
            'validator': lambda val: len(val) == 2,
            'message': 'Constant MODULE_COUNTRY must be ISO3166-2 compatible code https://fr.wikipedia.org/wiki/ISO_3166-2',
        })
        if msg:
            out['errors'].append(msg)

        # MODULE_PRICE
        msg = self.__check_constant({
            'name': 'MODULE_PRICE',
            'type': float,
            'value': getattr(class_, 'MODULE_PRICE', None),
            'none': True,
        })
        if msg:
            out['errors'].append(msg)

        # MODULE_LABEL
        msg = self.__check_constant({
            'name': 'MODULE_LABEL',
            'type': str,
            'value': getattr(class_, 'MODULE_LABEL', None),
            'none': True
        })
        if msg:
            out['errors'].append(msg)

        return out

    def check_frontend(self, module_name):
        """
        Check frontend

        Args:
            module_name (string): module name to check

        Returns:
            dict: frontend informations::
            
            {
                errors (list): list of errors
                warnings (list): list of warnings
                icon (string): icon name
                files (list): files informations::
                    [
                        {
                            fullpath (string): file fullpath
                            filename (string): filename
                            path (string): module path
                            usage (string): file usage
                            extension (string): file extension
                        }
                        ...
                    ]
            }

        """
        if not os.path.exists(os.path.join(config.MODULES_DST, module_name)):
            raise Exception('Module "%s" does not exist' % module_name)

        out = {
            'errors': [],
            'warnings': [],
            'files': [],
            'icon' : None
        }

        # get all files
        all_files = self.__get_frontend_files(module_name)
        
        # check desc.json
        desc_json_info = self.__get_desc_json(all_files)
        self.logger.debug('desc_json_info: %s' % desc_json_info)
        if not desc_json_info:
            out['errors'].append('desc.json file is missing. Please add it following Cleep recommandation')
        else:
            desc_json = self.__check_desc_json(desc_json_info)
            self.logger.debug('desc_json: %s' % desc_json)
            out['icon'] = desc_json['content'].get('icon', None)
            out['errors'] += desc_json['errors']
            out['warnings'] += desc_json['warnings']
        if not desc_json['content']:
            raise Exception('Invalid desc.json file. Please check content.')

        # give files usage according to desc.json
        if not out['errors']:
            all_checks = self.__check_frontend_files(module_name, all_files, desc_json)
            out['errors'] += all_checks['errors']
            out['warnings'] += all_checks['warnings']
            out['files'] = all_checks['files']

        return out

    def __check_modimgsrc_directive(self, module_name, js_files, all_files):
        """
        Check if developer uses mod-img-src directive to display its images

        Args:
            module_name (string): module name
            js_files (list): list of js files
            all_files (dict): list of all files

        Returns:
            tuple: list of warnings and list of found images::

            (
                ['warning1', 'warning2', ...],
                ['mod/img1.png', 'mod/img2.jpg', ...]
            )

        """
        # init
        cacheds = []
        warnings = []
        founds = []

        # get images
        image_files = [a_file for a_file in all_files['files'] if a_file['extension'] in ('.jpg', '.jpeg', '.gif', '.png', '.webp')]
        html_files = [a_file for a_file in all_files['files'] if a_file['extension'] == '.html']
        logging.debug('Image files %s' % image_files)
        logging.debug('Html files %s' % html_files)

        # no image, no need to go further
        if len(image_files) == 0:
            return warnings, founds

        # cache html files content
        for html_file in html_files:
            with open(html_file['fullpath'], 'r') as fdesc:
                cacheds.append('\n'.join(fdesc.readlines()))

        # check directive usage for found images
        for image_file in image_files:
            pattern = r"mod-img-src\s*=\s*[\"']\s*%s\s*[\"']" % image_file['path'].replace(module_name+'/', '')
            self.logger.debug('Mod-img-src pattern: %s' % pattern)
            found = False
            for cached in cacheds:
                matches = re.finditer(pattern, cached, re.MULTILINE)
                if len(list(matches)) > 0:
                    logging.debug('Image "%s" found' % image_file['path'])
                    found = True
                    founds.append(image_file['path'])
            if not found:
                warnings.append('Image "%s" may not be displayed properly because mod-img-src directive wasn\'t used' % image_file['filename'])

        return warnings, founds

    def __check_frontend_files(self, module_name, all_files, desc_json):
        """
        Check frontend files

        Args:
            module_name (string): module name
            all_files (list): list of all frontend files
            desc_json (dict): desc.json analyze result

        Returns:
            dict: check results::

            {
                errors (list): list of errors
                warnings (list): list of warnings
                files (list): list of all files updated with usage info
            }

        """
        out = {
            'errors': [],
            'warnings': [],
            'files': copy.deepcopy(all_files['files']),
        }
        content = desc_json['content']
        config_files = []
        global_files = []
        res_files = []
        pages_files = []
        html_files = []
        js_files = []
        css_files = []

        # fill found files
        if 'global' in content:
            global_files += content['global']['js'] if 'js' in content['global'] else []
            js_files += content['global']['js'] if 'js' in content['global'] else []
            global_files += content['global']['html'] if 'html' in content['global'] else []
            html_files += content['global']['html'] if 'html' in content['global'] else []
            global_files += content['global']['css'] if 'css' in content['global'] else []
            css_files += content['global']['css'] if 'css' in content['global'] else []
        if 'config' in content:
            config_files += content['config']['js'] if 'js' in content['config'] else []
            js_files += content['config']['js'] if 'js' in content['config'] else []
            config_files += content['config']['html'] if 'html' in content['config'] else []
            html_files += content['config']['html'] if 'html' in content['config'] else []
            config_files += content['config']['css'] if 'css' in content['config'] else []
            css_files += content['config']['css'] if 'css' in content['config'] else []
        if 'pages' in content:
            for page in content['pages']:
                pages_files += content['pages'][page]['js'] if 'js' in content['pages'][page] else []
                js_files += content['pages'][page]['js'] if 'js' in content['pages'][page] else []
                pages_files += content['pages'][page]['html'] if 'html' in content['pages'][page] else []
                html_files += content['pages'][page]['html'] if 'html' in content['pages'][page] else []
                pages_files += content['pages'][page]['css'] if 'css' in content['pages'][page] else []
                css_files += content['pages'][page]['css'] if 'css' in content['pages'][page] else []
        if 'res' in content:
            res_files += content['res']

        # check files place
        for a_file in js_files:
            if os.path.splitext(a_file)[1] != '.js':
                out['warnings'].append('File "%s" should not be in "js" section. Please fix it' % a_file)
        for a_file in html_files:
            if os.path.splitext(a_file)[1] not in ('.html', '.htm'):
                out['warnings'].append('File "%s" should not be in "html" section. Please fix it' % a_file)
        for a_file in css_files:
            if os.path.splitext(a_file)[1] != '.css':
                out['warnings'].append('File "%s" should not be in "css" section. Please fix it' % a_file)
        for a_file in res_files:
            if os.path.splitext(a_file)[1] not in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
                out['warnings'].append('File "%s" seems not to have a supported image format. Please convert it' % a_file)

        # check images
        warnings, found_images = self.__check_modimgsrc_directive(module_name, js_files, all_files)
        out['warnings'] += warnings

        # give flags to files
        for a_file in out['files']:
            if a_file['filename'] in global_files:
                a_file['usage'] = 'GLOBAL'
            elif a_file['filename'] in config_files:
                a_file['usage'] = 'CONFIG'
            elif a_file['filename'] in pages_files:
                a_file['usage'] = 'PAGES'
            elif a_file['filename'] in res_files:
                a_file['usage'] = 'RES'
            elif a_file['filename'] == 'desc.json':
                a_file['usage'] = 'CORE'
            elif a_file['path'] in found_images:
                a_file['usage'] = 'CONFIG'
            else:
                out['warnings'].append('File "%s" is unused' % a_file['path'])
                a_file['usage'] = 'UNUSED'

        # search for missing files
        paths = [item['path'].replace(module_name + '/', '') for item in all_files['files']]
        self.logger.debug('paths: %s' % paths)
        for a_file in global_files:
            a_file not in paths and out['errors'].append('File "%s" specified in desc.json "global" section is missing' % a_file)
        for a_file in config_files:
            a_file not in paths and out['errors'].append('File "%s" specified in desc.json "config" section is missing' % a_file)
        for a_file in res_files:
            a_file not in paths and out['errors'].append('File "%s" specified in desc.json "res" section is missing' % a_file)
        for a_file in pages_files:
            a_file not in paths and out['errors'].append('File "%s" specified in desc.json "pages" section is missing' % a_file)

        return out

    def __check_desc_json(self, desc_json_info):
        """
        Check desc.json content

        Args:
            desc_json_info: desc.json file info

        Returns:
            dict: check results::

            {
                errors (list): list of errors
                warnings (list): list of warnings
            }

        """
        out = {
            'errors': [],
            'warnings': [],
            'content': None,
        }

        try:
            with open(desc_json_info['fullpath']) as json_file:
                content = json.load(json_file)
                out['content'] = content
        except:
            if self.logger.getEffectiveLevel() == logging.DEBUG:
                self.logger.exception('Error loading desc.json:')
            out['errors'].append('Error loading "%s". Please check file content.' % desc_json['fullpath'])
            return out

        # check content
        if not all([key in list(content.keys()) for key in ('config', 'global', 'icon')]):
            out['errors'].append('Invalid desc.json content. At least one mandatory key is missing')

        # check global section
        if 'global' in content:
            if 'js' in content['global'] and not isinstance(content['global']['js'], list):
                out['errors'].append('Invalid global.js section: it must be an array')
            if 'html' in content['global'] and not isinstance(content['global']['html'], list):
                out['errors'].append('Invalid global.html section: it must be an array')
            if 'css' in content['global'] and not isinstance(content['global']['css'], list):
                out['errors'].append('Invalid global.css section: it must be an array')

        # check config section
        if 'config' in content:
            if 'js' in content['config'] and not isinstance(content['config']['js'], list):
                out['errors'].append('Invalid config.js section: it must be an array')
            if 'html' in content['config'] and not isinstance(content['config']['html'], list):
                out['errors'].append('Invalid config.html section: it must be an array')
            if 'css' in content['config'] and not isinstance(content['config']['css'], list):
                out['errors'].append('Invalid config.css section: it must be an array')

        # check res section
        if 'res' in content and not isinstance(content['res'], list):
            out['errors'].append('Invalid res section: it must be an array')

        # check pages section
        if 'pages' in content:
            for page in content['pages']:
                if 'js' in content['pages'][page] and not isinstance(content['pages'][page]['js'], list):
                    out['errors'].append('Invalid pages.%s.js section: it must be an array' % page)
                if 'html' in content['pages'][page] and not isinstance(content['pages'][page]['html'], list):
                    out['errors'].append('Invalid pages.%s.html section: it must be an array' % page)
                if 'css' in content['pages'][page] and not isinstance(content['pages'][page]['css'], list):
                    out['errors'].append('Invalid pages.%s.css section: it must be an array' % page)

        return out

    def __get_desc_json(self, all_files):
        """
        Get desc.json file

        Args:
            all_files (list): list of frontend files

        Returns:
            dict: desc.json file infos. None if file not found
        """
        self.logger.debug('all_files: %s' % all_files['files'])
        return next((a_file for a_file in all_files['files'] if a_file['filename'] == 'desc.json'), None)

    def __get_frontend_files(self, module_name):
        """
        Get list of frontend files

        Args:
            module_name (string): module name

        Returns:
            list: list of found files::

            {
                initpy (list): list of __init__.py fullpaths
                module (dict): main module infos::
                    {
                        fullpath (string): fullpath
                        filename (string): filename
                        path (string): path within module
                    },
                files (dict): other files infos::
                    [
                        {
                            fullpath (string): fullpath
                            filename (string): filename
                            path (string): path within module
                        },
                        ...
                    ],
                folders (list): list of module subfolders
            }

        """
        module_path = os.path.join(config.MODULES_HTML_DST, module_name)
        fullpaths = glob.glob(module_path + '/**/*', recursive=True)
        out = {
            'files': [],
        }
        for fullpath in fullpaths:
            # drop some files
            filename = os.path.split(fullpath)[1]
            if filename.startswith('.') or filename.startswith('~') or filename.endswith('.tmp'):
                continue

            # drop directories
            if os.path.isdir(fullpath):
                continue

            # store file infos
            out['files'].append({
                'fullpath': fullpath,
                'filename': filename,
                'path': fullpath.split('modules/')[1],
                'extension': os.path.splitext(fullpath)[1],
            })

        return out

    def check_scripts(self, module_name):
        """
        Check scripts files

        Args:
            module_name (string): module name

        Returns:
            dict: scripts infos::

            {
                errors (list): list of errors
                warnings (list): list of warnings
                files (list): list of files::
                    [
                        {
                            fullpath (string): file fullpath
                            filename (string): filename
                            path (string): module path
                        }
                        ...
                    ]
            }

        """
        if not os.path.exists(os.path.join(config.MODULES_DST, module_name)):
            raise Exception('Module "%s" does not exist' % module_name)

        scripts_path = os.path.join(config.MODULES_SRC, module_name, 'scripts')
        fullpaths = glob.glob(scripts_path + '/**/*', recursive=True)
        out = {
            'errors': [],
            'warnings': [],
            'files': [],
        }
        for fullpath in fullpaths:
            # store file infos
            out['files'].append({
                'fullpath': fullpath,
                'filename': os.path.split(fullpath)[1],
                'path': fullpath.split('modules/%s/' % module_name)[1],
            })

        return out

    def check_tests(self, module_name):
        """
        Check test files

        Args:
            module_name (string): module name

        Returns:
            dict: scripts infos::

            {
                errors (list): list of errors
                warnings (list): list of warnings
                files (list): list of files::
                    [
                        {
                            fullpath (string): file fullpath
                            filename (string): filename
                            path (string): module path
                        }
                        ...
                    ]
            }

        """
        if not os.path.exists(os.path.join(config.MODULES_DST, module_name)):
            raise Exception('Module "%s" does not exist' % module_name)

        scripts_path = os.path.join(config.MODULES_SRC, module_name, 'tests')
        fullpaths = glob.glob(scripts_path + '/**/*', recursive=True)
        out = {
            'errors': [],
            'warnings': [],
            'files': [],
        }
        for fullpath in fullpaths:
            # drop some files
            filename = os.path.split(fullpath)[1]
            ext = os.path.splitext(fullpath)[1],
            if filename.startswith('.') or filename.startswith('~') or filename.endswith('.tmp'):
                continue
            if '__pycache__' in fullpath:
                continue

            # store file infos
            out['files'].append({
                'fullpath': fullpath,
                'filename': filename,
                'path': fullpath.split('modules/%s/' % module_name)[1],
            })

        # check mandatory files
        filenames = [item['filename'] for item in out['files']]
        if '__init__.py' not in filenames:
            out['errors'].append('Mandatory "__init__.py" file is missing in tests folder. Please add it')
        if 'test_%s.py' % module_name not in filenames:
            out['errors'].append('Tests file "test_%s.py" must exists in tests folder' % module_name)

        return out

    def check_code_quality(self, module_name, rewrite_pylintrc=False):
        """
        Check code quality running pylint on backend. Add .pylintrc if file is missing

        Args:
            module_name (string): module name
            rewrite_pylintrc (bool): True to rewrite .pylintrc file

        Returns:
            dict: result of pylint::

            {
                errors (list): list of errors::
                {
                    filename (string): {
                        code (string): pylint code
                        msg (string): pylint message
                    }
                }
                warnings (list): list of warnings::
                {
                    filename (string): {
                        code (string): pylint code
                        msg (string): pylint message
                    }
                }
                score (float): code quality score (/10)
            }

        """
        if not os.path.exists(os.path.join(config.MODULES_DST, module_name)):
            raise Exception('Module "%s" does not exist' % module_name)

        backend_path = os.path.join(config.MODULES_SRC, module_name, 'backend')
        pylintrc_path = os.path.join(backend_path, '.pylintrc')
        if not os.path.exists(pylintrc_path) or rewrite_pylintrc:
            self.logger.debug('Create default "%s" file' % pylintrc_path)
            with open(pylintrc_path, 'w') as pylintrc_file:
                pylintrc_file.write(self.PYLINTRC)
            time.sleep(3.0)

        # launch pylint
        self.logger.debug('Launch pylint')
        cmd = 'cd "%s"; pylint *.py' % backend_path
        pattern = r'^(.*?\.py):(\d+):(\d+): ([CRWEF]\d+): (.*)$|^.*at (\d+\.\d+)\/10.*$'
        console = AdvancedConsole()
        results = console.find(cmd, pattern, timeout=60, check_return_code=False)
        self.logger.debug('Results: %s' % results)

        out = {
            'errors': [],
            'warnings': [],
            'score': 0.0,
        }
        if len(results) == 0:
            out['errors'].append({
                'code': None,
                'msg': 'Internal error: linter execution failed. Please check your code.',
            })
        for result in results:
            group = list(filter(None, result[1]))
            if len(group) == 5:
                # pylint output
                msg = '%s [%s %s:%s]' % (group[4], group[0], group[1], group[2])
                if group[3].startswith('E') or group[3].startswith('F'):
                    out['errors'].append({
                        'code': group[3],
                        'msg': msg
                    })
                else:
                    out['warnings'].append({
                        'code': group[3],
                        'msg': msg,
                    })
            elif len(group) == 1:
                # score
                out['score'] = float(group[0])

        self.logger.debug('Code quality output: %s' % out)
        return out

    def check_changelog(self, module_name):
        """
        Check module changelog

        Args:
            module_name (string): module name

        Returns:
            dict: changelog metadata::

            {
                version (string): module version
                changelog (string): latest version changelog
                unreleased (bool): True if version unreleased
            }

        """
        if not os.path.exists(os.path.join(config.MODULES_DST, module_name)):
            raise Exception('Module "%s" does not exist' % module_name)

        # search for changelog.md file
        changelog_path = None
        fullpaths = glob.glob(os.path.join(config.MODULES_SRC, module_name) + '/*')
        for fullpath in fullpaths:
            if os.path.basename(fullpath).lower() == 'changelog.md':
                changelog_path = fullpath
        if not changelog_path:
            raise Exception('Application changelog "changelog.md" does not exist. Please create it following https://keepachangelog.com/en/1.0.0/')
        self.logger.debug('Using changelog "%s"' % changelog_path)

        with open(changelog_path) as changelog_file:
            lines = changelog_file.readlines()

        # read all sections
        sections = []
        current_section = None
        for line in lines:
            if line.startswith('## '):
                current_section = [line,]
                sections.append(current_section)
            elif current_section:
                current_section.append(line)

        # get first section and search for version
        first_section = sections[0] if len(sections) > 0 else []
        found_version = None
        unreleased = False
        if len(first_section) > 0:
            pattern = re.compile(r'\d+\.\d+\.\d+')
            match = pattern.search(first_section[0])
            found_version = match.group() if match else None

            pattern = re.compile(r'%s' % self.VERSION_UNRELEASED)
            match = pattern.search(first_section[0].split('\n')[0])
            unreleased = match is not None
        self.logger.debug('Found version: %s' % found_version)
        self.logger.debug('Found unreleased: %s' % unreleased)

        return {
            'version': found_version,
            'changelog': ''.join(first_section).strip(),
            'unreleased': unreleased,
        }

