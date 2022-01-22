from .arch import Arch


class Endeavour(Arch):

    @classmethod
    def release_name(cls, infos):
        return infos['DISTRIB_ID'][:-2]
