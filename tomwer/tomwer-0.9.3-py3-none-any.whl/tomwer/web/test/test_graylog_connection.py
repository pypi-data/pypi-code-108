# # coding: utf-8
# # /*##########################################################################
# #
# # Copyright (c) 2016-2017 European Synchrotron Radiation Facility
# #
# # Permission is hereby granted, free of charge, to any person obtaining a copy
# # of this software and associated documentation files (the "Software"), to deal
# # in the Software without restriction, including without limitation the rights
# # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # copies of the Software, and to permit persons to whom the Software is
# # furnished to do so, subject to the following conditions:
# #
# # The above copyright notice and this permission notice shall be included in
# # all copies or substantial portions of the Software.
# #
# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# # THE SOFTWARE.
# #
# # ###########################################################################*/
# """ Not a unit test but send a simple test message error to gray log"""
#
# __authors__ = ["H. Payno"]
# __license__ = "MIT"
# __date__ = "24/01/2017"
#
# from tomwer.web.client import OWClient
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# class TestGrayLog(OWClient):
#     def __init__(self):
#         OWClient.__init__(self)
#
#     def sendErrorMessage(self):
#         logger.error("test error message")
#
#     def sendwarningMessage(self):
#         logger.warning("test warning message")
#
#     def sendInfoMessage(self):
#         logger.info("test info message")
#
#     def sendProcessEndedMessage(self):
#         logger.processEnded("test processEnded message")
#
#
# if __name__ == "__main__":
#     c = TestGrayLog()
#     c.sendErrorMessage()
#     c.sendwarningMessage()
#     c.sendInfoMessage()
#     c.sendProcessEndedMessage()
