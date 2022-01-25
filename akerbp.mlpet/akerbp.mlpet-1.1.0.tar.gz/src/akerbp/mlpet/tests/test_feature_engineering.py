# ONLY testing one function from feature_engineering. Would be good to expand this
# if we have some spare time in a sprint
from pandas.testing import assert_frame_equal

from akerbp.mlpet import feature_engineering
from akerbp.mlpet.tests.data import FORMATION_DF, FORMATION_TOPS_MAPPER


def test_add_formation_tops():
    df_with_tops = feature_engineering.add_formation_tops_label(
        FORMATION_DF[["DEPTH", "well_name"]],
        formation_tops_mapper=FORMATION_TOPS_MAPPER,
        id_column="well_name",
    )
    # Sorting columns because column order is not so important
    assert_frame_equal(df_with_tops.sort_index(axis=1), FORMATION_DF.sort_index(axis=1))

    return True
