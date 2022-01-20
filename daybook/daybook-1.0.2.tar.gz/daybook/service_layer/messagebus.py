from typing import List, Union
from daybook.domain.events import (
    Event,
    ReadingLogCreated,
    EntryAdded,
    EntryDeleted,
    ReadingLogUsed,
    EntryUpdated,
    BookUpdated,
    ReadingLogUpdated,
)
from daybook.domain.commands import (
    Command,
    CreateReadingLog,
    AddEntry,
    DelEntry,
    AddEntryUsingBookKey,
    UpdateEntry,
    UpdateBook,
    UpdateReadingLog,
)
from daybook.service_layer.handlers import (
    del_entry_cmd_handler,
    print_event,
    print_reader,
    create_reading_log_handler,
    add_entry_cmd_handler,
    add_entry_using_book_key_cmd_handler,
    entry_added_event_handler,
    update_last_reading_log_used,
    update_entry_cmd_handler,
    update_book_cmd_handler,
    update_reading_log_cmd_handler,
)
from daybook.service_layer.unit_of_work import AbstractUnitOfWork

EVENT_HANDLERS = {
    EntryAdded: [entry_added_event_handler],
    ReadingLogCreated: [print_reader],
    EntryDeleted: [print_event],
    ReadingLogUsed: [update_last_reading_log_used],
    EntryUpdated: [print_event],
    BookUpdated: [print_event],
    ReadingLogUpdated: [print_event]
}

COMMAND_HANDLERS = {
    CreateReadingLog: create_reading_log_handler,
    AddEntry: add_entry_cmd_handler,
    AddEntryUsingBookKey: add_entry_using_book_key_cmd_handler,
    DelEntry: del_entry_cmd_handler,
    UpdateEntry: update_entry_cmd_handler,
    UpdateBook: update_book_cmd_handler,
    UpdateReadingLog: update_reading_log_cmd_handler
}

Message = Union[Command, Event]


def handle_event(event: Event, queue: List[Message], uow: AbstractUnitOfWork):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            handler(event, uow)
            queue.extend(uow.collect_new_events())
        except Exception as ex:
            print(ex)
            continue


def handle_command(command: Command, queue: List[Message], uow: AbstractUnitOfWork):
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception as ex:
        print(ex)


def handle(message: Message, uow: AbstractUnitOfWork):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, Event):
            handle_event(message, queue, uow)
        elif isinstance(message, Command):
            results.append(handle_command(message, queue, uow))
    return results
