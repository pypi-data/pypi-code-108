from dataclasses import dataclass
from datetime import date

from daybook.domain.model import Reader, Book, PageRange


class Command:
    pass


@dataclass
class CreateReadingLog(Command):
    reader: Reader


@dataclass
class AddEntry(Command):
    date: date
    reader: Reader
    book: Book
    pages: PageRange


@dataclass
class AddEntryUsingBookKey(Command):
    date: date
    reader: Reader
    book_key: int
    pages: PageRange


@dataclass
class DelEntry(Command):
    reader: Reader
    id: int


@dataclass
class UpdateEntry(Command):
    id: int
    entry_date: date
    reader: Reader
    book: Book
    pages: PageRange


@dataclass
class UpdateBook(Command):
    reader: Reader
    book: Book


@dataclass
class UpdateReadingLog(Command):
    old_name: str
    new_name: str
