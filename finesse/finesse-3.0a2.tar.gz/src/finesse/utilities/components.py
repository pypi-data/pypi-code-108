"""Utility functions related to component objects."""
import os


def refractive_index(port, symbolic=False):
    """Obtains the refractive index of the space attached to the port/node `port`.

    Parameters
    ----------
    port : :class:`.Port` or :class:`.Node`
        Port or node.

    Returns
    -------
    nr : float
        The refractive index of the space attached to the port / node.
        Returns unity if no space is present.
    """
    get_nr = lambda space, symbol: space.nr.ref if symbol else space.nr.eval()

    space = port.space
    if space is not None:
        nr = get_nr(space, symbolic)
    else:
        from finesse.components import Beamsplitter

        # If we're at a beamsplitter then get nr
        # of port on same surface
        if isinstance(port.component, Beamsplitter):
            adj_port = port.component.get_adjacent_port(port)
            space = adj_port.space
            if space is None:
                # FIXME (sjr) This should probably raise an exception but parsing
                #             (at least for legacy files) means that both spaces
                #             can be None initially somehow when symbolising
                #             Beamsplitter ABCD matrices
                nr = 1
            else:
                nr = get_nr(space, symbolic)
        else:
            nr = 1

    return nr


def names_to_nodes(model, names, default_hints=()):
    """Attempts to convert a list of node/dof/ports into nodes. This is to provide a way
    for actions to convert string names into nodes for simulation use. It attempts to
    provide useful default behaviours, and can accept "hints" on how to select nodes.

    Parameters
    ----------
    names : iterable[str|(str, iterable[str])]
        A collection of names to convert. A (name, hint) pair can also be provided
        where hint is an iterable of strings.

    default_hints : iterable[str]
        Default hint to use with particular set of names if no hints are provided.

    Notes
    -----
    Posible hints when name is a Port or DOF:
    - `input` : try and select a singular input node
    - `output` : try and select a singular output node

    Examples
    --------
    Selecting various nodes from a model with and without hinting:

        >>> import finesse
        >>> from finesse.utilities.components import names_to_nodes
        >>> model = finesse.Model()
        >>> model.parse('''
        ... l l1 P=100k
        ... mod mod1 f=10M midx=0.1 order=1 mod_type=pm
        ... m m1 R=1-&m1.T T=0.014 Rc=-1984 xbeta=0n
        ... m m2 R=1 T=0 Rc=2245 xbeta=0n phi=0
        ... link(l1, mod1, m1, 3994, m2)
        ... dof DARM m1.dofs.z -1 m2.dofs.z +1
        ... ''')
        >>> names_to_nodes(model, ('m1.p1', 'DARM.AC'), default_hints=('output'))
        [<OpticalNode m1.p1.o @ 0x7f92c9a5c880>,
         <SignalNode DARM.AC.o @ 0x7f92c9a0e5b0>]
        >>> names_to_nodes(model, ('m1.p1', 'DARM.AC'), default_hints=('input'))
        [<OpticalNode m1.p1.i @ 0x7f92c9a5ca60>,
         <SignalNode DARM.AC.i @ 0x7f92c9a0e460>]
        >>> names_to_nodes(model, ('m1.p1.o', 'DARM.AC.i'))
        [<OpticalNode m1.p1.o @ 0x7f92c9a5c880>,
         <SignalNode DARM.AC.i @ 0x7f92c9a0e460>]

    Hints do not insist on a particular output. For example, this is valid:

        >>> names_to_nodes(model, ('m1.p1.o', ('DARM.AC.o', "input")))
    """
    from finesse.components import Port, Node, DegreeOfFreedom

    rtn = []
    for name in names:
        # Actions can provide hints on how to select nodes
        try:
            name, hints = name
        except Exception:
            hints = default_hints

        obj = model.get(name)
        is_port = isinstance(obj, Port)
        is_node = isinstance(obj, Node)
        is_dof = isinstance(obj, DegreeOfFreedom)

        # Grab the AC port by default for DOFs
        if is_dof:
            obj = obj.AC
            is_port = True
            is_dof = False

        if is_port:
            N = len(obj.nodes)
            if N == 1:
                # select only single node from port
                obj = obj.nodes[0]
            elif "input" in hints:
                is_input_node = tuple(_.is_input for _ in obj.nodes)
                if is_input_node.count(True) == 1:
                    idx = is_input_node.index(True)
                    obj = obj.nodes[idx]
                else:
                    raise ValueError(
                        f"Port {repr(obj)} does not have a single input node so you must specify which to use. It has \n{ os.linesep.join((repr(_) for _ in obj.nodes)) }"
                    )
            elif "output" in hints:
                is_output_node = tuple(not _.is_input for _ in obj.nodes)
                if is_output_node.count(True) == 1:
                    idx = is_output_node.index(True)
                    obj = obj.nodes[idx]
                else:
                    raise ValueError(
                        f"Port {repr(obj)} does not have a single output node so you must specify which to use. It has \n{ os.linesep.join((repr(_) for _ in obj.nodes)) }"
                    )
            else:
                raise ValueError(
                    f"Port {repr(obj)} does not have a single node to select from, so you must specify which to use. It has: \n{ os.linesep.join((repr(_) for _ in obj.nodes)) }"
                )
        elif not (is_node or is_port):
            raise ValueError(f"Value {repr(obj)} was neither a Port nor a Node")

        rtn.append(obj)
    return rtn
