import pandas as pd
import pytest

from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.cadata.CableDatabase import CableDatabase
import magnumapi.commons.json_file as json_file
from tests.resource_files import create_resources_path


def test_to_dict():
    # arrange
    json_path = create_resources_path('resources/geometry/roxie/16T/16T_rel.json')
    cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    cadata = CableDatabase.read_cadata(cadata_path)

    # act
    geometry = GeometryFactory.init_with_json(json_path, cadata)
    geometry.build_blocks()
    block_layer_defs = geometry.to_abs_geometry().to_dict()

    # assert
    json_ref_path = create_resources_path('resources/geometry/roxie/16T/16T_abs.json')
    block_layer_ref_defs = json_file.read(json_ref_path)

    pd.testing.assert_frame_equal(pd.DataFrame(block_layer_ref_defs['block_defs']).sort_index(axis=1),
                                  pd.DataFrame(block_layer_defs['block_defs']).sort_index(axis=1))

    pd.testing.assert_frame_equal(pd.DataFrame(block_layer_ref_defs['layer_defs']),
                                  pd.DataFrame(block_layer_defs['layer_defs']))


def test_to_abs_geometry():
    # arrange
    json_path = create_resources_path('resources/geometry/roxie/16T/16T_rel.json')
    cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    cadata = CableDatabase.read_cadata(cadata_path)

    # act
    geometry = GeometryFactory.init_with_json(json_path, cadata)
    geometry = geometry.to_abs_geometry()
    block_layer_defs = geometry.to_dict()

    # assert
    json_ref_path = create_resources_path('resources/geometry/roxie/16T/16T_abs.json')
    block_layer_ref_defs = json_file.read(json_ref_path)

    pd.testing.assert_frame_equal(pd.DataFrame(block_layer_ref_defs['block_defs']).sort_index(axis=1),
                                  pd.DataFrame(block_layer_defs['block_defs']).sort_index(axis=1))

    pd.testing.assert_frame_equal(pd.DataFrame(block_layer_ref_defs['layer_defs']),
                                  pd.DataFrame(block_layer_defs['layer_defs']))


def test_to_rel_dict():
    # arrange
    json_path = create_resources_path('resources/geometry/roxie/16T/16T_abs.json')
    cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    cadata = CableDatabase.read_cadata(cadata_path)

    # act
    geometry = GeometryFactory.init_with_json(json_path, cadata)
    geometry.build_blocks()
    block_layer_defs = geometry.to_rel_geometry().to_dict()

    # assert
    json_ref_path = create_resources_path('resources/geometry/roxie/16T/16T_rel.json')
    block_layer_ref_defs = json_file.read(json_ref_path)

    pd.testing.assert_frame_equal(pd.DataFrame(block_layer_ref_defs['block_defs']).sort_index(axis=1),
                                  pd.DataFrame(block_layer_defs['block_defs']).sort_index(axis=1))

    pd.testing.assert_frame_equal(pd.DataFrame(block_layer_ref_defs['layer_defs']),
                                  pd.DataFrame(block_layer_defs['layer_defs']))


def test_consistency_check_block_numbering_duplicates():
    # arrange
    block_layer_defs = {
        "block_defs": [
            {"no": 1, "radius": 25.0, "alpha": 0, "phi": 0.57294, "nco": 4, "type": 1, "current": 13500,
             "condname": "16TIL9", "n1": 2, "n2": 20, "imag": 0, "turn": 0},
            {"no": 1, "radius": 25.0, "alpha": 26, "phi": 23, "nco": 5, "type": 1, "current": 13500,
             "condname": "16TIL9", "n1": 2, "n2": 20, "imag": 0, "turn": 0}],
        "layer_defs": [{"no": 1, "symm": 1, "typexy": 1, "blocks": [1, 2, 3, 4]}]}
    cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    cadata = CableDatabase.read_cadata(cadata_path)

    # act
    # assert
    with pytest.raises(AttributeError) as excinfo:
        GeometryFactory.init_with_dict(block_layer_defs['block_defs'],
                                       block_layer_defs['layer_defs'],
                                       cadata)

    assert "The block numbering ([1, 1]) contains duplications!" in str(excinfo.value)


