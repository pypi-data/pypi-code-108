#!/usr/bin/env python3
import dataclasses
import json
import pathlib
import PySimpleGUI as sg
import shutil
import sys
import time

sg.theme("Dark Amber")

RETURN = chr(13)  # 13 is return char in ascii
ESC = chr(27)  # 27 is escape char in ascii


@dataclasses.dataclass
class Book:
    title: str
    author: str
    date: str
    series: str
    audiobook: bool

    @staticmethod
    def getHeadings():
        return [
            "Title",
            "Author",
            "Date",
            "Series",
            "Audiobook",
        ]

    def toList(self):
        return [self.title, self.author, self.date, self.series, self.audiobook]


def decode_book(dct):
    return Book(
        dct["title"],
        dct["author"],
        dct["date"],
        dct["series"],
        dct.get(
            "audiobook", False
        ),  # Special conversion for pre-audiobook database files
    )


def encode_book(b):
    return {
        "title": b.title,
        "author": b.author,
        "date": b.date,
        "series": b.series,
        "audiobook": b.audiobook,
    }


class BookList:
    database_file = pathlib.Path("book.json")

    def __init__(self):
        self.sort_key = "date"
        self.sort_reverse = True
        self.full_info = self.read_data()
        self.hide_audiobooks = False
        self.update_data(True)

    def invert_audio_flag(self):
        self.hide_audiobooks = not self.hide_audiobooks

    def update_sort(self, key):
        key = key.lower()
        if self.sort_key == key:
            self.sort_reverse = not self.sort_reverse
        self.sort_key = key

    def update_data(self, refresh):
        if refresh:
            self.full_authors = sorted(
                list(
                    {
                        item.author
                        for item in sorted(self.full_info, key=lambda x: x.author)
                    }
                )
            )
            self.full_series = sorted(
                list(
                    {
                        item.series
                        for item in sorted(self.full_info, key=lambda x: x.series)
                        if item.series
                    }
                )
            )
            self.author = None
            self.series = None
        self.data = []
        for item in sorted(
            self.full_info,
            key=lambda x: getattr(x, self.sort_key),
            reverse=self.sort_reverse,
        ):
            if self.hide_audiobooks and item.audiobook:
                continue
            author_match = not self.author or item.author == self.author
            series_match = not self.series or item.series == self.series
            if author_match and series_match:
                self.data.append(item.toList())

    def get_filtered_list(self, opposite_key, key, filter, default):
        if not filter:
            return default
        # need set comprehension here to eliminate dups
        return list(
            {item[opposite_key] for item in self.full_info if item[key] == filter}
        )

    def get_filtered_authors(self):
        return self.get_filtered_list(
            "author", "series", self.series, self.full_authors
        )

    def get_filtered_series(self):
        return self.get_filtered_list("series", "author", self.author, self.full_series)

    def read_data(self):
        data = None
        if self.database_file.is_file():
            with open(self.database_file, "r") as fp:
                data = json.load(fp, object_hook=decode_book)

        if not data or len(data) == 0:
            new_book = book_dialog("Add Book", [], [])
            if not new_book:
                print("No book information present")
                sys.exit()
            data = [new_book]
            self.write_data(data)

        return data

    def write_data(self, data=None):
        if self.database_file.is_file():
            backup_dir = pathlib.Path("BACKUP")
            backup_dir.mkdir(exist_ok=True)
            backup_name = time.strftime("%Y_%m_%d_%H_%M_%S_") + str(self.database_file)
            backup_file = backup_dir / backup_name
            shutil.copy(self.database_file, backup_file)

        if data is None:
            data = self.full_info
        with open(self.database_file, "w") as fp:
            json.dump(data, fp, indent=2, default=encode_book)

    def add_book(self, new_book):
        if new_book.title and new_book.author:
            self.full_info.append(new_book)
            self.write_data()
            self.update_data(True)

    def edit_book(self, old_book, new_book):
        for index, item in enumerate(self.full_info):
            if old_book == item:
                self.full_info[index] = new_book
                self.write_data()
                self.update_data(True)
                return

    def delete_book(self, book):
        for index, item in enumerate(self.full_info):
            if book == item:
                del self.full_info[index]
                self.write_data()
                self.update_data(True)

    def author_filter(self, author):
        self.author = author
        self.update_data(False)

    def series_filter(self, series):
        self.series = series
        self.update_data(False)

    def clear_filters(self):
        self.author = None
        self.series = None
        self.update_data(True)


def delete_dialog(book):
    result = sg.popup_yes_no(f"Delete {book.title} by {book.author}?")
    return result == "Yes"


def filter_dialog(title, items):
    if len(items) == 0:
        return ""
    orig_items = items
    layout = [
        [sg.Text("Filter On:"), sg.Input(key="-FILTER-")],
        [
            sg.Listbox(
                values=items,
                default_values=items[:1],
                select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                key="-LIST-",
                enable_events=True,
                bind_return_key=True,
                size=(50, 20),
            )
        ],
        [sg.OK(key="Ok"), sg.Cancel(key="Cancel")],
    ]

    window = sg.Window(title, layout=layout, return_keyboard_events=True)
    listbox = window["-LIST-"]
    filter = window["-FILTER-"]
    while True:
        event, values = window.read()
        if event in [sg.WIN_CLOSED, "Cancel", ESC]:
            window.close()
            return ""
        elif event in ["Ok", RETURN]:
            window.close()
            return values["-FILTER-"]
        elif event == "-LIST-":
            item = listbox.get()[0]
            filter.update(item)
        else:
            start = filter.get()
            items = [item for item in orig_items if item.startswith(start)]
            listbox.update(items)


