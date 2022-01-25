from inkit.metaclasses import ProductMetaclass
from inkit.resources import RenderResource


class Render(metaclass=ProductMetaclass):

    _main_resource = RenderResource()
