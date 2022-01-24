def string_query() -> str:
    return """
type Mode = 'default' | 'insensitive'

interface StringContainsQuery {
    _contains: string
    _mode?: Mode
}

interface StringPrefixQuery {
    _prefix: string
    _mode?: Mode
}

interface StringSuffixQuery {
    _suffix: string
    _mode?: Mode
}

interface StringMatchQuery {
    _match: string
    _mode?: Mode
}

interface StringEqQuery {
    _eq: string
}

interface StringNeqQuery {
    _neq: string
}

interface StringNullQuery {
    _null: boolean
}

interface StringCompareQuery {
    _gt?: string
    _gte?: string
    _lt?: string
    _lte?: string
}

interface StringOrQuery {
    _or: StringQuery[]
}

interface StringAndQuery {
    _and: StringQuery[]
}

export type StringQuery = string | StringContainsQuery | StringPrefixQuery | StringSuffixQuery | StringMatchQuery |
                          StringEqQuery | StringNeqQuery | StringNullQuery | StringCompareQuery | StringOrQuery | StringAndQuery
    """.strip() + "\n"
