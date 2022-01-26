import logging
import nbformat
import os
from .utils import (
    BLUE,
    CYAN,
    LIGHTPURPLE,
    NC,
    RED,
    YELLOW,
    from_nbnode,
    print_cropped_output,
)


def is_accessible(path, quiet):

    accessible = os.access(path, os.R_OK)
    errors = []

    if not accessible:
        error_message = "FILE NOT ACCESSIBLE"
        not quiet and print(RED, error_message, NC)
        errors.append(error_message)

    return accessible, errors


def is_readable(path, quiet):

    readable = False
    nb = []
    errors = []

    # Read the notebook
    try:
        nb = nbformat.read(path, nbformat.current_nbformat)
        readable = True
    except nbformat.reader.NotJSONError as e:
        not quiet and print(RED, type(e), "\n", e)
        errors.append("FILE NOT VALID")
        logging.error(e)
        not quiet and print(NC)
    except BaseException as e:
        not quiet and print(RED, type(e), "\n", e)
        errors.append(e)
        logging.error(e)
        not quiet and print(NC)

    return readable, nb, errors


def read_ipynb(path, quiet, debug):

    if not quiet:
        print("")
        print(LIGHTPURPLE, "*".center(80, "*"), NC)
        print(LIGHTPURPLE, "Reading output notebook", NC, path)
        print("")

        logging.info("Reading " + str(path))

    nb = []
    errors = []

    # Check if the file exists and is accessible
    accessible, errors = is_accessible(path, quiet)

    if accessible:

        # Read the notebook
        readable, nb, errors = is_readable(path, quiet)

        if readable:

            # Loop over cells
            for cell in nb.cells:

                debug and print(cell)

                # Skip some types of cells
                if "cell_type" in cell:
                    if cell["cell_type"] == "markdown":
                        debug and print(YELLOW, "skipping cell_type:",
                                        cell["cell_type"], NC)
                        continue

                # Print cell content, search for errors
                errors = print_cell_output(cell, quiet, errors)

    if not quiet:
        logging.info("Done reading " + str(path))

        for error_message in errors:
            print(RED, error_message, NC)
        print(LIGHTPURPLE, "Done reading")
        print(LIGHTPURPLE, "*".center(80, "*"), NC)
        print("")

    if debug and nb != []:
        nb_dict = from_nbnode(nb)
        print(nb_dict)

    return nb, errors


def print_cell_output(cell, quiet, errors):
    """Print cell source and output, append error to return value"""

    if not quiet and "source" in cell and "cell_type" in cell:
        if cell["cell_type"] == "code" and cell["source"] != "":
            logging.info("cell source: " + str(cell["source"]))
            print(BLUE, "-".center(80, "-"), NC)
            print(BLUE, "source: ", NC, cell["source"])

    if "outputs" in cell:
        COLOR = CYAN

        if len(cell["outputs"]) == 0:

            if not quiet:
                print(COLOR, "cell output: ", str(cell["outputs"]), NC)
                logging.info("cell output: " + str(cell["outputs"]))
                print(BLUE, "-".center(80, "-"), NC)
                print("")
        else:
            for output in cell["outputs"]:

                # Search for errors in the output
                if output.output_type == "error":
                    errors.append(output)
                    logging.error("cell output: " + str(output))
                    COLOR = RED
                else:
                    logging.info("cell output: " + str(output))

                if not quiet:
                    print(COLOR, "cell output: ", NC)
                    print_cropped_output(output)

            if not quiet and len(cell["outputs"]) > 0:
                print(BLUE, "-".center(80, "-"), NC)
                print("")

    return errors
