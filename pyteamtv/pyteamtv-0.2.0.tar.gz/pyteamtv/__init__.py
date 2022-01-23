import os
from typing import Optional

try:
    __PYTEAMTV_SETUP__
except NameError:
    __PYTEAMTV_SETUP__ = False

if not __PYTEAMTV_SETUP__:
    from .api import TeamTVApp, TeamTVUser

    def get_team(name: Optional[str] = None, resource_group_id: Optional[str] = None):
        if 'TEAMTV_API_TOKEN' in os.environ:
            app = TeamTVUser(os.environ['TEAMTV_API_TOKEN'])
            return app.get_team(name=name, resource_group_id=resource_group_id)


__version__ = "0.2.0"

