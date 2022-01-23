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
from gql import gql

from .base import StaticQuery


class MeQuery(StaticQuery):  # pylint:disable=too-few-public-methods
    """Retrieves info for the current user."""

    query = gql(
        """
        query {
            me {
                me {
                    ... on User {
                        username
                    }
                }
                errors {
                    message
                    fields
                }
            }
        }
    """
    )

    def _format_response(self, response: dict, *_) -> str:
        return response["me"]["me"]["username"]
