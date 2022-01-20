
"""SDK Version 2 backward compatibility

This convenience module provides compatibility with the ArthurAI SDK version 2.x, but is considered deprecated. Please
update your import paths according to the following:

* arthurai.client.apiv3.InputType → arthurai.common.constants.InputType
* arthurai.client.apiv3.OutputType → arthurai.common.constants.OutputType
* arthurai.client.apiv3.ValueType → arthurai.common.constants.ValueType
* arthurai.client.apiv3.Stage → arthurai.common.constants.Stage
* arthurai.client.apiv3.TextDelimiter → arthurai.common.constants.TextDelimiter
* arthurai.client.apiv3.ListableStrEnum → arthurai.common.constants.ListableStrEnum

* arthurai.client.apiv3.AttributeCategory → arthurai.core.attributes.AttributeCategory
* arthurai.client.apiv3.AttributeBin → arthurai.core.attributes.AttributeBin

* arthurai.client.apiv3.arthur_explainer → arthurai.explainability.arthur_explainer
* arthurai.client.apiv3.decorators → arthurai.core.decorators
* arthurai.client.apiv3.explanation_packager → arthurai.explainability.explanation_packager

"""

import logging

from arthurai.common.constants import InputType, OutputType, ValueType, Stage, TextDelimiter, ListableStrEnum
from arthurai.core import decorators
from arthurai.core.attributes import AttributeCategory, AttributeBin
from arthurai.explainability import arthur_explainer, explanation_packager


logger = logging.getLogger(__name__)
logger.warning("DEPRECATION WARNING: The arthurai.client.apiv3 module is provided for backward compatibility, but is "
               "deprecated and will be removed. Please update your import paths, for details see the "
               "arthurai.client.apiv3 module documentation")
