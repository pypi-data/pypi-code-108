import pytest
from transparentpath import TransparentPath
from pathlib import Path
import pandas as pd
from tablewriter import TableWriter

df = pd.read_csv(Path("tests") / "data" / "input.csv", index_col=0)
df_multi = pd.read_csv(Path("tests") / "data" / "input.csv", index_col=[0, 1])


@pytest.mark.parametrize(
    "cls", [Path, TransparentPath, str]
)
def test_tablewriter_from_dataframe(cls):
    table = TableWriter(
        path_output=cls("tests/data/output"),
        data=df,
        to_latex_args={"column_format": "lrr"},
        label="tab::example",
        caption="TableWriter example",
        hide_numbering=True,
    )
    table.compile(silenced=True)
    if cls == str:
        cls = Path
    assert cls("tests/data/output.tex").is_file()
    assert cls("tests/data/output.pdf").is_file()


@pytest.mark.parametrize(
    "cls", [Path, TransparentPath, str]
)
def test_tablewriter_from_dataframe_multiindex(cls):
    table = TableWriter(
        path_output=cls("tests/data/output_multi"),
        data=df_multi,
        to_latex_args={"column_format": "lrr"},
        label="tab::example",
        caption="TableWriter example",
        hide_numbering=True,
    )
    table.compile(silenced=True)
    if cls == str:
        cls = Path
    assert cls("tests/data/output_multi.tex").is_file()
    assert cls("tests/data/output_multi.pdf").is_file()


@pytest.mark.parametrize(
    "cls", [Path, TransparentPath, str]
)
def test_tablewriter_from_file(cls):
    table = TableWriter(
        path_output=cls("tests/data/output_from_file"),
        path_input=cls("tests/data/input.csv"),
        label="tab::example",
        caption="TableWriter example",
        read_from_file_args={"index_col": 0},
        number=3,
    )
    if cls == str:
        cls = Path
    table.compile(silenced=True)
    assert cls("tests/data/output_from_file.tex").is_file()
    assert cls("tests/data/output_from_file.pdf").is_file()


@pytest.mark.parametrize(
    "cls", [Path, TransparentPath, str]
)
def test_tablewriter_from_file_multiindex(cls):
    table = TableWriter(
        path_output=cls("tests/data/output_from_file_multi"),
        path_input=cls("tests/data/input.csv"),
        label="tab::example",
        caption="TableWriter example",
        read_from_file_args={"index_col": [0, 1]},
        number=3,
    )
    if cls == str:
        cls = Path
    table.compile(silenced=True)
    assert cls("tests/data/output_from_file_multi.tex").is_file()
    assert cls("tests/data/output_from_file_multi.pdf").is_file()
