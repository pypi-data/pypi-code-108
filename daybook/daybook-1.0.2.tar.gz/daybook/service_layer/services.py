from datetime import date

from daybook.domain.model import Reader, Author, BookTitle, BookSubtitle, Book, PageRange
from daybook.service_layer.unit_of_work import AbstractUnitOfWork
import daybook.service_layer.messagebus as msgbus
from daybook.domain.commands import (
    AddEntry,
    DelEntry,
    AddEntryUsingBookKey,
    UpdateEntry,
    UpdateBook,
    UpdateReadingLog,
)


def add_entry(
    entry_date: date,
    reader_name: str,
    author_name: str,
    book_title: str,
    start_page: int,
    end_page: int,
    uow: AbstractUnitOfWork,
):
    reader = Reader(reader_name)
    author = Author(author_name)
    title = BookTitle(book_title)
    subtitle = BookSubtitle("")
    book = Book(author, title, subtitle, None)
    pages = PageRange(start_page, end_page)
    cmd = AddEntry(entry_date, reader, book, pages)
    msgbus.handle(cmd, uow)


def add_entry_using_book_key(
    entry_date: date,
    reader_name: str,
    book_key: int,
    start_page: int,
    end_page: int,
    uow: AbstractUnitOfWork,
):
    reader = Reader(reader_name)
    pages = PageRange(start_page, end_page)
    cmd = AddEntryUsingBookKey(entry_date, reader, book_key, pages)
    msgbus.handle(cmd, uow)


def del_entry(entry_id: int, reader_name: str, uow: AbstractUnitOfWork):
    reader = Reader(reader_name)
    cmd = DelEntry(reader, entry_id)
    msgbus.handle(cmd, uow)


def update_entry(
    entry_id: int,
    entry_date: date,
    reader_name: str,
    author_name: str,
    book_title: str,
    start_page: int,
    end_page: int,
    uow: AbstractUnitOfWork,
):
    reader = Reader(reader_name)
    author = Author(author_name)
    title = BookTitle(book_title)
    subtitle = BookSubtitle("")
    book = Book(author, title, subtitle, None)
    pages = PageRange(start_page, end_page)
    cmd = UpdateEntry(entry_id, entry_date, reader, book, pages)
    msgbus.handle(cmd, uow)


def update_book(
    reader_name: str,
    book_key: int,
    author_name: str,
    book_title: str,
    book_subtitle: str,
    uow: AbstractUnitOfWork,
):
    reader = Reader(reader_name)
    author = Author(author_name)
    title = BookTitle(book_title)
    subtitle = BookSubtitle(book_subtitle)
    book = Book(author, title, subtitle, book_key)
    cmd = UpdateBook(reader, book)
    msgbus.handle(cmd, uow)


def update_reading_log(
    old_name: str,
    new_name: str,
    uow: AbstractUnitOfWork
):
    cmd = UpdateReadingLog(old_name, new_name)
    msgbus.handle(cmd, uow)
