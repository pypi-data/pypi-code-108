import os
import re
from subprocess import check_output
import click
from .api import MyelindlApi

def os_system_enable_raise(cmd):
    ret = os.system(cmd)
#    click.echo(click.style("System call return {}".format(ret), fg='green'))
    if ret != 0:
        raise Exception

## Buckets ##
@click.command(name="mb")
@click.argument('name', required=True)
def mk_bk(name):
    """make a bucket"""
    try:
        bk_name = None
        if name.startswith('bk/'):
            bk_name = name[3:]
        else:
            bk_name = name
        #register to server
        api = MyelindlApi()
        api.bucket_add(bk_name)
    except Exception as e:
        click.echo(click.style("Bucket created failed. {}".format(e), fg='red'))
        raise
    click.echo(click.style("Bucket `{}` created successfully.".format(name), fg='green'))


@click.command(name="rb")
@click.argument('name', required=True)
def rm_bk(name):
    """remove a bucket"""
    try:
        bk_name = name
        if name.startswith('bk/'):
            bk_name = name[3:]
        api = MyelindlApi()
        api.bucket_del(bk_name)
    except Exception as e:
        click.echo(click.style("Bucket delete failed. {}".format(e), fg='red'))
        raise
    click.echo(click.style("Bucket `{}` deleted successfully.".format(name), fg='green'))


## Objects ##
@click.command()
@click.argument('target', required=False, nargs=-1)
def ls(target):
    """list buckets and objects"""
    try:
        if target:
            args = ["{}".format(a) for a in target]
            objs = " ".join(args)
            out_b = check_output("mc ls {}".format(objs), shell=True)
            out = bytes.decode(out_b)
            for line in out.splitlines():
                if 'run-' not in line:
                    match = re.search(r"(\[.*\])\s+([^\s]+B) (.*)", line)
                    if match:
                        click.echo(click.style(match.group(1), fg='green')+'\t'+
                                   click.style(match.group(2), fg='yellow')+' '+
                                   click.style(match.group(3), fg='bright_cyan'))
        else:
            click.echo(click.style("Are you want to list bucket? try `steam data ls bk/`", fg='green'))
    except Exception as e:
        click.echo(click.style("ls failed. {}".format(e), fg='red'))
        raise


@click.command()
@click.argument('source', required=True, nargs=-1)
def cat(source):
    """display object contents"""
    try:
        args = [a for a in source]
        objs = " ".join(args)
        os_system_enable_raise("mc cat {}".format(objs))
    except Exception as e:
        click.echo(click.style("cat object failed. {}".format(e), fg='red'))
        raise


@click.command()
@click.option('-n', '--lines', default=10, help="print the first 'n' lines (default: 10)")
@click.argument('source', required=True, nargs=-1)
def head(lines, source):
    """display first 'n' lines of an object"""
    try:
        args = [a for a in source]
        objs = " ".join(args)
        os_system_enable_raise("mc head -n {} {}".format(lines, objs))
    except Exception as e:
        click.echo(click.style("cat object failed. {}".format(e), fg='red'))
        raise


@click.command()
@click.option('-r', '--recursive', is_flag=True, help="copy recursively")
@click.argument('source', required=True, nargs=-1)
@click.argument('target', required=True)
def cp(recursive, source, target):
    """copy objects"""
    try:
        args = [a for a in source]
        objs = " ".join(args)
        if recursive:
            os_system_enable_raise("mc cp --recursive {} {}".format(objs, target))
        else:
            os_system_enable_raise("mc cp {} {}".format(objs, target))
    except Exception as e:
        click.echo(click.style("copy failed. {}".format(e), fg='red'))
        raise


@click.command()
@click.option('-r', '--recursive', is_flag=True, help="remove recursively")
@click.argument('target', required=True, nargs=-1)
def rm(recursive, target):
    """remove objects"""
    try:
        args = [a for a in target]
        objs = " ".join(args)
        if recursive:
            os_system_enable_raise("mc rm --recursive --force {} ".format(objs))
        else:
            os_system_enable_raise("mc rm {}".format(objs))
    except Exception as e:
        click.echo(click.style("remove failed. {}".format(e), fg='red'))
        raise


@click.command()
@click.option('--overwrite', is_flag=True, help="overwrite object(s) on target")
@click.option('--remove', is_flag=True, help="remove extraneous object(s) on target")
@click.argument('source', required=True)
@click.argument('target', required=True)
def mirror(overwrite, remove, source, target):
    """synchronize object(s) to a remote site"""
    try:
        cmd = "mc mirror "
        if overwrite:
            cmd += "--overwrite "
        if remove:
            cmd += "--remove "
        cmd += "{} {}".format(source, target)
        os_system_enable_raise(cmd)
    except Exception as e:
        click.echo(click.style("mirror failed. {}".format(e), fg='red'))
        raise


@click.group(help='Groups of commands to manage datasets')
def data():
    pass

data.add_command(mk_bk)
data.add_command(rm_bk)
data.add_command(ls)
data.add_command(cat)
data.add_command(head)
data.add_command(cp)
data.add_command(rm)
data.add_command(mirror)
