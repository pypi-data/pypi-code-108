from poisson_approval import binary_figure


def test_heatmap_intensity_reverse():
    """
        >>> def f(x, y1, y2):
        ...     return (x**2 + y1) / (y2 + 1)
        >>> figure, tax = binary_figure(xscale=5, yscale=5, size_inches=(6, 4))
        >>> tax.heatmap_intensity(f,
        ...                       x_left_label='x-left',
        ...                       x_right_label='x-right',
        ...                       y_left_label='y-left',
        ...                       y_right_label='y-right',
        ...                       reverse_right=True)
        >>> tax.set_title('An intensity heat map')
    """
    pass


def test_heatmap_candidates_reverse():
    """
        >>> def g(x, y1, y2):
        ...     a = x**.5
        ...     b = y1**2
        ...     c = 1 - a - b
        ...     return [a, b, c]
        >>> figure, tax = binary_figure(xscale=5, yscale=5, size_inches=(6, 4))
        >>> tax.heatmap_candidates(g,
        ...                        x_left_label='x-left',
        ...                        x_right_label='x-right',
        ...                        y_left_label='y-left',
        ...                        y_right_label='y-right',
        ...                        legend_title='Candidates',
        ...                        legend_style='palette',
        ...                        reverse_right=True)
        >>> tax.set_title('A candidate heat map')
    """
    pass
