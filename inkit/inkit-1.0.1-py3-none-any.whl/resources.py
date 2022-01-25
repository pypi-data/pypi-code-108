from inkit.router import Router
from inkit.client import Client
from inkit.metaclasses import ResourceBuilderMetaclass


class RenderResource(metaclass=ResourceBuilderMetaclass):

    routes = Router.get_routes('render')
    client = Client()
