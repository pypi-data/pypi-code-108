import json

import click
import requests
from bibliocli_functions import addBookToDatabase, getBooks
from helper_functions import mapNotionResultToBook
from rich import print
from rich.console import Console
from rich.progress import track
from rich.style import Style
from rich.table import Table

__author__ = "Keagan Stokoe"

console = Console()


@click.group()
def bibliocli():
    """
    A command line utility for retrieving book information and adding it to your reading list.
    """
    pass


@bibliocli.command()
@click.argument("name")
@click.argument("author")
@click.option("--completed", default=False, help="Set to true if the book is completed")
def add(name: str, author: str, completed: bool = False) -> None:
    """Add book to database.

    Args:
        name (str): [Book title.]
        author (str): [Name of author.]
        completed (bool, optional): [description]. Defaults to False.
    """
    addBookToDatabase(name, author, completed)


# The "search" command.
@bibliocli.command()
@click.argument("query")
@click.option("--max")
def search(query, max):
    """🔎 Search by title or author. Use --max to indicate number of results to return (up to 40). Replace spaces with dashes."""
    # Make the Google Books API request after the user types in their "query" and "max".
    request_url = "https://www.googleapis.com/books/v1/volumes?"
    query = {"q": {query}, "maxResults": {max}}
    response = requests.get(request_url, params=query)
    json_response = response.json()
    json_response_books = json_response["items"]

    # "combine_dict" will be a temporary holding book space for each search.
    combine_dict = []

    # For each book called by the API ("json_response_books"), format it to only return the title, author(s), and publisher. Return default data if any info is missing ("~XXX not available~") ...
    def format_response():
        for item in json_response_books:
            try:
                title = item["volumeInfo"]["title"]
            except KeyError:
                title = "~Title not available]~"
            try:
                author = " & ".join(item["volumeInfo"]["authors"])
            except KeyError:
                author = "~Author not available~"
            try:
                publisher = item["volumeInfo"]["publisher"]
            except KeyError:
                publisher = "~Publisher not available~"
            reading_list = {"TITLE": title, "AUTHOR": author, "PUBLISHER": publisher}
            # ... And then add all these new books into our empty "combine_dict".
            combine_dict.append(reading_list)

    format_response()

    # Actually print off our new reading list in "combine_dict" in a more readable way for the user.
    def print_search():
        table = Table(title="Books")
        table.add_column("Title", justify="left", style="cyan", no_wrap=True)
        table.add_column("Author", justify="left", style="magenta", no_wrap=True)
        n = 0
        for item in combine_dict:
            n += 1
            table.add_row(f'{n}. {item["TITLE"]}', f'{item["AUTHOR"]}')
        console.print(table)

    print_search()

    # The user selects a book from the books returned above ...
    user_pick = int(input("Which book would you like to add? (enter a number): "))

    # ... And then we confirm the book that user selects from "combine_dict".
    user_selection = combine_dict[user_pick - 1]
    title = user_selection["TITLE"]
    author = user_selection["AUTHOR"]
    addBookToDatabase(title, author)


@bibliocli.command()
def getListedBooks():
    getBooks()


if __name__ == "__main__":
    bibliocli()


# Next steps:

# 1. Update commands so that you can search by title also - DONE
# 2. Figure out how to write to somewhere - DONE
# 3. Configure styling for the console
# 4. Figure out how to turn this into a Chrome extension
# 5. Figure out if it's possible to read text data from an image. It's a long shot but it'd be cool to take a picture of a book and have the information be extracted and written to your reading list.
