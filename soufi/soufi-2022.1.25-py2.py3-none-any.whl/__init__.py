# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.

"""A simple testing CLI to find and download source."""
import os
import shutil

import click

from soufi import exceptions, finder


class Finder:
    @classmethod
    def find(cls, finder):
        source = finder.find()
        click.echo(source)
        return source

    @classmethod
    def ubuntu(cls, name, version):
        click.echo("Logging in to Launchpad")
        ubuntu_finder = finder.factory(
            "ubuntu", name, version, finder.SourceType.os
        )
        click.echo("Finding source in Launchpad")
        return cls.find(ubuntu_finder)

    @classmethod
    def debian(cls, name, version):
        debian_finder = finder.factory(
            "debian", name, version, finder.SourceType.os
        )
        return cls.find(debian_finder)

    @classmethod
    def npm(cls, name, version):
        npm_finder = finder.factory(
            "npm", name, version, finder.SourceType.npm
        )
        return cls.find(npm_finder)

    @classmethod
    def python(cls, name, version, pyindex=None):
        python_finder = finder.factory(
            "python",
            name=name,
            version=version,
            s_type=finder.SourceType.python,
            pyindex=pyindex,
        )
        return cls.find(python_finder)

    @classmethod
    def centos(
        cls, name, version, repos=None, source_repos=None, binary_repos=None
    ):
        optimal = 'optimal' in repos
        centos_finder = finder.factory(
            "centos",
            name=name,
            version=version,
            s_type=finder.SourceType.os,
            repos=repos,
            optimal_repos=optimal,
            source_repos=source_repos,
            binary_repos=binary_repos,
        )
        return cls.find(centos_finder)

    @classmethod
    def alpine(cls, name, version, aports_dir):
        alpine_finder = finder.factory(
            "alpine",
            name=name,
            version=version,
            s_type=finder.SourceType.os,
            aports_dir=aports_dir,
        )
        return cls.find(alpine_finder)

    @classmethod
    def go(cls, name, version, goproxy):
        go_finder = finder.factory(
            "go",
            name=name,
            version=version,
            s_type=finder.SourceType.go,
            goproxy=goproxy,
        )
        return cls.find(go_finder)

    @classmethod
    def java(cls, name, version):
        java_finder = finder.factory(
            "java",
            name=name,
            version=version,
            s_type=finder.SourceType.java,
        )
        return cls.find(java_finder)

    @classmethod
    def gem(cls, name, version):
        gem_finder = finder.factory(
            "gem",
            name=name,
            version=version,
            s_type=finder.SourceType.gem,
        )
        return cls.find(gem_finder)

    @classmethod
    def photon(cls, name, version, source_repos=None, binary_repos=None):
        photon_finder = finder.factory(
            "photon",
            name=name,
            version=version,
            s_type=finder.SourceType.os,
            source_repos=source_repos,
            binary_repos=binary_repos,
        )
        return cls.find(photon_finder)

    @classmethod
    def rhel(cls, name, version, source_repos=None, binary_repos=None):
        rhel_finder = finder.factory(
            "rhel",
            name=name,
            version=version,
            s_type=finder.SourceType.os,
            source_repos=source_repos,
            binary_repos=binary_repos,
        )
        return cls.find(rhel_finder)


def make_archive_from_discovery_source(disc_src, fname):
    try:
        with disc_src.make_archive() as in_fd, open(fname, 'wb') as out_fd:
            # copyfileobj copies in chunks, so as not to exhaust memory.
            shutil.copyfileobj(in_fd, out_fd)
    except exceptions.DownloadError as e:
        click.echo(str(e))
        click.get_current_context().exit(255)


@click.command()
@click.argument("distro")
@click.argument("name")
@click.argument("version")
@click.option(
    "--pyindex",
    default="https://pypi.org/pypi/",
    help="Python package index if getting Python",
    show_default=True,
)
@click.option(
    "--aports",
    default=None,
    help="Path to a checked-out aports directory if getting Alpine",
    show_default=True,
)
@click.option(
    "--repo",
    default=(),
    multiple=True,
    help="For CentOS, name of repo to use instead of defaults. "
    "Use 'optimal' to use an extended optimal set. May be repeated.",
)
@click.option(
    "--source-repo",
    default=(),
    multiple=True,
    help="For Yum-based distros, URL of a source repo mirror to use "
    "for lookups instead of the distro defaults. May be repeated. "
    "On CentOS, this causes --repo to be ignored.",
)
@click.option(
    "--binary-repo",
    default=(),
    multiple=True,
    help="For Yum-based distros, URL of a binary repo mirror to use "
    "for lookups instead of the distro defaults. May be repeated. "
    "On CentOS, this causes --repo to be ignored.",
)
@click.option(
    "--goproxy",
    default="https://proxy.golang.org/",
    help="GOPROXY to use when downloading Golang module source",
    show_default=True,
)
@click.option(
    "--output",
    "-o",
    help="Download the source archive and write to this file name",
    default=None,
)
@click.option(
    "-O",
    "auto_output",
    is_flag=True,
    default=False,
    help="Download the source archive and write to a default file name."
    "The names vary according to the source type and the archive type, "
    "but will generally follow the format: "
    "{name}-{version}.{distro/type}.tar.[gz|xz] "
    "(This option takes precedence over -o/--output)",
)
def main(
    distro,
    name,
    version,
    pyindex,
    aports,
    repo,
    goproxy,
    output,
    auto_output,
    source_repo,
    binary_repo,
):
    """Find and optionally download source files.

    Given a binary name and version, will find and print the URL(s) to the
    source file(s).

    If the --output option is present, the URLs are all downloaded and
    combined into a LZMA-compressed tar file and written to the file
    name specifed.  If the original source is already an archive then that
    archive is used instead.

    The sources currently supported are 'debian', 'ubuntu', 'rhel', 'centos',
    'alpine', 'photon', 'java', 'go', 'python', and 'npm', one of which must be
    specified as the DISTRO argument.
    """
    try:
        func = getattr(Finder, distro)
    except AttributeError:
        click.echo(f"{distro} not available")
        click.get_current_context().exit(255)
    if distro == 'alpine' and aports is None:
        click.echo("Must provide --aports for Alpine")
        click.get_current_context().exit(255)
    try:
        if distro == 'python':
            disc_source = func(name, version, pyindex=pyindex)
        elif distro == 'alpine':
            disc_source = func(name, version, aports_dir=aports)
        elif distro == 'centos':
            disc_source = func(
                name,
                version,
                repos=repo,
                source_repos=source_repo,
                binary_repos=binary_repo,
            )
        elif distro in ('photon', 'rhel'):
            disc_source = func(
                name,
                version,
                source_repos=source_repo,
                binary_repos=binary_repo,
            )
        elif distro == 'go':
            disc_source = func(name, version, goproxy=goproxy)
        else:
            disc_source = func(name, version)
    except exceptions.SourceNotFound:
        click.echo("source not found")
        click.get_current_context().exit(255)

    if auto_output is not False or output is not None:
        fname = output
        if auto_output:
            name = name.replace(os.sep, '.')
            fname = f"{name}-{version}.{distro}{disc_source.archive_extension}"
        make_archive_from_discovery_source(disc_source, fname)


if __name__ == "__main__":
    main()
