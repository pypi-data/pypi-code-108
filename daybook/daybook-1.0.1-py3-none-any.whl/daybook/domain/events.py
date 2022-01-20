from dataclasses import dataclass
from datetime import date
from daybook.domain.model import Reader, Book, PageRange


class Event:
    pass


@dataclass
class ReadingLogCreated(Event):
    reader: Reader


@dataclass
class EntryAdded(Event):
    date: date
    reader: Reader
    book: Book
    pages: PageRange


@dataclass
class EntryUpdated(Event):
    id: int
    date: date
    reader: Reader
    book: Book
    pages: PageRange


@dataclass
class EntryDeleted(Event):
    id: int
    date: date
    reader: Reader
    book: Book
    pages: PageRange


@dataclass
class ReadingLogUsed(Event):
    reader: Reader


@dataclass
class BookUpdated(Event):
    old_val: Book
    new_val: Book


@dataclass
class ReadingLogUpdated(Event):
    old_val: Reader
    new_val: Reader
