from moz_sql_parser.keywords import *
UNION_DISTINCT = Group(UNION + DISTINCT).set_parser_name("union_distinct")
reserved = [
    ALL,
    AND,
    AS,
    ASC,
    BETWEEN,
    BY,
    CASE,
    CAST,
    COLLATE,
    CROSS_JOIN,
    CROSS,
    # DATETIME_SUB, DATETIME_ADD, DATE_SUB, DATE_ADD, TIMESTAMP_SUB, TIMESTAMP_ADD,
    DESC,
    DISTINCT,
    ELSE,
    END,
    FALSE,
    FROM,
    FULL_JOIN,
    FULL_OUTER_JOIN,
    FULL,
    GROUP_BY,
    GROUP,
    HAVING,
    IN,
    INNER_JOIN,
    INNER,
    INTERVAL,
    IS_NOT,
    IS,
    JOIN,
    LEFT_JOIN,
    LEFT_OUTER_JOIN,
    LEFT,
    LIKE,
    LIMIT,
    NOCASE,
    NOT_BETWEEN,
    NOT_IN,
    NOT_LIKE,
    NOT_RLIKE,
    NOT,
    NULL,
    OFFSET,
    ON,
    OR,
    ORDER_BY,
    ORDER,
    OUTER,
    OVER,
    PARTITION_BY,
    PARTITION,
    RIGHT_JOIN,
    RIGHT_OUTER_JOIN,
    RIGHT,
    RLIKE,
    SELECT_DISTINCT,
    SELECT,
    THEN,
    TRUE,
    UNION_DISTINCT,
    UNION_ALL,
    UNION,
    USING,
    WHEN,
    WHERE,
    WITH,
    WITHIN_GROUP,
    WITHIN,
]

unions = [UNION_DISTINCT, UNION_ALL, UNION]
joins = ['left', 'inner', 'outer', 'cross', 'full outer', 'right', 'right inner', 'right outer', 'left inner',
         'left outer']
min_keys = {
    "cast": [['value', 'type']],
    "mul": [['a', 'b']],
    "div": [['a', 'b']],
    "mod": [['a', 'b']],
    "neg": [['a', 'b']],
    # "add": [['a', 'b']],
    "sub": [['a', 'b']],
    "case": [['when', 'then']],
    "binary_not": [['a', 'b']],
    "binary_and": [['a', 'b']],
    "binary_or": [['a', 'b']],
    "timestamp_sub": [['a', 'b']],
    "timestamp_add": [['a', 'b']],
    "date_add": [['a', 'b']],
    "date_sub": [['a', 'b']],
    "datetime_sub": [['a', 'b']],
    "datetime_add": [['a', 'b']],
    "from": [['value'], ['join', 'using'], ['join', 'on'], ['left join', 'using'], ['left join', 'on'], ['value'],
             ['inner join', 'using'], ['inner join', 'on'], ['outer join', 'using'], ['outer join', 'on'],
             ['full outer join', 'using'], ['full outer join', 'on'], ['full join', 'using'], ['full join', 'on']
             ],
    "on": [['eq'], ['or'], ['and']],
    "gte": [['a', 'b']],
    "lte": [['a', 'b']],
    "join": [['value']],
    "lt": [['a', 'b']],
    "gt": [['a', 'b']],
    "eq": [['a', 'b']],
    "neq": [['a', 'b']],
    "between": [['a', 'b']],
    "not_between": [['a', 'b']],
    "interval": [['a', 'b']],
    "in": [['a', 'b']],
    "nin": [['a', 'b']],
    "is": [['a', 'b']],
    "like": [['a', 'b']],
    "not_like": [['a', 'b']],
    "rlike": [['a', 'b']],
    "not_rlike": [['a', 'b']],
    "similar_to": [['a', 'b']],
    "not_similar_to": [['a', 'b']],
    "where": [['gte'], ['lte'], ['lt'], ['gt'], ['eq'], ['neq'], ['between'], ['not_between'], ['interval'], ['in'],
              ['nin'], ['is'], ['like'], ['not_like'], ['rlike'], ['not_rlike'], ['similar_to'], ['not_similar_to'],
              ['missing'], ['and'], ['or']],
    "and": [['gte'], ['lte'], ['lt'], ['gt'], ['eq'], ['neq'], ['between'], ['not_between'], ['interval'], ['in'],
            ['nin'], ['is'], ['like'], ['not_like'], ['rlike'], ['not_rlike'], ['similar_to'], ['not_similar_to'],
            ['missing'], ['and'], ['or']],
    "or": [['gte'], ['lte'], ['lt'], ['gt'], ['eq'], ['neq'], ['between'], ['not_between'], ['interval'], ['in'],
           ['nin'], ['is'], ['like'], ['not_like'], ['rlike'], ['not_rlike'], ['similar_to'], ['not_similar_to'],
           ['missing'], ['and'], ['or']],
    **{"{} join".format(i): [['value']] for i in joins}
}

durations = {
    "microseconds": "microsecond",
    "microsecond": "microsecond",
    "microsecs": "microsecond",
    "microsec": "microsecond",
    "useconds": "microsecond",
    "usecond": "microsecond",
    "usecs": "microsecond",
    "usec": "microsecond",
    "us": "microsecond",
    "milliseconds": "millisecond",
    "millisecond": "millisecond",
    "millisecon": "millisecond",
    "mseconds": "millisecond",
    "msecond": "millisecond",
    "millisecs": "millisecond",
    "millisec": "millisecond",
    "msecs": "millisecond",
    "msec": "millisecond",
    "ms": "millisecond",
    "seconds": "second",
    "second": "second",
    "secs": "second",
    "sec": "second",
    "s": "second",
    "minutes": "minute",
    "minute": "minute",
    "mins": "minute",
    "min": "minute",
    "m": "minute",
    "hours": "hour",
    "hour": "hour",
    "hrs": "hour",
    "hr": "hour",
    "h": "hour",
    "days": "day",
    "day": "day",
    "d": "day",
    "dayofweek": "dow",
    "dow": "dow",
    "weekday": "dow",
    "weeks": "week",
    "week": "week",
    "w": "week",
    "months": "month",
    "month": "month",
    "mons": "month",
    "mon": "month",
    "quarters": "quarter",
    "quarter": "quarter",
    "years": "year",
    "year": "year",
    "decades": "decade",
    "decade": "decade",
    "decs": "decade",
    "dec": "decade",
    "centuries": "century",
    "century": "century",
    "cents": "century",
    "cent": "century",
    "c": "century",
    "millennia": "millennium",
    "millennium": "millennium",
    "mils": "millennium",
    "mil": "millennium",
    "epoch": "epoch",
}
