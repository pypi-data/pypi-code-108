import calendar
from datetime import date
from datetime import datetime
from datetime import timedelta
from harvest.endpoints import TimeEntryEndpoint
from harvest.endpoints import ProjectsEndpoint
from harvest.endpoints import TasksEndpoint
from harvest.endpoints import UsersMeEndpoint
from harvest.endpoints import UsersAssignmentsEndpoint


class BaseService(object):
    def __init__(self, credential):
        self.credential = credential


class TimeRangeBaseService(BaseService):
    def __init__(self, credential):
        self.today = datetime.now()
        super(TimeRangeBaseService, self).__init__(credential)

    def get_date_range(self):
        raise NotImplementedError

    def all(self, page=1):
        date_range = self.get_date_range()
        api = TimeEntryEndpoint(credential=self.credential)
        resp = api.get(params={"from": date_range[0], "to": date_range[1]})
        return resp.json()

    def blanks(self):
        resp = self.all()
        empty_time_entries = []
        for entry in resp["time_entries"]:
            if not entry["notes"]:
                empty_time_entries.append(entry)
        resp["time_entries"] = empty_time_entries
        return resp


class SingleDayTimeEntries(TimeRangeBaseService):
    def __init__(self, credential, date):
        self.date = date
        super(SingleDayTimeEntries, self).__init__(credential)

    def get_date_range(self):
        return (self.date, self.date)


class TodayTimeEntries(TimeRangeBaseService):
    def get_date_range(self):
        self.date_from = self.today.strftime("%Y-%m-%d")
        self.date_to = self.today.strftime("%Y-%m-%d")
        return (self.date_from, self.date_to)


class MonthTimeEntries(TimeRangeBaseService):
    def set_month(self, year, month):
        self.year = year
        self.month = month
        self.last_day = calendar.monthrange(year, month)[1]

    def get_date_range(self):
        self.date_from = date(self.year, self.month, 1)
        self.date_to = date(self.year, self.month, self.last_day)
        return (
            self.date_from.strftime("%Y-%m-%d"),
            self.date_to.strftime("%Y-%m-%d"),
            )


class CurrentWeekTimeEntries(TimeRangeBaseService):
    def get_date_range(self):
        self.date_from = self.today - timedelta(days=self.today.weekday())
        self.date_to = self.date_from + timedelta(days=6)
        self.date_from = self.date_from.strftime("%Y-%m-%d")
        self.date_to = self.date_to.strftime("%Y-%m-%d")
        return (self.date_from, self.date_to)


class PreviousWeekTimeEntries(TimeRangeBaseService):
    def get_date_range(self):
        self.today = self.today - timedelta(days=(6 - self.today.weekday()))
        self.date_from = self.today - timedelta(days=self.today.weekday())
        self.date_to = self.date_from + timedelta(days=6)
        return (
            self.date_from.strftime("%Y-%m-%d"),
            self.date_to.strftime("%Y-%m-%d"),
            )


class AllProjects(BaseService):
    def all(self):
        resp = ProjectsEndpoint(credential=self.credential).get()
        total_pages = resp.json()["total_pages"]
        ret = []
        for i in range(1, total_pages + 1):
            resp = ProjectsEndpoint(credential=self.credential).get(page=i)
            ret += resp.json()["projects"]
        return ret


class AllTasks(BaseService):
    def all(self):
        resp = TasksEndpoint(credential=self.credential).get()
        total_pages = resp.json()["total_pages"]
        ret = []
        for i in range(1, total_pages + 1):
            resp = TasksEndpoint(credential=self.credential).get(page=i)
            ret += resp.json()["tasks"]
        return ret


class CurrentUser(BaseService):
    def get(self):
        resp = UsersMeEndpoint(credential=self.credential).get()
        return resp.json()


class UsersAllAssignments(BaseService):
    def all(self):
        ret = []
        resp = UsersMeEndpoint(credential=self.credential).get()
        # user_id = resp.json()["id"]
        user_id = self.credential.account_id
        resp = UsersAssignmentsEndpoint(
            credential=self.credential, user_id=user_id).get()
        total_pages = resp.json()["total_pages"]
        for i in range(1, total_pages + 1):
            resp = UsersAssignmentsEndpoint(
                credential=self.credential, user_id=user_id).get(page=i)
            ret += resp.json()["project_assignments"]
        return ret


class WeekTimeEntriesService(TimeRangeBaseService):

    def __init__(self, credential, date):
        """
        Params:
            credential (harvest.credentials.OAuth2Credential):
            date (datetime.datetime):
        """
        super(WeekTimeEntriesService, self).__init__(credential)
        self.date = date

    def get_date_range(self):
        start = self.date + timedelta(0 - self.date.weekday())
        end = self.date + timedelta(6 - self.date.weekday())
        ret = (
            start.date(),
            end.date(),
        )
        return ret
