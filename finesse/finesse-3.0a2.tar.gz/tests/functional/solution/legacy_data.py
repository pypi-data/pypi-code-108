import pytest
import logging
from os import path
import numpy as np
from finesse import Model

# this gets regenetered each
# time which is quite expesive
# TODO optimise this unit test
# if it gets expensive to run
@pytest.fixture
def output_test_obj(noxaxis):
    """ Executed model object """
    ifo = Model()

    ifo.parse_legacy(
        """
l l1 1 0 0 ni
gauss g1 l1 ni 1m 0
s s1 10 ni n1
maxtem 1
tem l1 0 0 0 0
tem l1 1 0 1 0
phase 0
ad ad00 0 0 0 n1
ad ad10 1 0 0 n1
pd pd n1
#beam ccd 0 n1 this causes an error
yaxis re:im
        """
    )
    if noxaxis:
        ifo.parse_legacy("noxaxis")
    else:
        ifo.parse_legacy("xaxis s1 L lin 1 2 5")

    out = ifo.run()
    return out, ifo


@pytest.mark.parametrize("noxaxis", (True, False))
def test_get_legacy_data(output_test_obj):
    out, ifo = output_test_obj
    legacy_data, column_names, plot_type = out.get_legacy_data(ifo)
    assert isinstance(legacy_data, np.ndarray)
    assert isinstance(column_names, list)
    assert isinstance(plot_type, str)


# TODO: refactor this test
@pytest.mark.parametrize("noxaxis", (True,))
def test_write_legacy_data(caplog, tmpdir, output_test_obj):
    out, ifo = output_test_obj
    legacy_data, column_names, plot_type = out.get_legacy_data(ifo)

    # set one equal to None and check it emits warning
    Fout = tmpdir.join("output.out")
    with caplog.at_level(logging.WARNING):
        out.write_legacy_data(
            ifo,
            filename=Fout,
            legacy_data=legacy_data,
            column_names=None,
            plot_type=plot_type,
        )
        assert "recomputed" in caplog.text

    caplog.clear()
    with caplog.at_level(logging.WARNING):
        out.write_legacy_data(
            ifo,
            filename=Fout,
            legacy_data=legacy_data,
            column_names=column_names,
            plot_type=plot_type,
        )
        assert "recomputed" not in caplog.text

    # check file is actually ouput
    assert path.isfile(Fout)
