import pytest
import pathlib
import os
import math
import pandas as pd
import tempfile
import shutil
from typing import Iterable

from arthurai.core.data_service import DatasetService
from arthurai.core import util


IMAGE_COL_NAME = 'image'
EXTRA_COL_NAME = 'extra'  # dummy column, ensure we aren't loosing columns

IMAGE_PATH = os.path.join(pathlib.Path(__file__).parent.absolute(), "data", "test_image.png")
IMAGE_SIZE = os.path.getsize(IMAGE_PATH)

# (chunk size, file sizes)
chunk_image_set_cases = [pytest.param(3_000, [4_000], id="single-file"),
                         pytest.param(3_000, [400 for _ in range(10)], id="ten-files"),
                         pytest.param(3_000, [3_600, 400], id="diff-sized-files")]


@pytest.mark.parametrize("chunk_size, file_sizes", chunk_image_set_cases)
def test_chunk_parquet_image_set(chunk_size: int, file_sizes: Iterable[int]):
    image_counts_by_file = [math.ceil(target_size / IMAGE_SIZE) for target_size in file_sizes]
    # create temporary directory to generate input files in, with auto-cleanup
    with tempfile.TemporaryDirectory() as source_directory:
        # create the input files
        for i in range(len(image_counts_by_file)):
            # generate the image column data
            num_images = image_counts_by_file[i]
            image_col_data = [IMAGE_PATH for _ in range(num_images)]
            df = pd.DataFrame({IMAGE_COL_NAME: image_col_data, EXTRA_COL_NAME: 1})
            # and write it to parquet
            df.to_parquet(os.path.join(source_directory, f'test-{i}.parquet'))

        # chunk the input files
        output_directory = DatasetService.chunk_parquet_image_set(source_directory, IMAGE_COL_NAME,
                                                                  max_image_data_bytes=chunk_size)

        # validate no data loss in chunked files
        chunked_files = util.retrieve_parquet_files(output_directory)
        total_chunked_images = 0
        for chunked_file in chunked_files:
            df = pd.read_parquet(chunked_file)
            total_chunked_images += len(df)

            # don't lose columns
            assert EXTRA_COL_NAME in df

            # image chunk can be at most image_size + ~chunk_size, we check size after adding file
            cur_chunk_size = len(df) * IMAGE_SIZE
            assert cur_chunk_size - chunk_size <= IMAGE_SIZE
        assert total_chunked_images == sum(image_counts_by_file)

        # cleanup output directory created by the chunking function
        shutil.rmtree(output_directory)
