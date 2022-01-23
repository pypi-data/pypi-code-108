"""
:mod:`moke.core`
================

``moke`` is not like ``make``. The core package provides the ``task`` the
``task`` all in one decorator.

"""

__all__ = ["MokeError", "task", "stdin", "stdout", "stderr", "num", "doc",
           "INFO", "DEFAULT" ,"WARN", "ERROR", "required"]
__version__ = "1.2.1"


import io
import os
import sys
import inspect
import logging
import multiprocessing
from re import search
from .path import path
from itertools import zip_longest
from argparse import ArgumentParser, FileType, SUPPRESS
from configparser import SafeConfigParser

# logging
DEFAULT = 23
logging.addLevelName(DEFAULT, "DEFAULT")
logging.DEFAULT = DEFAULT

# do not remove, really
from logging import INFO, WARN, ERROR
from sys import stdin, stdout, stderr

class RequiredArgument(object):
    pass

required = RequiredArgument

__deflog__ = {"ls":stderr,    # log stream
              "ll":"default", # log level
              "lf":"nltm",    # log format
             }

__logforms__ = {
    "nltm":"%(name)s\t%(levelname)s\t%(asctime)s\t%(message)s"
}


nan = float("nan")
devnull = open(os.devnull, "wb")

# monkey patching now to have simpler code later
file_w = FileType("wb")
file_w.__dict__["__name__"] = "file_w"
file_r = FileType("rb")
file_r.__dict__["__name__"] = "file_r"
file_a = FileType("a+")
file_a.__dict__["__name__"] = "file_a"

# automatic import of mokelib

class MokeError(Exception):
    """General moke exception.
    """
    pass

def num(x):
    """(internal) check if value is a number.
    """
    try:
        num = int(x)
    except ValueError:
        try:
            num = float(x)
        except:
            num = nan
    return num

def doc(docstring):
    """Decorator that attaches a docstring to a function.
    
      - docstring(``str``) some documentation
    
    """
    def docwrapper(func):
        func.__doc__ = docstring
        return func

    return docwrapper


