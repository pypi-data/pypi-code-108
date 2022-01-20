#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MIT License
Copyright (c) 2020-2022 Chris1320

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
import json
import shlex
import pathlib

from getpass import getpass

from . import info
from . import simple
from . import advanced

try:
    import prettytable
    prettytable_support = True

except ImportError:
    prettytable_support = False


def promptGenerator(open_configfile: str = None):
    """
    Changes the prompt if a configuration file is open.

    :param str open_configfile: The name of the configuration file.
    """

    if open_configfile is None:
        return ">>> "

    else:
        return f"{open_configfile} >>> "


def helpMenu(config_file: str = None):
    """
    Show a help menu.
    """

    print()
    print("help                   Show this help menu.")
    print("status                 Show current configuration.")
    print()
    print("base64                 Toggle base64 encoding.")
    print("encoding <encoding>    Set encoding to use.")
    print("password               Set password.")
    print("readonly               Toogle read-only mode.")
    print("mode <mode>            Change the config handler.")
    print("    simple             Simple mode.")
    print("    advanced           Advanced mode.")
    print()
    if config_file is None:
        print("open <filename>        Open a configuration file.")

    else:
        print("close                  Close the current configuration file.")
        print("save                   Save the current configuration file.")
        print("get <key>              Get a value from the configuration file.")
        print("set <key> <value>      Set a value in the configuration file.")
        print("remove <key>           Remove a value from the configuration file.")
        print("keys                   Show all available keys in the configuration file.")
        print("list                   Show all available keys and values in the configuration file.")

    print()
    print("exit                   Exit the program.")
    print()
    print("When setting a value, you can explicitly convert them using the following:")
    print("    + str:<value>       Convert <value> to a string.")
    print("    + int:<value>       Convert <value> to an integer.")
    print("    + float:<value>     Convert <value> to a float.")
    print("    + bool:<value>      Convert <value> to a boolean.")
    print()


def parse(data: str):
    """
    Check if <data> needs explicit conversion.
    """

    if data.startswith("str:"):
        return str(data.partition('str:')[2])

    elif data.startswith("int:"):
        return int(data.partition('int:')[2])

    elif data.startswith("float:"):
        return float(data.partition('float:')[2])

    elif data.startswith("bool:"):
        if data.partition("bool:")[2].lower() == "true":
            return True

        elif data.partition("bool:")[2].lower() == "false":
            return False

        else:
            raise ValueError("[E] Invalid boolean value.")

    else:
        return data


