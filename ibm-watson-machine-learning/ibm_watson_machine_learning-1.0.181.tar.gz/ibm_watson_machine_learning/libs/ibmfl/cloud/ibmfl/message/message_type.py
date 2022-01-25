"""
 An enumeration class for the message type field which describe what
 kind of data is being sent inside the Message
"""
#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from enum import Enum

__author__ = "Supriyo Chakraborty, Shalisha Witherspoon, Dean Steuer"


class MessageType(Enum):
    """
    Message types for communication between party and aggregator
    """
    MODEL_UPDATE = 1
    MODEL_HYPERPARAMETERS = 2
    MODEL_PARAMETERS = 3
    REQUEST_MODEL_HYPERPARAMETERS = 4
    REQUEST_MODEL_UPDATE = 5
    REGISTER = 6
    TRAIN = 7
    SAVE_MODEL = 8
    PREDICT_MODEL = 9
    EVAL_MODEL = 10
    ACK = 11
    SYNC_MODEL = 12
    STOP = 14
    ERROR_AUTH = 400