class task(object):
    """Decorator that creates an argparse subcommand from a function.
    """
    
    __funcs = {}

    @staticmethod
    def _makecfg(args):
        args.pop("cargs")
        cfg = args.pop("config")
        parser = SafeConfigParser()
        parser.read(cfg.name)
        return parser

    @staticmethod
    def _makelgr(args, cfg):
        # default arguments
        options = ("level", "stream", "format")
        defargs = {"level": __deflog__["ll"],
                   "stream":__deflog__["ls"],
                   "format":__deflog__["lf"]
                   }
        # config file arguments
        cfgargs = dict.fromkeys(options)
        if cfg.has_section("log"):
            for name in ("level", "stream", "format"):
                if cfg.has_option("log", name):
                    value = cfg.get("log", name)
                    # manual type corrections
                    if name in ("stream",):
                        value = open(value, "a+")
                    cfgargs[name] = value
                else:
                    cfgargs[name] = None
        # command line arguments
        # these are set to defaults by argparse
        linargs = {"level": args.pop("ll"),
                   "stream":args.pop("ls"),
                   "format":args.pop("lf")
                   }
        finargs = {}
        for key in ("level", "stream", "format"):
            # default
            finargs[key] = defargs[key]
            # config if set
            if cfgargs[key]:
                finargs[key] = cfgargs[key]
            # linargs if set
            if linargs[key] != defargs[key]:
                finargs[key] = linargs[key]
        # prepare options
        logstream = finargs["stream"]
        try:
            loglevel = getattr(logging, finargs["level"].upper())
        except AttributeError:
            loglevel = getattr(multiprocessing, finargs["level"].upper())
        logformat = __logforms__[finargs["format"]]
        # setup logger handler
        lgr = logging.getLogger()
        lgr.setLevel(loglevel)
        sh = logging.StreamHandler(stream=logstream)
        sh.setFormatter(logging.Formatter(logformat))
        lgr.addHandler(sh)
        

    @staticmethod
    def _parsetype(line):
        # parses (sometypeX) or (``sometypeX``),
        # where X is a number or ? + * (argparse nargs)
        try:
            sometype, nargs = search("\(`{0,2}([a-z_]*)([\?\+\*]{1}|[0-9]?)`{0,2}\)",
                                     line).groups()
        except AttributeError:
            return None
        # test if sometype is a known type
        try:
            sometype = eval(sometype)
        except (NameError, SyntaxError):
            return None
        if not (issubclass(type(sometype), type) or \
                isinstance(sometype, FileType) or sometype is num):
            return None
        # fix empty string
        nargs = nargs or None
        if nargs not in ('+', '?', '*', None):
            try:
                nargs = int(nargs)
            except ValueError:
                return None
        return sometype, nargs

    @classmethod
    def _parsearg(cls, doclines, arg):
        docline, argtype, nargs = "", str, None # defaults
        # the space is mandatory for rst compatibility
        arg_type = "- " + arg + "(" # with type
        arg_noty = "- " + arg + " " # without type
        for line in doclines:
            if (arg_type in line or arg_noty in line) and line.startswith("-"):
                try:
                    docline = line.replace("-", "", 1).replace(arg, "", 1).strip()
                    argtype, nargs = cls._parsetype(line)
                except TypeError:
                    pass
                break # only the first match
        return docline, argtype, nargs

    @classmethod
    def _funcparse(cls, doc):
        # parses gathered functions
        main_parser = ArgumentParser(description=doc)

        # global options
        defcfg = os.path.join(os.path.dirname(__file__), "data", "mokefile.ini")
        main_parser.add_argument("-config", type=file_r, default=defcfg, 
                                 help="(file_r) [default: %s] configuration file" % defcfg)

        main_parser.add_argument("-cargs", type=str, default="", 
                                help="(str) [default: ''] configuration file over-rides")
        
        main_parser.add_argument("-ls", type=file_a,
                                 default=__deflog__["ls"],
                                 help="(file_a) [default: %s] logging stream" % __deflog__["ls"].name)

        main_parser.add_argument("-ll", type=str,
                                 default=__deflog__["ll"], choices=("debug", "info", "subdefault", 
                                                                    "default", "warn", "error"),
                                 help="(str) [default: %s] logging level" % __deflog__["ll"])

        main_parser.add_argument("-lf", type=str,
                                 default=__deflog__["lf"], choices=("nltm",),
                                 help="(str) [default: %s] logging format" % __deflog__["lf"])
        
        # subcommand options
        sub_parsers = None
        for name, func in cls.__funcs.items():
            args, varargs, varkwargs, defaults = inspect.getargspec(func)
            if varargs or varkwargs:
                raise MokeError("*args and **kwargs not supported in tasks")
            arglines = []
            doclines = []
            if func.__doc__ and func.__doc__.strip():
                for l in func.__doc__.splitlines():
                    l = l.strip()
                    if l.startswith("-"):
                        arglines.append(l)
                    elif l:
                        doclines.append(l)
            if name == "main":
                task_parser = main_parser
                task_parser.description = "\n".join(doclines)
            else:
                if not sub_parsers:
                    sub_parsers = main_parser.add_subparsers()
                    sub_parsers.required = True
                    sub_parsers.dest = "command"
                    
                task_parser = sub_parsers.add_parser(name, help="\n".join(doclines))
            
            task_parser.set_defaults(func = func)
            if defaults:
                ldef = len(defaults)
                required = args[:-ldef]
                optional = args[-ldef:]
            else:
                required = args
                optional = ()
                defaults = ()
            
            for arg, deft in zip_longest(optional, defaults):
                docline, argtype, nargs = cls._parsearg(arglines, arg)
                if deft is False:
                    if not docline:
                        docline = "(switch) [default: OFF]"
                    task_parser.add_argument("--" + arg, action="store_true",
                                             default=deft, help=docline)
                elif deft is True:
                    if not docline:
                        docline = "(switch) [default: ON]"
                    task_parser.add_argument("--" + arg, action="store_false",
                                                 default=deft, help=docline)
                else:
                    # function signature > docs string
                    if type(deft) == type and issubclass(deft, RequiredArgument):
                        pass
                    else:
                        arg = "-" + arg
                        if deft is not None:
                            argtype = type(deft)
                        if argtype is io.IOBase:
                            # stdin, stdout or an open file
                            argtype = eval("file_" + deft.mode[0])

                    # default = most types
                    argname = argtype.__name__
                    argrepr = getattr(deft, "name", str(deft))
                    argdoc = "(%s) [default: %s] " % (argname, \
                                                argrepr.replace("%", "%%"))
                    if docline:
                        # (XXX) [default: YYY] CONTENT, (XXX) CONTENT, CONTENT
                        argdoc += docline.split(")")[-1].split("]")[-1].strip()
                    task_parser.add_argument(arg, type=argtype, \
                                        nargs=nargs, default=deft, help=argdoc)
            
            for arg in required:
                docline, argtype, nargs = cls._parsearg(arglines, arg)
                argdoc = "(%s) " % argtype.__name__
                if docline:
                    argdoc += docline.split(")")[-1].split("]")[-1].strip()
                else:
                    argdoc += "a required positional argument"
                task_parser.add_argument(arg, type=argtype, nargs=nargs, \
                                         help=argdoc)
        return main_parser

    @classmethod
    def _callfunc(cls, args):
        # where are we?
        cwd = os.getcwd()
        mokefile = os.path.abspath(os.path.join(cwd, sys.argv[0]))
        # get config and logger
        cfg = cls._makecfg(args)
        cls._makelgr(args, cfg)
        # the function
        func = args.pop("func")
        args.pop("command", None)
        # remember default and command line args
        names, _, _, defs = inspect.getargspec(func)
        defs = (defs or ()) # defs can be None
        diff = len(names) - len(defs)
        # final set of function parameters
        full_args = {}
        for i, name in enumerate(names):
            try:
                full_args[name] = args[name]
            except KeyError:
                full_args[name] = defs[i - diff]
        # write logging header
        msgs = ("moke version: %s" % __version__,
                "cwd: \"%s\"" % cwd,
                "mokefile: \"%s\"" % mokefile,
                "task: %s" % func.__name__,
        ) + tuple("%s: %s" % (k,v) for (k,v) in sorted(full_args.items()))
        lgr = logging.getLogger("moke")
        for msg in msgs:
            lgr.log(DEFAULT, msg)
        # final call, leaving moke
        return func(**args)

    @classmethod
    def _call(cls, doc):
        # calls the selected function with the parsed arguments
        parser = cls._funcparse(doc)
        try:
            args = dict(parser.parse_args().__dict__)
        except Exception as e:
            sys.exit(e)
        retval = cls._callfunc(args) # modifies args
        return retval

    def __init__(self, func=None):
        # gather functions or call selected sub-command
        if inspect.isfunction(func):
            self.__name = func.__name__
            self.__funcs[self.__name] = func
        elif self.__funcs:
            # file contains some functions
            self._call(func)

    def __call__(self, *args, **kwargs):
        return self.__funcs[self.__name](*args, **kwargs)
