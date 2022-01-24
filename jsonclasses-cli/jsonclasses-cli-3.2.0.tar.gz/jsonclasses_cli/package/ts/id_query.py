def id_query():
    return """
interface IDQuery {
    _eq: String
    _neq: String
    _null: boolean
}
    """.strip() + "\n"