def main():
    """
    Start an interactive console.
    """

    print(info.title)
    print()
    print(f"Running on: `{pathlib.Path().cwd()}`")
    print()
    print("Type `help` for help.")
    print()
    if not advanced.ciphers.aes_support:
        print("[!] An encryption module is not installed on this system.")
        print("[!] Advanced mode won't be able to encrypt or decrypt.")
        print()

    config_file = None
    password = None
    mode = "simple"  # The default mode.
    encoding = "utf-8"  # The default encoding.
    readonly = False  # The default read-only mode.
    base64 = False  # The default base64 encoding mode.

    while True:
        try:
            command = str(input(promptGenerator(config_file)))

            if command == "help":
                helpMenu(config_file)
                continue

            elif command.startswith("status"):
                print()
                print("Current Configuration File: ", config_file)
                print("Config Mode:                ", mode)
                print("Encoding:                   ", encoding)
                print("Read-only:                  ", readonly)
                print("Base64:                     ", base64)
                print()
                print("Password:                   ", ("*" * len(password) if password is not None else "None"))
                print()
                continue

            elif command.startswith("readonly"):
                if readonly:
                    readonly = False
                    print("Read-only mode disabled.")

                else:
                    readonly = True
                    print("Read-only mode enabled.")

                continue

            elif command.startswith("password"):
                password = getpass("Enter password: ")
                print("[i] Password set.")

            elif command.startswith("base64"):
                if base64:
                    base64 = False
                    print("Base64 encoding disabled.")

                else:
                    base64 = True
                    print("Base64 encoding enabled.")

                continue

            elif command.startswith("encoding"):
                if command.partition(' ')[2] != '':
                    encoding = command.partition(' ')[2]
                    print(f"Encoding set to `{encoding}`.")

                else:
                    helpMenu(config_file)

                continue

            elif command.startswith("mode"):
                command_option = command.partition(' ')[2]
                if command_option == '':
                    print(f"[i] You are currently using `{mode}` mode.")

                elif command_option == "simple":
                    mode = "simple"
                    print("mode is set to `simple`.")

                elif command_option == "advanced":
                    mode = "advanced"
                    print("mode is set to `advanced`.")

                else:
                    print(f"[E] Unknown mode `{command_option}`.")

                continue

            elif command == "exit":
                print("[!] Quitting...")
                return 0

            elif config_file is None:
                if command.startswith("open"):
                    config_file = command.partition(' ')[2]
                    if config_file == '':
                        helpMenu(config_file)
                        config_file = None
                        continue

                    try:
                        if mode == "simple":
                            config = simple.Simple(config_file, base64, encoding, readonly)
                            print("[i] Configuration file opened.")
                            continue

                        elif mode == "advanced":
                            config = advanced.Advanced(config_file, password, readonly)
                            print("[i] Configuration file opened.")
                            continue

                        else:
                            config_file = None
                            print("[E] Unkown mode is set!")

                    except json.decoder.JSONDecodeError:
                        print("[E] The configuration file might be corrupted or you have entered an incorrect password.")
                        config_file = None

                    except ValueError:
                        print("[E] You must set a password before opening the configuration file.")
                        config_file = None

                else:
                    print(f"[E] Unknown command `{command}`.")
                    continue

            else:
                if command.startswith("close"):
                    config_file = None
                    config = None
                    print("[i] Configuration file closed.")
                    continue

                elif command.startswith("load"):
                    config.load()
                    print("[i] Configuration file loaded.")
                    continue

                elif command.startswith("keys"):
                    print("Available keys:")
                    for k in config.keys():
                        print("+", k)

                    continue

                elif command.startswith("list"):
                    if prettytable_support:
                        table = prettytable.PrettyTable()
                        table.field_names = ["Key", "Value", "Type"]
                        for key in config.keys():
                            table.add_row([key, config.get(key), type(config.get(key))])

                        print(table)

                    else:
                        print("Key=Value (Type)\n")
                        for key in config.keys():
                            print(f"+ {key}={config.get(key)} ({type(config.get(key))})")

                        print()

                elif command.startswith("new"):
                    if mode != "advanced":
                        print("[E] You can only call `new` in advanced mode.")
                        continue

                    else:
                        config_name = input("Configuration File Name (Blank for None): ")
                        config_author = input("Configuration File Author (Blank for None): ")
                        config_compression = input("Configuration File Compression (Blank for None): ")
                        config_encryption = input("Configuration File Encryption (Blank for None): ")
                        config_encoding = input("Configuration File Encoding (Blank for `utf-8`): ")

                        if config_name == '':
                            config_name = None

                        if config_author == '':
                            config_author = None

                        if config_compression == '':
                            config_compression = None

                        if config_encryption == '':
                            config_encryption = None

                        if config_encoding == '':
                            config_encoding = "utf-8"

                        print("Creating configuration file...")
                        config.new(
                            config_name,
                            config_author,
                            config_compression,
                            config_encryption,
                            config_encoding
                        )
                        continue

                elif command.startswith("save"):
                    try:
                        config.save()
                        print("[i] Configuration file saved.")

                    except Exception as e:
                        print("[E] An error occured:", e)

                    finally:
                        continue

                elif command.startswith("set"):
                    commands = shlex.split(command)
                    try:
                        key = commands[1]
                        try:
                            value = parse(commands[2])

                        except ValueError as e:
                            print(e)

                    except IndexError:
                        helpMenu(config_file)

                    else:
                        config.set(key, value)

                    finally:
                        del commands

                elif command.startswith("get"):
                    try:
                        print(config.get(command.partition(' ')[2]))

                    except(IndexError, KeyError):
                        helpMenu(config_file)

                elif command.startswith("remove"):
                    try:
                        config.remove(command.partition(' ')[2])
                        print("Key removed.")

                    except(IndexError, KeyError):
                        helpMenu(config_file)

                else:
                    print(f"[E] Unknown command `{command}`.")
                    continue

        except KeyboardInterrupt:
            print("\n[!] Forcing to quit...")
            return 2

        except Exception as e:
            print("\n[E] An unexpected error occurred:", e)
            input("Press enter to continue...")
            return 1


if __name__ == "__main__":
    sys.exit(main())
