# -*- mode: python; coding: utf-8 -*-
# Copyright 2019-2022 the AAS WorldWide Telescope project.
# Licensed under the MIT License.

"""
Entrypoints for the "toasty pipeline" command-line tools.
"""

__all__ = """
pipeline_getparser
pipeline_impl
""".split()

from fnmatch import fnmatch
import glob
import os.path
import sys
from wwt_data_formats.cli import EnsureGlobsExpandedAction

from ..cli import die
from . import NotActionableError


def evaluate_imageid_args(searchdir, args):
    """
    Figure out which image-ID's to process.
    """

    matched_ids = set()
    globs_todo = set()

    for arg in args:
        if glob.has_magic(arg):
            globs_todo.add(arg)
        else:
            # If an ID is explicitly (non-gobbily) added, always add it to the
            # list, without checking if it exists in `searchdir`. We could check
            # for it in searchdir now, but we'll have to check later anyway, so
            # we don't bother.
            matched_ids.add(arg)

    if len(globs_todo):
        for filename in os.listdir(searchdir):
            for g in globs_todo:
                if fnmatch(filename, g):
                    matched_ids.add(filename)
                    break

    return sorted(matched_ids)


# The "approve" subcommand


def approve_setup_parser(parser):
    parser.add_argument(
        "--workdir",
        metavar="PATH",
        default=".",
        help="The working directory for this processing session",
    )
    parser.add_argument(
        "cand_ids",
        nargs="+",
        action=EnsureGlobsExpandedAction,
        metavar="IMAGE-ID",
        help="Name(s) of image(s) to approve for publication (globs accepted)",
    )


def approve_impl(settings):
    from wwt_data_formats.folder import Folder, make_absolutizing_url_mutator
    from . import PipelineManager

    mgr = PipelineManager(settings.workdir)
    mgr.ensure_config()

    pub_url_prefix = mgr._config.get("publish_url_prefix")
    if pub_url_prefix:
        if pub_url_prefix[-1] != "/":
            pub_url_prefix += "/"

    proc_dir = mgr._ensure_dir("processed")
    app_dir = mgr._ensure_dir("approved")

    for cid in evaluate_imageid_args(proc_dir, settings.cand_ids):
        if not os.path.isdir(os.path.join(proc_dir, cid)):
            die(f"no such processed candidate ID {cid!r}")

        index_path = os.path.join(proc_dir, cid, "index.wtml")
        prefix = pub_url_prefix + cid + "/"

        try:
            f = Folder.from_file(os.path.join(proc_dir, cid, "index_rel.wtml"))
            f.mutate_urls(make_absolutizing_url_mutator(prefix))

            with open(index_path, "wt", encoding="utf8") as f_out:
                f.write_xml(f_out)
        except Exception as e:
            print(
                "error: failed to create index.wtml from index_rel.wtml",
                file=sys.stderr,
            )

            try:
                os.remove(index_path)
            except Exception:
                pass

            raise

        os.rename(os.path.join(proc_dir, cid), os.path.join(app_dir, cid))


# The "fetch" subcommand


def fetch_setup_parser(parser):
    parser.add_argument(
        "--workdir",
        metavar="PATH",
        default=".",
        help="The working directory for this processing session",
    )
    parser.add_argument(
        "cand_ids",
        nargs="+",
        action=EnsureGlobsExpandedAction,
        metavar="CAND-ID",
        help="Name(s) of candidate(s) to fetch and prepare for processing (globs accepted)",
    )


def fetch_impl(settings):
    from . import PipelineManager

    mgr = PipelineManager(settings.workdir)
    cand_dir = mgr._ensure_dir("candidates")
    rej_dir = mgr._ensure_dir("rejects")
    src = mgr.get_image_source()

    for cid in evaluate_imageid_args(cand_dir, settings.cand_ids):
        # Funky structure here is to try to ensure that cdata is closed in case
        # a NotActionable happens, so that we can move the directory on Windows.
        try:
            try:
                cdata = open(os.path.join(cand_dir, cid), "rb")
            except FileNotFoundError:
                die(f"no such candidate ID {cid!r}")

            try:
                print(f"fetching {cid} ... ", end="")
                sys.stdout.flush()
                cachedir = mgr._ensure_dir("cache_todo", cid)
                src.fetch_candidate(cid, cdata, cachedir)
                print("done")
            finally:
                cdata.close()
        except NotActionableError as e:
            print("not usable:", e)
            os.rename(os.path.join(cand_dir, cid), os.path.join(rej_dir, cid))
            os.rmdir(cachedir)


# The "init" subcommand


