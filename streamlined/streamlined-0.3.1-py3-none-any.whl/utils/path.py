from collections import deque
from pathlib import Path
from typing import Callable, Deque, Generator


def _walk(path: Path, depth: int = -1) -> Generator[Path, bool, None]:
    """
    Iterate a directory in breadth first order with a depth limit.
    For example, suppose the following folder structure
    ```
    /foo
        a.txt
        b.txt
        /bar
            c.txt
    ```
    + calling _walk at `/foo` with `depth = 0` will yield nothing
    + calling _walk at `/foo` with `depth = 1` will yield `a.txt`, `b.txt`, `/foo/bar`
    + calling _walk at `/foo` with `depth = 2` will yield `a.txt`, `b.txt`, `/foo/bar`, `/foo/bar/c.txt` if sending True at yielding `/foo/bar`
    + calling _walk at `/foo` with `depth >= 3` or `depth = -1` will yield the same as calling with `depth = 2`
    A path can be selectively explored by sending `True` when iterating. See `walk` for example.
    :param path: A path to start exploring.
    :param depth: At which depth to stop exploring, default to -1 which means infinite depth.
    """
    to_visit: Deque[Path] = deque([path])
    next_to_visit: Deque[Path] = deque()

    while depth:
        while to_visit:
            current_dir: Path = to_visit.popleft()
            for child_path in current_dir.iterdir():
                if child_path.is_dir():
                    should_iter = yield child_path
                    if should_iter:
                        next_to_visit.append(child_path)
                else:
                    yield child_path

        if not next_to_visit:
            # nothing to visit next, exit
            return

        depth -= 1
        to_visit = next_to_visit
        next_to_visit = deque()


def walk(
    path: Path, depth: int = -1, should_explore_dir: Callable[[Path], bool] = lambda path: True
) -> Generator[Path, None, None]:
    """
    When the path points to a directory, iteratively yield path objects of the
    directory contents until depth is reached. -1 means infinite depth.
    :param path: A path to start exploring.
    :param depth: At which depth to stop exploring, default to -1 which means infinite depth.
    :param predicate: An action to execute on a path. For path pointing to a
        file, returned value has no effect. While for path pointing to a
        directory, return False will prevent the contents in this directory
        from being explored.
    Example:
    With the following folder structure:
    ```
    /foo
        a.txt
        b.txt
        /bar
            c.txt
    ```
    >>> len(list(walk(tmpdir, depth=0)))
    0
    >>> len(list(walk(tmpdir, depth=1)))
    1
    >>> len(list(walk(tmpdir, depth=2)))
    4
    >>> len(list(walk(tmpdir, depth=3)))
    5
    >>> len(list(walk(tmpdir, depth=-1, predicate=lambda path: path.name != 'bar')))
    4
    """
    walker = _walk(path, depth)
    try:
        yield (path := next(walker))
        while True:
            yield (path := walker.send(should_explore_dir(path)))
    except StopIteration:
        return


if __name__ == "__main__":
    import doctest
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdirname:
        """
        /foo
            a.txt
            b.txt
            /bar
                c.txt
        """
        tmpdir = Path(tmpdirname)
        foodir = tmpdir.joinpath("foo")
        foodir.mkdir()

        afile = foodir.joinpath("a.txt")
        afile.touch()

        bfile = foodir.joinpath("b.txt")
        bfile.touch()

        bardir = foodir.joinpath("bar")
        bardir.mkdir()

        cfile = bardir.joinpath("c.txt")
        cfile.touch()

        doctest.testmod()
