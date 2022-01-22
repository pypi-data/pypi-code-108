resolve_issue = r"""
        ^\s* # possible space before "The"
        (
            The|
            In|
            Essentially,\s+the|
            Summed\s+up,\s+the|
        )\s+
        issues?\s+
        (
            in\s+th(ese|is)|
            for(\s+our)?|
            to\s+be
        )\s+
        (
            petitions?|
            resolution|
            resolved
        )\s+
        (in\s+the\s+present\s+case\s+)?
        (is|are)?
    """
