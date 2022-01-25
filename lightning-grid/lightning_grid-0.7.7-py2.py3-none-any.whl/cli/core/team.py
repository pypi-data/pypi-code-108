from __future__ import annotations

import typing
from typing import List

from grid.cli.core.base import GridObject
from grid.cli.exceptions import APIError

if typing.TYPE_CHECKING:
    from grid.cli.client import Grid


class Team(GridObject):
    """
    Team object in Grid
    """
    def refresh(self):
        pass

    @classmethod
    def get_all(cls) -> List['Team']:
        client: Grid = cls().client

        query = """
            query GetUserTeams {
                getUserTeams {
                    success
                    message
                    teams {
                        id
                        name
                        createdAt
                        role
                        members {
                            id
                            username
                            firstName
                            lastName
                        }
                    }
                }
            }
        """
        result = client.query(query)
        if not result['getUserTeams'] or not result['getUserTeams']['success']:
            raise APIError(result['getUserTeams']["message"])
        teams = []
        for detail in result['getUserTeams']['teams']:
            team = cls()
            team.data = detail
            teams.append(team)
        return teams
