import pandas as pd
import numpy as np
import plotly.graph_objects as go


def correlations_boxplots(correlations, to):
    """WIP"""
    rows = []

    for correlation in correlations:
        dataset = correlation.dataset
        local_df = correlation.kendall.corr
        local_df_p_values = correlation.kendall.p_values

        local_row = local_df.drop(to, axis=1)
        local_row.loc[to][local_df_p_values.drop(to, axis=1).loc[to] > 0.04] = np.NaN

        rows.append([dataset] + list(local_row.loc[to]))

    df = pd.DataFrame(
        rows,
        columns=["dataset"] + list(local_df.drop(to, axis=1).columns),
    )

    fig = go.Figure()

    for column in df.columns[1:]:
        fig.add_trace(
            go.Box(x=df[column], y=df["dataset"], name=column, boxpoints=False)
        )

    fig.update_layout(
        font_family="IBM Plex Sans",
        font_color="black",
        margin=dict(l=15, r=15, t=15, b=15),
        legend_traceorder="reversed",
        xaxis=dict(
            title=f"kendall correlation to {to}",
            zeroline=False,
            ticks="inside",
            showline=True,
            linecolor="black",
            linewidth=1,
            range=[-1, 1],
            mirror=True,
            dtick=0.2,
            tickangle=-90,
            gridcolor="rgba(200,200,200,1)",
            tickfont=dict(size=11, color="black"),
        ),
        boxmode="group",
        yaxis=dict(
            title="Dataset",
            linecolor="black",
            linewidth=1,
            mirror=True,
            tickangle=-90,
            tickfont=dict(size=11, color="black"),
        ),
        paper_bgcolor="rgba(255,255,255,1)",
        plot_bgcolor="rgba(255,255,255,1)",
        legend=dict(
            font=dict(size=10),
        ),
    )
    fig.update_traces(orientation="h")

    return fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        include_mathjax="cdn",
        default_width=739 // 2,
    )
