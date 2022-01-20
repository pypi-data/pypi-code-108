from daybook.domain.commands import Command
from daybook.domain.events import (
    EntryDeleted,
    Event,
    ReadingLogCreated,
    EntryAdded,
    ReadingLogUsed,
    EntryUpdated,
    BookUpdated,
    ReadingLogUpdated,
)
from daybook.service_layer.unit_of_work import AbstractUnitOfWork
import daybook.service_layer.messagebus as msgbus
from daybook.domain.model import ReadingLog
from daybook.settings import get_valid_reader, save_default_reader_to_settings


def print_reader(event: ReadingLogCreated, uow: AbstractUnitOfWork):
    print(f"New reading log created for {event.reader}")


def entry_added_event_handler(event: EntryAdded, uow: AbstractUnitOfWork):
    print(
        f"Entry added: {event.date}, {event.reader}, {event.book.title}, {event.book.author}, {event.pages.start}, {event.pages.end}"
    )


def print_event(event: Event, uow: AbstractUnitOfWork):
    print(event)


def update_last_reading_log_used(event: Event, uow: AbstractUnitOfWork):
    save_default_reader_to_settings(event.reader)


def create_reading_log_handler(cmd: Command, uow: AbstractUnitOfWork):
    created = False
    reader = get_valid_reader(cmd.reader)
    with uow:
        reading_log = ReadingLog(reader)
        created = uow.reading_logs.add(reading_log)
        uow.commit()
        reading_log_used = ReadingLogUsed(reading_log.reader)
        msgbus.handle(reading_log_used, uow)
        if created:
            event = ReadingLogCreated(reader)
            msgbus.handle(event, uow)


def add_entry_cmd_handler(cmd: Command, uow: AbstractUnitOfWork):
    reader = get_valid_reader(cmd.reader)
    with uow:
        reading_log = uow.reading_logs.get(reader)
        uow.commit()
        if reading_log:
            reading_log_used = ReadingLogUsed(reading_log.reader)
            msgbus.handle(reading_log_used, uow)
            entry = reading_log.add_entry(cmd.date, cmd.book, cmd.pages)
            if entry:
                uow.reading_logs.add(reading_log)
                uow.commit()
                entry_added = EntryAdded(
                    entry.date, entry.reader, entry.book, entry.pages
                )
                msgbus.handle(entry_added, uow)


def add_entry_using_book_key_cmd_handler(cmd: Command, uow: AbstractUnitOfWork):
    reader = get_valid_reader(cmd.reader)
    with uow:
        reading_log = uow.reading_logs.get(reader)
        uow.commit()
        if reading_log:
            reading_log_used = ReadingLogUsed(reading_log.reader)
            msgbus.handle(reading_log_used, uow)
            entry = reading_log.add_entry_using_book_key(
                cmd.date, cmd.book_key, cmd.pages
            )
            if entry:
                uow.reading_logs.add(reading_log)
                uow.commit()
                entry_added = EntryAdded(
                    entry.date, entry.reader, entry.book, entry.pages
                )
                msgbus.handle(entry_added, uow)


def del_entry_cmd_handler(cmd: Command, uow: AbstractUnitOfWork):
    reader = get_valid_reader(cmd.reader)
    with uow:
        reading_log = uow.reading_logs.get(reader)
        uow.commit()
        if reading_log:
            reading_log_used = ReadingLogUsed(reading_log.reader)
            msgbus.handle(reading_log_used, uow)
            entry = reading_log.delete_entry(cmd.id)
            if entry:
                uow.reading_logs.add(reading_log)
                uow.commit()
                event = EntryDeleted(
                    entry.id, entry.date, entry.reader, entry.book, entry.pages
                )
                msgbus.handle(event, uow)


def update_entry_cmd_handler(cmd: Command, uow: AbstractUnitOfWork):
    reader = get_valid_reader(cmd.reader)
    with uow:
        reading_log = uow.reading_logs.get(reader)
        uow.commit()
        if reading_log:
            reading_log_used = ReadingLogUsed(reading_log.reader)
            msgbus.handle(reading_log_used, uow)
            entry = reading_log.update_entry(
                cmd.id, cmd.entry_date, cmd.book, cmd.pages
            )
            if entry:
                uow.reading_logs.add(reading_log)
                uow.commit()
                entry_added = EntryUpdated(
                    cmd.id, entry.date, entry.reader, entry.book, entry.pages
                )
                msgbus.handle(entry_added, uow)


def update_book_cmd_handler(cmd: Command, uow: AbstractUnitOfWork):
    reader = get_valid_reader(cmd.reader)
    with uow:
        reading_log = uow.reading_logs.get(reader)
        uow.commit()
        if reading_log:
            reading_log_used = ReadingLogUsed(reading_log.reader)
            msgbus.handle(reading_log_used, uow)
            old_val = reading_log.update_book(cmd.book)
            if old_val:
                uow.reading_logs.add(reading_log)
                uow.commit()
                book_updated = BookUpdated(old_val, cmd.book)
                msgbus.handle(book_updated, uow)


def update_reading_log_cmd_handler(cmd: Command, uow: AbstractUnitOfWork):
    reader = get_valid_reader(cmd.new_name)
    with uow:
        reading_log = uow.reading_logs.get(cmd.old_name)
        uow.commit()
        if reading_log:
            reading_log.update_reader(reader)
            uow.reading_logs.add(reading_log)
            uow.commit()
            reading_log_used = ReadingLogUsed(reader)
            msgbus.handle(reading_log_used, uow)
            reading_log_updated = ReadingLogUpdated(cmd.old_name, reader)
            msgbus.handle(reading_log_updated, uow)
