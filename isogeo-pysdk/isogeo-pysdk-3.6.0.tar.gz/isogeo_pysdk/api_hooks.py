# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""Complementary set of hooks to use with Isogeo API."""

# ##############################################################################
# ########## Classes ###############
# ##################################


class IsogeoHooks(object):
    """Custom requests event hooks for Isogeo API.

    Requests has a hook system that you can use to manipulate portions of the request process,\
        or signal event handling. This module is a set of custom hooks to handle Isogeo API responses.

        WIP
    """

    def __init__(self):
        """Instanciate IsogeoHooks module."""
        super(IsogeoHooks, self).__init__()

    def check_for_error(self, resp, *args, **kwargs):
        resp.raise_for_status()

    def autofix_attributes_resource(self, resp, *args, **kwargs):
        # get result as dict (bytes -->)
        request_content = resp.json()
        # modify problematic attributes/keys
        request_content["coordinateSystem"] = request_content.pop(
            "coordinate-system", list
        )
        request_content["featureAttributes"] = request_content.pop(
            "feature-attributes", list
        )

        # return dumped dict (--> bytes)
        # resp.content = json.dumps(request_content).encode('utf-8')


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
    hooks = IsogeoHooks()
    print(hooks)
