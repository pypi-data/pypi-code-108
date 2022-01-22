import re

wherefore_regex = r"""
\s*
(
    (Where?fore)|
    (WHERE?FORE)|
    (ACCORDINGLY)| # ACCORDINGLY examples, http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/63290; http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/64934
    (IN\s+VIEW\s+ # IN VIEW WHEREOF http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33483
        (
            (W?HEREOF)| # IN VIEW HEREOF http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33471
            (THEREOF)| # IN VIEW THEREOF http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/34340
            (OF\s+(ALL\s+)?THE\s+FOREGOING)| # IN VIEW OF ALL THE FOREGOING http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/64489
            (OF\s+THESE\s+CONSIDERATIONS) # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33679
        )
    )|
    (ON\s+ALL\s+THE\s+FOREGOING\s+CONSIDERATIONS)| # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33964
    (CONSIDERING\s+THE\s+FOREGOING)| # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33587, http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/34150, http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/34759
    (PREMISES CONSIDERED)| # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33729
    (FOR\s+THE\s+FOREGOING\s+REASONS)| # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33600
    (UPON\s+THESE\s+PREMISES) # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/34578
)
\,?
\s*
"""

wherefore_pattern = re.compile(wherefore_regex, re.X)