def book_dialog(dialog_title, authors, series, book=None):
    # sourcery skip: extract-method
    authors_combo = sg.Combo(authors, key="-AUTH-", expand_x=True)
    series_combo = sg.Combo(series, key="-SER-", expand_x=True)
    is_audio = book.audiobook if book else False
    layout = [
        [sg.Text("Title:"), sg.Input(key="-TITLE-")],
        [
            sg.CalendarButton(
                "Date Finished",
                format="%Y/%m/%d",
                key="-CAL-",
                enable_events=True,
            ),
            sg.Text("Not Set", key="-DATE-"),
        ],
        [sg.Text("Author:"), authors_combo],
        [sg.Text("Series:"), series_combo],
        [sg.Text("Audiobook:"), sg.Checkbox("", default=is_audio, key="-AUDIO-")],
        [sg.OK(key="Ok"), sg.Cancel(key="Cancel")],
    ]
    window = sg.Window(dialog_title, layout=layout, return_keyboard_events=True)
    window.finalize()  # obligatory to allow updating boxes
    if book and book.title:
        window["-TITLE-"].update(value=book.title)
    if book and book.author:
        window["-AUTH-"].update(value=book.author)
    if book and book.series:
        window["-SER-"].update(value=book.series)
    if book and book.date:
        window["-DATE-"].update(value=book.date)
    title = None
    author = None
    while True:
        event, values = window.read()
        if event in [sg.WIN_CLOSED, "Cancel", ESC]:
            window.close()
            return None

        if event == "-CAL-":
            date_text = window["-DATE-"]
            date_text.update(values["-CAL-"])

        if event in ["Ok", RETURN]:
            title = values["-TITLE-"]
            author = values["-AUTH-"]
            audio = values["-AUDIO-"]
            if title and author:  # must supply title and author
                cal = window["-DATE-"].get()
                if cal == "Not Set":
                    cal = ""
                series = values["-SER-"]
                window.close()
                return Book(title, author, cal, series, audio)
            window.close()
            return None


def update_ui(window, books):
    books.update_data(False)
    window["-AUTHOR-FILTER-"].update(books.author or "None")
    window["-SERIES-FILTER-"].update(books.series or "None")
    table = window["-BOOKTABLE-"]
    table.update(books.data)
    if len(table.Values):
        table.update(select_rows=[0])


def main():
    books = BookList()

    layout = [
        [
            sg.Button("Author Filter:"),
            sg.Text("None", key="-AUTHOR-FILTER-", size=20),
            sg.Button("Series Filter:"),
            sg.Text("None", key="-SERIES-FILTER-", size=20),
            sg.Checkbox("Hide Audiobooks", enable_events=True, key="-AUDIO-"),
        ],
        [
            sg.Table(
                values=books.data,
                headings=Book.getHeadings(),
                justification="center",
                expand_x=True,
                expand_y=True,
                key="-BOOKTABLE-",
                enable_events=True,
                change_submits=True,
                selected_row_colors="red on yellow",
                select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            )
        ],
        [
            sg.Button("Clear Filters"),
            sg.Button("Add"),
            sg.Button("Edit"),
            sg.Button("Exit"),
        ],
    ]
    window = sg.Window(
        "Book of Books", layout, return_keyboard_events=True, resizable=True
    )
    window.finalize()
    table = window["-BOOKTABLE-"]
    table.block_focus(False)
    table.update(select_rows=[0])
    table.bind("<Button-1>", "Click")

    while True:
        event, values = window.read()
        # For some reason, keyboard events are coming in the form of "a:38" or "b:56"
        # Split out the keyboard code
        if event and ":" in event:
            event = event.split(":")[0]
        # print(event, values)
        if event in [sg.WIN_CLOSED, "Exit", ESC]:
            break
        elif event == "Clear Filters":
            books.clear_filters()
            update_ui(window, books)
        elif event == "-AUDIO-":
            books.invert_audio_flag()
            update_ui(window, books)
        elif event == "-BOOKTABLE-Click":
            e = table.user_bind_event
            region = table.Widget.identify("region", e.x, e.y)
            if region == "heading":
                sort_indices = Book.getHeadings()
                column = int(table.Widget.identify_column(e.x)[1:]) - 1
                books.update_sort(sort_indices[column])
                update_ui(window, books)
        elif event == "-AUTHORS-":
            books.author_filter(values["-AUTHORS-"][0])
            update_ui(window, books)
        elif event == "-SERIES-":
            books.series_filter(values["-SERIES-"][0])
            update_ui(window, books)
        elif event in ["Add", "a", "A"]:
            new_book = book_dialog("Add Book", books.full_authors, books.full_series)
            if new_book is not None:
                books.add_book(new_book)
                update_ui(window, books)
        elif event in ["Edit", "e", "E"]:
            if table and table.SelectedRows:
                book = Book(*table.Values[table.SelectedRows[0]])
                new_book = book_dialog(
                    "Edit Book", books.full_authors, books.full_series, book
                )
                if new_book is not None:
                    books.edit_book(book, new_book)
                    update_ui(window, books)
        elif event in ["Delete", "d", "D"]:
            if table and table.SelectedRows:
                book = Book(*table.Values[table.SelectedRows[0]])
                if delete_dialog(book):
                    books.delete_book(book)
                    update_ui(window, books)
        elif event == "Author Filter":
            authors = books.get_filtered_authors()
            val = filter_dialog("authors", authors)
            if val and len(val) != 0:
                books.author_filter(val)
                update_ui(window, books)
        elif event == "Series Filter":
            series = books.get_filtered_series()
            val = filter_dialog("series", series)
            if val and len(val) != 0:
                books.series_filter(val)
                update_ui(window, books)
    window.close()


if __name__ == "__main__":
    main()
