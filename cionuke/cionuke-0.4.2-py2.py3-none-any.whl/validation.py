"""
Validate the submission.
"""

import os
import sys

from ciocore.validator import Validator
from cionuke import const as k
from cionuke.components import frames


import json

class ValidateTaskCount(Validator):
    def run(self, _):
        main_seq, scout_seq = frames.get_sequences(self._submitter)

        count = len(main_seq.chunks())
        if count > 1000:
            self.add_warning(
                "This submission contains over 1000 tasks ({}). Are you sure this is correct?".format(
                    count
                )
            )



def run(submitter):

    meta_warnings = set()

    validators = [plugin(submitter) for plugin in Validator.plugins()]

    for validator in validators:
        try:
            validator.run(None)
        except BaseException as ex:
            meta_warnings.add(
                "[{}]:\nValidator failed to run. Don't panic, it's probably due to an unsupported feature and can be ignored.\n{}".format(
                    validator.title(), str(ex)
                )
            )

    return {
        "error": list(set.union(*[validator.errors for validator in validators])),
        "warning": list(set.union(*[validator.warnings for validator in validators]))
        + list(meta_warnings),
        "info": list(set.union(*[validator.notices for validator in validators])),
    }

