# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

from typing import Sequence, Union


ISSUE_SEPARATOR = ": "


def FactorizedIssuesAsStr(
    issue: Union[str, Sequence[str]], /, *, max_n_contexts: int = 1000
) -> str:
    """"""
    if isinstance(issue, str):
        return issue

    issues = issue
    issues_per_content = {}
    for issue in issues:
        if ISSUE_SEPARATOR in issue:
            context, content = issue.split(ISSUE_SEPARATOR, 1)
        else:
            context, content = "", issue
        if content in issues_per_content:
            issues_per_content[content].append(context)
        else:
            issues_per_content[content] = [context]

    factorized = []
    first_half = max_n_contexts // 2
    last_half = max_n_contexts - first_half - 1
    for content, contexts in issues_per_content.items():
        contexts = tuple(_ctx for _ctx in contexts if _ctx.__len__() > 0)
        if (n_contexts := contexts.__len__()) > 1:
            if n_contexts > max_n_contexts:
                contexts = contexts[:first_half] + ("...",) + contexts[(-last_half):]
            contexts_as_str = " / ".join(contexts)
            factorized.append(f"{content}{ISSUE_SEPARATOR}{contexts_as_str}")
        elif n_contexts > 0:
            factorized.append(f"{contexts[0]}{ISSUE_SEPARATOR}{content}")
        else:
            factorized.append(content)

    return " | ".join(factorized)
