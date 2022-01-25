import argparse
from pathlib import Path
from . import tools


def parse_cmd_line_args():
    # Get neighboring directories
    # neighbors = list(p.name for p in IMAGES_DIR.iterdir() if p.is_dir())
    # Command line argument parsing
    parser = argparse.ArgumentParser(
        description="Utility for building/tagging/pushing docker images."
    )
    parser.add_argument(
        "-r",
        "--rebuild",
        action="store_true",
        help="Rebuild with --no-cache option",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress stdout",
    )
    subparsers = parser.add_subparsers(
        title="mode", dest="mode", help="Mode of specifying a build."
    )
    workflow_parser = subparsers.add_parser("workflow")
    dockerfiles_parser = subparsers.add_parser("dockerfiles")

    # Specify a yaml workflow
    workflow_parser.add_argument(
        "workflow",
        type=str,
        help="Path to workflow yaml file image filenames(s).",
    )

    # Manually specify docker files or paths to search for dockerfiles
    dockerfiles_parser.add_argument(
        "paths",
        type=str,
        nargs="+",
        help="Docker image filenames(s) or directories to search.",
    )
    dockerfiles_parser.add_argument(
        "-o",
        "--organization",
        type=str,
        required=True,
        help="Organization for images.",
    )
    dockerfiles_parser.add_argument(
        "-c",
        "--context",
        type=str,
        default=str(Path.cwd()),
        help="Build context. By default the current directory.",
    )
    dockerfiles_parser.add_argument(
        "-x",
        "--allow_cross_platform",
        action="store_true",
        help="Allow cross platform (x86 vs aarch64) building. Default is False.",
    )
    dockerfiles_parser.add_argument(
        "-p",
        "--push",
        action="store_true",
        help="Run docker push on the latest tag. Default is False.",
    )
    dockerfiles_parser.add_argument(
        "-n",
        "--max_num_workers",
        type=int,
        default=1,
        help=(
            "Maximum number of build workers. If >1 multiprocessing is used. "
            f"Max value is half this computer's cpu count: {tools.MAX_NUM_WORKERS}. "
            "Default is 1."
        ),
    )
    return parser.parse_args()


def main():
    args = parse_cmd_line_args()
    if args.mode == "workflow":
        tools.run_workflow(args.workflow, rebuild=args.rebuild, quiet=args.quiet)
    elif args.mode == "dockerfiles":
        dockerfiles = tools.get_dockerfiles_from_paths(args.paths)
        tools.make_images(
            dockerfiles,
            args.organization,
            context=args.context,
            max_num_workers=args.max_num_workers,
            allow_cross_platform=args.allow_cross_platform,
            push=args.push,
            rebuild=args.rebuild,
            quiet=args.quiet,
        )
    else:
        raise ValueError(f"Unknown mode: {args.mode}")
    print("Done!")
