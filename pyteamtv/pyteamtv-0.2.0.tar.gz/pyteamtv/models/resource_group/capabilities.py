from datetime import datetime

from pyteamtv.infra.requester import Requester
from ..list import List

from ..sporting_event import SportingEvent
from ..team import Team
from ..video import Video
from ..exercise import Exercise
from ..app_storage import AppStorageTokens


def iso8601(datetime_: datetime):
    assert datetime_.tzname() == "UTC", datetime_

    return datetime_.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class BaseMixin(object):
    _requester: Requester


class _HasStorage(BaseMixin):
    def get_app_storage_tokens(self):
        return AppStorageTokens(
            self._requester,
            self._requester.request(
                "GET",
                "/apps/current/storageTokens"
            )
        )


class _HasTeamsMixin(BaseMixin):
    def get_teams(self):
        return List(
            Team,
            self._requester,
            "GET",
            "/teams"
        )

    def create_team(self, name: str, sport_type: str, tags: dict = None):
        data = self._requester.request(
            "POST",
            "/teams",
            dict(
                name=name,
                sportType=sport_type,
                tags=tags if tags else {}
            )
        )
        return Team(
            self._requester,
            data
        )


class _HasExercisesMixin(BaseMixin):
    def get_exercises(self):
        return List(
            Exercise,
            self._requester,
            "GET",
            "/exercises"
        )

    def create_exercise(self, title: str, exercise_template_id: str = "exercise-template-sv", tags: dict = None):
        data = self._requester.request(
            "POST",
            "/exercises",
            dict(
                title=title,
                exerciseTemplateId=exercise_template_id,
                tags=tags if tags else {}
            )
        )
        return Exercise(
            self._requester,
            data
        )


class _HasSharingGroupResourceGroupsMixin(BaseMixin):
    def get_sharing_group_resource_groups(self):
        from .factory import factory

        return List(
            factory,
            self._requester,
            "GET",
            "/resourceGroups"
        )

    def create_sharing_group_resource_group(self, name: str, description: str, sport_type: str, visibility_type: str = 'public', attributes:dict = None):
        from .factory import factory

        data = self._requester.request(
            "POST",
            "/resourceGroups",
            dict(
                name=name,
                sportType=sport_type,
                description=description,
                visibility_type=visibility_type,
                attributes=attributes if attributes else {}
            )
        )
        return factory(
            self._requester,
            data
        )


class _HasSportingEventsMixin(BaseMixin):
    def get_sporting_events(self):
        return List[SportingEvent](
            SportingEvent,
            self._requester,
            "GET",
            "/sportingEvents"
        )

    def get_sporting_event(self, sporting_event_id: str):
        data = self._requester.request(
            "GET",
            f"/sportingEvents/{sporting_event_id}"
        )
        return SportingEvent(
            self._requester,
            data
        )

    def create_sporting_event(self,
                              home_team: Team,
                              away_team: Team,
                              scheduled_at: datetime,
                              tags: dict = None,
                              type: str = "match"):
        data = self._requester.request(
            "POST",
            "/sportingEvents",
            dict(
                type=type,
                name=f"{home_team.name} - {away_team.name}",
                homeTeamId=home_team.team_id,
                awayTeamId=away_team.team_id,
                scheduledAt=iso8601(scheduled_at),
                tags=tags if tags else {}
            )
        )
        return SportingEvent(
            self._requester,
            data
        )


class _HasVideosMixin(BaseMixin):
    def get_videos(self):
        return List(
            Video,
            self._requester,
            "GET",
            "/videos"
        )

    def get_video(self, video_id):
        data = self._requester.request(
            "GET",
            f"/videos/{video_id}"
        )

        return Video(
            self._requester,
            data
        )
