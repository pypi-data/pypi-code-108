# -*- coding: utf-8 -*-
from tokenize import Token

from pip_services3_expressions.io.IScanner import IScanner
from pip_services3_expressions.tokenizers.ISymbolState import ISymbolState
from pip_services3_expressions.tokenizers.ITokenizer import ITokenizer
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.SymbolRootNode import SymbolRootNode


class GenericSymbolState(ISymbolState):
    """
    The idea of a symbol is a character that stands on its own, such as an ampersand or a parenthesis.
    For example, when tokenizing the expression **(is_ready)& (is_willing) **, a typical
    tokenizer would return 7 tokens, including one for each parenthesis and one for the ampersand.
    Thus a series of symbols such as **)&( ** becomes three tokens, while a series of letters
    such as **is_ready** becomes a single word token.

    Multi-character symbols are an exception to the rule that a symbol is a standalone character.  
    For example, a tokenizer may want less-than-or-equals to tokenize as a single token. This class
    provides a method for establishing which multi-character symbols an object of this class should
    treat as single symbols. This allows, for example, **"cat &lt;= dog"** to tokenize as 
    three tokens, rather than splitting the less-than and equals symbols into separate tokens.

    By default, this state recognizes the following multi-character symbols:
    **!=, :-, &lt;=, &gt;=**
    """

    def __init__(self):
        super(GenericSymbolState, self).__init__()
        self.__symbols = SymbolRootNode()

    def next_token(self, scanner: IScanner, tokenizer: ITokenizer) -> Token:
        """
        Return a symbol token from a scanner.

        :param scanner: A textual string to be tokenized.
        :param tokenizer: A tokenizer class that controls the process.
        :return: The next token from the top of the stream.
        """
        return self.__symbols.next_token(scanner)

    def add(self, value, token_type: TokenType):
        """
        Add a multi-character symbol.
        
        :param value: The symbol to add, such as "=:="
        :param token_type:
        """
        self.__symbols.add(value, token_type)
