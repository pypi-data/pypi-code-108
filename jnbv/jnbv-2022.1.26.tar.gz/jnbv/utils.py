import datetime
import logging
import nbformat
import os


# Make it purrty
LIGHTPURPLE = "\033[1;35m"
YELLOW = "\033[0;33m"
GREEN = "\033[0;32m"
BLUE = "\033[34m"
CYAN = "\033[1;36m"
RED = "\033[31m"
NC = "\033[0m"


def from_nbnode(value):
    """Recursively convert NotebookNode to dict."""
    if isinstance(value, nbformat.NotebookNode):
        return {k: from_nbnode(v) for k, v in value.items()}
    return value


def setup_logger(save, logfile_name, remove_if_exists, debug):
    """Setup up a simple log file"""

    if not save:
        return

    new_file = False

    # Check if this log file already exists
    new_file != os.path.exists(logfile_name)
    if debug:
        print("Does log file exist:", os.path.exists(logfile_name))

    # Delete the file first if desired, and it already exists
    if remove_if_exists and os.path.exists(logfile_name):
        os.remove(logfile_name)
        new_file = True
        debug and print("Log file deleted:", logfile_name)

    if new_file:

        # If making a new log file, remove the old logging handler, if it
        # exists
        log = logging.getLogger()
        for hdlr in log.handlers[:]:  # remove the existing file handlers
            if isinstance(hdlr, logging.FileHandler):
                log.removeHandler(hdlr)

    # Set logging filename, format, logging level
    FORMAT = "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s\n" \
             "  %(message)s"
    logging.basicConfig(filename=logfile_name, level=logging.INFO,
                        format=FORMAT)

    # Log some information
    if new_file:
        logging.info("Created log file: " + str(logfile_name))
        debug and print("Created log file:", logfile_name)
    else:
        logging.info("Appending to log file: " + str(logfile_name))
        debug and print("Appending to log file:", logfile_name)


def create_output_dir(save, execute, kernel, debug):

    if not (save and execute and kernel):
        return False

    # The uppermost directory for saved output
    test_results_dir = "test-results"
    if not os.path.isdir(test_results_dir):
        os.makedirs(test_results_dir, exist_ok=True)
        os.chmod(test_results_dir, mode=0o777)

    # Create the output directory for the kernel
    kernel_dir = test_results_dir + "/" + kernel
    if not os.path.isdir(kernel_dir):
        os.makedirs(kernel_dir, exist_ok=True)
        os.chmod(kernel_dir, mode=0o777)

    # Output directory will be created with current datetime
    dt_date = datetime.datetime.now()
    dt_date_str = dt_date.strftime("%Y-%m-%d_%H-%M-%S")
    debug and print("Current datetime:    ", dt_date)

    # Create the output directory for this particular set of tests
    output_dir = kernel_dir + "/" + dt_date_str + "/"
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        os.chmod(output_dir, mode=0o777)

    debug and print("output_dir:          ", output_dir)

    return output_dir


def create_output_files(save, notebook_filename, output_dir,
                        debug):

    if not save:
        return "output.ipynb", "output.log"

    basename = os.path.basename(notebook_filename)
    output_ipynb = output_dir + basename
    output_log = output_dir + os.path.splitext(basename)[0] + ".log"
    if os.path.isdir(output_dir):
        touch(output_ipynb)
        os.chmod(output_ipynb, mode=0o666)
        touch(output_log)
        os.chmod(output_log, mode=0o666)

    if debug:
        print("notebook_filename:   ", notebook_filename)
        print("output_ipynb:        ", output_ipynb)
        print("output_log:          ", output_log)

    return output_ipynb, output_log


def touch(fname):
    try:
        os.utime(fname, None)
    except OSError:
        open(fname, "a").close()


def print_cropped_output(output):
    """Crop long output to the terminal"""

    if len(str(output)) > 1000:
        print(str(output)[:500], YELLOW, "\n   <output cropped> \n", NC,
              str(output)[-500:])
    else:
        print(output)
