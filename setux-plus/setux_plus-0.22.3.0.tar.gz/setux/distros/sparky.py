from setux.distros.debian import Debian_11


class Sparky_6(Debian_11):

    @classmethod
    def release_name(cls, infos):
        did = infos['DISTRIB_ID']
        ver,_ ,_ = infos['DISTRIB_RELEASE'].partition('.')
        return f'{did}_{ver}'
