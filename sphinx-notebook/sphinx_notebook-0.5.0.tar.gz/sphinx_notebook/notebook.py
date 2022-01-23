"""Main module."""

from itertools import chain

import anytree
import nanoid

NANOID_ALPHABET = '-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
NANOID_SIZE = 10


def _get_title(note):
    """Extract title from note.

    :param note: path not note file
    :type note: class: `pathlib.path`

    :return: Note title
    :rrtype: str
    """
    title = note.stem

    with note.open(encoding="utf-8") as fd_in:
        found_line = False

        for line in fd_in.readlines():
            if "=======" in line:  # pylint: disable=no-else-continue
                found_line = True
                continue

            elif found_line:
                title = line.strip()
                break

    return title


def get_target():
    """Create a random target ID.

    :return: target id
    :rrtype: str
    """
    return nanoid.generate(NANOID_ALPHABET, NANOID_SIZE)


def get_tree(root_dir):
    """Get a tree of notes.

    :param root_dir: The root directory of the notebook
    :type root_dir: class: `pathlib.Path`

    :return: Tree root node
    :rtype: class: anytree.Node
    """
    # print(root_dir)
    # build/notes/rst
    nodes = {root_dir.name: anytree.Node(root_dir.name)}

    for note in sorted(root_dir.glob('**/*.rst')):

        tmp = note.relative_to(root_dir)
        target = f'/{tmp.parent}/{tmp.stem}'  # /1._overview/0_readme

        parts = []

        for part in chain([root_dir.name], tmp.parts[:-1]):
            parts.append(part)

            if '/'.join(parts) not in nodes:
                parent = nodes['/'.join(parts[:-1])]
                nodes['/'.join(parts)] = anytree.Node(part, parent=parent)

        anytree.Node(note.name,
                     parent=nodes['/'.join(parts)],
                     title=_get_title(note),
                     target=target)

    return nodes[root_dir.name]


def prune_tree(root, prune):
    """Prune nodes that shouldn't be rendered on the index page.

    :param root: Root node of the notes tree
    :type root: anytree.Node

    :param prune: An tuple of node names to be pruned
    :type prune: tuple

    :return: None
    """
    for node in anytree.search.findall(
            root, filter_=lambda node: node.name in prune):
        node.parent = None


def render_index(root, template, out):
    """Render notebook tree into index.rst.

    :param root: notebook tree root node
    :type root: class: anytree.Node

    :param template: A jinja2 template
    :type template: class: Jinja2.Template

    :param fd_out: Open file like object.
    :type fd_out: File Like Object

    :return: None
    """
    nodes = [node for node in anytree.PreOrderIter(root) if node.depth]
    out.write(template.render(nodes=nodes))


def render_note(template, out):
    """Render a note.

    :param template: A jinja2 template
    :type template: class: Jinja2.Template

    :param out: Open file like object.
    :type out: File Like Object

    :return: None
    """
    note_id = get_target()
    out.write(template.render(note_id=note_id))
