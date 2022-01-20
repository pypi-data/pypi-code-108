from __future__ import absolute_import, division, print_function, unicode_literals


def get_author_from_overview(overview):
    authors_page = [page for page in overview if "authors" in page["information_card"]["title"].lower()]
    if not authors_page:
        return ""

    authors_section = [section for section in authors_page[0]["information_card"]["sections"]
                       if "author" in section["title"].lower()]
    if not authors_section:
        return ""

    authors = [author["author"]["name"].split(",")[0] for author in authors_section[0]["body"]]
    if not authors:
        return ""

    return ", ".join(authors)
