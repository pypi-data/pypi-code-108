import plotly.graph_objects as go
import pandas as pd
import numpy as np


def visualize(LEVELs, title=title, returnTrue=False):
    r"""
    Example:
        >>> from ailever.utils import VISUAL
        >>> ...
        >>> LEVELs = {'L1':[[1,1,3,1,1],['T00','T01','T02','T03','T04']],
        >>>           'L2':[[3,4,5,1,0],['T10','T11','T12','T13','T14']],
        >>>           'L3':[[3,1,3,0,0],['T20','T21','T22','T23','T24']],
        >>>           }
        >>> VISUAL.hbar(LEVELs, title='TITLE', returnTrue=False)

    """

    Levels = dict()
    Texts = list()
    
    for level, value in LEVELs.items():
        Levels[level] = value[0]
        Texts.append(value[1])

    Levels_df = pd.DataFrame(Levels)
    Levels = Levels_df.loc[:, Levels_df.columns[::-1]].to_dict()
    Texts = Texts[::-1]

    df = pd.DataFrame(Levels)
    index = list()
    for idx in range(df.shape[0]):
        index.append('D'+str(idx))

    df.index = index
    for level_idx, col in enumerate(df.values.T):
        col = col/col.sum()
        df.iloc[:, level_idx] = col

    _df = np.cumsum(df)
    _X = [0]*df.shape[1]

    fig = go.Figure()
    annotations = list()
    for D, (S_row, _S_row) in enumerate(zip(df.iloc, _df.iloc)):
        fig.add_trace(go.Bar(
            y=df.columns,
            x=S_row.values,
            name=S_row.name,
            orientation='h',
            marker=dict(
                color=f'rgba(200, 200, 200, 0.6)',
                line=dict(color='rgba(255, 255, 255, 1.0)', width=3)
            )
        ))
        for L, x in enumerate(_S_row):
            if S_row[L] != 0:
                X = _X[L] + (x - _X[L])/2
                annotations.append(dict(
                                        x=X, y=L,
                                        text=Texts[L][D],
                                        font=dict(family='Arial', size=14,
                                                color='rgb(67, 67, 67)'),
                                        showarrow=False))
                _X[L] = x

    fig.update_layout(title_text=title, showlegend=False)
    fig.update_layout(barmode='stack', annotations=annotations)
    fig.show()

    if returnTrue:
        return fig
