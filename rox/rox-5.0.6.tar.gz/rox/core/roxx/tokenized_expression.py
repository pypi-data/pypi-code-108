from rox.core.roxx import symbols
from rox.core.roxx.node import Node, NodeTypes
from rox.core.roxx.string_tokenizer import StringTokenizer
from rox.core.roxx.token_type import TokenTypes
from rox.core.utils.type_utils import is_string


class TokenizedExpression:
    DICT_START_DELIMITER = '{'
    DICT_END_DELIMITER = '}'
    ARRAY_START_DELIMITER = '['
    ARRAY_END_DELIMITER = ']'
    TOKEN_DELIMITERS = '{}[]():, \t\r\n"'
    PRE_POST_STRING_CHAR = ''
    STRING_DELIMITER = '"'
    ESCAPED_QUOTE = r'\"'
    ESCAPED_QUOTE_PLACEHOLDER = r'\RO_Q'

    def __init__(self, expression, operators):
        self.expression = expression
        self.operators = operators
        self.result_list = None
        self.array_accumulator = None
        self.dict_accumulator = None
        self.dict_key = None

    def get_tokens(self):
        return self.tokenize(self.expression)

    def push_node(self, node):
        if self.dict_accumulator is not None and self.dict_key is None:
            self.dict_key = str(node.value)
        elif self.dict_accumulator is not None and self.dict_key is not None:
            self.dict_accumulator[self.dict_key] = node.value
            self.dict_key = None
        elif self.array_accumulator is not None:
            self.array_accumulator.append(node.value)
        else:
            self.result_list.append(node)

    def tokenize(self, expression):
        self.result_list = []
        self.dict_accumulator = None
        self.array_accumulator = None
        self.dict_key = None

        delimiters_to_use = TokenizedExpression.TOKEN_DELIMITERS
        normalized_expression = expression.replace(TokenizedExpression.ESCAPED_QUOTE, TokenizedExpression.ESCAPED_QUOTE_PLACEHOLDER)
        tokenizer = StringTokenizer(normalized_expression, delimiters_to_use, True)

        prev_token, token = None, None
        while tokenizer.has_more_tokens():
            prev_token = token
            token = tokenizer.next_token(delimiters_to_use)
            in_string = delimiters_to_use == TokenizedExpression.STRING_DELIMITER

            if not in_string and token == TokenizedExpression.DICT_START_DELIMITER:
                self.dict_accumulator = {}
            elif not in_string and token == TokenizedExpression.DICT_END_DELIMITER:
                dict_result = self.dict_accumulator
                self.dict_accumulator = None
                self.push_node(self.node_from_token(dict_result))
            elif not in_string and token == TokenizedExpression.ARRAY_START_DELIMITER:
                self.array_accumulator = []
            elif not in_string and token == TokenizedExpression.ARRAY_END_DELIMITER:
                array_result = self.array_accumulator
                self.array_accumulator = None
                self.push_node(self.node_from_token(array_result))
            elif token == TokenizedExpression.STRING_DELIMITER:
                if prev_token == TokenizedExpression.STRING_DELIMITER:
                    self.push_node(self.node_from_token(symbols.ROXX_EMPTY_STRING))
                delimiters_to_use = TokenizedExpression.TOKEN_DELIMITERS if in_string else TokenizedExpression.STRING_DELIMITER
            else:
                if delimiters_to_use == TokenizedExpression.STRING_DELIMITER:
                    self.push_node(Node(NodeTypes.RAND, token.replace(TokenizedExpression.ESCAPED_QUOTE_PLACEHOLDER, TokenizedExpression.ESCAPED_QUOTE)))
                elif token not in TokenizedExpression.TOKEN_DELIMITERS and token != TokenizedExpression.PRE_POST_STRING_CHAR:
                    self.push_node(self.node_from_token(token))

        return self.result_list

    def node_from_token(self, obj):
        if isinstance(obj, list):
            return Node(NodeTypes.RAND, obj)
        elif isinstance(obj, dict):
            return Node(NodeTypes.RAND, obj)
        elif str(obj) in self.operators:
            return Node(NodeTypes.RATOR, obj)
        elif is_string(obj):
            if obj == symbols.ROXX_TRUE:
                return Node(NodeTypes.RAND, True)
            if obj == symbols.ROXX_FALSE:
                return Node(NodeTypes.RAND, False)
            if obj == symbols.ROXX_UNDEFINED:
                return Node(NodeTypes.RAND, TokenTypes.UNDEFINED)

            token_type = TokenTypes.from_token(obj)
            if token_type == TokenTypes.STRING:
                return Node(NodeTypes.RAND, obj[1:-2])
            if token_type == TokenTypes.NUMBER:
                try:
                    return Node(NodeTypes.RAND, float(obj))
                except Exception as ex:
                    raise ValueError('Excepted Number, got \'%s\' (%s): %s' % (obj, token_type, ex))
        return Node(NodeTypes.UNKNOWN, None)
