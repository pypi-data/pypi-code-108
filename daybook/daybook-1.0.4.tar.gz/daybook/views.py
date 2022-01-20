from datetime import date

from daybook.service_layer.unit_of_work import AbstractUnitOfWork
from daybook.settings import get_valid_reader, get_current_reading_period_start


def list_entries(
    uow: AbstractUnitOfWork, reader_name: str, start_date: date, end_date: date = None
):
    entries = None
    reader = get_valid_reader(reader_name)
    if not start_date:
        start_date = get_current_reading_period_start()
    with uow:
        if end_date:
            query = f"SELECT id, date, book_title, book_author, start_page, end_page FROM reading_log_entry WHERE reader = '{reader}' AND (date BETWEEN '{start_date}' AND '{end_date}') ORDER BY date DESC, start_page DESC;"
        else:
            query = f"SELECT id, date, book_title, book_author, start_page, end_page FROM reading_log_entry WHERE reader = '{reader}' AND date >= '{start_date}' ORDER BY date DESC, start_page DESC;"
        uow.session.execute(query)
        entries = uow.session.fetchall()
    return reader, start_date, entries


def get_entry(uow: AbstractUnitOfWork, entry_id: int):
    entry = None
    if entry_id:
        query = f"SELECT date, book_title, book_author, start_page, end_page FROM reading_log_entry WHERE id = '{entry_id}'"
        with uow:
            uow.session.execute(query)
            entry = uow.session.fetchone()
    return entry


def get_book_record(uow: AbstractUnitOfWork, book_key: int):
    book_record = None
    if book_key:
        query = f"SELECT author, title, subtitle FROM book WHERE key = {book_key}"
        with uow:
            uow.session.execute(query)
            book_record = uow.session.fetchone()
    return book_record


def get_reading_log_record(uow: AbstractUnitOfWork, log_id: int):
    reader_log_record = None
    if log_id:
        query = f"SELECT reader FROM reading_log WHERE id = '{log_id}';"
        with uow:
            uow.session.execute(query)
            reader_log_record = uow.session.fetchone()
    return reader_log_record


def search_books(uow: AbstractUnitOfWork, search_string: str):
    books = None
    if search_string:
        query = f"SELECT key, author, title, subtitle FROM book WHERE title LIKE '%{search_string}%' OR author LIKE '%{search_string}%' OR subtitle LIKE '%{search_string}%';"
    else:
        query = "SELECT key, author, title, subtitle FROM book;"
    with uow:
        uow.session.execute(query)
        books = uow.session.fetchall()
    return books


def list_logs(uow: AbstractUnitOfWork):
    query = "SELECT id, reader FROM reading_log;"
    with uow:
        uow.session.execute(query)
        logs = uow.session.fetchall()
    return logs
