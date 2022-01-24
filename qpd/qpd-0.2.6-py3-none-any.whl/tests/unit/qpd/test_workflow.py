from qpd.workflow import QPDWorkflow, QPDWorkflowContext, WorkflowDataFrame
from qpd_pandas import QPDPandasEngine
import pandas as pd
from pytest import raises


def test_workflow():
    ctx = QPDWorkflowContext(
        QPDPandasEngine(),
        {
            "x": pd.DataFrame([[0, 1], [2, 3]], columns=["a", "b"]),
            "y": pd.DataFrame([[True], [False]], columns=["aa"]),
        },
    )
    wf = QPDWorkflow(ctx)
    df = wf.dfs["x"]
    # invalid to add non workflow dfs
    raises(ValueError, lambda: WorkflowDataFrame(df, ctx.dfs["y"]))
    assert 5 == len(wf._spec.tasks)  # x: 2+1, y: 1+1
    df = df[["b", "a"]]
    assert 6 == len(wf._spec.tasks)
    df = wf.op_to_df(["b", "a"], "filter_df", df, wf.dfs["y"]["aa"])
    assert 10 == len(wf._spec.tasks)
    col1 = df["a"]
    col2 = df["b"]
    col4 = wf.op_to_col("binary_arithmetic_op", col1, col2, "+").rename("p")
    col5 = wf.const_to_col(3, "y").rename("y")  # rename will not take effect
    assert 13 == len(wf._spec.tasks)
    wf.assemble_output(col4, col5)
    wf.assemble_output(col4, col5)  # dedupped
    assert 15 == len(wf._spec.tasks)

    assert [[1, 3]] == wf.run().values.tolist()