def init_setup_parser(parser):
    parser.add_argument(
        "--azure-conn-env",
        metavar="ENV-VAR-NAME",
        help="The name of an environment variable contain an Azure Storage "
        "connection string",
    )
    parser.add_argument(
        "--azure-container",
        metavar="CONTAINER-NAME",
        help="The name of a blob container in the Azure storage account",
    )
    parser.add_argument(
        "--azure-path-prefix",
        metavar="PATH-PREFIX",
        help="A slash-separated path prefix for blob I/O within the container",
    )
    parser.add_argument(
        "--local", metavar="PATH", help="Use the local-disk I/O backend"
    )
    parser.add_argument(
        "workdir",
        nargs="?",
        metavar="PATH",
        default=".",
        help="The working directory for this processing session",
    )


def _pipeline_io_from_settings(settings):
    from . import azure_io, local_io

    if settings.local:
        return local_io.LocalPipelineIo(settings.local)

    if settings.azure_conn_env:
        conn_str = os.environ.get(settings.azure_conn_env)
        if not conn_str:
            die(
                "--azure-conn-env=%s provided, but that environment variable is unset"
                % settings.azure_conn_env
            )

        if not settings.azure_container:
            die("--azure-container-name must be provided if --azure-conn-env is")

        path_prefix = settings.azure_path_prefix
        if not path_prefix:
            path_prefix = ""

        azure_io.assert_enabled()

        return azure_io.AzureBlobPipelineIo(
            conn_str, settings.azure_container, path_prefix
        )

    die("An I/O backend must be specified with the arguments --local or --azure-*")


def init_impl(settings):
    pipeio = _pipeline_io_from_settings(settings)
    os.makedirs(settings.workdir, exist_ok=True)
    pipeio.save_config(os.path.join(settings.workdir, "toasty-store-config.yaml"))


# The "refresh" subcommand
#
# TODO: for large feeds, we should potentially add features to make it so that
# we don't re-check every single candidate that's ever been posted.


def refresh_setup_parser(parser):
    parser.add_argument(
        "--workdir",
        nargs="?",
        metavar="PATH",
        default=".",
        help="The working directory for this processing session",
    )


def refresh_impl(settings):
    from . import PipelineManager

    mgr = PipelineManager(settings.workdir)
    cand_dir = mgr._ensure_dir("candidates")
    rej_dir = mgr._ensure_dir("rejects")
    src = mgr.get_image_source()
    n_cand = 0
    n_saved = 0
    n_done = 0
    n_skipped = 0
    n_rejected = 0

    for cand in src.query_candidates():
        n_cand += 1
        uniq_id = cand.get_unique_id()

        if mgr._pipeio.check_exists(uniq_id, "index.wtml"):
            n_done += 1
            continue  # skip already-done inputs

        if mgr._pipeio.check_exists(uniq_id, "skip.flag"):
            n_skipped += 1
            continue  # skip inputs that are explicitly flagged

        cand_path = os.path.join(cand_dir, uniq_id)

        try:
            with open(cand_path, "wb") as f:
                cand.save(f)
            n_saved += 1
        except NotActionableError as e:
            os.remove(cand_path)

            with open(os.path.join(rej_dir, uniq_id, "wb")) as f:
                pass  # for now, just touch the file

            n_rejected += 1

    print(f"analyzed {n_cand} candidates from the image source")
    print(f"  - {n_saved} processing candidates saved")
    print(f"  - {n_rejected} rejected as definitely unusable")
    print(f"  - {n_done} were already done")
    print(f"  - {n_skipped} were already marked to be ignored")
    print()
    print("See the `candidates` directory for candidate image IDs.")


# Other subcommands not yet split out.


def pipeline_getparser(parser):
    subparsers = parser.add_subparsers(dest="pipeline_command")

    def add_manager_command(name):
        subp = subparsers.add_parser(name)
        subp.add_argument(
            "--workdir",
            nargs="?",
            metavar="WORKDIR",
            default=".",
            help="The local working directory",
        )
        return subp

    approve_setup_parser(subparsers.add_parser("approve"))
    fetch_setup_parser(subparsers.add_parser("fetch"))
    add_manager_command("ignore-rejects")
    init_setup_parser(subparsers.add_parser("init"))
    add_manager_command("process-todos")
    add_manager_command("publish")
    refresh_setup_parser(subparsers.add_parser("refresh"))


def pipeline_impl(settings):
    from . import PipelineManager

    if settings.pipeline_command is None:
        print('Run the "pipeline" command with `--help` for help on its subcommands')
        return

    if settings.pipeline_command == "approve":
        approve_impl(settings)
    elif settings.pipeline_command == "fetch":
        fetch_impl(settings)
    elif settings.pipeline_command == "ignore-rejects":
        mgr = PipelineManager(settings.workdir)
        mgr.ignore_rejects()
    elif settings.pipeline_command == "init":
        init_impl(settings)
    elif settings.pipeline_command == "process-todos":
        mgr = PipelineManager(settings.workdir)
        mgr.process_todos()
    elif settings.pipeline_command == "publish":
        mgr = PipelineManager(settings.workdir)
        mgr.publish()
    elif settings.pipeline_command == "refresh":
        refresh_impl(settings)
    else:
        die('unrecognized "pipeline" subcommand ' + settings.pipeline_command)
