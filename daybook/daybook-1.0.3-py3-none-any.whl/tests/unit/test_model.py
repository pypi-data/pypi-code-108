import uuid
from datetime import datetime, timedelta

from daybook.domain.model import (
    PageRange,
    Reader,
    ReadingLog,
    Book,
    ReadingLogEntry,
)
from .config import (
    TEST_AUTHOR,
    TEST_BOOK,
    TEST_BOOK_TITLE,
    TEST_BOOK_SUBTITLE,
    TEST_DATE,
    TEST_PAGES,
    TEST_READER_1,
    TEST_READER_2,
    TEST_ENTRY,
)


def gen_id_string():
    return str(uuid.uuid4())


class TestReadingLog:
    def test_each_reading_log_has_reader(self):
        reading_log = ReadingLog(TEST_READER_1)
        assert TEST_READER_1 == reading_log.reader

    def test_update_reader(self):
        reading_log = ReadingLog(TEST_READER_1)
        new_reader_name = Reader("Leonardo Bigollo Pisano")
        reading_log.update_reader(new_reader_name)
        assert new_reader_name == reading_log.reader

    def test_equality(self):
        reading_log_1 = ReadingLog(TEST_READER_1)
        reading_log_2 = ReadingLog(TEST_READER_1)
        assert reading_log_1 == reading_log_2

    def test_inequality_reader(self):
        reading_log_1 = ReadingLog(TEST_READER_1)
        reading_log_2 = ReadingLog(TEST_READER_2)
        assert reading_log_1 != reading_log_2

    def test_sortable_by_reader(self):
        reading_log_1 = ReadingLog(Reader("A"))
        reading_log_2 = ReadingLog(Reader("B"))
        assert reading_log_1 < reading_log_2

    def test_add_entry(self):
        reading_log = ReadingLog(TEST_READER_1)
        entry = ReadingLogEntry(None, TEST_DATE, TEST_READER_1, TEST_BOOK, TEST_PAGES)
        assert reading_log.add_entry(TEST_DATE, TEST_BOOK, TEST_PAGES) == entry
        assert entry in reading_log.entries.values()

    def test_del_entry(self):
        reading_log = ReadingLog(TEST_READER_1)
        reading_log.add_entry(TEST_DATE, TEST_BOOK, TEST_PAGES)
        entry = reading_log.delete_entry(None)
        assert entry.id is None


class TestBook:
    def test_book_has_title(self):
        book = Book(TEST_AUTHOR, TEST_BOOK_TITLE, TEST_BOOK_SUBTITLE)
        assert TEST_BOOK_TITLE == book.title

    def test_book_has_author(self):
        book = Book(TEST_AUTHOR, TEST_BOOK_TITLE, TEST_BOOK_SUBTITLE)
        assert TEST_AUTHOR == book.author

    def test_book_equality(self):
        book_1 = Book(TEST_AUTHOR, TEST_BOOK_TITLE, TEST_BOOK_SUBTITLE)
        book_2 = Book(TEST_AUTHOR, TEST_BOOK_TITLE, TEST_BOOK_SUBTITLE)
        assert book_1 == book_2

    def test_book_inequality_author(self):
        book_1 = Book(TEST_AUTHOR, TEST_BOOK_TITLE, TEST_BOOK_SUBTITLE)
        book_2 = Book(TEST_AUTHOR + "DIFF", TEST_BOOK_TITLE, TEST_BOOK_SUBTITLE)
        assert book_1 != book_2

    def test_book_inequality_title(self):
        book_1 = Book(TEST_AUTHOR, TEST_BOOK_TITLE, TEST_BOOK_SUBTITLE)
        book_2 = Book(TEST_AUTHOR, TEST_BOOK_TITLE + "DIFF", TEST_BOOK_SUBTITLE)
        assert book_1 != book_2

    def test_book_inequality_subtitle(self):
        book_1 = Book(TEST_AUTHOR, TEST_BOOK_TITLE, TEST_BOOK_SUBTITLE)
        book_2 = Book(TEST_AUTHOR, TEST_BOOK_TITLE, TEST_BOOK_SUBTITLE + "DIFF")
        assert book_1 != book_2

    def test_books_are_sortable_by_title(self):
        book_1 = Book(TEST_AUTHOR, "A", TEST_BOOK_SUBTITLE)
        book_2 = Book(TEST_AUTHOR, "B", TEST_BOOK_SUBTITLE)
        assert book_1.title < book_2.title


class TestReadingLogEntry:
    def test_has_date(self):
        assert TEST_ENTRY.date == TEST_DATE

    def test_has_reader(self):
        assert TEST_ENTRY.reader == TEST_READER_1

    def test_has_book(self):
        assert TEST_ENTRY.book == TEST_BOOK

    def test_has_pages(self):
        assert TEST_ENTRY.pages == TEST_PAGES

    def test_equality(self):
        entry = ReadingLogEntry(None, TEST_DATE, TEST_READER_1, TEST_BOOK, TEST_PAGES)
        assert TEST_ENTRY == entry

    def test_inequality_date(self):
        date_diff = (datetime.now() + timedelta(days=1)).date()
        entry = ReadingLogEntry(None, date_diff, TEST_READER_1, TEST_BOOK, TEST_PAGES)
        assert TEST_ENTRY != entry

    def test_inequality_reader(self):
        reader_diff = TEST_READER_1 + "DIFF"
        entry = ReadingLogEntry(None, TEST_DATE, reader_diff, TEST_BOOK, TEST_PAGES)
        assert TEST_ENTRY != entry

    def test_inequality_book(self):
        book_diff = Book(TEST_BOOK.author, TEST_BOOK.title + "DIFF", TEST_BOOK.subtitle)
        entry = ReadingLogEntry(None, TEST_DATE, TEST_READER_1, book_diff, TEST_PAGES)
        assert TEST_ENTRY != entry

    def test_inequality_pages(self):
        pages_diff = PageRange(100, 120)
        entry = ReadingLogEntry(None, TEST_DATE, TEST_READER_1, TEST_BOOK, pages_diff)
        assert TEST_ENTRY != entry
