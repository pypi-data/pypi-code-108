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
from typing import Tuple

from gql import gql

from .base import StaticQuery


class CreateTokenQuery(StaticQuery):  # pylint:disable=too-few-public-methods
    """Creates new access and refresh tokens."""

    query = gql(
        """
        mutation createToken($username: String!, $password: String!) {
            createToken (
                input: {
                    username: $username
                    password: $password
                }
            )
            {
                token {
                    access
                    refresh
                }
                errors {
                    message
                    fields
                }
            }
        }
    """
    )

    def _get_variable_values(
        self, username: str, password: str
    ):  # pylint:disable=arguments-differ
        return {"username": username, "password": password}

    def _format_response(self, response: dict, *_) -> Tuple[str, str]:
        token_obj = response["createToken"]["token"]
        access_token = token_obj["access"]
        refresh_token = token_obj["refresh"]
        return access_token, refresh_token
