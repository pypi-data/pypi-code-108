#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2021.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import os
from pathlib import Path

from freezegun import freeze_time

from pyxel.configuration import load


def test_load_2_times():
    """Test function 'pyxel.inputs_outputs.load' called two times."""
    filename = "tests/data/dummy_simple.yaml"

    # Get full filename
    full_filename = Path(filename)  # type: Path
    assert full_filename.exists()

    # Load the configuration file for the first time
    with freeze_time("2021-06-15 14:11"):
        _ = load(full_filename)

    # Load the configuration file for the second time
    with freeze_time("2021-06-15 14:11"):
        _ = load(full_filename)
