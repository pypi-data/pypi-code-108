import altair as alt
import pandas as pd

data = pd.DataFrame({'x': ['A', 'B', 'C', 'D', 'E'], 'y': [5, 3, 6, 7, 2]})
chart = (
    alt.Chart(data)
    .mark_bar()
    .encode(
        x='x',
        y='y',
    )
    .interactive()
)

chart.show()
