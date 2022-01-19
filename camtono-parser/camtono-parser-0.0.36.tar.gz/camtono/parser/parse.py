from __future__ import absolute_import, division, unicode_literals

from mo_parsing.engine import Engine
from mo_parsing.helpers import delimitedList, restOfLine
from moz_sql_parser.windows import sortColumn, window

from camtono.parser.keywords import *
from camtono.parser.dialects import load_dialect_module
from camtono.parser.clean import strip_comments, wrap_variables, pad_comparisons, ENCODING_CHARACTER

HINT_STRING = "|"


def parse_query(query, sql_dialect, feature_name=None) -> tuple:
    """

    :param query:
    :param sql_dialect:
    :param feature_name:
    :return:
    """
    dialect = load_dialect_module(dialect_name=sql_dialect)
    standardized_query = strip_comments(query=query)
    standardized_query = pad_comparisons(query=standardized_query)
    standardized_query, variables = wrap_variables(
        query=standardized_query, encoding_character='', wrap_character=ENCODING_CHARACTER,
    )
    query_ast = dialect.parse_query(query=standardized_query)
    query_input, dependencies = label_input(variable_set=variables, query_ast=query_ast)

    output = label_output(query_ast=query_ast)
    return query_ast, query_input, output, dependencies


def label_input(variable_set, query_ast):
    """

    :param variable_set:
    :param query_ast:
    :return:
    """
    import json
    import re
    variables = dict()
    dependencies = dict()
    for group in variable_set:
        for variable in re.findall('(\{[\S]+?\})', group):
            if all(variable not in i for i in [variables.keys(), dependencies.keys()]):
                allows_list = False
                data_type = None
                default_value = None
                clean_name = variable.replace('{', "").replace('}', '')
                display_name = clean_name
                location, found = locate_string(s=variable, json=query_ast)
                if '@' in display_name:
                    dependencies[variable] = dict(feature_id=clean_name.replace('@', ''), locations=location)
                else:
                    variables[variable] = dict(
                        name=clean_name, display_name=display_name.split('.')[-1], default_value=default_value,
                        data_type=data_type, allows_list=allows_list, full_string=group,
                        is_literal=False if clean_name == 'grain' else True,
                        locations=location
                    )

    return list(variables.values()), list(dependencies.values())


def locate_string(s, json):
    locations = []
    found = False
    if isinstance(json, list):
        for idx, v in enumerate(json):
            l, f = locate_string(s, v)
            if f:
                for i in l:
                    locations.append(
                        dict(
                            location={idx: i['location']},
                            value=i['value'],
                            level=i['level'] + 1,
                            is_wrapped_literal=i['is_wrapped_literal']
                        )
                    )
                found = True
    elif isinstance(json, dict):
        for k, v in json.items():
            l, f = locate_string(s, v)
            if f:
                for i in l:
                    locations.append(
                        dict(
                            location={k: i['location']},
                            value=i['value'],
                            level=i['level'] + 1,
                            is_wrapped_literal=True if i['level'] == 0 and k == 'literal' else i['is_wrapped_literal']
                        )
                    )
                found = True
    elif isinstance(json, str):
        if s in json:
            found = True
            locations.append(dict(location=dict(), value=json, level=0, is_wrapped_literal=False))
    return locations, found


def label_output(query_ast: dict):
    import json
    outputs = list()
    for idx, column in enumerate(get_select_columns(find_first_node(node_key='select', parse_result=query_ast))):
        display_name = column
        column_pieces = column.split(HINT_STRING)
        is_nullable = True
        data_type = 'string'
        if len(column_pieces) == 3:
            display_name = column_pieces[0]
            data_type = column_pieces[1]
            is_nullable = json.loads(column_pieces[2])
        output = dict(
            display_name=display_name.split('.')[-1],
            index=idx,
            name=column,
            is_nullable=is_nullable,
            data_type=data_type
        )
        outputs.append(output)
    return outputs


def get_select_columns(select):
    """
    This function searches the given parsed select dictionary to return list of output columns
    :param select: (dict) The select portion of a select statement.
    """
    result = []

    def extract_column_name(i):
        names = []

        if isinstance(i, str):
            names.append(i)
        elif isinstance(i, dict):
            if 'name' in i.keys():
                names.append(i['name'])
            elif 'literal' in i.keys():
                names.append(i['literal'])
            elif 'value' in i.keys():
                names += extract_column_name(i['value'])
            else:
                names += extract_column_name(list(i.values())[0])
        elif isinstance(i, list):
            for x in i:
                n = extract_column_name(i=x)
                if n:
                    names += n
        return names

    if isinstance(select, list):
        for i in select:
            result += extract_column_name(i)
    else:
        result += extract_column_name(select)
    return result


