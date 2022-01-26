#!/usr/bin/env python
import argparse
import logging
import json
import sys

from .compare import (
    compare_ipynb_notebooks,
    parse_input_names,
    print_comparison_results,
    parse_compare_input,
)
from .execute import execute_ipynb_pm
from .read import read_ipynb
from .test import test_ipynb
from .utils import (
    BLUE,
    CYAN,
    GREEN,
    NC,
    RED,
    create_output_dir,
    create_output_files,
    setup_logger,
)


def main():
    """The main function - usage and help, argument parsing"""

    # Setup arguments
    parser = argparse.ArgumentParser(
        description="Execute Jupyter notebooks (.ipynb format) in the terminal"
        ". Compare outputs from different executions, save results."
    )
    parser.add_argument(
        "input_notebook_filenames",
        nargs="*",
        help="The input Jupyter notebook file names - one or more are "
             "required",
    )

    # Optional arguments
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="debug output"
    )
    parser.add_argument(
        "--kernel",
        required=False,
        default=False,
        help="The name of the kernel to use when executing a notebook.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to test_results/"
    )
    # parser.add_argument(
    #     "--output",
    #     required=False,
    #     default="output.ipynb",
    #     help="Output Jupyter notebook filename. The default is a temporary "
    #          "file that is not saved.",
    # )
    # parser.add_argument(
    #     "--log",
    #     required=False,
    #     default=False,
    #     help="Output results of action to a log file. The default is no log"
    #          "file.",
    # )

    # Action arguments - one or more required
    action_arguments = parser.add_argument_group(
        "action arguments - one or more are required"
    )
    action_arguments.add_argument(
        "--execute",
        action="store_true",
        help="Execute the notebook, output saved to output.ipynb"
    )
    action_arguments.add_argument(
        "--read",
        action="store_true",
        help="Read the given Jupyter notebook file."
    )
    action_arguments.add_argument(
        "--test",
        action="store_true",
        help="Check the given Jupyter notebook (.ipynb) file for errors",
    )
    action_arguments.add_argument(
        "--compare",
        nargs='*',
        help="Zero or one arguments can be given",
    )
    action_arguments.add_argument(
        "--validate",
        action="store_true",
        help="Combination of: --execute, --read, --test, --compare, --save",
    )

    # Parse the input arguments
    args = parser.parse_args()
    args.debug and print("\nInput arguments:",
                         json.dumps(vars(args), indent=4), "\n")

    # Print help if no input files given
    if args.input_notebook_filenames == []:
        print(RED, "\nNo input ipynb files given\n", NC)
        args = parser.parse_args(["-h"])
        sys.exit()

    # Parse input file names, also check if they exist, assert error created
    # if not
    notebook_filenames = parse_input_names(
        args.input_notebook_filenames, args.debug)

    # Parse the compare option input, also check if they exist, assert error
    # created if not
    args.compare = parse_compare_input(
        args.compare, args.execute, args.debug)

    # Check if selected actions are valid
    args = parse_actions(args, parser)

    args.save = (args.save and args.execute and args.kernel)
    # output_dir = create_output_dir(args)
    output_dir = create_output_dir(args.save, args.execute, args.kernel,
                                   args.debug)

    kernel_notebook_test_results = {}
    kernel_test_results = True
    complete_test_result = True

    # Loop over input notebook files
    for notebook_filename in notebook_filenames:

        # Create output log and ipynb notebook, using default locations
        output_ipynb, output_log = create_output_files(
            args.save, notebook_filename, output_dir, args.debug
        )
        setup_logger(args.save, output_log, False, args.debug)

        # Run an action with the notebook, e.g. execute, read
        successful_execution, test_result, comparison_result = \
            run_actions(args.execute, args.read, args.test, args.compare,
                        args.save, args.kernel, args.debug,
                        notebook_filename, output_ipynb, output_log)

        # Add to a list of results, to be printed at the end
        kernel_notebook_test_results[notebook_filename] = (
            successful_execution and test_result and comparison_result
        )
        if not successful_execution or not test_result or \
                not comparison_result:
            complete_test_result = False
            kernel_test_results = False

    assert_final_validation_results(args.execute, args.test, args.compare,
                                    args.kernel,
                                    complete_test_result,
                                    kernel_test_results,
                                    kernel_notebook_test_results)


