"""taoist_main.py"""
from taoist.parse_args import parse_args
from taoist.run_task import run_task
from taoist.run_project import run_project
from taoist.run_init import run_init
from taoist.run_label import run_label

def main():
    """
    Entry point for taoist program
    """

    # Parse arguments
    args = parse_args()

    # Fork execution stream
    if args.command == "project":
        run_project(args)
    elif args.command == "task":
        run_task(args)
    elif args.command == "init":
        run_init(args)
    elif args.command == "label":
        run_label(args)
    else:
        raise Exception(f"Command {args.command} not recognized")

if __name__ == "__main__":
    main()
