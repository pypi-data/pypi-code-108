from typing import Sequence


def copy_tree(tree):
    tree_copy = []
    queue = [(tree, tree_copy)]

    while queue:
        source_node, destination_node = queue.pop(0)

        for source_child in source_node:
            if isinstance(source_child, Sequence):
                new_node = []
                destination_node.append(new_node)
                queue.append((source_child, new_node))
            else:
                destination_node.append(source_child)

    return tree_copy


def zip_tree(*trees):
    tree_new = []
    queue = [(trees, tree_new)]

    while queue:
        source_nodes, destination_node = queue.pop(0)

        for source_children in zip(*source_nodes):
            if isinstance(source_children[0], Sequence):
                new_node = []
                destination_node.append(new_node)
                queue.append((source_children, new_node))
            else:
                destination_node.append(source_children)

    return tree_new


def flatten_tree(data, paths):
    data_flat = []

    for path in paths:
        node = data

        path = [path] if isinstance(path, int) else path

        for index in path:
            node = node[index]

        data_flat.append(node)

    return data_flat


def unflatten_tree(tree, data_flat, paths):
    new_tree = copy_tree(tree)

    for datum, path in zip(data_flat, paths):
        node = new_tree

        path = [path] if isinstance(path, int) else path

        for index in path[:-1]:
            node = node[index]

        node[path[-1]] = datum

    return new_tree


def map_tree(function, *trees):
    new_tree = zip_tree(*trees)

    queue = [new_tree]

    while queue:
        node = queue.pop(0)

        for index, child in enumerate(node):
            if isinstance(child, list):
                queue.append(child)
            else:
                arguments = child if isinstance(child, tuple) else tuple(child)
                node[index] = function(*arguments)

    return new_tree


def select_tree(tree, mask):
    tree_copy = []

    forward_stack = [(tree, mask, tree_copy)]
    backward_stack = []

    while forward_stack:
        source_node, mask_node, destination_node = forward_stack.pop()

        for source_child, mask_child in zip(source_node, mask_node):
            if isinstance(source_child, Sequence):
                new_node = []
                forward_stack.append((source_child, mask_child, new_node))
                backward_stack.append((new_node, destination_node))
            elif mask_child:
                backward_stack.append((source_child, destination_node))

    while backward_stack:
        child, parent = backward_stack.pop()

        if child:
            parent.insert(0, child)

    return tree_copy


def map_tree_subset(function, data, paths):
    leaves = flatten_tree(data, paths)
    results = function(leaves)
    output = unflatten_tree(data, results, paths)

    return output
