class SetuxError(Exception):

    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def __str__(self):
        return f'\n\n    ! {self.msg} !\n\n'


class MissingModuleError(SetuxError):
    def __init__(self, module, distro):
        lineage = '.'.join(distro.lineage)
        super().__init__(
            f'module "{module}" not defined for "{lineage}"'
        )


class ModuleTypeError(SetuxError):
    def __init__(self, module):
        super().__init__(
            f'"{module}" must be a module, not [{type(module).__name__}]'
        )


class UnsupportedDistroError(SetuxError):
    def __init__(self, target):
        super().__init__(
            f'Unsupported distro on {target}'
        )


class ExecError(SetuxError):
    def __init__(self, cmd, ret, out, err):
        sep = '\n    > '
        out = sep+sep.join(out) if out else ''
        sep = '\n    X '
        err = sep+sep.join(err) if err else ''
        super().__init__(
            f'{cmd} ! {ret} ! {out} {err}'
        )
