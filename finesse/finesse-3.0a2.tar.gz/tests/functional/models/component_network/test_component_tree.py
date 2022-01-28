"""Test cases for model component tree generation."""


def test_component_tree_contains_network_nodes(network_model_michelson):
    """Test that all branches of the tree contain network nodes, regardless of starting node."""
    model, network = network_model_michelson

    for start in (model.L0, model.BS, model.IMX, model.IMY, model.EMX, model.EMY):
        tree = model.component_tree(start)
        assert set([child.name for child in tree.get_all_children()]).issubset(
            set(network.nodes)
        )


def test_component_tree_flattens_cyclic_network(network_model_sagnac):
    """Test that component tree contains a flattened, acyclic version of a cyclic component \
    network.

    Note: cyclic networks are handled by :meth:`networkx.dfs_tree`, so
    :meth:`.TreeNode.from_network` does not need to detect and avoid such cycles.
    """
    model, _ = network_model_sagnac

    for start in (model.L0, model.BS, model.M1, model.M2, model.M3):
        tree = model.component_tree(start)
        assert len(tree.get_all_children()) + 1 == len(model.components)
