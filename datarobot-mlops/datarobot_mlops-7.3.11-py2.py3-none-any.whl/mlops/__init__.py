#  Copyright (c) 2019 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2021.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.

# See http://python-future.org/imports.html#aliased-imports
# I'm putting this at the root of the package so other packages
# don't need to worry about loading the aliases as this code
# will take care of it and other modules can just write PY3
# imports and they will automagically work in PY2
from future.standard_library import install_aliases
install_aliases()
