from pathlib import Path
import functools
from typing import Callable, TypeVar, Any, Protocol

_T = TypeVar('_T')


class FunctionCaller(Protocol):
    """
    A type which describes functions which call a given function.
    """
    def __call__(self, __fn: Callable[..., _T], *args: Any, **kwargs: Any) -> Any:
        ...


def _call(__fn: Callable[..., _T], *args: Any, **kwargs: Any) -> _T:
    """
    Literally just call it.
    """
    return __fn(*args, **kwargs)


def vectorize(
        func: Callable[[Path], Path] = None, /, *,
        name_mapper: str | Callable[[Path], Path] = None,
        parents: bool = True,
        glob: str = '**/*',
        executor: FunctionCaller = _call
):
    """
    Creates a decorator which changes a function that operates on
    single files to one that processes every file in a directory.

    Examples
    --------

    Transform a function which processes input files, to a function
    that processes every input file in a directory:

    ```python
    @vectorize
    def process(input_file: Path, output_file: Path):
        ...
    ```

    Set a filter to only process `*.nii` files, and rename files
    so a file "brain.nii" gets written to "brain_segmentation.nii":

    ```python
    @vectorize(
        name_mapper='_segmentation',
        glob='**/*.nii'
    )
    def process(input_file: Path, output_file: Path):
        ...
    ```

    Use [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor)
    to parallelize subprocesses:

    ```python
    from pathlib import Path
    import subprocess as sp
    from concurrent.futures import ThreatPoolExecutor

    with ThreadPoolExecutor(max_workers=4) as pool:
        @vectorize(executor=pool.submit)
        def process(input_file: Path, output_file: Path):
            sp.run(['external_command', str(input_file), str(output_file)])

        process(Path('incoming/'), Path('outgoing/'))
    ```

    Add a progress bar with [tqdm](https://github.com/tqdm/tqdm):

    ```python
    from tqdm import tqdm

    num_files = 0
    @vectorize(glob='*.fasta')
    def count_files(_i, _o):
        nonlocal num_files
        num_files += 1

    count_files(inputdir, outputdir)

    with tqdm(total=num_files) as bar:
        @vectorize(glob='*.fasta')
        def process(input_file, output_file):
            nonlocal bar
            ...
            bar.update()

        process(inputdir, outputdir)
    ```

    Parameters
    ----------
    name_mapper: str or Callable
        Either a string which is appended to the file name
        before the file extension of the input file to get
        the output file name, or a function which, given
        the input file name, produces the output file name.
    parents: bool
        If True, create parent directories for output files as needed.
    glob: str
        file name pattern
    executor: Callable
        Used to make calls to the decorated function.
        Concurrency can be achieved by using a
        [`concurrent.futures.Executor.submit`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Executor.submit)
    """
    def wrap(fn: Callable[[Path], Path]):
        @functools.wraps(fn)
        def wrapper(inputdir: Path, outputdir: Path):
            get_output_name = name_mapper
            if get_output_name is None:
                get_output_name = ''
            if isinstance(get_output_name, str):
                get_output_name = _curry_suffix(inputdir, outputdir, get_output_name)

            for input_file in inputdir.glob(glob):
                if not input_file.is_file():
                    continue
                output_file = get_output_name(input_file)
                if parents:
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                executor(fn, input_file, output_file)
        return wrapper

    # See if we're being called as @vectorize or @vectorize().
    if func is None:
        # We're called with parens.
        return wrap

    # We're called as @vectorize without parens.
    return wrap(func)


def _curry_suffix(inputdir: Path, outputdir: Path, suffix: str) -> Callable[[Path], Path]:
    def append_suffix(input_file: Path) -> Path:
        rel = input_file.relative_to(inputdir)
        return (outputdir / rel).with_stem(input_file.stem + suffix)
    return append_suffix
