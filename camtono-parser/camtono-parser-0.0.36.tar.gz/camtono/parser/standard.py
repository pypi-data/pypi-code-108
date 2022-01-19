def format_query(query_ast: dict) -> str:
    from .format import BaseFormatter
    return BaseFormatter().format(query_ast)


def format_schema(column_name, data_type: str):
    return dict(name=column_name, type=data_type)


def parse_query(query: str) -> dict:
    from .parse import Parser
    return Parser().parse(query)
