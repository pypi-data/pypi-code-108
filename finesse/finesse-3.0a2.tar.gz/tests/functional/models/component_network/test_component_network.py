"""Test cases for model component network generation."""


def test_component_network_nodes_represent_model_components(network_model_michelson):
    """Test that the nodes of component networks are the model component names."""
    model, network = network_model_michelson
    assert list(network.nodes) == [component.name for component in model.components]


def test_component_network_edges_link_model_components(network_model_michelson):
    """Test that the edges of component networks link components in the network."""
    model, network = network_model_michelson

    component_names = [component.name for component in model.components]

    for u, v in network.edges:
        assert u in component_names
        assert v in component_names


def test_component_network_edges_contain_connector_data(network_model_michelson):
    """Test that the edges of component networks contain related connector object data."""
    model, network = network_model_michelson

    for _, _, data in network.edges(data=True):
        assert "connection" in data
        # Resolve weakref and check the object is in the model's elements.
        assert data["connection"]() in model.elements.values()


def test_component_network_can_handle_cyclic_models(network_model_sagnac):
    """Test that the component network can handle models with cyclic connections."""
    model, network = network_model_sagnac

    assert len(model.components) == len(network.nodes)
