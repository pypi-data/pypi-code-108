from textwrap import dedent
from os import path
import black
from fava.core.utils import variables

"""
Prepare
"""
controllers_dir = variables.get_app_dir() + "/" + variables.get("CONTROLLERS_DIR")


def create_new_controller(controller_name):
    """
    Create new controller file
    :param name:
    :return:
    """

    name = controller_name.lower()
    if path.exists(controllers_dir + "/" + name + "_controller.py"):
        print("#######")
        print("Error!")
        print("The " + controllers_dir + "/" + name + "_controller.py exists!")
        print("#######")

    else:
        with open(controllers_dir + "/" + name + "_controller.py", "w") as controller:
            content = dedent("""\
                from flask import jsonify
                
                
                def index():
                    return jsonify(
                        {
                            "message": "Hello, """ + name + """ controller "
                        }
                    )
                """)

            mode = black.FileMode()
            formatted = black.format_file_contents(content, fast=False, mode=mode)
            controller.write(formatted)

            print("#######")
            print("Controller " + controllers_dir + "/" + name + "_controller.py created!")
            print("#######")




