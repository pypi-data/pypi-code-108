"""
description: this module provides the class Server.
"""

import asyncio
import platform
import signal
from pathlib import Path

import yaml
import tornado.ioloop
import tornado.web
from pistar_echo_agent.resources.loggers import server_logger

from pistar_echo_agent.services.echotest.agent import get_services
from pistar_echo_agent.utilities.configuration.server_configuration import server_configuration
from pistar_echo_agent.utilities.constants import API_DOCUMENT_FIELD
from .handlers import create_request_handler


class Server:
    """
    description: |
        this class is used to parse the configuration file,
        and to register apis and schedule jobs.
    """
    __logger = None
    __scheduler = None
    __exit = None
    __start = None
    __is_closing = None
    __request_handler_list = None
    __configuration = None
    __port = None

    def __init__(
            self,
            report_path,
            port
    ):
        super().__init__()
        server_configuration.report_path = Path.cwd().joinpath(report_path)

        # setup the member variables.
        server_logger.create_file_handler()
        self.__logger = server_logger
        self.__request_handler_list = list()

        # set the port.
        self.__port = port

        services = get_services()
        for function in services:
            function.__document__ = yaml.load(
                function.__doc__, Loader=yaml.SafeLoader
            )
            if API_DOCUMENT_FIELD.METHODS in function.__document__ \
                    and API_DOCUMENT_FIELD.API_PATH in function.__document__:
                try:
                    api_path, request_handler = \
                        create_request_handler(function, self.__logger)
                except BaseException as exception:
                    self.__logger.warning(exception.args[0])
                    continue

                self.__request_handler_list.append((api_path, request_handler))
                self.__logger.info(f"The api '{api_path}' is registered successfully.")

        self.__logger.info("PiStar echo agent is ready. Agent version: 1.0.2")

    def closing(self, signum, frame):
        """
        description: this function is used to set __is_closing to True.
        """
        self.__logger.info(f"Receive signal '{signum}' , frame is '{frame}'.")
        self.__is_closing = True

    def start(self):
        """
        description: this function is used to
                     execute the functions which are regist as start.
        """
        # 此处是解决tornado框架在windows下的问题
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        application = tornado.web.Application(self.__request_handler_list)
        http_server = tornado.web.HTTPServer(application)
        signal.signal(signal.SIGINT, self.closing)
        self.__logger.info(f"The task report path is '{server_configuration.report_path}'.")
        self.__logger.info(f"Server start at {self.__port} port.")
        http_server.listen(self.__port)

        tornado.ioloop.PeriodicCallback(self.exit, 100).start()
        tornado.ioloop.IOLoop.current().start()

    def exit(self):
        """
        description: this function is used to execute the functions
                     which are regist as exit.
        """
        if not self.__is_closing:
            return
        self.__logger.close()
        tornado.ioloop.IOLoop.instance().stop()
