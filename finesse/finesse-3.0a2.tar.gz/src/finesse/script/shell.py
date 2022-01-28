"""Kat shell tools."""

import cmd
from collections import ChainMap

from . import parse
from .spec import KatSpec
from ..exceptions import FinesseException
from .. import PROGRAM, __version__, Model


class KatShell(cmd.Cmd):
    """Kat shell."""

    intro = f"Welcome to the {PROGRAM} {__version__} shell. Type help or ? to list commands.\n"
    prompt = "(kat) "
    doc_leader = "For further help on a topic, type 'help <topic>'.\n"
    doc_header = "Available elements:"
    misc_header = "Available commands ('!<command>'):"
    model = None
    solution = None

    def __init__(self, *args, **kwargs):
        spec = KatSpec()

        # Set kat script elements as shell commands.
        for element, adapter in spec.elements.items():
            setattr(self.__class__, f"do_{element}", self._wrap_kat_element(element))
            setattr(
                self.__class__,
                f"help_{element}",
                self._wrap_kat_directive_help(adapter),
            )

        # Set kat script command as magic methods.
        for command, adapter in ChainMap(spec.commands, spec.analyses).items():
            setattr(
                self.__class__, f"_magic_{command}", self._wrap_kat_command(command)
            )
            setattr(
                self.__class__,
                f"help_{command}",
                self._wrap_kat_directive_help(adapter),
            )

        # Set help for magic methods.
        for attr in dir(self):
            if attr.startswith("_magic_"):
                setattr(self.__class__, f"help_{attr[7:]}", self._wrap_magic_help(attr))

        super().__init__(*args, **kwargs)

    @classmethod
    def _wrap_kat_element(cls, element):
        def wrapper(*args):
            # Get rid of self, and add the element instead.
            shell = args[0]
            args = [element] + list(args[1:])

            original_line = " ".join(args)

            try:
                parse(original_line, model=shell.model)
            except FinesseException as e:
                print(e, file=shell.stdout)

        return wrapper

    @classmethod
    def _wrap_kat_command(cls, command):
        def wrapper(*args):
            # Get rid of self, and add the command instead.
            shell = args[0]
            args = [command] + list(args[1:])

            original_line = " ".join(args)

            try:
                parse(original_line, model=shell.model)
            except FinesseException as e:
                print(e, file=shell.stdout)

        return wrapper

    @classmethod
    def _wrap_kat_directive_help(cls, adapter):
        def wrapper(*args):
            shell = args[0]
            print(
                adapter.call_signature_type.__doc__,
                file=shell.stdout,
            )

        return wrapper

    @classmethod
    def _wrap_magic_help(cls, method):
        def wrapper(*args):
            shell = args[0]
            print(
                getattr(cls, method).__doc__,
                file=shell.stdout,
            )

        return wrapper

    def _reset(self):
        self.model = Model()

    def preloop(self):
        self._reset()

    def close(self):
        self.model = None
        self.solution = None

    def do_shell(self, arg):
        """Handler for commands starting with "!"."""
        magic_attr = f"_magic_{arg}"
        if hasattr(self, magic_attr):
            try:
                getattr(self, magic_attr)(arg)
            except FinesseException as e:
                print(e, file=self.stdout)
        else:
            try:
                parse(arg, model=self.model)
            except FinesseException as e:
                print(e, file=self.stdout)

    def _magic_model_info(self, arg):
        """Show information about the current model (if no argument is specified) or a
        particular model element (if its name is specified as an argument)."""
        item = self.model.get(arg) if arg else self.model
        print(f"{item.info()}", file=self.stdout)

    def _magic_model_get(self, arg):
        """Get a model element attribute."""
        print(self.model.get(arg), file=self.stdout)

    def _magic_model_set(self, arg):
        """Set an attribute of the model or a model element."""
        self.model.set(*arg.split())

    def _magic_model_run(self, arg):
        """Run the analysis."""
        try:
            self.solution = self.model.run()
        except FinesseException as e:
            print(e, file=self.stdout)

    def _magic_model_plot(self, arg):
        """Plot the solution."""
        self.solution.plot()

    def _magic_kat_load(self, arg):
        """Parse the specified kat file into the current model."""
        self.model.parse_file(arg)

    def _magic_kat_save(self, arg):
        """Save the current model to file."""
        self.model.unparse_file(arg)

    def _magic_model_reset(self, arg):
        """Reset the model."""
        self._reset()
