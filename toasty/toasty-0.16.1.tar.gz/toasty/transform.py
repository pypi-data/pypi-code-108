# -*- mode: python; coding: utf-8 -*-
# Copyright 2020-2021 the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""
Within-tile data transformations. Mainly, transforming floating-point data to
RGB.
"""

__all__ = '''
f16x3_to_rgb
u8_to_rgb
'''.split()

from astropy import visualization as viz
import numpy as np
from tqdm import tqdm

from .image import ImageMode, Image
from .pyramid import depth2tiles, generate_pos


# Generalized transform machinery, with both serial and parallel support

def _do_a_transform(pio, depth, make_buf, do_one, pio_out=None, parallel=None, cli_progress=False):
    from .par_util import resolve_parallelism
    parallel = resolve_parallelism(parallel)

    if pio_out is None:
        pio_out = pio

    if parallel > 1:
        _transform_parallel(pio, pio_out, depth, make_buf, do_one, cli_progress, parallel)
    else:
        buf = make_buf()

        with tqdm(total=depth2tiles(depth), disable=not cli_progress) as progress:
            for pos in generate_pos(depth):
                do_one(buf, pos, pio, pio_out)
                progress.update(1)

        if cli_progress:
            print()


def _transform_parallel(pio_in, pio_out, depth, make_buf, do_one, cli_progress, parallel):
    import multiprocessing as mp

    # Start up the workers

    done_event = mp.Event()
    queue = mp.Queue(maxsize = 16 * parallel)
    workers = []

    for _ in range(parallel):
        w = mp.Process(target=_transform_mp_worker, args=(queue, done_event, pio_in, pio_out, make_buf, do_one))
        w.daemon = True
        w.start()
        workers.append(w)

    # Send out them tiles

    with tqdm(total=depth2tiles(depth), disable=not cli_progress) as progress:
        for pos in generate_pos(depth):
              queue.put(pos)
              progress.update(1)

    # All done

    queue.close()
    queue.join_thread()
    done_event.set()

    for w in workers:
        w.join()

    if cli_progress:
        print()


def _transform_mp_worker(queue, done_event, pio_in, pio_out, make_buf, do_one):
    """
    Do the colormapping.
    """
    from queue import Empty

    buf = make_buf()

    while True:
        try:
            pos = queue.get(True, timeout=1)
        except Empty:
            if done_event.is_set():
                break
            continue

        do_one(buf, pos, pio_in, pio_out)


# float-to-RGB(A), with a generalized float-to-unit transform

def f16x3_to_rgb(pio, start_depth, clip=1, **kwargs):
    transform = viz.SqrtStretch() + viz.ManualInterval(0, clip)
    _float_to_rgb(pio, start_depth, transform, **kwargs)


def _float_to_rgb(pio_in, depth, transform, out_format='png', **kwargs):
    make_buf = lambda: np.empty((256, 256, 3), dtype=np.uint8)
    do_one = lambda buf, pos, pio_in, pio_out: _float_to_rgb_do_one(buf, pos, pio_in, pio_out, transform, out_format)
    _do_a_transform(pio_in, depth, make_buf, do_one, **kwargs)


def _float_to_rgb_do_one(buf, pos, pio_in, pio_out, transform, out_format):
    img = pio_in.read_image(pos, format='npy')
    if img is None:
        return

    mapped = transform(img.asarray())

    if mapped.ndim == 2:
        # TODO: allow real colormaps
        valid = np.isfinite(mapped)
        mapped = mapped.reshape((256, 256, 1))
    else:
        valid = np.all(np.isfinite(mapped), axis=2)

    mapped[~valid] = 0
    mapped = np.clip(mapped * 255, 0, 255).astype(np.uint8)
    buf[...] = mapped
    rgb = Image.from_array(buf)
    pio_out.write_image(pos, rgb, format=out_format, mode=ImageMode.RGB)


def _float_to_rgba(pio_in, depth, transform, **kwargs):
    make_buf = lambda: np.empty((256, 256, 4), dtype=np.uint8)
    do_one = lambda buf, pos, pio_in, pio_out: _float_to_rgba_do_one(buf, pos, pio_in, pio_out, transform)
    _do_a_transform(pio_in, depth, make_buf, do_one, **kwargs)


def _float_to_rgba_do_one(buf, pos, pio_in, pio_out, transform):
    img = pio_in.read_image(pos, format='npy')
    if img is None:
        return

    mapped = transform(img.asarray())

    if mapped.ndim == 2:
        # TODO: allow real colormaps
        valid = np.isfinite(mapped)
        mapped[~valid] = 0
        mapped = np.clip(mapped * 255, 0, 255).astype(np.uint8)
        buf[...,:3] = mapped.reshape((256, 256, 1))
        buf[...,3] = 255 * valid
    else:
        valid = np.all(np.isfinite(mapped), axis=2)
        mapped[~valid] = 0
        mapped = np.clip(mapped * 255, 0, 255).astype(np.uint8)
        buf[...,:3] = mapped
        buf[...,3] = 255 * valid

    rgba = Image.from_array(buf)
    pio_out.write_image(pos, rgba, format='png', mode=ImageMode.RGBA)


# u8-to-RGB

def u8_to_rgb(pio, depth, **kwargs):
    make_buf = lambda: np.empty((256, 256, 3), dtype=np.uint8)
    _do_a_transform(pio, depth, make_buf, _u8_to_rgb_do_one, **kwargs)


def _u8_to_rgb_do_one(buf, pos, pio_in, pio_out):
    img = pio_in.read_image(pos, format='npy')
    if img is None:
        return

    buf[...] = img.asarray()[...,np.newaxis]
    rgb = Image.from_array(buf)
    pio_out.write_image(pos, rgb, format='jpg', mode=ImageMode.RGB)
