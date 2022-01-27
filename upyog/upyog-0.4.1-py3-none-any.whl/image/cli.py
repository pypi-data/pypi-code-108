from upyog.imports import *
from upyog.image import *
from upyog.os import *
from upyog.utils import *
from upyog.cli import *
from upyog.cli import Param as P


@call_parse
def create_image_grid_from_folders(
    # fmt: off
    i: P("An arbitrary number of inputs folders", str, nargs="+") = None,
    o: P("Output path - must be a folder (created if it doesn't exist)", str) = None,
    H: P("Height of _each_ image inside the grid", int) = 384,
    W: P("Width of each image inside the grid", int) = 640,
    num_columns: P("Number of columns in the grid", int) = 3,
    sample:      P("Random sample this no. of files from the folder", int) = None,
    shuffle:   P("(Bool) shuffle the order of files", action="store_true") = False,
    foreach:     P("(Bool) Create a dedicated grid for _each_ input folder given", action="store_true") = False,
    exp_quality: P("Export quality (0-100). ~85 is a good tradeoff", int) = 85,
    # fmt: on
):
    """
            --------- IMAGE GRID CREATOR ---------

    Create image grids from multiple folders. By default, files from
    all folders are combined to create a single grid. You can pick a
    random sample of `N` images  using the `sample` arg, or shuffle
    the order of images by passing `--shuffle`.

    To create grids for multiple folders, use the `--foreach` flag.

     Usage
    -------

    generate-image-grid                 \\
        --i inp-folder-1  inp-folder-2  \\
        --o ~/Desktop                   \\
        --sample 200      # Select 200 randomly sampled images

    generate-image-grid                 \\
        --i inp-folder-1  inp-folder-2  \\
        --o ~/Desktop                   \\
        --shuffle                       \\
        --foreach         # Creates 2 grids, one for each input folder
    """
    input_paths = []
    output_path = Path(o)
    for folder in i:
        path = Path(folder)
        assert path.is_dir(), f"!! Given input '{path}' is not a folder !!"
        input_paths += [path]

    # Output directory validation
    if not output_path.suffix == "":
        raise ValueError(
            f"Expected a folder path, but looks like you entered a filepath instead: {output_path}"
        )
    output_path.mkdir(exist_ok=True)

    # Create grids
    if foreach:
        for path in input_paths:
            files = get_image_files(path)
            grid = make_grid_from_files(files, num_columns, (W, H), sample, shuffle)
            grid.save(output_path / f"{path.stem}.jpg", quality=exp_quality)
    else:
        files = flatten(get_image_files(path) for path in input_paths)
        grid = make_grid_from_files(files, num_columns, (W, H), sample, shuffle)
        grid.save(output_path / "Image-Grid.jpg", quality=exp_quality)


def make_grid_from_files(files, ncol, size_WH, sample=None, shuffle=False):
    if sample:
        files = random.sample(files, sample)
    if shuffle:
        random.shuffle(files)

    imgs = [load_image(fn) for fn in files]
    return make_img_grid(imgs, ncol, size_WH, pad=True)
