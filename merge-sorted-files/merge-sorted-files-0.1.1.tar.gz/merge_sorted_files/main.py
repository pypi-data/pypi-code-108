import click
import tqdm
from pathlib import Path
from typing import TextIO, Iterable

from merge_sorted_files.reader import IntReader
from merge_sorted_files.iterator import MergeSortedIterators

@click.command()
@click.argument("input_filenames", nargs=-1, type=click.File("r"))
@click.argument("output_filename", type=click.Path(exists=False, path_type=Path))
def main(input_filenames: Iterable[TextIO], output_filename: Path) -> None:
    """Merge sorted input files into one sorted output file.
    
    The input files should be sorted in ascending order and have one integer per line.
    The output file will be sorted in ascending order.
    """
    readers = [IntReader(fp) for fp in input_filenames]

    output_filename.parent.mkdir(parents=True, exist_ok=True)
    if output_filename.exists():
        click.echo("Output file exists!", err=True)
        exit(1)

    with output_filename.open("w") as fp:
        merge_files = MergeSortedIterators(readers)

        for value in tqdm.tqdm(merge_files, desc="Writing values to output"):
            fp.write(f"{value}\n")



if __name__ == "__main__":
    main()
