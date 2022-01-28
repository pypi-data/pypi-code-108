import numpy as np


class ApertureExtractor:
    """
    Used to convert aperture boolean masks into aperture pixel arrays and vice-versa.
    """
    @staticmethod
    def from_boolean_mask(boolean_mask, column, row):
        """
        Returns the aperture pixels coordinates for the given boolean mask.
        @param boolean_mask: the boolean mask centered in the given column and row.
        @param column: the center column of the mask.
        @param row: the center row of the mask.
        @return: the pixels columns and rows in an array.
        """
        boolean_mask = np.transpose(boolean_mask)
        # TODO resize pipeline_mask to match
        pipeline_mask_triceratops = np.zeros((len(boolean_mask), len(boolean_mask[0]), 2))
        for i in range(0, len(boolean_mask)):
            for j in range(0, len(boolean_mask[0])):
                pipeline_mask_triceratops[i, j] = [column + i, row + j]
        pipeline_mask_triceratops[~boolean_mask] = None
        aperture = []
        for i in range(0, len(pipeline_mask_triceratops)):
            for j in range(0, len(pipeline_mask_triceratops[0])):
                if not np.isnan(pipeline_mask_triceratops[i, j]).any():
                    aperture.append(pipeline_mask_triceratops[i, j])
        return aperture

    @staticmethod
    def from_pixels_to_boolean_mask(aperture_pixels, column, row, col_len, row_len):
        """
        Converts an aperture pixels array into a boolean mask of a given size, centered in the given row and column.
        :param aperture_pixels: the aperture given as column-row pairs
        :param column: the center column
        :param row: the center row
        :param col_len: the lenght of the pixel columns
        :param row_len: the length of the pixel rows
        :return: the boolean mask centered in the column and row
        """
        boolean_mask = np.full((row_len, col_len), False)
        for i in range(row, row + row_len):
            for j in range(column, column + col_len):
                if isinstance(aperture_pixels[0], np.ndarray):
                    boolean_mask[i - row][j - column] = any(([j, i] == x).all() for x in aperture_pixels)
                else:
                    boolean_mask[i - row][j - column] = any(([j, i] == x) for x in aperture_pixels)
        return boolean_mask

