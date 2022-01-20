from sortedcontainers import SortedListWithKey


def shamos_hoey(edges):
    """Determine if a polyline is self intersecting.

    Args:
        edges:

    Returns:

    """
    POINT, EDGE, IDX, SIDE = 0, 1, 2, 3
    LEFT, RIGHT = -1, 1
    event_queue = SortedListWithKey(key=lambda event: event[POINT]._coords)
    for (idx, edge) in enumerate(edges):
        p_left, p_right = edge.ordered()
        e_left, e_right = (p_left, edge, idx, LEFT), (p_right, edge, idx, RIGHT)
        event_queue.add(e_left)
        event_queue.add(e_right)

    count = len(event_queue) / 2

    sweep_line = SortedListWithKey(
        key=lambda event: tuple(p._coords for p in event[EDGE].ordered())
    )

    def consecutive(e1, e2):
        distance = abs(e1[IDX] - e2[IDX])
        if 1 < distance < count - 1:
            return False
        return True

    while event_queue:
        event = event_queue.pop(0)
        if event[SIDE] == LEFT:
            sweep_line.add(event)
            idx = sweep_line.index(event)
            if idx + 1 < len(sweep_line):
                above = sweep_line[idx + 1]
                if not consecutive(event, above):
                    if event[EDGE].does_intersect(above[EDGE]):
                        return False
            if idx > 0:
                below = sweep_line[idx - 1]
                if not consecutive(event, below) and event[EDGE].does_intersect(
                    below[EDGE]
                ):
                    return False
        else:
            idx = sweep_line.bisect_left(event)
            if 0 < idx < len(sweep_line) - 1:
                above = sweep_line[idx]
                below = sweep_line[idx - 1]
                if not consecutive(above, below) and above[EDGE].does_intersect(
                    below[EDGE]
                ):
                    return False
            sweep_line.pop(idx)

    return True
