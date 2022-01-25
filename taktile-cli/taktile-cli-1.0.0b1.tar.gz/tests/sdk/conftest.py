import shutil

import numpy
import pandas
import pandas._testing as tm
import pytest

from tktl.core.managers.project import ProjectManager
from tktl.core.t import TemplateT


@pytest.fixture
def serializer_df_inputs():
    # from: pandas.tests.frame.conftest.float_frame_with_na
    df = pandas.DataFrame(tm.getSeriesData())
    # set some NAs
    df.iloc[5:10] = numpy.nan
    df.iloc[15:20, -2:] = numpy.nan
    return df


@pytest.fixture
def serializer_series_inputs(serializer_df_inputs):
    return serializer_df_inputs.B


@pytest.fixture
def serializer_l_of_d_sequence_inputs():
    return [
        {"a": i, "b": j}
        for i, j in zip(range(100), numpy.random.randn(100).tolist())  # noqa
    ]


@pytest.fixture
def serializer_dict_inputs():
    return {"a": 1000, "b": 1.0, "c": "strfgadfsv"}


@pytest.fixture
def serializer_list_and_tuple_inputs():
    return (
        numpy.random.randn(100).tolist(),
        [numpy.random.randn(100).tolist(), numpy.random.randn(100).tolist()],
        [1, 2, 2],
        ["fdefswdefswde", "dfasfwefgwe", "fjnlsjnk2"],
        (1, 2, 2, 1, 2323, 123, 12, 342, 14, 1234, 123, 43),
    )


@pytest.fixture
def serializer_list_inputs():
    return numpy.random.randn(100).tolist()


@pytest.fixture(scope="function")
def create_proj():
    ProjectManager.init_project(None, "sample_project", TemplateT.REPAYMENT)
    yield
    shutil.rmtree("sample_project")
