import argparse
import subprocess
import warnings
from pathlib import Path
from os.path import relpath
from typing import List, Optional, Union

HELP = """
integer - traverse into that directory
? - show this help message
p - print current state
P - refresh
u or .. - go up to parent directory
c - show directories relative to this one
g /foo - go to a new directory
r - switch between relative or absolute paths
s - switch between sorting by name or by size
h - human-readable numbers
o - open this directory (MacOS only)
q - quit
"""

OUPs = Optional[Union[Path, str]]


def humanize(size: int) -> str:
    if size > 1024 ** 3:
        return f'{size / 1024 ** 3:>9.1f}T'
    elif size > 1024 ** 2:
        return f'{size / 1024 ** 2:>9.1f}G'
    elif size > 1024:
        return f'{size / 1024:>9.1f}M'
    else:
        return f'{size:>8d}K'


class DirectoryDu:
    """Disk usage information for a single directory. All paths are
    resolved as absolute paths using Path.resolve().
    """

    def __init__(self, path: OUPs, size: int):
        self.path = Path(path).resolve()
        self.size = size

    def __eq__(self, other):
        return (
            self.path.resolve() == other.path.resolve()
            and self.size == other.size
        )

    def __str__(self):
        return f'{self.path} {self.size}'

    def __hash__(self):
        return hash((self.path, self.size))

    __repr__ = __str__


class IDu:
    """Interactive disk usage analyser."""

    def __init__(self, directory: OUPs = None, base_directory: OUPs = None):
        if directory is not None:
            self.directory = Path(directory).resolve()
        else:
            self.directory = Path.cwd()

        if base_directory is not None:
            self.base_directory = Path(base_directory).resolve()
        else:
            self.base_directory = Path.cwd()
        self.results = []
        self.sort_by_size = True
        self.human = True
        self.rel = True

    def update(
        self,
        directory: OUPs = None,
        cached: bool = True,
    ):
        if directory is None:
            directory = self.directory

        directory = Path(directory).resolve()
        try:
            cached_paths = [r.path for r in self.results]
            if not (cached and directory in cached_paths):
                self.results, stderr = run_du(directory)
                if stderr:
                    warnings.warn(stderr)
                self.resort()

            self.directory = directory

        except KeyboardInterrupt:  # catch ctrl-C
            pass

    def here(self):
        return [r for r in self.results
                if r.path == self.directory or r.path.parent == self.directory]

    def resort(self):
        if self.sort_by_size:
            self.results = sorted(self.results, key=lambda x: x.size)
        else:
            self.results = sorted(self.results, key=lambda x: x.path)

    def prompt(self):
        ans = input('> ')
        try:
            if self.results is None:
                raise KeyError
            options = {n: r for n, r in enumerate(self.here())}
            self.update(options[int(ans)].path, cached=True)
            print(self)
        except (KeyError, ValueError):
            if ans == '?':
                print(HELP)
            elif ans == 'q':
                exit(0)
            elif ans == 'p':
                print(self)
            elif ans == 'P':
                self.update(cached=False)
                print(self)
            elif ans in {'..', 'u'}:
                self.update(self.directory.parent, cached=True)
                print(self)
            elif ans == 'c':
                self.base_directory = self.directory
                print(self)
            elif ans[:2] == 'g ':
                self.update(self.base_directory / Path(ans[2:]))
                print(self)
            elif ans == 'r':
                self.rel = not self.rel
                print(self)
            elif ans == 's':
                self.sort_by_size = not self.sort_by_size
                self.resort()
                print(self)
            elif ans == 'h':
                self.human = not self.human
                print(self)
            elif ans == 'o':
                try:
                    subprocess.run(['open', self.directory])
                except FileNotFoundError:
                    print('\'open\' command not found.')
            else:
                print('?')

    def loop(self):
        self.update()
        print(self)
        while True:
            try:
                self.prompt()
            except (KeyboardInterrupt, EOFError):
                break

    def __str__(self):
        # Show only the current directory and its immediate children
        here = self.here()
        children_size = sum(
            r.size for r in here if r.path.parent == self.directory
        )
        my_size = sum(r.size for r in here if r.path == self.directory)
        output = str(self.base_directory.resolve()) + '\n'

        def fmt(n, r):
            percentage = r.size / my_size * 100
            string = ''
            string += f'{n:<9d}'
            if self.human:
                string += f'{humanize(r.size):>10s}'
            else:
                string += f'{r.size:>10d}'

            string += f'  ({percentage:>6.2f}%)\t'

            if self.rel:
                rel = relpath(r.path, self.base_directory)
                string += f'{rel}'
            else:
                string += f'{r.path}'

            return string

        output += '\n'.join([fmt(n, r) for n, r in enumerate(here)])
        output += '\n'
        residue = my_size - children_size
        if humanize:
            output += f'of which {humanize(residue)}\tis from files in {self.directory}'
        else:
            output += f'of which {residue:>10d}\tis from files in {self.directory}'

        return output

    __repr__ = __str__


def run_du(directory: Union[str, Path]) -> (List[DirectoryDu], str):
    directory = str(directory)
    du_res = subprocess.run(
        ['du', '-k', directory], capture_output=True, text=True
    )
    out = du_res.stdout.split('\n')[:-1]
    out_2 = [o.split('\t') for o in out]
    return (
        [DirectoryDu(path, int(size)) for size, path in out_2],
        du_res.stderr
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Directory to du', nargs='?', default='.')
    args = parser.parse_args()

    idu = IDu(directory=Path(args.dir), base_directory=Path(args.dir))
    idu.loop()


if __name__ == '__main__':
    main()