def find_first_node(node_key, parse_result):
    """
    Searches a parsed query for item with matching node_key.
    :param node_key: (str) - The key to find.
    :param parse_result (dict) - Parsed query
    :return: (dict) - Returns item as dictionary to preserve original key/value pair.
    """
    if node_key in parse_result:
        return parse_result[node_key]

    for k in parse_result:
        a = None

        if isinstance(parse_result, dict):
            if isinstance(parse_result[k], dict) or isinstance(parse_result[k], list):
                a = find_first_node(node_key, parse_result[k])
        elif isinstance(parse_result, list):
            a = find_first_node(node_key, k)

        if a is not None:
            return a

    return None


def to_date_math_call(tokens):
    # ARRANGE INTO {op: params} FORMAT
    op = tokens["op"].lower()
    op = binary_ops.get(op, op)
    params = scrub(tokens["params"])
    if not params:
        params = {}
    if scrub(tokens["ignore_nulls"]):
        ignore_nulls = True
    else:
        ignore_nulls = None

    return ParseResults(
        tokens.type,
        tokens.start,
        tokens.end,
        [{op: params, "ignore_nulls": ignore_nulls}],
    )

def to_ordinal_call(instring, tokens_start, ret_tokens):
    """
    Creates the token structure to support analytics [ordinal(2)] expressions
    :param instring: (string) source string, not used but required by format
    :param tokens_start: (list) tokens for instring
    :param ret_tokens: (list) list of return tokenized parts
    :returns: (set) SQL:2011 analytics function representation
    """
    tok = ret_tokens

    return {"value": instring.tokens[0][0], instring.tokens[2][0]: instring.tokens[4][0]}

def to_json_call(tokens):
    # ARRANGE INTO {op: params} FORMAT
    op = tokens["op"].lower()
    op = binary_ops.get(op, op)
    params = scrub(tokens["params"])
    if not params:
        params = {}
    if scrub(tokens["ignore_nulls"]):
        ignore_nulls = True
    else:
        ignore_nulls = None

    result = {op: params, "ignore_nulls": ignore_nulls}
    if scrub(tokens["ordinal_offset"]):
        result = {'value': result, tokens['ordinal_offset'].tokens[0]:tokens['ordinal_offset'].tokens[1][0]}
    return ParseResults(
        tokens.type,
        tokens.start,
        tokens.end,
        [result],
    )


