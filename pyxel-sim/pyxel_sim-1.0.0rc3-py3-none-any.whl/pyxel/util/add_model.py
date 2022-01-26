#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Functions to add new models."""

import logging
import os
import shutil
import sys
import time
import typing as t


def create_model(newmodel: str) -> None:
    """Create a new module using pyxel/templates/MODELTEMPLATE.py.

    Parameters
    ----------
    newmodel: modeltype/modelname

    Returns
    -------
    None
    """

    location, model_name = get_name_and_location(newmodel)

    # Is not working on UNIX AND Windows if I do not use os.path.abspath
    path = os.path.abspath(os.getcwd() + "/pyxel/models/" + location + "/")
    template_string = "_TEMPLATE"
    template_location = "_LOCATION"

    # Copying the template with the user defined model_name instead
    import pyxel

    src = os.path.abspath(os.path.dirname(pyxel.__file__) + "/templates/")
    dest = os.path.abspath(
        os.path.dirname(pyxel.__file__) + "/models/" + location + "/"
    )

    try:
        os.mkdir(dest)
        # Replacing all of template in filenames and directories by model_name
        for dirpath, subdirs, files in os.walk(src):
            for x in files:
                pathtofile = os.path.join(dirpath, x)
                new_pathtofile = os.path.join(
                    dest, x.replace(template_string, model_name)
                )
                shutil.copy(pathtofile, new_pathtofile)
                # Open file in the created copy
                with open(new_pathtofile, "r") as file_tochange:
                    # Replace any mention of template by model_name
                    new_contents = file_tochange.read().replace(
                        template_string, model_name
                    )
                    new_contents = new_contents.replace(template_location, location)
                    new_contents = new_contents.replace("%(date)", time.ctime())
                with open(new_pathtofile, "w+") as file_tochange:
                    file_tochange.write(new_contents)
                # Close the file other we can't rename it
                file_tochange.close()

            for x in subdirs:
                pathtofile = os.path.join(dirpath, x)
                os.mkdir(pathtofile.replace(template_string, model_name))
            logging.info("Module " + model_name + " created.")
        print("Module " + model_name + " created in " + path + ".")
    except FileExistsError:
        logging.info(f"{dest} already exists, folder not created")
    # Directories are the same
    except shutil.Error as e:
        logging.critical("Error while duplicating " + template_string + ": %s" % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        logging.critical(model_name + " not created. Error: %s" % e)
    return None


def get_name_and_location(newmodel: str) -> t.Tuple[str, str]:
    """Get name and location of new model from string modeltype/modelname.

    Parameters
    ----------
    newmodel: str

    Returns
    -------
    location: str
    model_name: str
    """

    try:
        arguments = newmodel.split("/")
        location = f"{arguments[0]}"
        model_name = f"{arguments[1]}"
    except Exception:
        sys.exit(
            f"""
        Can't create model {arguments}, please use location/newmodelname
        as an argument for creating a model
        """
        )
    return location, model_name
