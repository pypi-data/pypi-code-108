from django.db import models

from jeraconv import jeraconv
from datetime import date

from jp_birthday.fields import BirthdayField
from jp_birthday.managers import JpBirthdayManager


class BaseBirthdayModel(models.Model):
    """[summary]

    Args:
        models ([type]): [description]
    """

    objects = JpBirthdayManager()
    birthday = BirthdayField()

    w2j = jeraconv.W2J()

    class Meta:
        abstract = True

    @property
    def birthday_month(self):
        return self.birthday.timetuple().tm_mon

    @property
    def birthday_day(self):
        return self.birthday.timetuple().tm_mday

    @property
    def birthday_month_day(self):
        month = self.birthday.timetuple().tm_mon
        if 10 > month:
            month = "0" + str(month)

        day = self.birthday.timetuple().tm_mday
        if 10 > day:
            day = "0" + str(day)

        return str(month) + "-" + str(day)

    @property
    def birthday_tm_yday(self):
        return self.birthday.timetuple().tm_yday

    def _get_wareki_birthday(self) -> dict:
        birthday = self.birthday

        era_date = self.w2j.convert(
            birthday.year, birthday.month, birthday.day, return_type="dict"
        )

        era = era_date["era"]
        era_year = era_date["year"]

        reading = self.w2j._W2J__data_dic[era]["reading"]
        era_en = reading["en"]
        era_en_short = era_en[0]

        return {
            "era": era_en,
            "era_short": era_en_short,
            "year": int(era_year),
            "month": int(birthday.month),
            "day": int(birthday.day),
        }

    def get_wareki_birthday(self, dict_type=False) -> object:
        wareki_birthday = self._get_wareki_birthday()
        if not dict_type:
            wareki = wareki_birthday["era_short"]
            year = str(wareki_birthday["year"])
            month = str(wareki_birthday["month"])
            day = str(wareki_birthday["day"])
            wareki_birthday = wareki + "-" + year + "-" + month + "-" + day
        return wareki_birthday

    def get_age(self) -> int:
        """[summary]

        Returns:
            [type]: [description]
        """
        today = date.today()

        this_year_birthday = date(today.year, self.birthday.month, self.birthday.day)

        age = (today - self.birthday).days
        age = int(age / 365)

        if this_year_birthday > today:
            age -= 1

        return age


class BirthdayModel(BaseBirthdayModel):
    """[summary]

    Args:
        BaseBirthdayModel ([type]): [description]
    """

    class Meta:
        abstract = True
