"""Argument parser for parsing command line input."""

import abc
import sys


class Parser(abc.ABC):
    """Represents a base class that subclasses should adhere to."""

    @abc.abstractmethod
    def parse_args(self) -> None:
        pass


class ArgumentParser(Parser):
    """Argument parser that handles parsing command line input."""

    def __init__(self, argv: list, program: str) -> None:
        """Initializes ArgumentParser."""
        self.argv: list = argv
        self.program: str = program
        self.args: dict = {"short": None, "long": None, "invalid": None}

        self.__switches: dict = {
            "version": False,
            "authors": False,
            "help": False
        }

    @property
    def version(self) -> bool:
        """Getter that gets the version's state (and whether it's on or off)."""
        return self.__switches["version"]

    @version.setter
    def version(self, value: bool) -> None:
        """
        Setter that sets the version's state. This isn't, however, for setting
        the 'version number'. Instead, when either '-V' or '--version' is invoked
        on the command line, it sets the state of version to 'on', indicating that
        version was requested. This is so that main() in main.py can use the
        <parser>.version -property.
        """
        if value in {True, False}:
            self.__switches["version"] = value

    @property
    def authors(self) -> str:
        """Getter that gets the author's state (and whether it's on or off)."""
        return self.__switches["authors"]

    @authors.setter
    def authors(self, value: bool) -> None:
        """
        Setter that sets the author's state. Check version setter's docstring
        for more info.
        """
        if value in {True, False}:
            self.__switches["authors"] = value

    @property
    def help(self) -> bool:
        """Getter that gets the help's state (and whether it's on or off)."""
        return self.__switches["help"]

    @help.setter
    def help(self, value: bool) -> None:
        """
        Setter that sets the help's state. Check version setter's docstring
        for more info.
        """
        if value in {True, False}:
            self.__switches["help"] = value

    def __hyphens(self, arg: str, number: int) -> bool:
        """Checks if argument is prefixed with specified number of hyphens."""
        return arg[0:number] == "-" * number and arg[number] != "-"

    def __sort_short(self) -> None:
        """Gathers all '-' prefixed command line arguments."""
        self.args["short"] = (i for i in self.argv if self.__hyphens(i, 1))

    def __sort_long(self) -> None:
        """Gathers all '--' prefixed command line arguments."""
        self.args["long"] = (i for i in self.argv if self.__hyphens(i, 2))

    def __parse_short(self) -> None:
        """Parses all '-' prefixed command line arguments."""
        for arg in self.args["short"]:
            for idx, letter in enumerate(arg):
                if idx == 0:
                    continue
                if letter == "V":
                    self.version = True
                elif letter == "A":
                    self.authors = True
                elif letter == "h":
                    self.help = True
                else:
                    if self.args["invalid"] is None:
                        self.args["invalid"] = []
                    self.args["invalid"].append(f"-{letter}")

    def __parse_long(self) -> None:
        """Parses all '--' prefixed command line arguments."""
        for arg in self.args["long"]:
            if arg == "--version":
                self.version = True
            elif arg == "--authors":
                self.authors = True
            elif arg == "--help":
                self.help = True
            else:
                if self.args["invalid"] is None:
                    self.args["invalid"] = []
                self.args["invalid"].append(arg)

    def __parse_invalid(self) -> None:
        """Parses invalid arguments, if there is any."""
        if self.args["invalid"] is not None:
            for arg in self.args["invalid"]:
                msg: str = f"{self.program}: error: invalid argument '{arg}'"
                print(msg, file=sys.stderr)

            del arg, msg
            sys.exit(1)

    def parse_args(self) -> None:
        """Parses command line input."""
        self.__sort_short()
        self.__sort_long()
        self.__parse_short()
        self.__parse_long()
        self.__parse_invalid()
