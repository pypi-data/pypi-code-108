from PySimultan.default_types import BuildInFace


class ExtendedBuildInFace(BuildInFace):

    def __init__(self, *args, **kwargs):
        BuildInFace.__init__(self, *args, **kwargs)

    def __getstate__(self):

        obj_dict = dict()
        for key in dir(self.__class__):
            if type(getattr(self.__class__, key)) is property:
                print(key)
                obj_dict[key] = getattr(self, key)

        return obj_dict

    def __setstate__(self, state):

        for key, value in state.items():
            try:
                setattr(self, key, value)
            except AttributeError as e:
                pass
