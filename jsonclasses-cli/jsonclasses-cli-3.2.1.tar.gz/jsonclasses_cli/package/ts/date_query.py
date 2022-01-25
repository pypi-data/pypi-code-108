def date_query() -> str:
    return """
interface DateValueQuery {
    _gt?: Date
    _gte?: Date
    _lt?: Date
    _lte?: Date
    _on?: Date
}

interface DateEqQuery {
    _eq: Date
}

interface DateNeqQuery {
    _neq: Date
}

interface DateNullQuery {
    _null: boolean
}

interface DateOrQuery {
    _or: DateQuery[]
}

interface DateAndQuery {
    _and: DateQuery[]
}

interface DateBeforeQuery {
    _before: Date
}

interface DateAfterQuery {
    _after: Date
}

export type DateQuery = Date | DateValueQuery | DateEqQuery | DateNeqQuery | DateNullQuery | DateOrQuery | DateAndQuery |
                        DateBeforeQuery | DateAfterQuery
    """.strip() + "\n"
