"""
Utility class to handle windowed read and write rasterio operations.
"""

from typing import Union, Iterable

import rasterio as rio
from rasterio.windows import Window
from rasterio.enums import Resampling
import numpy as np


class WindowsUtil:
    """
    Utility class to handle raster IO in windows. Can do regular windows, buffered
    windows and transform windows.
    """

    def __init__(self, rio_ds: Union[rio.io.DatasetReader, rio.io.DatasetWriter]):
        """
        Initialize the instance with a rasterio dataset (read or write).

        Arguments:
            rio_ds: An open rasterio dataset.
        """
        self.rio_ds = rio_ds
        self.windows = rio_ds.block_windows(1)

    def windows_regular(self) -> Iterable[Window]:
        """
        Method that returns regular rasterio windows.

        Returns:
            An iterable of rasterio windows.
        """
        for _, window in self.windows:
            yield window

    def windows_buffered(self, buffer: int = 0) -> Iterable[Window]:
        """
        Method that returns buffered windows with a given int buffer.

        Arguments:
            buffer: A buffer size in pixels.

        Returns:
            An iterable of rasterio windows.
        """
        for _, window in self.windows:
            buffered_window = self.buffer_window(window, buffer)
            yield window, buffered_window

    def windows_transformed(
        self, dst_transform: rio.Affine, dst_px_height: int, dst_px_width: int
    ) -> Iterable[Window]:
        """
        Method that returns windows with a transformed into a given rasterio Dataset
        Affine transform.

        Arguments:
            dst_transform: A target transform to use to generate windows.
            dst_px_height: The destination dataset pixel height.
            dst_px_width: The destination dataset pixel width.

        Returns:
            An iterable of rasterio windows.
        """
        for _, window in self.windows:
            transformed_window = self.transform_window(window, dst_transform)
            transformed_window = self.limit_window_to_raster_bounds(
                transformed_window, dst_px_height, dst_px_width
            )
            yield window, transformed_window

    def upsample_window_array(
        self,
        low_res_window: Window,
        high_res_window: Window,
        resampling_method: Resampling = Resampling.bilinear,
    ) -> np.array:
        """
        Method that returns an upsampled array to a given window, with an adapatable
        resampling method.

        Arguments:
            low_res_window: The low resolution window.
            high_res_window: The upsampled high resolution target window.
            resampling_method: The resampling method to use.

        Returns:
            An upsampled window numpy array.
        """
        up_ar = self.rio_ds.read(
            window=low_res_window,
            out_shape=(
                self.rio_ds.count,
                high_res_window.height,
                high_res_window.width,
            ),
            resampling=resampling_method,
        )
        return up_ar

    def buffer_window(self, window: Window, buffer: int) -> Window:
        """
        Buffers a window with a set number of pixels (buffer) in every possible direction
        given a shape of the overall raster file where window is derived from.

        For instance, if window matches the shape of the source raster file, the shape
        of the source raster file is returned in window format.

        Arguments:
            window: Original window (for instance from block).
            buffer: Number of pixels to buffer by where possible.

        Returns:
            A buffered window.
        """
        row_slice, col_slice = window.toslices()

        can_row_start = row_slice.start - buffer
        can_row_stop = row_slice.stop + buffer

        can_col_start = col_slice.start - buffer
        can_col_stop = col_slice.stop + buffer

        out_row_slice = slice(can_row_start, can_row_stop)
        out_col_slice = slice(can_col_start, can_col_stop)

        return self.limit_window_to_raster_bounds(
            Window.from_slices(out_row_slice, out_col_slice, boundless=True)
        )

    def transform_window(self, window: Window, out_transform: rio.Affine) -> Window:
        """
        Transforms a window using the geopgraphical bounds to generate a new window
        given the Affine transform.

        Arguments:
            window: Original window.
            out_transform: Transformation of the destination dataset.

        Returns:
            The original window transformed into the destination dataset.
        """
        out_window = rio.windows.from_bounds(
            *rio.windows.bounds(window, transform=self.rio_ds.transform),
            transform=out_transform
        ).round_shape("ceil")
        return out_window

    def limit_window_to_raster_bounds(
        self, window: Window, dst_height: int = None, dst_width: int = None
    ) -> Window:
        """
        Make sure the window fits in the dst raster. If not "clips" window to the
        bounds of the raster.
        This method is required because when applying a transform in the Windows
        precision in the Affine transformation can cause inconsistencies on the
        size of the windows in relation to the final output file.

        Arguments:
            window: Original window.
            dst_height: Destination dataset height.
            dst_width: Destination dataset width.

        Returns:
            The original window limited to the destination dataset.
        """
        if dst_height is None:
            dst_height = int(self.rio_ds.height)
        if dst_width is None:
            dst_width = int(self.rio_ds.width)

        window_slices_row, window_slices_col = window.toslices()
        result_row = [int(window_slices_row.start), int(window_slices_row.stop)]
        result_col = [int(window_slices_col.start), int(window_slices_col.stop)]

        if window_slices_row.start < 0:
            result_row[0] = 0
        if window_slices_row.stop > dst_height:
            result_row[1] = dst_height

        if window_slices_col.start < 0:
            result_col[0] = 0
        if window_slices_col.stop > dst_width:
            result_col[1] = dst_width

        return Window.from_slices(result_row, result_col)

    def crop_array_to_window(
        self, buffered_array: np.array, window: Window, window_buffer: Window
    ) -> np.array:
        """
        Crops an array created with the windows_buffered to the extent of
        window. Makes use of the a higher res Affine to "reproject" the original
        window to the extent of window_buffer.

        Arguments:
            buffered_array: Buffered array read with window_buffer.
                Has same shape as buffered window.
            window: Original window.
                Buffered window cropped with a given buffer.
            window_buffer: Buffered window.

        Returns:
            A cropped numpy array.
        """
        buffer_transform = rio.windows.transform(window_buffer, self.rio_ds.transform)
        window_transformed = rio.windows.from_bounds(
            *rio.windows.bounds(window, transform=self.rio_ds.transform),
            transform=buffer_transform
        )

        # row, col
        (
            window_buffer_slices_row,
            window_buffer_slices_col,
        ) = window_transformed.toslices()

        slice_col_start = int(round(window_buffer_slices_col.start))
        slice_row_start = int(round(window_buffer_slices_row.start))

        slice_col_stop = int(round(window_buffer_slices_col.stop))
        slice_row_stop = int(round(window_buffer_slices_row.stop))

        cropped_array = buffered_array[
            :, slice_row_start:slice_row_stop, slice_col_start:slice_col_stop
        ]
        return cropped_array
