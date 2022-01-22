hence_this = r"""
        ^\s* # possible space before "Hence"
        Hence
        ,? # comma optional
        \s+
        (
            (
                th(e|is) # the / this
            )|
            petitioners'
        )
        \s+
        (
            (
                instant|
                present
            )\s+
        )?
        (
            [Pp]etition|
            [Aa]ppeal|
            [Rr]ecourse
        )
        (
            \s+ # might end in petition, e.g. hence this petition.
            (
                (,\s*with\s+the\s+following\s+issues?)|
                (for\s+review\s+on\s+certiorari)
            )?
        )?
    """
