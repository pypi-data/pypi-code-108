from datetime import date

from daybook.domain.model import (
    Reader,
    Author,
    BookTitle,
    BookSubtitle,
    Book,
    PageRange,
    ReadingLogEntry,
)

TEST_READER_1 = Reader("Leonhard Euler")
TEST_READER_2 = Reader("Leonardo Bigollo Pisano")
TEST_AUTHOR = Author("Carl Friedrich Gauss")
TEST_BOOK_TITLE = BookTitle("Disquisitiones Arithmeticae")
TEST_BOOK_SUBTITLE = BookSubtitle("")
TEST_BOOK = Book(TEST_BOOK_TITLE, TEST_AUTHOR, TEST_BOOK_SUBTITLE)
TEST_PAGES = PageRange(1, 42)
TEST_DATE = date.today()
TEST_ENTRY = ReadingLogEntry(None, TEST_DATE, TEST_READER_1, TEST_BOOK, TEST_PAGES)
