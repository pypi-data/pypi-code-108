from bioimage.io import *


def show_images(*images, titles=None, cols: int = 2,
                height_pixels: float = 200,
                output_folder: Path = None,
                cmap="gray",
                width_pixels: float = None):
    '''
    Shows images in a nice grid
    :param images:
    :param titles:
    :param cols:
    :param height:
    :param output_folder:
    :param cmap:
    :return:
    '''
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    height = height_pixels * px
    width_pixels = height_pixels if width_pixels is None else width_pixels
    width = width_pixels * px

    from skimage import img_as_float
    images = [img_as_float(img) for img in images]

    if titles is None:
        titles = [''] * len(images)
    vmin = min(map(np.min, images))
    vmax = max(map(np.max, images))
    num = len(images)
    ncols = cols if num > cols else num
    nrows = round(num / cols)
    plot_height = height * nrows
    plot_width = width * ncols
    print(f"columns ({cols}), rows ({nrows}), num ({num}), width_pixels ({width_pixels}), height_pixels ({height_pixels}), plot_height_inches ({plot_height}), plot_width_inches ({plot_width})")
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                             figsize=(plot_width, plot_height))
    fig.tight_layout()
    for ax, img, label in zip(axes.ravel(), images, titles):
        ax.imshow(img, vmin=vmin, vmax=vmax, cmap=cmap)
        ax.set_title(label)
    plt.subplots_adjust(wspace=None, hspace=None)
    if output_folder is not None:
        fig.savefig(output_folder / f"condition_comparison_automatically_generated.png", bbox_inches='tight')


def show_file_images(*files: Path, cols: int = 2, height_pixels: float = 200,
                     output_folder: Path = None,
                     cmap="gray",
                     width_pixels: float = None):
    """
    shows images in a grid starting from files
    :param files:
    :param cols:
    :param height:
    :return:
    """
    titles = [file.name for file in files]
    images = seq(files).map(load_frame).to_list()
    show_images(*images, cols=cols, height_pixels = height_pixels, output_folder = output_folder, cmap= cmap, titles=titles, width_pixels=width_pixels)
