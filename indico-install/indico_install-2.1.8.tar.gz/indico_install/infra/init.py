import pkg_resources
from click import pass_context

from indico_install.updraft import init_tracking

def init(location):
    @pass_context
    def wrapper(ctx):
        """
        Initialize cluster configuration
        """
        template = pkg_resources.resource_filename(location, "cluster.yaml")
        ctx.invoke(init_tracking, input_yaml=template)

    return wrapper
