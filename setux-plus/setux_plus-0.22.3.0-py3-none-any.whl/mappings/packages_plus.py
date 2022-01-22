from setux.core.mapping import Packages


class Fedora(Packages):
    pkg = dict(
        setuptools = 'python3-setuptools',
        pip        = 'python3-pip',
        vim        = 'vim-enhanced',
        gvim       = 'vim-X11',
        shellcheck = 'ShellCheck',
	sshfs      = 'fuse-sshfs',
        netcat     = 'nmap-ncat',
    )


class Arch(Packages):
    pkg = dict(
        setuptools = 'python-setuptools',
        pip        = 'python-pip',
        netcat     = 'openbsd-netcat',
        sqlite     = 'sqlite3',
    )


class Artix(Packages):
    pkg = dict(
        setuptools = 'python-setuptools',
        pip        = 'python-pip',
        netcat     = 'openbsd-netcat',
        sqlite     = 'sqlite3',
        cron       = 'cronie',
    )