class Parser(object):
    parser = None
    known_types = known_types
    union_keywords = unions
    known_ops = KNOWN_OPS
    precedence = precedence
    join_keywords = join_keywords

    reserved = reserved
    durations = durations

    def __init__(self):
        engine = Engine().use()
        engine.add_ignore(Literal("--") + restOfLine)
        engine.add_ignore(Literal("#") + restOfLine)

        # IDENTIFIER
        literal_string = Regex(r'\"(\"\"|[^"])*\"').addParseAction(unquote)
        mysql_ident = Regex(r"\`(\`\`|[^`])*\`").addParseAction(unquote)
        sqlserver_ident = Regex(r"\[(\]\]|[^\]])*\]").addParseAction(unquote)
        placeholder_pattern = Regex(r"(\'[\w\d\_]*\{\S+\}[\w\d\_]*\')").addParseAction(unquote)
        ident = Combine(
            ~MatchFirst(self.reserved)
            + (delimitedList(
                Literal("*")
                | literal_string
                | placeholder_pattern
                | mysql_ident
                | sqlserver_ident
                | Word(IDENT_CHAR),
                separator=".",
                combine=True,
            )
            )
        ).set_parser_name("identifier")

        LBRACKET = Literal('[').suppress()
        RBRACKET = Literal(']').suppress()

        # CASE
        case = (
                CASE
                + Group(ZeroOrMore(
            (WHEN + expr("when") + THEN + expr("then")).addParseAction(to_when_call)
        ))("case")
                + Optional(ELSE + expr("else"))
                + END
        ).addParseAction(to_case_call)
        # SWITCH
        switch = (
                CASE
                + expr("value")
                + Group(ZeroOrMore(
            (WHEN + expr("when") + THEN + expr("then")).addParseAction(to_when_call)
        ))("case")
                + Optional(ELSE + expr("else"))
                + END
        ).addParseAction(to_switch_call)
        # CAST
        cast = Group(
            CAST("op") + LB + expr("params") + AS + self.known_types("params") + RB
        ).addParseAction(to_json_call)

        _standard_time_intervals = MatchFirst([
            Keyword(d, caseless=True).addParseAction(lambda t: self.durations[t[0].lower()])
            for d in self.durations.keys()
        ]).set_parser_name("duration")("params")

        duration = (realNum | intNum | ident)("params") + _standard_time_intervals

        interval = (
                INTERVAL + ("'" + delimitedList(duration) + "'" | duration)
        ).addParseAction(to_interval_call)

        timestamp = (
                time_functions("op")
                + (
                        sqlString("params")
                        | MatchFirst([
                    Keyword(t, caseless=True).addParseAction(lambda t: t.lower()) for t in times
                ])("params")
                )
        ).addParseAction(to_json_call)

        extract = (
                Keyword("extract", caseless=True)("op")
                + LB
                + (_standard_time_intervals | expr("params"))
                + FROM
                + expr("params")
                + RB
        ).addParseAction(to_json_call)

        namedColumn = Group(
            Group(expr)("value") + Optional(Optional(AS) + Group(ident))("name")
        )

        distinct = (
                DISTINCT("op") + delimitedList(namedColumn)("params")
        ).addParseAction(to_json_call)

        ordered_sql = Forward()

        call_function = (
                ident("op")
                + LB
                + Optional(Group(ordered_sql) | delimitedList(expr))("params")
                + Optional(
            Keyword("ignore", caseless=True) + Keyword("nulls", caseless=True)
        )("ignore_nulls")
                + RB + Optional(
            LBRACKET + (Keyword('ordinal', caseless=True) | Keyword('offset', caseless=True)) + LB + expr(
                'offset') + RB + RBRACKET
        )('ordinal_offset')
        ).addParseAction(to_json_call)

        ordinal_column = (
                             ident.copy() +
                LBRACKET + (Keyword('ordinal', caseless=True) | Keyword('offset', caseless=True)) + LB + expr(
            'offset') + RB + RBRACKET
        ).addParseAction(to_ordinal_call)

        compound = (
                NULL
                | TRUE
                | FALSE
                | NOCASE
                | interval
                | timestamp
                | extract
                | case
                | switch
                | cast
                | distinct
                | ordinal_column
                | (LB + Group(ordered_sql) + RB)
                | (LB + Group(delimitedList(expr)).addParseAction(to_tuple_call) + RB)
                | sqlString.set_parser_name("string")
                | call_function
                | self.known_types
                | realNum.set_parser_name("float")
                | intNum.set_parser_name("int")
                | ident
        )

        expr << (
                (
                    infixNotation(
                        compound,
                        [
                            (
                                o,
                                1 if o in unary_ops else (3 if isinstance(o, tuple) else 2),
                                RIGHT_ASSOC if o in unary_ops else LEFT_ASSOC,
                                to_json_operator,
                            )
                            for o in self.known_ops
                        ],
                    ).set_parser_name("expression")
                )("value")
                + Optional(window)
        ).addParseAction(to_expression_call)

        alias = (
            (Group(ident) + Optional(LB + delimitedList(ident("col")) + RB))("name")
                .set_parser_name("alias")
                .addParseAction(to_alias)
        )

        selectColumn = (
            Group(
                Group(expr).set_parser_name("expression1")("value")
                + Optional(Optional(AS) + alias)
                | Literal("*")("value")
            )
                .set_parser_name("column")
                .addParseAction(to_select_call)
        )
        table_source = (
                ((LB + ordered_sql + RB) | call_function)("value").set_parser_name("table source")
                + Optional(Optional(AS) + alias)
                | (ident("value").set_parser_name("table name") + Optional(AS) + alias)
                | ident.set_parser_name("table name")
        )
        join = ((
                        CROSS_JOIN
                        | FULL_JOIN
                        | FULL_OUTER_JOIN
                        | INNER_JOIN
                        | JOIN
                        | LEFT_JOIN
                        | LEFT_OUTER_JOIN
                        | RIGHT_JOIN
                        | RIGHT_OUTER_JOIN
                )("op")
                + Group(table_source)("join")
                + Optional((ON + expr("on")) | (USING + expr("using")))
                ).addParseAction(to_join_call)
        unordered_sql = Group(
            SELECT
            + Optional(
                TOP
                + expr("value")
                + Optional(Keyword("percent", caseless=True))("percent")
                + Optional(WITH + Keyword("ties", caseless=True))("ties")
            )("top").addParseAction(to_top_clause)
            + delimitedList(selectColumn)("select")
            + Optional(
                (FROM + delimitedList(Group(table_source)) + ZeroOrMore(join))("from")
                + Optional(WHERE + expr("where"))
                + Optional(GROUP_BY + delimitedList(Group(namedColumn))("groupby"))
                + Optional(HAVING + expr("having"))
            )
        ).set_parser_name("unordered sql")
        ordered_sql << (
                (unordered_sql + ZeroOrMore((MatchFirst(self.union_keywords)) + unordered_sql))("union")
                + Optional(ORDER_BY + delimitedList(Group(sortColumn))("orderby"))
                + Optional(LIMIT + expr("limit"))
                + Optional(OFFSET + expr("offset"))
        ).set_parser_name("ordered sql").addParseAction(to_union_call)

        statement = Forward()
        statement << (
                Optional(
                    WITH + delimitedList(Group(ident("name") + AS + LB + statement("value") + RB))
                )("with")
                + Group(ordered_sql)("query")
        ).addParseAction(to_statement)
        self.parser = statement
        engine.release()

    def parse(self, sql):
        from moz_sql_parser.utils import scrub
        sql = sql.rstrip().rstrip(";")
        parse_result = self.parser.parseString(sql, parseAll=True)
        return scrub(parse_result)
