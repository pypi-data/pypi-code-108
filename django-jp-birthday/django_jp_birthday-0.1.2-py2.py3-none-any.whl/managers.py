from django.db import models
from django.db.models import Case, When

# from django.db.models.query_utils import Q

from jeraconv import jeraconv

# from math import pow
from datetime import datetime, date, time, timedelta
import pytz

import unicodedata
import jaconv


class JpBirthdayManager(models.Manager):
    """[summary]

    Args:
        models ([type]): [description]
    """

    j2w = jeraconv.J2W()

    def _check_language(self, string):
        l_type = ""
        for ch in string:
            name = unicodedata.name(ch)

            if "CJK UNIFIED" in name:
                l_type = "kanji"
            elif "HIRAGANA" in name:
                l_type = "hiragana"
            elif "KATAKANA" in name:
                l_type = "katakana"
            elif "LATIN" in name:
                l_type = "english"
            else:
                l_type = "none"
        return l_type

    def get_wareki_birthdays(self, wareki: str):
        """[summary]

        Args:
            wareki (str): [description]
        """

        l_type = self._check_language(wareki)

        data = None
        for key, value in self.j2w._J2W__data_dic.items():
            reading = value["reading"]

            reading_jp = reading["jp"]
            reading_en = reading["en"]

            if l_type == "kanji":
                if wareki == key:
                    data = value
            elif l_type == "katakana" or l_type == "hiragana":
                wareki = jaconv.kata2hira(wareki)
                if wareki == reading_jp:
                    data = value
                    break
            elif l_type == "english":
                if wareki == reading_en:
                    data = value
                    break
            else:
                break

        if data:
            start = data["start"]
            end = data["end"]

            start_date = str(start["year"]) + "-"
            start_date += str(start["month"]) + "-"
            start_date += str(start["day"])

            end_date = str(end["year"]) + "-"
            end_date += str(end["month"]) + "-"
            end_date += str(end["day"])

            range_birthdays = self.filter(birthday__range=[start_date, end_date])
            return range_birthdays
        return self.filter(birthday=None)

    def get_upcoming_birthdays(
        self, days=30, after=None, include_day=True, order=True, reverse=False
    ):
        # 今後の誕生日

        birthdays = self.filter()
        birthdays_list = [b.birthday_tm_yday for b in birthdays]

        if after:
            after = datetime.combine(after, time())
            after = pytz.timezone("Asia/Tokyo").localize(after)
        else:
            after = datetime.now()

        days += 1
        if not include_day:
            after = after + timedelta(days=1)
            days -= 1

        after_list = [
            (after + timedelta(days=i)).date().timetuple().tm_yday for i in range(days)
        ]

        idx_list = []
        for a_t in after_list:
            if birthdays_list.count(None) == len(birthdays_list):
                break

            for _ in birthdays_list:
                if a_t in birthdays_list:
                    n = birthdays_list.index(a_t)
                    # print("n", n, a_t, birthdays_list[n])
                    birthdays_list[n] = None
                    idx_list.append(n)

        pk_list = [birthdays[idx].pk for idx in idx_list]

        birthdays = birthdays.filter(pk__in=pk_list)
        if order:
            birthdays = birthdays.order_by(*("birthday",))

        if reverse:
            birthdays = birthdays.reverse()
        return birthdays

    def get_birthdays(self, day=None):
        if not day:
            day = date.today()

        birthdays = self.filter(
            birthday__month__exact=day.month,
            birthday__day__exact=day.day,
        )
        return birthdays

    def order_by_birthday(self, reverse=False):
        """[summary]

        Args:
            reverse (bool, optional): [description]. Defaults to False.

        Returns:
            [type]: [description]
        """

        birthdays_ids = []
        for i in range(1, 13):
            birthdays_ids += [
                b.pk
                for b in self.filter(birthday__month__exact=i).order_by(*("birthday",))
            ]

        cases = [When(id=id, then=pos) for pos, id in enumerate(birthdays_ids)]
        order = Case(*cases)

        birthdays = self.filter(id__in=birthdays_ids).order_by(order)

        if reverse:
            birthdays = birthdays.reverse()
        return birthdays
