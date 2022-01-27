# 22/01/2021
# Jason Brown
# Object Functions


import dill
import os

from .text_ui import prompt


def save_object(_object: object, filename: str, folder=None):
    """
    Saves a python object as a .txt file in the given folder with the given filename.
    Folder path starts at wherever the if __name__ == '__main__' was executed from.

    :param _object: Object to save
    :param filename: Name of .txt file
    :param folder: Folder to place it in
    """
    filename = f"{filename}.pkl"
    path = os.path.join(folder, filename)

    try:
        with open(path, 'wb') as _output:
            dill.dump(_object, _output)
    except FileNotFoundError:
        os.system(f"mkdir {folder}")
        with open(path, 'wb') as _output:
            dill.dump(_object, _output)


def load_object(filename, folder):
    """
    Load an object in a .pkl file that was created via save_object
    Folder path starts at wherever the if __name__ == '__main__' was executed from.

    :param filename: Name of .pkl file
    :param folder: Folder it's located
    :return: The object to load
    """
    filename = f"{filename}.pkl" if filename.split('.')[-1] != "pkl" else filename
    path = os.path.join(folder, filename)

    with open(path, 'rb') as _input:
        _object = dill.load(_input)

    return _object


def rename_object(_object):
    """
    Change the name property of an object via text ui. Can be called even if it doesn't already exist to give it a name

    :param _object: Object to change the name property of
    """
    old_name = getattr(_object, "name", None)
    new_name = prompt(f"Current name is {old_name}\nNew name?\n")
    setattr(_object, "name", new_name)


def redefine_object_property(_object, _property):
    """
    Change a generic property of an object via text ui. New property value must cast to same type as previous value,
    unless previous value was None. If property doesn't exist it's created.

    :param _object: Object to change
    :param _property: Property of that object to change
    """

    # Get old type and property
    old_property = getattr(_object, _property, None)
    old_type = type(old_property)

    # Get new value and set type
    new_property = prompt(f"Current value of {_property} is {old_property}\nNew value?\n", old_type)
    new_property = old_type(new_property) if old_property is not None else new_property

    # Assign value to property
    setattr(_object, _property, new_property)
