from concurrent.futures import ThreadPoolExecutor

from rich import filesize
from rich.text import Text
from .wiki_reader import find_films
from .db_writer import DBWriter
import os
import argparse
from .wiki_downloader import WikiDumpDownloader
from multiprocessing import cpu_count
from importlib.metadata import version
from rich import print
from rich.progress import FileSizeColumn, Progress, ProgressColumn
from rich.progress import TextColumn, Task


class TransferSpeedColumn(ProgressColumn):
    """Renders human readable transfer speed."""

    def render(self, task: "Task") -> Text:
        """Show data transfer speed."""
        speed = task.finished_speed or task.speed
        if speed is None:
            return Text("?", style="magenta")
        data_speed = filesize.decimal(int(speed))
        return Text(f"{data_speed}/s", style="magenta")


progress = Progress(
    TextColumn("{task.description}", style="white"),
    "•",
    FileSizeColumn(),
    "•",
    TransferSpeedColumn(),
)


def main():
    parser = argparse.ArgumentParser(
        prog="archean",
        description="Archean is a tool to process Wikipedia dumps and \
            extract required information from them. The parser \
                accepts a few parameters that can be specified during \
                    script invokation.",
    )

    parser.add_argument(
        "--version", action="store_true", help="Display the version of the package"
    )

    parser.add_argument(
        "--host",
        help="Host location for the database server",
    )
    parser.add_argument("--user", help="Username for the database authentication")
    parser.add_argument("--password", help="Password for the database authentication")
    parser.add_argument("--port", help="Port for database")
    parser.add_argument("--db", help="Database name to point to. Defaults to `media`.")
    parser.add_argument(
        "--collection",
        help="Collection in which the extracted JSON data will \
            be stored in. Defaults to `movies`.",
    )
    parser.add_argument(
        "--remote-dir",
        help="The remote directory from which the dump is to be downloaded",
    )
    parser.add_argument(
        "--extraction-dir",
        default="extracts",
        help="Directory to store extracted information",
    )
    parser.add_argument(
        "--download-only",
        action="store_true",
        help="Only download files, Do NOT process them",
    )
    args = parser.parse_args()

    if args.version:
        app_version = version("archean")
        print(f"archean v{app_version}\n")
        return

    if args.remote_dir:
        loader = WikiDumpDownloader(args.remote_dir)
        loader.fetch_dumps(None)

        if args.download_only:
            # exit if download only
            return

    if args.download_only:
        print("[yellow]Please provide a remote directory to download the dumps.\n")
        return

    if any(
        list(
            map(
                bool,
                [
                    args.host,
                    args.port,
                    args.db,
                    args.collection,
                    args.user,
                    args.password,
                ],
            )
        )
    ) and not all(
        list(
            map(
                bool,
                [
                    args.host,
                    args.port,
                    args.db,
                    args.collection,
                    args.user,
                    args.password,
                ],
            )
        )
    ):
        print(
            "[yellow]Please provide all arguments for DB: host, port, dbname, collection, username and password\n"
        )
        return

    files = []
    skipped = 0
    contents = [os.path.realpath(file) for file in os.listdir() if "xml-p" in file]
    if len(contents) == 0:
        print(
            "[yellow]No compressed dumps found to process in the current directory. "
            + "Please download first or execute the command in the directory where dumps are present.\n"
            + "To download, use the --remote-dir option.\n"
        )
        return
    # create a extraction directory in current folder
    if not os.path.exists(f"./{args.extraction_dir}"):
        os.mkdir(args.extraction_dir)

    extraction_fullpath = os.path.realpath(args.extraction_dir)

    # Create a list of compressed dumps to be processed.
    # Skip if a same .json file is present in extraction directory
    for file in contents:
        # Create file name based on partition name
        f_name = os.path.splitext(os.path.basename(file).split("/")[-1])[0]
        JSON_file = os.path.join(extraction_fullpath, f"{f_name}.json")
        if os.path.exists(JSON_file):
            print(f"[blue]Skipping {f_name} since it's already processed")
            skipped += 1
            continue
        else:
            files.append(file)

    print(f"[blue]Skipped {skipped} files")
    # Create a pool of workers to execute processes
    with progress:
        with ThreadPoolExecutor(max_workers=cpu_count() - 2) as executor:
            for file in files:
                task_id = progress.add_task(
                    description=os.path.basename(file),
                    start=False,
                )
                executor.submit(
                    find_films,
                    extraction_dir=extraction_fullpath,
                    data_path=file,
                    task_id=task_id,
                    progress=progress,
                )

    # Write to db
    if all(
        list(
            map(
                bool,
                [
                    args.host,
                    args.port,
                    args.db,
                    args.collection,
                    args.user,
                    args.password,
                ],
            )
        )
    ):
        writer = DBWriter(
            connection_str=args.conn,
            host=args.host,
            user=args.u,
            passwrd=args.p,
            collection=args.collection,
            db=args.db,
            port=args.port,
        )
        if os.path.exists(extraction_fullpath):
            writer.write(extraction_fullpath)
            writer.process_dates()
        else:
            # Raise RuntimeError if partition directory does not exist
            print(
                "[bold red]No extracted data found.\n"
                + "Download some data and process it first.\n"
                + "Run archean -h for help"
            )


if __name__ == "__main__":
    main()
