from abc import ABC, abstractmethod

from daybook.domain.model import (
    Author,
    Book,
    BookSubtitle,
    BookTitle,
    PageRange,
    Reader,
    ReadingLog,
)


class AbstractReadingLogRepository(ABC):
    def __init__(self) -> None:
        self.seen = set()

    def add(self, reading_log: ReadingLog) -> bool:
        self.seen.add(reading_log)
        return self._add(reading_log)

    def get(self, reader: Reader):
        reading_log = self._get(reader)
        if reading_log:
            self.seen.add(reading_log)
        return reading_log

    @abstractmethod
    def _add(self, reading_log: ReadingLog) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _get(self, reader: Reader) -> ReadingLog:
        raise NotImplementedError


class FakeRepository(AbstractReadingLogRepository):
    def __init__(self) -> None:
        super().__init__()
        self._reading_logs = set()

    def _add(self, reading_log: ReadingLog) -> bool:
        return self._reading_logs.add(reading_log)

    def _get(self, reader: Reader) -> ReadingLog:
        result = None
        if len(self._reading_logs) > 0:
            for reading_log in self._reading_logs:
                if reading_log.reader == reader:
                    result = reading_log
                    break
        return result

    def list(self):
        return list(self._reading_logs)


class SqlRepository(AbstractReadingLogRepository):
    def __init__(self, cursor) -> None:
        super().__init__()
        self.cursor = cursor
        self.cache = {}

    def _add(self, reading_log: ReadingLog) -> bool:
        curr_reading_log = self._get(reading_log.reader)
        try:
            # reader
            add_reader = f"INSERT OR IGNORE INTO reading_log(reader) VALUES('{reading_log.reader}');"
            self.cursor.execute(add_reader)
            # for each entry
            for entry in reading_log.entries:
                if not entry.id:
                    # add book
                    add_book = f"INSERT OR IGNORE INTO book(title, author, subtitle) VALUES('{entry.book.title}', '{entry.book.author}', '{entry.book.subtitle}');"
                    self.cursor.execute(add_book)
                    add_entry = f"INSERT OR IGNORE INTO reading_log_entry(date, reader, book_title, book_author, start_page, end_page) VALUES('{entry.date}', '{entry.reader}', '{entry.book.title}', '{entry.book.author}', '{entry.pages.start}', '{entry.pages.end}');"
                    self.cursor.execute(add_entry)
            deleted = curr_reading_log.entries.difference(reading_log.entries)
            for entry in deleted:
                del_entry = f"DELETE FROM reading_log_entry WHERE id = {entry.id};"
                self.cursor.execute(del_entry)
            return True
        except Exception as ex:
            print(ex)
        return False

    def _get(self, reader: Reader) -> ReadingLog:
        reading_log = ReadingLog(reader)
        try:
            get_entries = f"SELECT id, date, book_title, book_author, start_page, end_page FROM reading_log_entry WHERE reader =  '{reader}';"
            self.cursor.execute(get_entries)
            for (
                id,
                date,
                book_title,
                book_author,
                start_page,
                end_page,
            ) in self.cursor:
                book = Book(Author(book_author), BookTitle(book_title), None)
                pages = PageRange(start_page, end_page)
                reading_log.add_entry(date, book, pages, id)
        except Exception as ex:
            print(ex)
        return reading_log


