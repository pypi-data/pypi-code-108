# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring
import datetime
from typing import Union

from gql import gql

from qctrl.queries.base import StaticQuery


class ActionExportQuery(StaticQuery):
    """
    Extracts data from the actions table.
    """

    query = gql(
        """
        query exportActions($limit: Int, $filterBy: ActionFilter) {
            actions(limit: $limit, filterBy: $filterBy){
                actions {
                    user {
                      username
                    }
                    modelId
                    name
                    status
                    errors {
                        exception
                        traceback
                    }
                    createdAt
                    updatedAt
                    terminatedAt
                    runtime
                }
                errors {
                    message
                }
            }
        }
    """
    )

    MAX_RECORDS = 50000

    def _get_variable_values(  # pylint:disable=arguments-differ
        self,
        start_date: Union[datetime.date, str],
        end_date: Union[datetime.date, str],
        ignore_test_users: bool = True,
    ):

        if isinstance(start_date, str):
            start_date = self.str_to_date(start_date)

        if isinstance(end_date, str):
            end_date = self.str_to_date(end_date)

        if start_date > end_date:
            raise ValueError(f"Invalid date range: {start_date} to {end_date}")

        filter_by = {
            "createdAt": {
                "range": [self.date_to_str(start_date), self.date_to_str(end_date)]
            },
            "ignoreTestUsers": ignore_test_users,
        }

        return {"limit": self.MAX_RECORDS, "filterBy": filter_by}

    def _format_response(self, response: dict, *_) -> dict:
        return response["actions"]["actions"]

    @staticmethod
    def str_to_date(date_str: str) -> datetime.date:
        """Helper function to convert a date string
        to a datetime.date object."""
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    @staticmethod
    def date_to_str(date: datetime.date) -> str:
        """Helper function to convert a datetime.date
        object to a string."""
        return date.strftime("%Y-%m-%d")
