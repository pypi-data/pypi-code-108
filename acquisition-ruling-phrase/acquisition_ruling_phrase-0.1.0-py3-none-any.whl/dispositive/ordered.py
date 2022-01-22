import re

ordered_regex = r"""
    (
        (SO)?
        \s*
        ORE?DERED? # see http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/64960 ORDERED vs. SO ORDERED
    ) # see misspelt SO OREDERED. in http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/34304
    \s*
    \.? # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/61481 OPTIONAL period
    """

ordered_pattern = re.compile(ordered_regex, re.X)
