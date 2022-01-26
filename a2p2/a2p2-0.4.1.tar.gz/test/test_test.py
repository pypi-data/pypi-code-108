#!/usr/bin/env python
# Tested on GITHub/Travis
# on your machine, just run pytest in this directory or execute it to get outputs
#

import os
import pytest

from a2p2.ob import OB
from a2p2 import A2p2Client


FIXTURE_DIR = os.path.join( os.path.dirname(os.path.realpath(__file__)) )

ALL_OBXML_VALUE_ERROR = pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR,"aspro-sample-bad-coords.obxml", ''),
    os.path.join(FIXTURE_DIR,"aspro-sample-bad-k.obxml", ''),
    os.path.join(FIXTURE_DIR,"aspro-sample.obxml", ''),
    os.path.join(FIXTURE_DIR,"aspro-sample-bad-insmode.obxml", ''),
)

ALL_OBXML_GENERAL_ERROR = pytest.mark.datafiles(
)

ALL_OBXML_NO_ERROR = pytest.mark.datafiles(
)


@ALL_OBXML_VALUE_ERROR
def test_obxml_value_error(datafiles):
    a2p2c=A2p2Client(True)

    for filepath in datafiles.listdir():
        file = str(filepath)
        errorLog = processOB(a2p2c, file)

        print("> ERROR log for %s"+ file)
        print(errorLog)
        print("< ERROR log \n\n")

        assert "Value error" in errorLog

def processOB(a2p2c, file):
    print("checking OB at %s location" % file)
    ob = OB(file)
    for obsc in ob.observationConfiguration:
        print("obsConfig.id=%s" % obsc.id)
    for obss in ob.observationSchedule.OB:
        print("obsSchedule.ref=%s" % str(obss.ref))
    #    print(ob)
    print("\n\n")
    a2p2c.clearErrors()
    a2p2c.processOB(ob)
    errorLog = "\n\r".join(a2p2c.getErrors())
    return errorLog
