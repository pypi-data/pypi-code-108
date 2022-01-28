import re
import datetime
import logging
import xml.etree.ElementTree as ET

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

from .relaton_bib import parse_date


class BibliographicDateType(str, Enum):
    PUBLISHED = "published"
    ACCESSED = "accessed"
    CREATED = "created"
    IMPLEMENTED = "implemented"
    OBSOLETED = "obsoleted"
    CONFIRMED = "confirmed"
    UPDATED = "updated"
    ISSUED = "issued"
    TRANSMITTED = "transmitted"
    COPIED = "copied"
    UNCHANGED = "unchanged"
    CIRCULATED = "circulated"
    ADAPTED = "adapted"
    VOTE_STARTE = "vote-started"
    VOTE_ENDED = "vote-ended"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclass
class BibliographicDate:
    NO_YEAR: ClassVar[str] = "--"

    type: str
    on: datetime.date = None
    from_: datetime.date = None
    to: datetime.date = None

    def __post_init__(self):
        if not BibliographicDateType.has_value(self.type):
            logging.warning(
                f"[relaton-bib] invalid bibliographic date type: {self.type}")

        if isinstance(self.type, BibliographicDateType):
            self.type = self.type.value

        if not (self.on or self.from_):
            raise ValueError("expected on or from_ argument")

        if self.on and isinstance(self.on, str):
            self.on = parse_date(self.on)

        if self.from_ and isinstance(self.from_, str):
            self.from_ = parse_date(self.from_)

        if self.to and isinstance(self.to, str):
            self.to = parse_date(self.to)

    def to_xml(self, parent, opts={}):
        name = "date"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        result.attrib["type"] = self.type
        date_format = opts.get("date_format")
        no_year = opts.get("no_year")
        if self.on:
            on_node = ET.SubElement(result, "on")
            if no_year:
                on_node.text = self.NO_YEAR
            else:
                on_node.text = self.date_format(self.on, date_format)
        elif self.from_:
            form_node = ET.SubElement(result, "from")
            if no_year:
                form_node.text = self.NO_YEAR
            else:
                form_node.text = self.date_format(self.from_, date_format)
                if self.to:
                    to_node = ET.SubElement(result, "to")
                    to_node.text = self.date_format(self.to, date_format)

        return result

    def to_asciibib(self, prefix="", count=1):
        pref = prefix + "." if prefix else prefix
        out = [f"{pref}date::"] if count > 1 else []
        out.append(f"{pref}date.type:: {self.type}")
        if self.on:
            out.append(f"{pref}date.on:: {self.on}")
        if self.from_:
            out.append(f"{pref}date.from:: {self.from_}")
        if self.to:
            out.append(f"{pref}date.to:: #{self.to}")
        return "\n".join(out)

    def value(self, prop="on", part=None) -> str:
        return self._process_date(getattr(self, prop), part)

    def part(self, part="year") -> str:
        return self.value("on", part) or self.value("from", part) \
            or self.value("to", part)

    def date_format(self, date, fmt_name=None):
        if fmt_name == "short":
            fmt = "%Y-%m"
        elif fmt_name == "full":
            fmt = "%Y-%m-%d"
        else:
            return date

        date = self._parse_date(date)

        return date.strftime(fmt) if isinstance(date, datetime.date) else date

    def _process_date(self, date, part=None):
        if not (date and part):
            return date

        date = self._parse_date(date)

        if part == "date":
            return date

        return getattr(date, part) if isinstance(date, datetime.date) else date

    def _parse_date(self, date):
        if re.match(r"^\d{4}-\d{2}-\d{2}", date):
            return datetime.datetime.strptime(date, "%Y-%m-%d")  # 2012-02-11
        elif re.match(r"^\d{4}-\d{2}", date):
            return datetime.datetime.strptime(date, "%Y-%m")  # 2012-02
        elif re.match(r"^\d{4}", date):
            return datetime.datetime.strptime(date, "%Y")  # 2012
        else:
            return date
