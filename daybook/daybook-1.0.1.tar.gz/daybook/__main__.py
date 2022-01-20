import sys
import argparse
from datetime import datetime
from versioneer import get_version
from daybook.service_layer.services import (
    add_entry,
    del_entry,
    add_entry_using_book_key,
    update_entry,
    update_book,
    update_reading_log
)
from daybook.views import list_entries, search_books, list_logs, get_entry, get_book_record, get_reading_log_record
from daybook.service_layer.unit_of_work import SQLiteUnitOfWork
from daybook.settings import (
    get_default_reading_log_reader,
    get_valid_reader,
    set_default_reading_log_reader,
)


# sub-command functions
def add_cmd(args, uow):
    if args.book_key is None:
        add_entry(
            args.date,
            args.reader,
            args.author,
            args.title,
            args.start,
            args.end,
            uow,
        )
    else:
        add_entry_using_book_key(
            args.date, args.reader, args.book_key, args.start, args.end, uow
        )


def del_cmd(args, uow):
    del_entry(args.entry_id, args.reader, uow)


def books_cmd(args, uow):
    search_string = str(args.query) if args.query else None
    books = search_books(uow, search_string)

    print()
    title = "Books"
    print(title)
    print("=" * len(title))

    for book in books:
        print(
            f'Key {book[0]}, Author: {book[1]}, Title: "{book[2]}", Subtitle: "{book[3]}"'
        )
    print()


def entries_cmd(args, uow):
    reader_name, start_date, entries = list_entries(
        uow, args.reader, args.from_date, args.to_date
    )
    title = f"\nReading Log for {reader_name} since {start_date}"
    print(title)
    print("=" * (len(title) - 1))

    for entry in entries:
        print(
            f'ID {entry[0]}, Date: {entry[1]}, Book: "{entry[2]}" by {entry[3]}, Pages: {entry[4]}-{entry[5]}'
        )
    print()


def settings_cmd(args, uow):
    if args.get_default_reading_log:
        reader = get_default_reading_log_reader()
        print(reader)
    elif args.default_reading_log:
        reader = get_valid_reader(args.default_reading_log)
        set_default_reading_log_reader(reader)


def logs_cmd(args, uow):
    title = "\nReading Logs"

    print(title)
    print("=" * (len(title) - 1))

    logs_records = list_logs(uow)
    for log_record in logs_records:
        print(f"ID: {log_record[0]}, Name: {log_record[1]}")
    print()


