from datetime import date, timedelta
from schema import Or, Schema, Use, Optional
from random import randint

from .reference import to_ref
from .base import FieldGenerator


class DateFieldGenerator(FieldGenerator):
    option_schema = Schema({
        "min": Or(Use(to_ref), Use(date.fromisoformat)),
        "max": Or(Use(to_ref), Use(date.fromisoformat)),
        Optional("delta_min", default=0): Use(int),
        Optional("delta_max"): Use(int),
        Optional("delta"): Use(int)
    })

    def validate(self):
        self.options = self.option_schema.validate(self.options)

        delta = self.options.get("delta") is not None
        delta_min = self.options.get("delta_min") is not None
        delta_max = self.options.get("delta_max") is not None

        if delta and (delta_min or delta_max):
            raise Exception(
                f"Provide either the 'delta' option or the options 'delta_min' and 'delta_max'")

    def generate(self, **kwargs):
        options = self.prepare_options(**kwargs)
        min = options["min"]
        max = options["max"]

        if max < min:
            raise Exception(
                f"Option 'max' ({max}) must be equal or larger than 'min' ({min})")

        delta = options.get("delta")

        if delta is not None:
            add_days = delta
        else:
            delta_min = options["delta_min"]
            delta_max = options.get("delta_max", delta_min)

            if delta_max < delta_min:
                raise Exception(
                    f"'delta_max' ({delta_max}) must be equal or larger than 'delta_min' ({delta_min})")

            add_days = randint(delta_min, delta_max)

        day_difference = (max - min).days
        value = min + timedelta(days=randint(0, day_difference) + add_days)

        return value
