from .arch import Arch


class Manjaro(Arch):

    @classmethod
    def release_name(cls, infos):
        return infos['ID'].strip().title()
