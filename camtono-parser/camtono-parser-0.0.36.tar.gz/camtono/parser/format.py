from .dialects import load_dialect_module
from .clean import strip_comments, unwrap_variables, ENCODING_CHARACTER
from moz_sql_parser.formatting import Formatter as MozFormatter, escape, string_types, text
from .keywords import *


def format_query(query_ast, sql_dialect) -> str:
    """

    :param query_ast:
    :param sql_dialect:
    :return:
    """
    dialect = load_dialect_module(dialect_name=sql_dialect)
    formatted_query = dialect.format_query(query_ast=query_ast)

    formatted_query = unwrap_variables(
        query=formatted_query, encoding_character=ENCODING_CHARACTER, skip_characters=len(ENCODING_CHARACTER)
    )
    formatted_query = unwrap_variables(
        query=formatted_query, encoding_character='"',
        skip_characters=len(ENCODING_CHARACTER)
    )
    return formatted_query


def get_allowed_dialects(query_ast):
    """

    :param query_ast:
    :return:
    """
    from .dialects import list_dialects

    allowed_dialects = []
    for dialect in list_dialects():
        try:
            format_query(query_ast=query_ast, sql_dialect=dialect)
        except Exception:
            pass
        else:
            allowed_dialects.append(dialect)
    return allowed_dialects


class BaseFormatter(MozFormatter):
    """"""

    def op(self, json):
        if len(json) > 1:
            print(json)
            raise Exception("Operators should have only one key!")
        key, value = list(json.items())[0]

        # check if the attribute exists, and call the corresponding method;
        # note that we disallow keys that start with `_` to avoid giving access
        # to magic methods
        attr = "_{0}".format(key)
        if hasattr(self, attr) and not key.startswith("_"):
            method = getattr(self, attr)
            return method(value)

        # treat as regular function call
        if isinstance(value, dict) and len(value) == 0:
            return (
                    key.upper() + "()"
            )  # NOT SURE IF AN EMPTY dict SHOULD BE DELT WITH HERE, OR IN self.dispatch()
        else:
            return "{0}({1})".format(key.upper(), self.dispatch(value))

    def _union(self, json, wrap=True):
        return "(" + self.union(json) + ")"

    def _union_all(self, json, wrap=True):
        return "(" + self.union_all(json) + ")"

    def union_distinct(self, json):
        return " UNION DISTINCT ".join(self.query(query) for query in json)

    def _union_distinct(self, json):
        return "(" + self.union_distinct(json=json) + ')'

    def _interval(self, json):
        return 'INTERVAL {0} {1}'.format(*json)

    def _distinct(self, json):
        if isinstance(json, list):
            return "DISTINCT " + self.dispatch(json=json)
        else:
            return "DISTINCT(" + self.dispatch(json=json) + ')'

    def value(self, json):
        if 'value' in json:
            parts = [self.dispatch(json["value"])]
        else:
            parts = ['NULL']
        if 'over' in json:
            parts.extend(['OVER', self.over(json=json['over'])])
        if 'offset' in json or 'ordinal' in json.keys():
            k = 'offset' if 'offset' in json.keys() else 'ordinal'
            parts[0] +='[{0}({1})]'.format(k, json[k])
        if "name" in json:
            parts.extend(["AS", self.dispatch(json["name"])])
        return " ".join(parts)

    def over(self, json):
        result = []
        if json.get('partitionby'):
            result.append("PARTITION BY")
            result.append(self.dispatch(json=json['partitionby']))

        if json.get('orderby'):
            result.append(self.orderby(json=json))

        output = '(' + ' '.join(result) + ')'
        return output

    def format(self, json):
        base = ""
        if "union" in json:
            base = self.union(json["union"])
        elif "union_all" in json:
            base = self.union_all(json["union_all"])
        elif "union_distinct" in json:
            base = self.union_distinct(json["union_distinct"])
        if base:
            return (self.query(json) + " " + base).strip()
        else:
            return self.query(json)

    def _in(self, json):
        valid = self.dispatch(json[1])
        # `(10, 11, 12)` does not get parsed as literal, so it's formatted as
        # `10, 11, 12`. This fixes it.
        if not valid.startswith("("):
            valid = "({0})".format(valid)

        return "{0} IN {1}".format(self.dispatch(json[0]), valid)

    def _cast(self, json):
        _type = json[1]
        if isinstance(_type, dict):
            _type = list(_type.keys())[0]
        return "cast({0} AS {1})".format(json[0], _type)

    def _safe_add(self, json):
        if isinstance(json, list):
            return "safe_add({0},{1})".format(json[0], json[1])

        value = json.get('literal')
        if isinstance(value, list):
            return "safe_add({0},{1})".format(value[0], value[1])
        else:
            return "safe_add({0})".format(value)

    def _add(self, json):
        value = json if isinstance(json, list) else json.get('literal')
        value = [str(x) for x in value]
        return ' + '.join(value)

    def _join_on(self, json):
        detected_join = join_keywords & set(json.keys())
        if len(detected_join) == 0:
            raise Exception(
                'Fail to detect join type! Detected: "{}" Except one of: "{}"'.format(
                    [on_keyword for on_keyword in json if on_keyword != "on"][0],
                    '", "'.join(join_keywords),
                )
            )

        join_keyword = detected_join.pop()

        acc = []
        acc.append(join_keyword.upper())
        acc.append(self.dispatch(json[join_keyword]))

        if json.get("on"):
            acc.append("ON")
            acc.append(self.dispatch(json["on"]))
        if json.get("using"):
            acc.append("USING")
            acc.append('(' + self.dispatch(json["using"]) + ')')
        return " ".join(acc)

    def dispatch(self, json):
        if isinstance(json, list):
            return self.delimited_list(json)
        if isinstance(json, dict):
            if len(json) == 0:
                return ""
            elif "value" in json or len(json.keys()) == 1 and 'name' in json.keys():
                return self.value(json)
            elif any(i in json for i in ['from', 'select', 'select_distinct', 'union', 'union_all', 'union_distinct']):
                # Nested queries
                return "({})".format(self.format(json))
            elif "on" in json:
                return self._join_on(json)
            elif "null" in json:
                return "NULL"
            else:
                return self.op(json)
        if isinstance(json, string_types):
            return escape(json, self.ansi_quotes, self.should_quote)
        if json == None:
            return "NULL"

        return text(json)
