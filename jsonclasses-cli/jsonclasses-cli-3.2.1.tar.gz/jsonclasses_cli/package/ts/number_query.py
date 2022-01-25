def number_query() -> str:
    return """
interface NumberValueQuery {
    _gt?: number
    _gte?: number
    _lt?: number
    _lte?: number
}

interface NumberEqQuery {
    _eq: number
}

interface NumberNeqQuery {
    _neq: number
}

interface NumberNullQuery {
    _null: boolean
}

interface NumberOrQuery {
    _or: NumberQuery[]
}

interface NumberAndQuery {
    _and: NumberQuery[]
}

export type NumberQuery = number | NumberEqQuery | NumberNeqQuery | NumberNullQuery | NumberValueQuery | NumberOrQuery | NumberAndQuery
    """.strip() + '\n'
