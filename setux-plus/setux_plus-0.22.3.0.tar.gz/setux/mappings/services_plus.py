from setux.core.mapping import Services


class Artix(Services):
    mapping = dict(
        cron = 'cronie',
        ssh  = 'sshd',
    )


class Arch(Services):
    mapping = dict(
        ssh = 'sshd',
    )


class Fedora(Services):
    mapping = dict(
        ssh = 'sshd',
    )