def assert_final_validation_results(execute, test, compare, kernel,
                                    complete_test_result,
                                    kernel_test_results,
                                    kernel_notebook_test_results):

    # Print final results after looping over all notebooks
    if execute and test and compare:
        print(BLUE, "*".center(80, "*"), NC)
        if complete_test_result:
            print(BLUE, "** FINAL RESULT: ", GREEN, " PASSED ", NC)
        else:
            print(BLUE, "** FINAL RESULT: ", RED, " FAILED ", NC)

        print(BLUE, "**", NC, "  Kernel:     ",
              GREEN if kernel_test_results else RED,
              kernel)

        for notebook in kernel_notebook_test_results:
            print(BLUE, "**", NC, "    Notebook: ",
                  GREEN if kernel_notebook_test_results[notebook] else RED,
                  notebook)

        print(BLUE, "*".center(80, "*"), NC)

        # If assertion fails, program will exit
        print(RED)
        if not complete_test_result:
            raise AssertionError
        print(NC)


def parse_actions(args, parser):
    # validate is meant to be an option to quickly select several options
    if args.validate:
        args.execute = True
        args.read = True
        args.test = True
        args.compare = True
        args.save = True

    # Check if atleast one action argument was given
    if not args.execute and not args.read and not args.test \
            and not args.compare:
        print(RED, "\nNo action arguments given\n", NC)
        args = parser.parse_args(["-h"])
        sys.exit()

    # Require a kernel to be specified if executing
    if args.execute and not args.kernel:
        print(RED, "\nKernel name needs to be specified when executing "
                   "notebooks.\n", NC)
        args = parser.parse_args(["-h"])
        sys.exit()

    return args


def run_actions(execute, read, test, compare, save, kernel, debug,
                notebook_filename, output_ipynb, output_log):

    successful_execution = False
    test_result = False
    comparison_result = False

    print_notebook_information_before(execute, test, compare, save,
                                      kernel,  notebook_filename,
                                      output_ipynb, output_log)

    # Execute an ipynb notebook, save output to new ipynb notebook
    if execute:

        # Execute the notebook with papermill
        successful_execution = execute_ipynb_pm(
            notebook_filename, output_ipynb, kernel, debug
        )

        notebook_to_examine = output_ipynb
    else:
        notebook_to_examine = notebook_filename

    # Read output
    if read:
        nb, errors = read_ipynb(notebook_to_examine, False, debug)

    # Test for errors
    if test:
        test_result = test_ipynb(notebook_to_examine, debug)

    # Compare with the original or the given notebook file
    if compare:
        notebook_to_compare = ""
        if isinstance(compare, bool):
            notebook_to_compare = notebook_filename
        if isinstance(compare, str):
            notebook_to_compare = compare

        (
            comparison_result,
            error_message,
            error_content,
        ) = compare_ipynb_notebooks(
            [notebook_to_compare, notebook_to_examine], debug
        )
        print_comparison_results(
            [notebook_to_compare, notebook_to_examine],
            comparison_result,
            error_message,
            error_content,
            debug,
        )

    print_notebook_information_after(execute, test, compare, save, kernel,
                                     notebook_filename, output_ipynb,
                                     output_log, successful_execution,
                                     test_result, comparison_result)

    return successful_execution, test_result, comparison_result


def print_notebook_information_before(execute, test, compare, save,
                                      kernel, notebook_filename,
                                      output_ipynb, output_log):

    # Print something extra if test and comparison will also be done
    if execute and test and compare:
        print("")
        print(CYAN, "*".center(80, "*"), NC)
        print(CYAN, "** STARTING VALIDATIONS FOR:")
        print(CYAN, "**", NC, "  Kernel:   ", kernel)
        print(CYAN, "**", NC, "  Notebook: ", notebook_filename)
        print(CYAN, "** OUTPUT:")
        print(CYAN, "**", NC, "  Notebook:", output_ipynb)
        save and print(CYAN, "**", NC, "  Log:     ", output_log)
        print(CYAN, "*".center(80, "*"), NC)


def print_notebook_information_after(execute, test, compare, save, kernel,
                                     notebook_filename, output_ipynb,
                                     output_log, successful_execution,
                                     test_result, comparison_result):
    # If executing, comparing and testing, print results for this notebook
    if execute and test and compare:
        result_color = RED
        result_word = "FAILED"
        if successful_execution and test_result and comparison_result:
            result_color = GREEN
            result_word = "PASSED"

        print(CYAN, "*".center(80, "*"), NC)
        print(CYAN, "** FINISHED VALIDATIONS FOR:")
        print(CYAN, "**", NC, "  Kernel:   ", kernel)
        print(CYAN, "**", NC, "  Notebook: ", notebook_filename)
        print(CYAN, "** OUTPUT:")
        print(CYAN, "**", NC, "  Notebook:", output_ipynb)
        save and print(CYAN, "**", NC, "  Log:     ", output_log)
        print(CYAN, "** RESULT:", result_color, result_word)
        print(CYAN, "*".center(80, "*"), NC)
        print("")

        # Log the result
        save and logging.info("FINAL RESULT: " + str(result_word))


#######################
# RUN THE APPLICATION #
#######################

if __name__ == "__main__":
    main()
