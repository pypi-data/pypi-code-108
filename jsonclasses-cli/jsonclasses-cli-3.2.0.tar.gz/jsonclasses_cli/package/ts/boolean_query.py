def boolean_query() -> str:
    return """
interface BooleanEqQuery {
    _eq: boolean
}

interface BooleanNeqQuery {
    _neq: boolean
}

interface BooleanNullQuery {
    _null: boolean
}

interface BooleanOrQuery {
    _or: BooleanQuery[]
}

interface BooleanAndQuery {
    _and: BooleanQuery[]
}

export type BooleanQuery = boolean | BooleanEqQuery | BooleanNeqQuery | BooleanNullQuery | BooleanOrQuery | BooleanAndQuery
    """.strip() + "\n"
