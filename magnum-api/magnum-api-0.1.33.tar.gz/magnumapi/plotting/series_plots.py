import plotly.graph_objects as go
import plotly.express as px


def plot(x, y, xlabel='', ylabel='') -> None:
    fig = go.Figure()
    fig.add_trace(px.line(x=x, y=y).data[0])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(title=dict(text=xlabel))
    fig.update_yaxes(title=dict(text=ylabel))
    fig.show()