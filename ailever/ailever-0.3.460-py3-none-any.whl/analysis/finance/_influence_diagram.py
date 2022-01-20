import plotly.graph_objects as go

def InfluenceDiagram(labels, source, target, value, title="Influence Diagram", returnTrue=False):
    r"""
    Examples:
        >>> labels = {0 : 'Loan',
        >>>           1 : 'Capital',
        >>>           2 : 'Repay',
        >>>           3 : 'DSRA',
        >>>           4 : 'Net Income',
        >>>           5 : 'Working Capital',
        >>>           6 : 'Depreciation',
        >>>           7 : 'Inintial Working Captial',
        >>>           8 : 'Initial DSRA',
        >>>           9 : 'CAPEX', 
        >>>           10 : 'Development Expense',
        >>>           11 : 'Cash Flow for Finance',
        >>>           12 : 'Cash Flow for Business',
        >>>           13 : 'Cash Flow for Investment',
        >>>           14 : 'Cash Flow'}
        >>> 
        >>> source = [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13]
        >>> target = [11, 11, 11, 11, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14]
        >>> value  = [ 1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  4,  3,  4]
    """

    fig = go.Figure(go.Sankey(
        arrangement = "snap",
        node=dict(label=list(labels.values())),
        link = {
            "source": source,
            "target": target,
            "value":  value}))

    fig.update_layout(title_text=title, font_size=10)
    fig.show()

    if returnTrue:
        return fig

