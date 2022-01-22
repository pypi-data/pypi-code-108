from shlex import split, quote
from subprocess import (
    PIPE,
    CalledProcessError,
    run,
)
from functools import partial

from pybrary.func import todo

from setux.logger import debug, info, error

from .errors import (
    MissingModuleError,
    ModuleTypeError,
    UnsupportedDistroError,
    ExecError,
)
from .distro import Distro
from .module import Module
from . import plugins
import setux.distros


# pylint: disable= filter-builtin-not-iterating


class CoreTarget:
    def __init__(self, *,
        name = None,
        distro = None,
        outdir = None,
        exclude = None,
    ):
        self.name = name or 'target'
        self.outdir = outdir
        self.release_infos = None

        self.cnx = self.chk_cnx()
        if self.cnx:
            self.distros = plugins.Distros(self,
                Distro, setux.distros
            )
            self.probe_distro()
            self.exclude = exclude
        else:
            self.distro = None

    @property
    def outdir(self):
        return getattr(self, '_outdir_', None)

    @outdir.setter
    def outdir(self, path):
        self._outdir_ = path
        if path:
            run(f'mkdir -p {path}', shell=True)
            self.set_trace()

    def chk_cnx(self, report='quiet'):
        ''' to be overwriten
        '''
        return True

    def probe_distro(self):
        Distros = self.distros
        infos = Distro.release_default(self)
        for Dist in Distros:
            if Dist.release_check(self, infos):
                self.distro = Dist(self)
                debug(f'{self.distro.system.hostname} : {self.distro.name}')
                break
        else:
            raise UnsupportedDistroError(self)

    def set_trace(self):
        self.outrun = f'{self.outdir}/{self.name}.run'
        self.outlog = f'{self.outdir}/{self.name}.log'
        try:
            with open(self.outrun, 'w') as log:
                debug(f'outrun : {log.name}')
            with open(self.outlog, 'w') as log:
                debug(f'outlog : {log.name}')
        except Exception as x:
            error(x)
            self.outdir = None

    def trace(self, cmd, ret, out, err, **kw):
        if self.outdir:
            with open(self.outrun, 'a') as log:
                log.write(f'{cmd}\n')

            with open(self.outlog, 'a') as log:
                log.write(f'\n[{ret:^3}] {cmd}\n')
                if out:
                    if kw.get('report')=='quiet':
                        log.write(f'[out] ... ({len(out)})\n')
                    else:
                        if len(out)==1:
                            out = out[0]
                        else:
                            out = '\n'+'\n'.join(out)
                        log.write(f'[out] {out}\n')
                if err:
                    if len(err)==1:
                        err = err[0]
                    else:
                        err = '\n'+'\n'.join(err)
                    log.write(f'[err] {err}\n')

    def __getattr__(self, attr):
        return getattr(self.distro, attr)

    def parse(self, *arg, **kw):
        shell = kw.get('shell')
        if shell is None and len(arg)==1:
            shell = any(x in arg[0] for x in '*|>?<')
            kw['shell'] = shell

        args = []

        if not shell and len(arg)==1:
            arg = filter(None,
                (quote(i.strip()) for i in split(arg[0]))
            )
        args.extend(arg)
        return args, kw

    def run(self, *arg, report='normal', critical=True, raw=False, skip=None, **kw):
        def log(*msg):
            if report=='verbose':
                debug(*msg)

        cmd = arg
        command = ' '.join(cmd)
        if kw.get('shell'):
            cmd = command

        try:
            # log('running "%s" ...', command)
            try:
                proc = run(cmd, stdout=PIPE, stderr=PIPE, **kw)
            except OSError:
                kw['shell'] = True
                proc = run(cmd, stdout=PIPE, stderr=PIPE, **kw)

            out = proc.stdout.decode('utf-8', errors='replace').strip()
            if out:
                if report!='quiet':
                    debug("%s [out]:\n%s", command, out)
                if not raw:
                    out = [i.strip() for i in out.split('\n')]
                    if skip:
                        out = [i for i in out if not skip(i)]

            err = proc.stderr.decode('utf-8', errors='replace').strip()
            if err:
                log("%s [err]:\n%s", command, err)
                if not raw:
                    err = [i.strip() for i in err.split('\n')]
                    if skip:
                        err = [i for i in err if not skip(i)]

            ret = proc.returncode
            log('"%s" [ret]: %s', command, ret)

            return ret, out, err

        except CalledProcessError as exc:
            if critical:
                error(
                    "\n%s > %s\n%s\n%s",
                    " ".join(exc.cmd),
                    exc.returncode,
                    exc.stdout.decode('utf-8', errors='replace'),
                    exc.stderr.decode('utf-8', errors='replace'),
                )
            return -1, "ERROR", str(exc)

        except Exception as exc:
            error("%s raised: %s", cmd, exc)
            raise

    def check_one(self, cmd):
        ret, out, err = self.run(cmd)
        return ret==0

    def check_all(self, cmds):
        return all(
            self.check_one(cmd)
            for cmd in cmds.strip().split('\n')
        )

    def check(self, cmd):
        return self.check_all(cmd) if '\n' in cmd else self.check_one(cmd)


    def deploy(self, module, **kw):
        if not self.cnx:
            error('deploy ! no cnx')
            return

        if isinstance(module, str):
            try:
                cls = self.distro.modules.items[module]
            except KeyError:
                raise MissingModuleError(module, self.distro)
        else:
            cls = module

        try:
            if not issubclass(cls, Module):
                raise ModuleTypeError(cls)
        except TypeError:
            raise ModuleTypeError(cls)

        report = kw.pop('report', 'normal') != 'quiet'
        ret = cls(self.distro).deploy(self, **kw)
        if report:
            name = kw.pop('name', None)
            params = ', '.join(f'{k}={v}' for k, v in kw.items()) if kw else ''
            params = f' {params}' if params else ''
            status = '.' if ret else 'X'
            if name:
                info(f'\t{name}{params} {status}')
            else:
                info(f'\t{module}{params} {status}')
        return ret

    def register(self, module, name):
        if name in self.__dict__:
            error(f'\n ! Register Error !\n{self} has already a "{name}" attribute.\n')
            return
        setattr(self, name, partial(self.deploy, module, name=name))
        debug(f'{module.__module__} registred as {name}')

    def rsync_check(self):
        if hasattr(self, '_rsync_checked_'): return
        ret, out, err =  self.run('rsync --version', report='quiet')
        if ret:
            self.Package.install('rsync')
        self._rsync_checked_ = True

    def rsync_opt(self):
        ''' additional rsync opts
        '''

    def rsync(self, *arg, **kw):
        self.rsync_check()
        arg, kw = self.parse(*arg, **kw)
        cmd = 'rsync -qlpogcr -zz --delete'.split()
        if self.exclude:
            cmd.extend(['--exclude-from', self.exclude, '--delete-excluded'])
        opt = self.rsync_opt()
        if opt:
            cmd.append(opt)
        cmd.extend(arg)
        kw['report'] = 'verbose'
        ret, out, err =  CoreTarget.run(self, *cmd, **kw)
        self.trace('rsync '+' '.join(arg), ret, out, err, **kw)
        return ret==0

    def script(self, content, cmd=None, user=None, path=None, name=None, trim=True, remove=True, report='quiet'):
        path = path or '/tmp/setux'
        self.run(f'mkdir -p {path}')
        self.run(f'chmod 777 {path}')
        name = name or 'script'
        full = '/'.join((path, name))
        if trim:
            lines = (line.strip() for line in content.split('\n'))
            content = '\n'.join(line for line in lines if line)+'\n'
        self.write(full, content, report='quiet')
        if cmd:
            if user:
                cmd = f'sudo -u {user} {cmd}'
            self.run(f'chmod 644 {full}')
            ret, out, err = self.run(cmd.format(full))
        else:
            self.run(f'chmod +x {full}')
            ret, out, err = self.run(full)
        if remove:
            self.run(f'rm {full}', report='quiet')
        return ret, out, err

    def read(self, path, mode='rt', report='normal'): todo(self)
    def write(self, path, content, mode='wt', report='normal'): todo(self)
    def send(self, local, remote): todo(self)
    def fetch(self, remote, local): todo(self)
    def sync(self, src, dst=None): todo(self)
    def export(self, path): todo(self)
    def remote(self, module, export_path=None, **kw): todo(self)

