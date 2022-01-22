def join(*args, axes=None):
    args = [Tensor(x) for x in args]
    n = args[0].shape[-1]

    e = LeviCivitaTensor(n, False)

    free_indices = list(range(args[0].ndim - 1))

    points = _outer_product(*args, axes=free_indices)
    points = Tensor(points, covariant=range(len(free_indices), len(free_indices) + len(args)))
    diagram = TensorDiagram(*[(points, e)] * len(args))

    return diagram.calculate()


def meet(*args, axes=None):
    args = [Tensor(x) for x in args]

    n = args[0].shape[-1]
    e = LeviCivitaTensor(n)

    x = Tensor(_outer_product(lines1, lines2), covariant=range(lines1.ndim + lines2.ndim - 2 * n + 3))
    free_indices = list(range(1, lines1.ndim + lines2.ndim - 2 * n + 4))

    diagram = TensorDiagram(*[(e, x)] * (n - 2), (e, x))
    points = diagram.calculate().array

    points = points.transpose(free_indices + [0] + list(range(len(free_indices) + 1, points.ndim)))

    if n > 3:
        max_ind = np.abs(points).reshape((np.prod(points.shape[:len(free_indices)]), -1)).argmax(1)
        i = np.unravel_index(max_ind, points.shape[len(free_indices):])
        indices = tuple(x.flatten() for x in np.indices(points.shape[:len(free_indices)]))
        points = points[indices + (slice(None),) + i[1:]].reshape(points.shape[:len(free_indices) + 1])

    return points


def _outer_product(*args, axes=(0,)):

    einsum_args = []
    index_count = len(axes)
    for arr in args:
        einsum_args.append(arr)
        einsum_args.append(list(axes) + list(range(index_count, index_count+arr.ndim-len(axes))))
        index_count += arr.ndim - len(axes)

    result_indices = list(range(index_count))

    return np.einsum(*einsum_args, result_indices)


def _meet_planes_lines(planes, lines):

    n = planes.shape[-1]
    e = LeviCivitaTensor(n)

    x = Tensor(_outer_product(planes, lines), covariant=[0])

    diagram = TensorDiagram((e, x), *[(e, x)]*(n-2))
    return diagram.calculate()