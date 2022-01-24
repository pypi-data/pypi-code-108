import pytest

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.tiling_dataset_element import Tile, TilingDatasetElement
from azureml.automl.dnn.vision.common.tiling_utils import validate_tiling_settings, get_tiles


class TestTile:
    def test_init(self):
        tile = Tile((0, 0, 300, 200))
        assert tile.as_tuple() == (0, 0, 300, 200)
        assert tile.top_left_x == 0
        assert tile.top_left_y == 0
        assert tile.bottom_right_x == 300
        assert tile.bottom_right_y == 200

    def test_equal(self):
        # The assert a == b calls __eq__ with self = a and other = b.
        # The assert b == a calls __eq__ with self = b and other = a.
        a = Tile((0, 0, 300, 200))
        b = None
        assert a != b
        assert b != a

        a = Tile((0, 0, 300, 200))
        b = Tile((0, 0, 300, 400))
        assert a != b
        assert b != a

        a = Tile((0, 0, 300, 200))
        b = Tile((0, 0, 300, 200))
        assert a == b
        assert b == a

    def test_less_than(self):
        # All the tests in this function have a <= b.
        # The assert a < b calls __lt__ with self = a and other = b. Hence, it verifies cases when self <= other
        # The assert b < a calls __lt__ with self = b and other = a. Hence, it verifies cases when self >= other
        a = Tile((0, 0, 300, 200))
        b = Tile((0, 0, 300, 200))
        assert not a < b
        assert not b < a

        a = Tile((0, 0, 300, 100))
        b = Tile((0, 0, 300, 200))
        assert a < b
        assert not b < a

    def test_hash(self):
        a = Tile((0, 0, 300, 200))
        b = Tile((0, 0, 300, 200))
        assert hash(a) == hash(b)

    def test_common_uses(self):
        a = Tile((0, 0, 300, 100))
        b = Tile((0, 0, 300, 200))

        # As keys in dictionary
        sample_dict = {a: "a", b: "b"}
        assert sample_dict[a] == "a"
        assert sample_dict[b] == "b"

        # In sets
        tile_set = set([a, b])
        assert a in tile_set
        assert b in tile_set

        # can be sorted
        tile_sorted = sorted(tile_set)
        assert tile_sorted[0] == a
        assert tile_sorted[1] == b


class TestTilingDatasetElement:
    def test_init(self):
        element = TilingDatasetElement("1.jpg", None)
        assert element.image_url == "1.jpg"
        assert element.tile is None

        element = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        assert element.image_url == "1.jpg"
        assert element.tile == Tile((0, 0, 300, 200))

    def test_equal(self):
        # The assert a == b calls __eq__ with self = a and other = b.
        # The assert b == a calls __eq__ with self = b and other = a.
        a = TilingDatasetElement("1.jpg", None)
        b = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        assert a != b
        assert b != a

        a = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        b = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 400)))
        assert a != b
        assert b != a

        a = TilingDatasetElement("1.jpg", None)
        b = TilingDatasetElement("2.jpg", None)
        assert a != b
        assert b != a

        a = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        b = TilingDatasetElement("2.jpg", Tile((0, 0, 300, 200)))
        assert a != b
        assert b != a

        a = TilingDatasetElement("1.jpg", None)
        b = TilingDatasetElement("1.jpg", None)
        assert a == b
        assert b == a

        a = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        b = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        assert a == b
        assert b == a

    def test_less_than(self):
        # All the tests in this function have a <= b.
        # The assert a < b calls __lt__ with self = a and other = b. Hence, it verifies cases when self <= other
        # The assert b < a calls __lt__ with self = b and other = a. Hence, it verifies cases when self >= other
        a = TilingDatasetElement("1.jpg", None)
        b = TilingDatasetElement("2.jpg", None)
        assert a < b
        assert not b < a

        a = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        b = TilingDatasetElement("2.jpg", Tile((0, 0, 300, 200)))
        assert a < b
        assert not b < a

        a = TilingDatasetElement("1.jpg", None)
        b = TilingDatasetElement("1.jpg", None)
        assert not a < b
        assert not b < a

        a = TilingDatasetElement("1.jpg", None)
        b = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        assert a < b
        assert not b < a

        a = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 100)))
        b = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        assert a < b
        assert not b < a

        a = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        b = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        assert not a < b
        assert not b < a

    def test_hash(self):
        a = TilingDatasetElement("1.jpg", None)
        b = TilingDatasetElement("1.jpg", None)
        assert hash(a) == hash(b)

        a = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        b = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))
        assert hash(a) == hash(b)

    def test_common_uses(self):
        a = TilingDatasetElement("1.jpg", None)
        b = TilingDatasetElement("1.jpg", Tile((0, 0, 300, 200)))

        # As keys in dictionary
        sample_dict = {a: "a", b: "b"}
        assert sample_dict[a] == "a"
        assert sample_dict[b] == "b"

        # In sets
        tile_set = set([a, b])
        assert a in tile_set
        assert b in tile_set

        # can be sorted
        tile_sorted = sorted(tile_set)
        assert tile_sorted[0] == a
        assert tile_sorted[1] == b


class TestTilingUtils:

    def test_validate_tiling_settings(self):
        validate_tiling_settings(None, None)

        validate_tiling_settings(None, 0.5)

        invalid_setting_combinations = [
            ("not a list", 0.5),
            ((3, 2, 3), 0.5),
            ((3.0, 2.0), 0.5),
            ((-1, -2), 0.5),
            ((0, 2), 0.5),
            ((1, 1), 0.5),
            ((3, 2), "not a float"),
            ((3, 2), -0.25),
            ((3, 2), 1.0),
            ((3, 2), 1.5)
        ]

        for setting in invalid_setting_combinations:
            with pytest.raises(AutoMLVisionValidationException):
                validate_tiling_settings(setting[0], setting[1])

        validate_tiling_settings((3, 2), 0.5)

    def test_get_tiles(self):

        def _test(image_size, tile_grid_size, tile_overlap_ratio):
            # This is copied from get_tiles function
            tile_width = image_size[0] / (tile_grid_size[0] * (1 - tile_overlap_ratio) + tile_overlap_ratio)
            tile_height = image_size[1] / (tile_grid_size[1] * (1 - tile_overlap_ratio) + tile_overlap_ratio)

            result = get_tiles(tile_grid_size, tile_overlap_ratio, image_size)

            expected_result = []
            x = 0.0
            for i in range(tile_grid_size[0]):
                y = 0.0
                for j in range(tile_grid_size[1]):
                    expected_result.append((round(x), round(y), round(x + tile_width), round(y + tile_height)))
                    y += (1 - tile_overlap_ratio) * tile_height
                x += (1 - tile_overlap_ratio) * tile_width

            # Tiles should cover the entire image
            assert result[-1].bottom_right_x == image_size[0]
            assert result[-1].bottom_right_y == image_size[1]

            assert len(result) == len(expected_result)
            for i in range(len(result)):
                assert result[i].as_tuple() == expected_result[i]

        image_sizes = [(640, 480), (1080, 1080), (1280, 720), (1920, 1080)]
        tile_grid_sizes = [(2, 1), (1, 2), (3, 2), (2, 3), (4, 3), (3, 4)]
        tile_overlap_ratios = [0.0, 0.25, 0.5, 0.75]
        for image_size in image_sizes:
            for tile_grid_size in tile_grid_sizes:
                for tile_overlap_ratio in tile_overlap_ratios:
                    _test(image_size, tile_grid_size, tile_overlap_ratio)
