#   Copyright © 2020 Sidemash Cloud Services
#
#   Licensed under the Apache  License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless  required  by  applicable  law  or  agreed to in writing,
#   software  distributed  under  the  License  is distributed on an
#   "AS IS"  BASIS, WITHOUT  WARRANTIES  OR CONDITIONS OF  ANY KIND,
#   either  express  or  implied.  See the License for the  specific
#   language governing permissions and limitations under the License.


from typing import Dict
import json


class InstanceStatus:
    def __init__(self, value: str):
        self._type = "InstanceStatus" 
        self.value = value

    @staticmethod
    def Initializing():
        return InstanceStatus("Initializing")

    @staticmethod
    def Running():
        return InstanceStatus("Running")

    @staticmethod
    def Restarting():
        return InstanceStatus("Restarting")

    @staticmethod
    def Updating():
        return InstanceStatus("Updating")

    @staticmethod
    def Maintaining():
        return InstanceStatus("Maintaining")

    @staticmethod
    def PartiallyAvailable():
        return InstanceStatus("PartiallyAvailable")

    @staticmethod
    def NotAvailable():
        return InstanceStatus("NotAvailable")

    @staticmethod
    def Terminating():
        return InstanceStatus("Terminating")

    @staticmethod
    def Terminated():
        return InstanceStatus("Terminated")

    @staticmethod
    def all_possibles_values():
        return {"Initializing",
                "Running",
                "Restarting",
                "Updating",
                "Maintaining",
                "PartiallyAvailable",
                "NotAvailable",
                "Terminating",
                "Terminated"}

    @staticmethod
    def from_string(value):
        if value == "Initializing": return InstanceStatus.Initializing()
        elif value == "Running": return InstanceStatus.Running()
        elif value == "Restarting": return InstanceStatus.Restarting()
        elif value == "Updating": return InstanceStatus.Updating()
        elif value == "Maintaining": return InstanceStatus.Maintaining()
        elif value == "PartiallyAvailable": return InstanceStatus.PartiallyAvailable()
        elif value == "NotAvailable": return InstanceStatus.NotAvailable()
        elif value == "Terminating": return InstanceStatus.Terminating()
        elif value == "Terminated": return InstanceStatus.Terminated()
        else: return None

    @staticmethod
    def is_valid(value):
        return value in InstanceStatus.all_possibles_values()

    def is_not_initializing(self):
        return self.value != "Initializing"

    def is_not_running(self):
        return self.value != "Running"

    def is_not_restarting(self):
        return self.value != "Restarting"

    def is_not_updating(self):
        return self.value != "Updating"

    def is_not_maintaining(self):
        return self.value != "Maintaining"

    def is_not_partially_available(self):
        return self.value != "PartiallyAvailable"

    def is_not_not_available(self):
        return self.value != "NotAvailable"

    def is_not_terminating(self):
        return self.value != "Terminating"

    def is_not_terminated(self):
        return self.value != "Terminated"

    def is_initializing(self):
        return self.value == "Initializing"

    def is_running(self):
        return self.value == "Running"

    def is_restarting(self):
        return self.value == "Restarting"

    def is_updating(self):
        return self.value == "Updating"

    def is_maintaining(self):
        return self.value == "Maintaining"

    def is_partially_available(self):
        return self.value == "PartiallyAvailable"

    def is_not_available(self):
        return self.value == "NotAvailable"

    def is_terminating(self):
        return self.value == "Terminating"

    def is_terminated(self):
        return self.value == "Terminated"

    def to_json(self):
        return json.dumps(self.value)

    def __to_remote_json(self):
        return json.dumps(self.value)

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return "InstanceStatus(value=" + self.value + ")"

    def __str__(self):
        return self.value