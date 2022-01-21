"""taoist_main.py"""
import asyncio
from taoist.parse_args import parse_args
from taoist.run_task import run_task
from taoist.run_project import run_project
from taoist.run_init import run_init
from taoist.run_label import run_label
from taoist.run_section import run_section

def main():
    """
    Entry point for taoist program
    """

    # Parse arguments
    args = parse_args()

    # Get the current event loop
    loop = asyncio.get_event_loop()

    # Fork execution stream
    if args.command == "project":
        loop.run_until_complete(run_project(args))
    elif args.command == "task":
        loop.run_until_complete(run_task(args))
    elif args.command == "init":
        run_init(args)
    elif args.command == "label":
        loop.run_until_complete(run_label(args))
    elif args.command == "section":
        loop.run_until_complete(run_section(args))
    else:
        raise Exception(f"Command {args.command} not recognized")

if __name__ == "__main__":
    main()
