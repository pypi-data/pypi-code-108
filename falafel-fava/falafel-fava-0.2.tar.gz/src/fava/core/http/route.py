from textwrap import dedent
from os import path
import toml
import inflect
import black
from fava.core.utils import variables

"""
Prepare
"""
routes_dir = variables.get_app_dir() + "/" + variables.get("ROUTES_DIR")
controllers_dir = variables.get_app_dir() + "/" + variables.get("CONTROLLERS_DIR")
p = inflect.engine()
mode = black.FileMode()


def create_new_route(name):
    """
    Create new Route file
    :param name:
    :return:
    """

    name = name.lower()
    if path.exists(controllers_dir + "/" + name.lower() + "_controller.py"):

        if check_route_exists(name):
            print("#######")
            print("Error!")
            print("The " + routes_dir + "/" + name.loqer() + "_route.py exists!")
            print("#######")

        else:
            with open(routes_dir + '/' + name.lower() + '_route.py', 'w') as route:
                content = dedent("""\
                    from """ + variables.get("CONTROLLERS_DIR").replace("/", ".") + """ import """ + name.lower() + """_controller
                    from flask import Blueprint
                    """ + name + """ = Blueprint('""" + name + """', __name__, url_prefix='/""" + p.plural(name) + """')

                    @""" + name + """.route("/", methods=['GET'])
                    def index():
                        return """ + name.lower() + """_controller.index()

                    def init_app(app):
                        app.register_blueprint(""" + name + """)

                    """)

                formatted = black.format_file_contents(content, fast=False, mode=mode)
                route.write(formatted)

                update_route_list(name)

                print("#######")
                print("The " + routes_dir + "/" + name.lower() + "_route.py created!")
                print("#######")
    else:
        print("#######")
        print("Error!")
        print("The " + name.lower() + "_controller doesn't exists!")
        print("For create a new route you need to create a controller before.")
        print("Create the controller file first!")
        print("Run: fava -mkcontroller " + name.lower())
        print("#######")


def update_route_list(route):
    """
    Update extensions file
    :param route:
    :return:
    """

    try:
        app_config_file = variables.get_app_dir() + "/app/config/app.toml"
        app_config_data = toml.load(app_config_file)
        is_new = True
        for extension in app_config_data.get('default').get('EXTENSIONS'):
            print(extension)

        if is_new:
            app_config_data.get('default').get('EXTENSIONS').append(
                'app.http.routes.' + route + ':init_app')
            toml.dump(app_config_data, app_config_file)

    except BaseException as err:
        print("An error occurring!")
        raise SystemExit(err)


def check_route_exists(name):
    """
    Model file exists?
    """
    if path.exists(routes_dir + '/' + name + '.py'):
        return True
    else:
        return False
