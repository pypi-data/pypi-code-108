import logging
import papermill as pm

from .utils import BLUE, LIGHTPURPLE, NC, RED


def execute_ipynb_pm(input_name, output_name, kernel, debug):

    if debug:
        print("input_name:  ", input_name)
        print("output_name: ", output_name)
        print("kernel: ", kernel)

    print("")
    print(LIGHTPURPLE, "*".center(80, "*"), NC)
    print(LIGHTPURPLE, "Executing notebook ", NC, input_name)
    print(BLUE, "Using kernel       ", NC, kernel)

    logging.info("Executing notebook: " + str(input_name))

    successful_execution = True
    # Sometimes kernels die for no apparent reason - looks for those instances
    # and retry execution
    for attempt in range(5):
        debug and print("execution attempt: ", attempt)
        try:
            # For options see:
            #   https://github.com/nteract/papermill/blob/main/papermill/
            #       execute.py
            pm.execute_notebook(
                input_name,
                output_name,
                kernel_name=kernel,
                progress_bar=False,
                log_output=True,
                report_mode=False,
            )
            successful_execution = True
            break
        except BaseException as e:
            print(RED)
            print("Unknown error")
            print(e)
            print(NC)
            logging.error("Unknown error")
            logging.error(e)
            successful_execution = False
            if "Kernel died" in str(e):
                continue
            else:
                break

    logging.info("Done executing notebook: " + str(input_name))
    logging.info("Output saved to: " + str(output_name))

    print(LIGHTPURPLE, "Done executing")
    print(LIGHTPURPLE, "Output Saved to    ", NC, output_name)
    print(LIGHTPURPLE, "*".center(80, "*"), NC)
    print("")

    return successful_execution
