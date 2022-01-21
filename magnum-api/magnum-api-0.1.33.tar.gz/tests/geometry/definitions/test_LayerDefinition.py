from magnumapi.geometry.definitions.LayerDefinition import LayerDefinition


def test_layer_definition():
    # arrange
    layer_def = LayerDefinition(no=1, symm=1, typexy=1, blocks=[1, 2, 3, 4])

    # act
    dct = layer_def.to_roxie_dict()

    # assert
    assert dict(no=1, symm=1, typexy=1, blocks='1 2 3 4') == dct
