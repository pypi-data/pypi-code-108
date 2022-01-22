from setux.distros.debian import Debian_10


class Mint_20(Debian_10):

    @classmethod
    def release_name(cls, infos):
        did = infos['DISTRIB_ID']
        if did=='LinuxMint':
            did='Mint'
        ver, _, _ = infos['DISTRIB_RELEASE'].partition('.')
        return f'{did}_{ver}'
