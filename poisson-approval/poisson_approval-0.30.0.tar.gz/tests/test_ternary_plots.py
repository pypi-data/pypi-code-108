import pytest
from poisson_approval import ternary_figure


def test():
    """
        >>> def f(right, top, left):
        ...     return (right**2 + top) / (left + 1)
        >>> figure, tax = ternary_figure(scale=10, size_inches=(6, 4))
        >>> tax.heatmap_intensity(f,
        ...                       left_label='left',
        ...                       right_label='right',
        ...                       top_label='top',
        ...                       cb_kwargs={})
        >>> tax.set_title_padded('An intensity heat map')
    """
    pass


def test_save_data():
    """
        >>> def g(right, top, left):
        ...     a = top**.5
        ...     b = left**2
        ...     c = 1 - a - b
        ...     return [a, b, c]
        >>> figure, tax = ternary_figure(scale=5)
        >>> tax.heatmap_candidates(g,
        ...                        left_label='left',
        ...                        right_label='right',
        ...                        top_label='top',
        ...                        legend_title='Candidates',
        ...                        legend_style='palette',
        ...                        file_save_data='zzz_test_ternary_plots.sav')
        >>> tax.set_title_padded('A candidate heat map')
    """
    pass


def test_f_point_values_():
    with pytest.raises(ValueError):
        figure, tax = ternary_figure(scale=5)
        tax.f_point_values_(right=0.5, top=0.3, left=0.2)


def test_annotate_condorcet_old():
    figure, tax = ternary_figure(scale=5)
    with pytest.raises(NotImplementedError):
        tax._annotate_condorcet_old(right_ranking='abc', left_ranking='bac', top_ranking='cab',
                                    d_order_fixed_share={'cba': 0.2})
    # Same top
    tax._annotate_condorcet_old(right_ranking='abc', left_ranking='abc', top_ranking='acb')
    # Two different tops
    tax._annotate_condorcet_old(right_ranking='abc', left_ranking='acb', top_ranking='bac')
    tax._annotate_condorcet_old(right_ranking='abc', left_ranking='bac', top_ranking='acb')
    tax._annotate_condorcet_old(right_ranking='bac', left_ranking='abc', top_ranking='acb')
    # Three different tops
    # Sub-case: Three different bottoms (Condorcet cycle)
    tax._annotate_condorcet_old(right_ranking='abc', left_ranking='bca', top_ranking='cab')
    # Sub-case: Two different bottoms (divided majority)
    tax._annotate_condorcet_old(right_ranking='abc', left_ranking='bac', top_ranking='cab')
    tax._annotate_condorcet_old(right_ranking='bac', left_ranking='abc', top_ranking='cab')
    tax._annotate_condorcet_old(right_ranking='bac', left_ranking='cab', top_ranking='abc')
