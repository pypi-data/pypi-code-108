from os import environ
from pathlib import Path
from subprocess import call


from setux.core.manage import Manager
from setux.core.package import CommonPackager


def run(target, arg):
    target(arg)

def module(target, arg):
    mod = target.modules.items.get(arg)
    if mod:
        hlp = mod.help()
        title = f'module {arg}'
        print(title)
        print('-'*len(title))
        print(hlp)
    else:
        print(f' ! unkown module ! {arg}')

def modules(target, arg):
    modules = target.modules.items
    print('modules')
    print('-------')
    width = len(max(modules.keys(), key=len))+4
    for name, mod in sorted(modules.items()):
        hlp = mod.help()
        first = hlp.split('\n')[0]
        if (
            not arg
            or arg in name
            or arg in first.lower()
        ): print(f'{name:>{width}} {first}')

def manage(target, line):
    cmd, *arg = line.split()
    manager, _, command = cmd.partition('.')
    manager = getattr(target, manager)
    if '=' in command:
        attr, _, val = command.partition('=')
        setattr(manager, attr, val)
    else:
        command = getattr(manager, command)
        if callable(command):
            gen = command(*arg)
            try:
                for vals in gen:
                    print('\t'.join(vals))
            except Exception: pass
        else:
            print(command)

def manager(target, arg):
    manager = target.managers.get(arg)
    if manager:
        hlp = manager.help()
        title = f'manager {arg}'
        print(title)
        print('-'*len(title))
        print(hlp)
    else:
        print(f' ! unkown manager ! {arg}')

def managers(target, arg):
    managers = target.managers
    print('managers')
    print('-------')
    width = len(max(managers.keys(), key=len))+4
    for name, manager in sorted(managers.items()):
        hlp = manager.help()
        first = hlp.split('\n')[0]
        if (
            not arg
            or arg in name
            or arg in first.lower()
        ): print(f'{name:>{width}} {first}')

def mappings(target, arg):
    width = 0
    packages = target.pkgmap
    if packages:
        print('packages :')
        width = len(max(packages.keys(), key=len))+4
        for name, pkg in sorted(packages.items()):
            print(f'{name:>{width}} {pkg}')

    for manager in target.managers.values():
        if isinstance(manager, CommonPackager):
            packages = manager.pkgmap
            if packages:
                print(f'{manager.manager} :')
                w = len(max(packages.keys(), key=len))+4
                width = max(width, w)
                for name, pkg in sorted(packages.items()):
                    print(f'{name:>{width}} {pkg}')

    services = target.svcmap
    if services:
        print('\nservices :')
        w = len(max(services.keys(), key=len))+4
        width = max(width, w)
        for name, svc in sorted(services.items()):
            print(f'{name:>{width}} {svc}')

def deploy(target, arg):
    report = 'quiet' if arg=='infos' else 'normal'
    target.deploy(arg, report=report)

def remote(target, arg):
    target.remote(arg)

def update(target, arg):
    target.Package.update()

def upgrade(target, arg):
    target.Package.upgrade()

def installed(target, arg):
    pkg = list(target.Package.installed(arg))
    print('\n'.join(f'{n} {v}' for n, v in pkg))

def installable(target, arg):
    pkg = target.Package.installable(arg)
    print('\n'.join(f'{n} {v}' for n, v in pkg))

def search(target, arg):
    found = target.search(arg, report='quiet')
    print('\n'.join(f'{p} {n} {v}' for p, n, v in found))

def bigs(target, arg):
    pkg = list(target.Package.bigs())
    print('\n'.join(pkg))

def upgradable(target, arg):
    pkg = list(target.Package.upgradable())
    print('\n'.join(n for n, v in pkg))

def install(target, arg):
    target.Package.install(arg)

def remove(target, arg):
    target.Package.remove(arg)

def cleanup(target, arg):
    target.Package.cleanup()

def status(target, arg):
    target.Service.status(arg)

def start(target, arg):
    target.Service.start(arg)

def stop(target, arg):
    target.Service.stop(arg)

def restart(target, arg):
    target.Service.restart(arg)

def enable(target, arg):
    target.Service.enable(arg)

def disable(target, arg):
    target.Service.disable(arg)

def download(target, arg):
    url, dst = arg.split(' ') if ' ' in arg else arg, None
    target.deploy('download', url=url, dst=dst)

def outrun(target, arg):
    log = target.outrun
    if log:
        print(open(log).read())
    else:
        print('target outrun not defined')

def outlog(target, arg):
    log = target.outlog
    if log:
        print(open(log).read())
    else:
        print('target outlog not defined')

def edit(target, remote):
    editor = environ.get('EDITOR','vim')
    dest = Path('/tmp/setux')
    dest.mkdir(exist_ok=True)
    path = Path(remote)
    local = f'{dest}/{path.name}'
    ok = target.fetch(remote, local, quiet=True)
    if not ok: return False
    orginal = open(local).read()
    call([editor, local])
    edited = open(local).read()
    if edited!=orginal:
        ok = target.send(local, remote)
        status = '.' if ok else 'X'
        print(f'write {remote} {status}')
        return ok
    return True
