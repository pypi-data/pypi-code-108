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


class RefreshTokenQuery(StaticQuery):  # pylint:disable=too-few-public-methods
    """Uses the refresh token to obtain new access
    and refresh tokens.
    """

    query = gql(
        """
        mutation refreshToken($token: String!) {
            refreshToken (
                input: {
                    token: $token
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
        self, refresh_token: str
    ):  # pylint:disable=arguments-differ
        return {"token": refresh_token}

    def _format_response(self, response: dict, *_) -> Tuple[str, str]:
        token_obj = response["refreshToken"]["token"]
        access_token = token_obj["access"]
        refresh_token = token_obj["refresh"]
        return access_token, refresh_token
