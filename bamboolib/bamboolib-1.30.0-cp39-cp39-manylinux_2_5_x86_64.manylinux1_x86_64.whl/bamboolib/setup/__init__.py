# Copyright (c) 8080 Labs GmbH.
# Distributed under the terms of our End-User License Agreement (see bamboolib.com/eula
# for more information).


def test_setup():
    """
    Function to test the setup of bamboolib.

    The output contains widgets that need to work for bamboolib to work as a whole.
    In addition, the output gives guidance about the expected and installed versions of the dependencies.

    """
    # import inline in order to not cause any circular import issues

    from IPython.display import display
    import ipywidgets as widgets
    import pandas as pd

    import ipyslickgrid
    import plotly
    import plotly.graph_objs as go

    import bamboolib as bam
    from bamboolib.widgets import Multiselect

    print("Testing Jupyter extensions:")

    print("")
    print("ipywidgets:")
    display(widgets.Text("ipywidgets works"))
    print("")
    print("ipyslickgrid:")
    print(f"Python library version is {ipyslickgrid.__version__}")
    ipyslickgrid_df = pd.DataFrame.from_dict(
        {"test ipyslickgrid": ["ipyslickgrid widget works"]}
    )
    display(
        ipyslickgrid.show_grid(
            ipyslickgrid_df, grid_options={"maxVisibleRows": 2, "minVisibleRows": 2}
        )
    )

    print("")
    print("plotly:")
    print(f"Python library version is {plotly.__version__}")
    trace = go.Bar(x=["Plotly", "works"], y=[1, 2])
    layout = dict(height=350, width=500)
    display(go.FigureWidget(data=[trace], layout=layout))

    print("")
    print("bamboolib:")
    print(f"Python library version is {bam.__version__}")
    print(f"Needed version of Jupyter extension is {bam.__widgets_version__}")
    display(Multiselect(placeholder="bamboolib widget works"))

    print("")
    try:
        from jupyterlab import commands
    except ImportError:
        return
    print("JupyterLab and Labextensions:")
    commands.list_extensions()
