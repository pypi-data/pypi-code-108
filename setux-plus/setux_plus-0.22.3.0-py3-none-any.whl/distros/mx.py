from setux.distros.debian import Debian_10


class MX(Debian_10):
    Service = 'SystemV'

    @classmethod
    def release_name(cls, infos):
        did = infos['DISTRIB_ID']
        ver, _, _ = infos['DISTRIB_RELEASE'].partition('.')
        return f'{did}_{ver}'


class MX_19(MX): pass


class MX_21(MX): pass
