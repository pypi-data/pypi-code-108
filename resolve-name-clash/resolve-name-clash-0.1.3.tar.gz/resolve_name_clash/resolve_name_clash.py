from pathlib import Path

import click


def resolve_name_clash(src: Path, dest: Path) -> Path:
    # Figure out a target filename that doesn't exist.
    candidate = dest / src.name

    if candidate.exists():
        suffixes = candidate.suffixes

        # Strip all the suffixes off the candidate so we can
        # put the dedupe indentifier at the end of the base name
        basename = candidate
        while basename.suffix in suffixes:
            basename = basename.with_suffix("")

        # Keep trying successive dedupe indices until we find
        # one that doesn't exist
        dedupe_idx = 1
        while candidate.exists():
            candidate = basename.with_stem(f"{basename.name}_{dedupe_idx}").with_suffix(
                "".join(suffixes)
            )
            dedupe_idx += 1

    return candidate


@click.command()
@click.argument("src_filename")
@click.argument("dest_dir")
def cli(src_filename: str, dest_dir: str):
    result = resolve_name_clash(Path(src_filename), Path(dest_dir))
    click.echo(result)