class SQLiteRepository(AbstractReadingLogRepository):
    def __init__(self, cursor) -> None:
        super().__init__()
        self.cursor = cursor
        self.cache = {}

    def _add(self, reading_log: ReadingLog) -> bool:
        curr_reading_log = self._get_by_id(reading_log.id) if reading_log.id else None

        try:
            if reading_log.id:
                sql_statement = f"UPDATE reading_log SET reader = '{reading_log.reader}' WHERE id = {reading_log.id};"
            else:
                sql_statement = f"INSERT OR IGNORE INTO reading_log(reader) VALUES('{reading_log.reader}');"

            for entry_id in reading_log.entries:
                if curr_reading_log and curr_reading_log.entries.get(entry_id):
                    old_val = curr_reading_log.entries.get(entry_id)
                    new_val = reading_log.entries.get(entry_id)
                    if old_val != new_val:
                        # update
                        sql_statement += f"UPDATE reading_log_entry SET date = '{new_val.date}', reader = '{new_val.reader}', book_title = '{new_val.book.title}', book_author = '{new_val.book.author}', start_page = {new_val.pages.start}, end_page = {new_val.pages.end} WHERE id = {old_val.id};"
                        sql_statement += f"UPDATE book SET author = '{new_val.book.author}', title = '{new_val.book.title}', subtitle = '{new_val.book.subtitle}' WHERE key = {old_val.book.key};"
                else:
                    # add
                    new_entry = reading_log.entries.get(entry_id)
                    sql_statement += f"INSERT OR IGNORE INTO book(title, author, subtitle, key) VALUES('{new_entry.book.title}', '{new_entry.book.author}', '{new_entry.book.subtitle}', (SELECT IFNULL(MAX(key), 0) + 1 FROM book));"
                    sql_statement += f"INSERT OR IGNORE INTO reading_log_entry(date, reader, book_title, book_author, start_page, end_page) VALUES('{new_entry.date}', '{new_entry.reader}', '{new_entry.book.title}', '{new_entry.book.author}', '{new_entry.pages.start}', '{new_entry.pages.end}');"
            if curr_reading_log:
                for entry_id in curr_reading_log.entries:
                    if curr_reading_log.entries.get(
                        entry_id
                    ) and not reading_log.entries.get(entry_id):
                        # del
                        deleted_entry = curr_reading_log.entries.get(entry_id)
                        sql_statement += (
                            f"DELETE FROM reading_log_entry WHERE id = {deleted_entry.id};"
                        )

            self.cursor.executescript(sql_statement)
            return True
        except Exception as ex:
            print(ex)
        return False

    def load_avail_books(self, reading_log: ReadingLog):
        get_books_records = "SELECT author, title, subtitle, key FROM book;"
        self.cursor.execute(get_books_records)
        book_records = self.cursor.fetchall()
        for book_record in book_records:
            book = Book(
                Author(book_record[0]),
                BookTitle(book_record[1]),
                BookSubtitle(book_record[2]),
                book_record[3],
            )
            reading_log.add_available_book(book)

    def load_entries(self, reading_log: ReadingLog):
        get_entries = f"SELECT id, date, book_title, book_author, start_page, end_page, key FROM reading_log_entry, book AS b WHERE book_title = b.title AND book_author = b.author AND reader =  '{reading_log.reader}';"
        self.cursor.execute(get_entries)
        for (
            id,
            date,
            book_title,
            book_author,
            start_page,
            end_page,
            key,
        ) in self.cursor:
            book_record = Book(
                Author(book_author), BookTitle(book_title), None, key
            )
            pages = PageRange(start_page, end_page)
            reading_log.add_entry(date, book_record, pages, id)

    def _get(self, reader: Reader) -> ReadingLog:
        reading_log = ReadingLog(reader)
        try:
            get_reading_log_id = f"SELECT id FROM reading_log WHERE reader = '{reader}';"
            self.cursor.execute(get_reading_log_id)
            reading_log.id = self.cursor.fetchone()[0]
            self.load_avail_books(reading_log)
            self.load_entries(reading_log)
        except Exception as ex:
            print(ex)
        return reading_log

    def _get_by_id(self, id: int):
        reading_log = None
        try:
            get_reader_name = f"SELECT reader FROM reading_log WHERE id = '{id}';"
            self.cursor.execute(get_reader_name)
            reader_name = self.cursor.fetchone()[0]
            reading_log = ReadingLog(reader_name, id)
            self.load_avail_books(reading_log)
            self.load_entries(reading_log)
        except Exception as ex:
            print(ex)
        return reading_log
