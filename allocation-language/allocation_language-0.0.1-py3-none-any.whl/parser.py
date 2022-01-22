from rply import ParserGenerator
import allocation_language.lexer as lexer
from allocation_language.ast_nodes.alloc_lang_aggregate import *
from allocation_language.ast_nodes.alloc_lang_alloc import *
from allocation_language.ast_nodes.alloc_lang_assess import *
from allocation_language.ast_nodes.alloc_lang_binops import *
from allocation_language.ast_nodes.alloc_lang_blocks import *
from allocation_language.ast_nodes.alloc_lang_discard import *
from allocation_language.ast_nodes.alloc_lang_primitives import *
from allocation_language.ast_nodes.alloc_lang_scope import *
from allocation_language.ast_nodes.alloc_lang_set import *

import warnings
warnings.filterwarnings('ignore')

pg = ParserGenerator(lexer.get_lexer_tokens(), cache_id="alloc_lang")

# ERROR HANDLING
@pg.error
def error_handler(token):
    if (token.getstr() == "$end"):
        raise ValueError(f"Reached end of line early. Did you forget the ';'?")
    raise ValueError(f"Ran into a {token.getstr()} where it wasn't expected")

# MAIN STATEMENTS
@pg.production("main : statements")
def main(s):
    return s[0]

@pg.production("statements : statement EOL statements")
def statments(s):
    return Block([s[0]] + [s[2]])

@pg.production("statements : statement EOL")
def statements_statement_eol(s):
    return Statement(s[0])

# COMMAND: "set_value"
@pg.production("statement : SET_VALUE field value")
def set_value_start(s):
    return SetValue(s[1], s[2])

# COMMAND: "assess"
@pg.production("statement : ASSESS agg_field")
def assess_start(s):
    return AssessNode(s[1])

# COMMAND: "alloc"
@pg.production("statement : ALLOC field expr field")
def alloc_fields_int(s):
    return Alloc(s[1], s[2], s[3])

# COMMAND: "aggregate"
@pg.production("statement : AGGREGATE agg_fields")
def aggregation_keyless(s):
    return KeylessAggregateNode(s[1])

@pg.production("statement : AGGREGATE KEY field agg_fields")
def aggregation_keyed(s):
    return KeyedAggregateNode(s[2], s[3])

@pg.production("agg_fields : agg_field agg_fields")
def aggregation_fields(s):
    return [s[0]] + s[1]

@pg.production("agg_fields : agg_field")
def aggregation_fields_end(s):
    return [s[0]]

# COMMAND: "scope"
@pg.production("statement : SCOPE condition")
def scope_command(s):
    return Scope(s[1])

@pg.production("condition : condition AND condition")
def conditional_and(s):
    return AndNode(s[0], s[2])

@pg.production("condition : condition OR condition")
def conditional_or(s):
    return OrNode(s[0], s[2])

@pg.production("condition : LPAREN condition RPAREN")
def conditional_wrapped(s):
    return s[1]

@pg.production("condition : expr COMPARATOR expr")
def condition_compare(s):
    return Condition(s[0], s[1].getstr(), s[2])

# COMMAND: "discard"
@pg.production("statement : DISCARD condition")
def discard_command(s):
    return DiscardNode(s[1])

# EXPRESSION MANAGEMENT
@pg.production("expr : LPAREN expr RPAREN")
def parenthesized_expression(s):
    return s[1]

@pg.production("expr : expr EXP expr")
def expression_product(s):
    return Exponentiate(s[0], s[2])

@pg.production("expr : expr MULT expr")
def expression_product(s):
    return Multiply(s[0], s[2])

@pg.production("expr : expr DIV expr")
def expression_product(s):
    return Divide(s[0], s[2])

@pg.production("expr : expr ADD expr")
def expression_product(s):
    return Add(s[0], s[2])

@pg.production("expr : expr SUB expr")
def expression_product(s):
    return Subtract(s[0], s[2])

@pg.production("expr : value")
def expression_value(s):
    return s[0]

@pg.production("value : field")
def field_as_value(s):
    return s[0]

# NAME MANAGMENT
@pg.production("field : FIELD_START NAME FIELD_END")
def field_name(s):
    return Field(s[1].getstr())

@pg.production("agg_field : FIELD_START NAME FIELD_END AGG_MODE")
def aggregate_field(s):
    return AggField(s[1].getstr(), s[3].getstr()[1:])

@pg.production("value : VAR_START NAME")
def live_var_name(s):
    return LiveVar(s[1].getstr())


# CONSTANTS AND VALUES
@pg.production("value : NUMBER")
def num_value(s):
    return Number(s[0].getstr())

@pg.production("value : NUMBER PERCENT")
def percent_value(s):
    return Percent(s[0].getstr())

@pg.production("value : STRING")
def string_value(s):
    return String(s[0].getstr()[1:-1])

parser = pg.build()