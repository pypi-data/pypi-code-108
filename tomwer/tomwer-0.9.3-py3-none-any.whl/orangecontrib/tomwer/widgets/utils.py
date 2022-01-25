# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

"""utils for orange widget"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "21/02/2020"


class WidgetLongProcessing:
    """Class to display processing for some widgets with long processing"""

    def processing_state(self, working: bool, info=None) -> None:
        """

        :param working:
        :param Union[str, None] info:
        """
        # default orange version don't have Processing.
        try:
            if working:
                self.Processing._add_general(
                    info or "processing", text=None, shown=True
                )
            else:
                self.Processing.clear()
        except AttributeError:
            # in case we are on an orange version not having `Processing`
            pass

    def setDryRun(self, dry_run):
        pass

    def _startProcessing(self, *args, **kwargs):
        self.processing_state(working=True, info="processing")

    def _endProcessing(self, *args, **kwargs):
        self.processing_state(working=False, info="processing")
