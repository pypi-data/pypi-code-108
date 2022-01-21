#!/usr/bin/env python
# Needs requests and html-table-parser-python3
from html_table_parser.parser import HTMLTableParser
import requests
import sys


def get_categories_from_site(url: str) -> list[str]:
    r = requests.get(url)
    p = HTMLTableParser()
    p.feed(r.text)
    result = []
    for table in p.tables:
        if "Description" in table[0]:
            for i in table:
                if "Description" not in i:
                    result.append(i[0])
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: UpdateCategories <path>", file=sys.stderr)
        sys.exit(1)

    categories = get_categories_from_site("https://specifications.freedesktop.org/menu-spec/latest/apa.html")
    categories += get_categories_from_site("https://specifications.freedesktop.org/menu-spec/latest/apas02.html")

    with open(sys.argv[1], "w", encoding="utf-8") as f:
        for i in categories:
            f.write(i + "\n")


if __name__ == "__main__":
    main()