def test_consistency_check_layer_numbering_duplicates():
    # arrange
    block_layer_defs = {
        "block_defs": [
            {"no": 1, "radius": 25.0, "alpha": 0, "phi": 0.57294, "nco": 4, "type": 1, "current": 13500,
             "condname": "16TIL9", "n1": 2, "n2": 20, "imag": 0, "turn": 0},
            {"no": 2, "radius": 25.0, "alpha": 26, "phi": 23, "nco": 5, "type": 1, "current": 13500,
             "condname": "16TIL9", "n1": 2, "n2": 20, "imag": 0, "turn": 0}],
        "layer_defs": [{"no": 1, "symm": 1, "typexy": 1, "blocks": [1, 2]},
                       {"no": 1, "symm": 1, "typexy": 1, "blocks": [1, 2]}]}
    cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    cadata = CableDatabase.read_cadata(cadata_path)

    # act
    # assert
    with pytest.raises(AttributeError) as excinfo:
        GeometryFactory.init_with_dict(block_layer_defs['block_defs'],
                                       block_layer_defs['layer_defs'],
                                       cadata)

    assert "The layer numbering ([1, 1]) contains duplications!" in str(excinfo.value)


def test_consistency_check_block_layer_numbering_duplicates():
    # arrange
    block_layer_defs = {
        "block_defs": [
            {"no": 1, "radius": 25.0, "alpha": 0, "phi": 0.57294, "nco": 4, "type": 1, "current": 13500,
             "condname": "16TIL9", "n1": 2, "n2": 20, "imag": 0, "turn": 0},
            {"no": 2, "radius": 25.0, "alpha": 26, "phi": 23, "nco": 5, "type": 1, "current": 13500,
             "condname": "16TIL9", "n1": 2, "n2": 20, "imag": 0, "turn": 0}],
        "layer_defs": [{"no": 1, "symm": 1, "typexy": 1, "blocks": [1, 2]},
                       {"no": 2, "symm": 1, "typexy": 1, "blocks": [1, 2]}]}
    cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    cadata = CableDatabase.read_cadata(cadata_path)

    # act
    # assert
    with pytest.raises(AttributeError) as excinfo:
        GeometryFactory.init_with_dict(block_layer_defs['block_defs'],
                                       block_layer_defs['layer_defs'],
                                       cadata)

    assert "The layer numbering of blocks ([1, 2, 1, 2]) contains duplications!" in str(excinfo.value)


def test_consistency_check_block_and_block_layer_numbering_duplicates():
    # arrange
    block_layer_defs = {
        "block_defs": [
            {"no": 1, "radius": 25.0, "alpha": 0, "phi": 0.57294, "nco": 4, "type": 1, "current": 13500,
             "condname": "16TIL9", "n1": 2, "n2": 20, "imag": 0, "turn": 0},
            {"no": 2, "radius": 25.0, "alpha": 26, "phi": 23, "nco": 5, "type": 1, "current": 13500,
             "condname": "16TIL9", "n1": 2, "n2": 20, "imag": 0, "turn": 0}],
        "layer_defs": [{"no": 1, "symm": 1, "typexy": 1, "blocks": [1, 2]},
                       {"no": 2, "symm": 1, "typexy": 1, "blocks": [3]}]}
    cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    cadata = CableDatabase.read_cadata(cadata_path)

    # act
    # assert
    with pytest.raises(AttributeError) as excinfo:
        GeometryFactory.init_with_dict(block_layer_defs['block_defs'],
                                       block_layer_defs['layer_defs'],
                                       cadata)

    assert "The numbering in block [1, 2] and layer [1, 2, 3] do not match!" in str(excinfo.value)


def test_to_roxie_layer_df():
    # arrange
    json_path = create_resources_path('resources/geometry/roxie/16T/16T_rel.json')
    cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    cadata = CableDatabase.read_cadata(cadata_path)

    # act
    geometry = GeometryFactory.init_with_json(json_path, cadata)
    geometry.build_blocks()

    df = geometry.to_layer_df()

    # assert
    df_ref = pd.DataFrame({'no': {0: 1, 1: 2, 2: 3, 3: 4},
                           'symm': {0: 1, 1: 1, 2: 1, 3: 1},
                           'typexy': {0: 1, 1: 1, 2: 1, 3: 1},
                           'blocks': {0: '1 2 3 4', 1: '5 6 7', 2: '8 9 10', 3: '11 12'}})
    # print(RoxieAPI.convert_bottom_header_table_to_str(df, keyword='LAYER', suffix=' /'))

    pd.testing.assert_frame_equal(df_ref, df)
