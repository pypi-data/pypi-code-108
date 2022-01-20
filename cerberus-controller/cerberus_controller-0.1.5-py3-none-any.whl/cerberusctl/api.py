import traceback
import json

from ryu.app.wsgi import ControllerBase, route
from webob import Response, Request

class api(ControllerBase):
    """ API front end for Cerberus.

        Builds on top of Ryu's built in wsgi to
        provide basic API endpoint for Cerberus
    """
    def __init__(self, req, link, data, **config):
        super(api, self).__init__(req, link, data, **config)
        self.app = data['cerberus_main']


    # TODO: Remove this once cerberus becomes more stable
    @route("cerberus", "/api/hello_world", methods=['GET'])
    def hello_world(self, req: Request, **kwargs) -> Response:
        """ Hello world API call for testing purposes

        Args:
            req (Request): Empty GET request

        Returns:
            Response: Test data to retrieve from cerberus main
        """
        self.app.logger.info(f"Hello world was called by:\t{req.host}")
        return Response(content_type='application/json',
                        json=self.app.hello_world())


    @route("cerberus", "/api/switches", methods=['GET'])
    def switches(self, req: Request, **kwargs )-> Response:
        """ GET all the switch objects from cerberus and how they are configured

        Args:
            req (Request): Empty GET request object

        Returns:
            Response: JSON object cotaining switch objects
        """
        self.app.logger.info(f"Request for switches was called by:\t{req.host}")
        return Response(content_type='application/json',
                        json=self.app.get_switches())


    @route("cerberus", "/api/push_config", methods=['PUT'])
    def push_new_config(self, req: Request, **kwargs) -> Response:
        """ PUT request that contains new configuration to be used in cerberus

        Args:
            req (Request): Request containing candidate config file as JSON

        Returns:
            Response: If any changes were made and if they were applied successfully
        """
        self.app.logger.info(f"A config update was sent in by:\t{req.host}")
        try:
            return Response(content_type='application/json',
                            json=self.app.push_new_config(req.body))
        except:
            return Response(status=500,
                            json={"error": traceback.format_exc()})


    @route("cerberus", "/api/get_config", methods=['GET'])
    def get_running_config(self, req: Request, **kwargs) -> Response:
        """ Get the current running configuration file

        Args:
            req (Request): Get request

        Returns:
            Response: JSON response of config file
        """
        self.app.logger.info(f"Request for switches was called by:\t{req.host}")
        try:
            return Response(content_type='application/json',
                            json=self.app.get_running_config_file())
        except:
            return Response(status=500, json={"error": traceback.format_exc()})


    @route("cerberus", "/api/get_full_config", methods=['GET'])
    def get_full_config(self, req: Request, **kwargs) -> Response:
        """ Returns the full config. Primarily for debugging purposes.

        Args:
            req (Request): Get Request

        Returns:
            Response: Response containing the full config in cerberus
        """
        self.app.logger.info(f"Request for full config was called by:\t{req.host}")
        try:
            return Response(content_type='application/json',
                            json=self.app.get_running_config())
        except:
            return Response(status=500, json={"error": traceback.format_exc()})