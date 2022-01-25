def links_interface() -> str:
    return """
interface Link {
    _add: String
}

interface UnLink {
    _del: String
}
    """.strip() + "\n"
