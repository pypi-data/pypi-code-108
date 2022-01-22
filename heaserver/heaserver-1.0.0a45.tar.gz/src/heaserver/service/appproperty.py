"""
Application properties that are loaded into the aiohttp app context when heaserver.service.runner.start is called.
"""

HEA_REGISTRY = 'HEA_registry'        # The base URL for the registry service.
HEA_WSTL_BUILDER_FACTORY = 'HEA_WeSTL_builder_factory'  # A zero-argument callable for getting the service's design-time WeSTL document.
HEA_DB = 'HEA_db'                    # The database object to use.
HEA_COMPONENT = 'HEA_component'      # This service's base URL.
HEA_CLIENT_SESSION = 'HEA_client_session'  # A aiohttp.ClientSession instance.
