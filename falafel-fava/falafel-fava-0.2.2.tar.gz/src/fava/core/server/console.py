import os

banner = """

███████╗ █████╗ ██╗      █████╗ ███████╗███████╗██╗     
██╔════╝██╔══██╗██║     ██╔══██╗██╔════╝██╔════╝██║     
█████╗  ███████║██║     ███████║█████╗  █████╗  ██║     
██╔══╝  ██╔══██║██║     ██╔══██║██╔══╝  ██╔══╝  ██║     
██║     ██║  ██║███████╗██║  ██║██║     ███████╗███████╗
╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚══════╝
                                                     
"""


def run(server):
    """
    Run local webserver
    :param server:
    :return:
    """
    print(banner)
    print('###############################################')
    print('-> Running server in port: ' + server)
    print('-> Isn\'t for production use!')
    print('###############################################\n')

    os.environ['FLASK_ENV'] = "development"
    os.environ['FLASK_APP'] = "app.falafel:create_app"
    os.system("flask run --host='0.0.0.0' --port " + server)