def parse_date_str(date_str: str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def get_valid_str(old_val: str, new_val: str) -> str:
    result = None
    if not new_val:
        result = old_val
    elif len(new_val) <= 0:
        result = ""
    else:
        result = new_val
    return result


def get_valid_int(old_val: str, new_val: str) -> int:
    result = None
    if not new_val:
        result = old_val
    elif len(new_val) <= 0:
        result = 0
    else:
        result = int(new_val)
    return result


def update_cmd(args, uow):
    if args.entry_id:
        entry_id = int(args.entry_id)
        (
            curr_entry_date,
            curr_book_title,
            curr_book_author,
            curr_page_start,
            curr_page_end,
        ) = get_entry(uow, entry_id)

        new_date_str = input(f"Date [{curr_entry_date}]: ")
        new_date = (
            parse_date_str(new_date_str)
            if new_date_str
            else parse_date_str(curr_entry_date)
        )

        new_book_title = input(f"Book Title [{curr_book_title}]: ")
        new_book_title = get_valid_str(curr_book_title, new_book_title)

        new_book_author = input(f"Book Author [{curr_book_author}]: ")
        new_book_author = get_valid_str(curr_book_author, new_book_author)

        new_page_start = input(f"Start Page: [{curr_page_start}]: ")
        new_page_start = get_valid_int(curr_page_start, new_page_start)

        new_page_end = input(f"End Page [{curr_page_end}]: ")
        new_page_end = get_valid_int(curr_page_end, new_page_end)

        update_entry(
            entry_id,
            new_date,
            args.reader,
            new_book_author,
            new_book_title,
            new_page_start,
            new_page_end,
            uow,
        )

    elif args.book_key:
        book_key = int(args.book_key)
        curr_author, curr_title, curr_subtitle = get_book_record(uow, book_key)

        new_author_input = input(f"Author [{curr_author}]: ")
        new_author = get_valid_str(curr_author, new_author_input)

        new_title_input = input(f"Title [{curr_title}]: ")
        new_title = get_valid_str(curr_title, new_title_input)

        new_subtitle_input = input(f"Subtitle [{curr_subtitle}]: ")
        new_subtitle = get_valid_str(curr_subtitle, new_subtitle_input)

        update_book(args.reader, book_key, new_author, new_title, new_subtitle, uow)

    elif args.log_id:
        log_id = int(args.log_id)
        curr_log_name, = get_reading_log_record(uow, log_id)

        new_reading_log_name_input = input(f"Reading Log [{curr_log_name}]: ")
        new_reading_log_name = get_valid_str(curr_log_name, new_reading_log_name_input)

        update_reading_log(curr_log_name, new_reading_log_name, uow)


def main():
    # create top-level parser
    parser = argparse.ArgumentParser(
        prog="daybook",
        description=f"daybook is a reading log app made for the command-line interface (cli). version: {get_version()}",
        add_help=True,
    )
    parser.add_argument(
        "-v",
        "--version",
        dest="print_version",
        action="store_true",
        help="print the current version",
    )
    subparsers = parser.add_subparsers()

    # create parser for add command
    add_cmd_parser = subparsers.add_parser("add")
    reader_options = add_cmd_parser.add_argument_group(title="reading log")
    reader_options.add_argument(
        "-r",
        "--reader",
        dest="reader",
        type=str,
    )
    add_book_options = add_cmd_parser.add_argument_group(title="book")
    add_book_options.add_argument(
        "-k",
        "--key",
        dest="book_key",
        type=int,
        help="this can be used instead of title and author",
    )
    add_book_options.add_argument(
        "-t", "--title", dest="title", type=str, help="requires author"
    )
    add_book_options.add_argument(
        "-a", "--author", dest="author", type=str, help="requires title"
    )
    date_options = add_cmd_parser.add_argument_group(title="date")
    date_options.add_argument(
        "-d",
        "--date",
        dest="date",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
    )
    pages = add_cmd_parser.add_argument_group(title="pages")
    pages.add_argument(
        "--start",
        dest="start",
        type=int,
    )
    pages.add_argument("--end", dest="end", type=int, required=True)
    add_cmd_parser.set_defaults(func=add_cmd)

    # create parser for del command
    del_cmd_parser = subparsers.add_parser("del")
    reader_options = del_cmd_parser.add_argument_group(title="reading log")
    reader_options.add_argument(
        "-r",
        "--reader",
        dest="reader",
        type=str,
    )
    del_entry_options = del_cmd_parser.add_argument_group(title="entry")
    del_entry_options.add_argument(
        "-e", "--entry", dest="entry_id", type=int, required=True
    )
    del_cmd_parser.set_defaults(func=del_cmd)

    # create parser for books command
    books_cmd_parser = subparsers.add_parser("books")
    books_cmd_parser.add_argument(
        "-q",
        "--query",
        dest="query",
        type=str,
        help="this query returns all books containing this value in their titles, authors, or subtitles",
    )
    books_cmd_parser.set_defaults(func=books_cmd)

    # create parser for entries command
    entries_cmd_parser = subparsers.add_parser("entries")
    entries_reader_options = entries_cmd_parser.add_argument_group(title="reading log")
    entries_reader_options.add_argument(
        "-r",
        "--reader",
        dest="reader",
        type=str,
    )
    entries_date_options = entries_cmd_parser.add_argument_group(title="date range")
    entries_date_options.add_argument(
        "--from",
        dest="from_date",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
    )
    entries_date_options.add_argument(
        "--to", dest="to_date", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date()
    )
    entries_cmd_parser.set_defaults(func=entries_cmd)

    # create parser for logs command
    logs_cmd_parser = subparsers.add_parser("logs")
    logs_cmd_parser.set_defaults(func=logs_cmd)

    # create parser for update command
    update_cmd_parser = subparsers.add_parser("update")
    update_cmd_parser.add_argument("-r", "--reader", dest="reader", type=str)
    update_cmd_group = update_cmd_parser.add_mutually_exclusive_group(required=True)
    update_cmd_group.add_argument(
        "-e", "--entry", dest="entry_id", type=int, metavar="ENTRY_ID"
    )
    update_cmd_group.add_argument(
        "-b", "--book", dest="book_key", type=int, metavar="KEY"
    )
    update_cmd_group.add_argument(
        "-l", "--log", dest="log_id", type=int, metavar="KEY"
    )
    update_cmd_parser.set_defaults(func=update_cmd)

    # create parser for settings command
    settings_cmd_parser = subparsers.add_parser("config")
    reading_log_options = settings_cmd_parser.add_argument_group(title="reading log")
    reading_log_options.add_argument(
        "--get-default-reading-log",
        dest="get_default_reading_log",
        action="store_true",
    )
    reading_log_options.add_argument(
        "--set-default-reading-log",
        dest="default_reading_log",
        type=str,
    )
    settings_cmd_parser.set_defaults(func=settings_cmd)

    args = parser.parse_args()
    if args.print_version:
        print(f"daybook version {get_version()}")
    else:
        uow = SQLiteUnitOfWork()
        args.func(args, uow)


if __name__ == "__main__":
    sys.exit(main())
