# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale_cli.enums import Environment

"""
Constants used throughout the fast-path CLI.
"""

# Stores the environment mapping to the scikit-learn version trained DDM folder
DRIFT_ARCHIVE_ENV_MAPPING = {
    Environment.PUBLIC_CLOUD.value: "scikit_0.24.1",
    Environment.CPD_3_X.value: "scikit_0.20.2",
    Environment.CPD_4_0_0.value: "scikit_0.20.2",
    Environment.CPD_4_0_1.value: "scikit_0.20.2",
    Environment.CPD_4_0_2_PLUS.value: "scikit_0.24.1"
}

# Stored the environment mapping to the Spark version supported by WML for the Spark model
WML_SPARK_VERSION_SUPPORT_MAPPING = {
    Environment.PUBLIC_CLOUD.value: "spark_3.0",
    Environment.CPD_3_X.value: "spark_2.4",
    Environment.CPD_4_0_0.value: "spark_2.4",
    Environment.CPD_4_0_1.value: "spark_2.4",
    Environment.CPD_4_0_2_PLUS.value: "spark_3.0"
}

# Stored the environment to use for the Challenger model
WML_CHALLENGER_ENVIRONMENT_MAPPING = {
    Environment.PUBLIC_CLOUD.value: "py_3.8",
    Environment.CPD_3_X.value: "py_3.7",
    Environment.CPD_4_0_0.value: "py_3.7",
    Environment.CPD_4_0_1.value: "py_3.7",
    Environment.CPD_4_0_2_PLUS.value: "py_3.7"
}
# Software spec mapping for the challenger model
WML_CHALLENGER_SOFTWARE_SPEC_MAPPING = {
    Environment.PUBLIC_CLOUD.value: "default_py3.8",
    Environment.CPD_3_X.value: "default_py3.7",
    Environment.CPD_4_0_0.value: "default_py3.7",
    Environment.CPD_4_0_1.value: "default_py3.7",
    Environment.CPD_4_0_2_PLUS.value: "default_py3.7_opence"
}